"""Moshimo Pool (もしもプール): the whole pool of formulas a rule search looked at, and which of them the dials cannot take.

pythdragoras/rule_search.py tries every formula the candidate file allows ((c1 and c2) or (c3 and c4) ...), puts each
on the 2x2 table of the target, ranks them by the Matthews correlation (MCC) and keeps the top K. Only those can be
registered as propositions. Everything else never gets that far, so it never meets the converse, inverse and
contrapositive that a registered proposition is judged by, and that is where the zero cells are:

    a = 0   original and converse are 0           b = 0   original and contrapositive are 1 (no counterexample)
    c = 0   converse and inverse are 1            d = 0   contrapositive and inverse are 0

A zero cell puts two forms on the boundary at once (the counterexamples b are shared by original and contrapositive,
c by converse and inverse), and an empty row or column leaves a form with no unit at all. The Moshimo Box refuses such
a table unless an ε is given for a zero cell (moshimo_box ``--eps``; an empty row or column stays refused: 0/0 is
undefined, not small). How to treat the boundary (the ε question) is not decided. This module counts them ahead of
time, for the pool as a whole and against the cut of the top K, and substitutes nothing. rule_search itself gives an empty margin the
score 0.0 without saying so; ``silent_zero_mcc`` counts those.

The enumeration is plain Python integers as bit sets (numpy is not needed) and follows rule_search: the same units
(exclusions of the analysis config applied, units with an empty value in a used column dropped), the same formulas
(a term never uses a column twice) and the same ordering key. Ranks here are by MCC alone: 1 + the number of formulas
with a strictly higher MCC, so tied formulas share a rank.

    python moshimo_pool.py --season outputs/season.jsonl --config analysis.toml --candidates rule_candidates.toml \\
        --top 20 --list 10 --json pool.json
"""
from __future__ import annotations

import argparse
import bisect
import itertools
import json
import math
import operator
import tomllib
from collections import Counter
from pathlib import Path

import polars as pl

import moshimo_box as mb

OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}
CELL_MEANING = {"a": "A and B", "b": "A and not B", "c": "not A and B", "d": "not A and not B"}


class PoolError(ValueError):
    pass


def _check(conds: list[dict]) -> None:
    for c in conds:
        if not isinstance(c, dict) or not {"col", "op", "value"} <= set(c) or c["op"] not in OPS:
            raise PoolError(f"a condition is {{col, op, value}} with op one of {', '.join(OPS)}: {c}")


def load_units(season: Path, exclude: list[dict], columns: list[str]) -> pl.DataFrame:
    """The units rule_search.main searches: seasons of the config's [[exclude]] removed (each with a reason), then units
    with an empty value in a used column dropped."""
    for e in exclude:
        if not str(e.get("reason", "")).strip():
            raise PoolError(f"an exclusion needs a reason: {e}")
    df = pl.read_ndjson(season)
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise PoolError(f"no such column in {season}: {', '.join(missing)}")
    return df.filter(~pl.col("season").is_in([int(e["season"]) for e in exclude])).drop_nulls(columns)


def _mask(df: pl.DataFrame, conds: list[dict]) -> int:
    """Bit i is set when unit i meets every condition."""
    expr = pl.lit(True)
    for c in conds:
        expr = expr & OPS[c["op"]](pl.col(c["col"]), pl.lit(c["value"]))
    return sum(1 << i for i, flag in enumerate(df.select(x=expr)["x"].to_list()) if flag)


def _mcc(a: int, b: int, c: int, d: int) -> tuple[float, bool]:
    """MCC of the table, and whether a margin is empty (rule_search scores that 0.0 without saying so)."""
    q = (a + b) * (a + c) * (b + d) * (c + d)
    return ((a * d - b * c) / math.sqrt(q), False) if q else (0.0, True)


def _logic_key(groups: list[list[dict]]) -> str:
    """rule_search's tie-break: only col, op and value count (records of where a condition came from do not)."""
    slim = [[c if set(c) == {"col", "op", "value"} else {k: c[k] for k in ("col", "op", "value")} for c in g] for g in groups]
    return json.dumps(slim, ensure_ascii=False)


def _boundary(a: int, b: int, c: int, d: int) -> dict:
    """The forms a table puts at 0 or 1 (a rate) or leaves without a unit (None)."""
    return {f: r for f, r in mb.rates(a, b, c, d).items() if r is None or r in (0.0, 1.0)}


def scan(df: pl.DataFrame, target: list[dict], candidates: list[dict], *, max_terms: int = 2, max_conds: int = 2,
         top: int = 20, listing: int = 10) -> dict:
    """Every formula of the pool on the target's 2x2 table: a census by zero cells, the top K (as rule_search keeps
    them) and the ``listing`` best-ranked formulas that sit on the boundary."""
    if isinstance(top, bool) or not isinstance(top, int) or top < 1:
        raise PoolError(f"top must be an integer of at least 1, got {top!r}")
    _check(target)
    _check(candidates)
    n = df.height
    full = (1 << n) - 1
    y = _mask(df, target)
    cand = [(c, _mask(df, [c])) for c in candidates]
    terms = []
    for k in range(1, max_conds + 1):
        for combo in itertools.combinations(cand, k):
            if len({c["col"] for c, _ in combo}) < k:
                continue
            m = full
            for _, cm in combo:
                m &= cm
            terms.append(([c for c, _ in combo], m))
    census, scores, best, edge, silent, total = Counter(), [], [], [], 0, 0
    distinct: dict[str, set] = {}  # unit sets, per zero-cell pattern: formulas that pick the same units are one rule

    def keep(bucket, size, key, row):
        bisect.insort(bucket, (key, row), key=lambda t: t[0])
        del bucket[size:]

    for k in range(1, max_terms + 1):
        for combo in itertools.combinations(terms, k):
            m = 0
            for _, tm in combo:
                m |= tm
            a, b, c, d = (m & y).bit_count(), (m & ~y & full).bit_count(), (~m & y & full).bit_count(), n - (m | y).bit_count()
            mcc, empty = _mcc(a, b, c, d)
            total += 1
            silent += empty
            zero = "".join(cell for cell, v in zip("abcd", (a, b, c, d)) if v == 0)
            census[zero] += 1
            distinct.setdefault(zero, set()).add(m)
            r, conds = round(mcc, 12), sum(len(g) for g, _ in combo)
            scores.append(r)
            wanted = [(best, top)] + ([(edge, listing)] if zero and listing else [])
            for bucket, size in wanted:
                if len(bucket) == size and (-r, conds) > bucket[-1][0][:2]:
                    continue
                groups = [g for g, _ in combo]
                key = (-r, conds, _logic_key(groups))
                if len(bucket) == size and key >= bucket[-1][0]:
                    continue
                keep(bucket, size, key, {"if_any": groups, "conditions": conds, "tp": a, "fp": b, "fn": c, "tn": d,
                                         "mcc": mcc, "zero_cells": zero})
    scores.sort()
    rank = lambda r: 1 + len(scores) - bisect.bisect_right(scores, r)  # noqa: E731
    top_rows = [row for _, row in best]
    in_top = Counter(row["zero_cells"] for row in top_rows)
    tables = [{"zero_cells": zero or "interior", "formulas": count, "unit_sets": len(distinct[zero]),
               "share": count / total if total else None, "in_top": in_top[zero], "at_boundary": _boundary(*_filled_except(zero)) if zero else {}}
              for zero, count in sorted(census.items(), key=lambda kv: (kv[0] != "", -kv[1], kv[0]))]
    edge_rows = [{**row, "rank": rank(round(row["mcc"], 12)), "at_boundary": _boundary(row["tp"], row["fp"], row["fn"], row["tn"])}
                 for _, row in edge]
    boundary_total = total - census[""]
    return {"units": n, "target_units": y.bit_count(), "candidates": len(candidates), "terms": len(terms),
            "max_terms": max_terms, "max_conds": max_conds, "formulas": total, "top": top,
            "cut": top_rows[-1]["mcc"] if len(top_rows) == top else None, "silent_zero_mcc": silent, "tables": tables,
            "boundary": {"formulas": boundary_total, "unit_sets": sum(len(v) for z, v in distinct.items() if z), "in_top": sum(v for z, v in in_top.items() if z), "best": edge_rows},
            "top_rows": top_rows}


def _filled_except(zero: str) -> tuple:
    """A table with exactly these cells empty (the others 1): which forms that puts on the boundary does not depend on the counts."""
    return tuple(0 if cell in zero else 1 for cell in "abcd")


def _forms(at_boundary: dict) -> str:
    return ", ".join(f"{f} has no unit" if r is None else f"{f} = {r:g}" for f, r in at_boundary.items()) or "-"


def render(result: dict) -> str:
    cut = "n/a" if result["cut"] is None else f"{result['cut']:.3f}"
    lines = [f"units {result['units']} (target true for {result['target_units']}), candidates {result['candidates']}, "
             f"terms {result['terms']}, formulas {result['formulas']} (up to {result['max_terms']} terms of "
             f"{result['max_conds']} conditions), top {result['top']} cut: MCC {cut}",
             f"empty margin scored 0.0 by rule_search: {result['silent_zero_mcc']}", "",
             "| zero cells | formulas | different unit sets | share | in the top | forms on the boundary |", "|---|---|---|---|---|---|"]
    for t in result["tables"]:
        share = "n/a" if t["share"] is None else f"{100 * t['share']:.1f}%"
        if t["zero_cells"] == "interior":
            label = "none: all four cells filled"
        else:
            label = " and ".join(f"{c} = 0 ({CELL_MEANING[c]})" for c in t["zero_cells"])
        lines.append(f"| {label} | {t['formulas']} | {t['unit_sets']} | {share} | {t['in_top']} | {_forms(t['at_boundary'])} |")
    b = result["boundary"]
    lines += ["", f"on the boundary: {b['formulas']} formulas picking {b['unit_sets']} different sets of units, "
                  f"{b['in_top']} of them in the top {result['top']}"]
    if b["best"]:
        lines += ["", "| rank by MCC | MCC | a / b / c / d | on the boundary | formula |", "|---|---|---|---|---|"]
        for r in b["best"]:
            formula = " or ".join("[" + " and ".join(f"{c['col']} {c['op']} {c['value']}" for c in g) + "]" for g in r["if_any"])
            lines.append(f"| {r['rank']} | {r['mcc']:.3f} | {r['tp']} / {r['fp']} / {r['fn']} / {r['tn']} | "
                         f"{_forms(r['at_boundary'])} | {formula} |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--season", type=Path, required=True, help="season.jsonl, one unit per line")
    ap.add_argument("--config", type=Path, required=True, help="analysis config (TOML): its [[exclude]] is applied")
    ap.add_argument("--candidates", type=Path, required=True, help="rule_search candidate file (TOML): target, candidate, max_terms, max_conds")
    ap.add_argument("--top", type=int, default=20, help="the cut: how many formulas rule_search keeps")
    ap.add_argument("--list", type=int, default=10, metavar="N", help="list the N best-ranked formulas on the boundary")
    ap.add_argument("--json", type=Path, help="write the result as JSON")
    a = ap.parse_args(argv)
    try:
        spec = tomllib.loads(a.candidates.read_text(encoding="utf-8"))
        cfg = tomllib.loads(a.config.read_text(encoding="utf-8"))
        _check([*spec["target"], *spec["candidate"]])
        cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
        result = scan(load_units(a.season, cfg.get("exclude", []), cols), spec["target"], spec["candidate"],
                      max_terms=int(spec.get("max_terms", 2)), max_conds=int(spec.get("max_conds", 2)),
                      top=a.top, listing=a.list)
    except (ValueError, OSError, KeyError, tomllib.TOMLDecodeError) as exc:
        ap.error(f"{type(exc).__name__}: {exc}")
    print(render(result))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
