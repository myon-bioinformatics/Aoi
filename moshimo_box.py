"""Moshimo Box (もしもボックス): turn the dials of a proposition's converse, inverse and contrapositive.

"If A then B" has four forms, and all four read the same 2x2 table of units
(a: A and B, b: A and not B, c: not A and B, d: not A and not B):

    original        A  -> B     rate a / (a + b)   precision                       counterexamples b
    contrapositive  ¬B -> ¬A    rate d / (b + d)   specificity                     shares b with the original
    converse        B  -> A     rate a / (a + c)   recall                          counterexamples c
    inverse         ¬A -> ¬B    rate d / (c + d)   negative predictive value       shares c with the converse

The box has three dials: converse, inverse, contrapositive. **There is no dial for the original.**
With the number of units fixed, three rates fix the table, so the original's rate is a readout, never an input.
Its odds are exactly the product of the dials' odds:

    logit(original) = logit(converse) + logit(contrapositive) - logit(inverse)

so, with the other two dials held, raising the converse or the contrapositive raises the original, and raising the
inverse lowers it. "What does the proposition do when its other forms move?" is answered by turning one dial.

Where it sits: proposition generation. pythdragoras/rule_search.py ranks a candidate rule by the Matthews correlation
(MCC) of this same table. Ranking by the original's own accuracy invites tuning toward it, so the box does the
opposite: it never touches the original, turns the other three forms, and reads out what happens to the original's
rate and to the ranking score (``mcc``). The score splits over the four forms: with the same numerator ad - bc,
informedness J = converse + contrapositive - 1 (over the product of the B and not-B margins) and markedness
MK = original + inverse - 1 (= P(B | A) - P(B | not A), over the product of the A and not-A margins), and
mcc^2 = J * MK exactly. The original appears only inside MK, paired with the inverse.

Three ways to use it besides turning the dials by hand:

* ``--ledger propositions.jsonl --id P1`` starts the dials from a real proposition (its own converse, inverse and
  contrapositive and its n, read from its 2x2 table), so "what if its inverse were 0.7?" is asked of a real rule.
* ``--threshold 0.75`` (read from the proposition with --ledger) prints the original's room above the threshold, one
  number in logit units, and for each dial the value that would put the original exactly on the threshold with the
  other two held. The point estimate meeting the threshold is not the verdict flipping: the verdict also asks the
  confidence interval to clear it, and ``--readout`` shows the verdict at any dial value.
* a proposition with a form at exactly 0 or 1 (a zero cell: no counterexample, or nothing missed) is refused, and so
  is one with an empty row or column (the condition holds for every unit, so there is no converse or inverse to
  turn): that boundary is the ε question.
* ``--eps 1e-6`` (with --ledger) is the opt-in answer for the zero cell only: the empty cell is lifted to ε (a count,
  epsilon.lift) and the dials exist. ε's value is not decided, so nothing is lifted unless it is given, and it is never
  defaulted. A lifted table has fractional cells ("exact"), so it has no units and no --readout. An empty row or column
  stays refused: 0/0 is undefined, not small. The numbers that depend on ε are the logit-based ones (the original's
  logit and the headroom move with log(1/ε)); the MCC is defined at a zero cell and moves only by about ε.

Synthetic only: the units are model checks, never NPB observations. There is no randomness. A dial must be strictly
between 0 and 1: at 0 or 1 a cell is empty and the table degenerates. How to treat that boundary (the ε question) is
not decided, so the box stops with a message instead of substituting a number.

    python moshimo_box.py --converse 0.6 --inverse 0.7 --contrapositive 0.8 --n 168
    python moshimo_box.py --converse 0.6 --inverse 0.7 --contrapositive 0.8 --n 168 --sweep converse=0.3,0.5,0.7,0.9
    python moshimo_box.py --ledger cycles/c001-chunichi/outputs/propositions.jsonl --id P1 --sweep inverse=0.6,0.8,0.9
    # read the table back through PythDRagoras' own evaluator (PYTHONPATH=<Aoi>/pythdragoras):
    python moshimo_box.py --converse 0.6 --inverse 0.7 --contrapositive 0.8 --n 168 --readout usually
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import synthetic_league as sl
from epsilon import check_eps, lift

DIALS = ("converse", "inverse", "contrapositive")
FORMS = ("original", "contrapositive", "converse", "inverse")
CELLS = ("a", "b", "c", "d")
SIGN = {"converse": 1, "contrapositive": 1, "inverse": -1}  # logit(original) = sum of SIGN * logit(dial)


class MoshimoError(ValueError):
    pass


def _check_dial(name: str, value) -> float:
    if name not in DIALS:
        raise MoshimoError(f"{name!r} is not a dial. The dials are {', '.join(DIALS)}; "
                           "the original proposition's rate cannot be set, it is read out from them")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 < value < 1:
        raise MoshimoError(f"dial {name} must be a number strictly between 0 and 1, got {value!r} "
                           "(0 and 1 leave a cell empty; how to treat that boundary is not decided)")
    return float(value)


def _odds(p: float) -> float:
    return p / (1 - p)


def _logit(p: float) -> float:
    return math.log(p) - math.log1p(-p)


def _expit(x: float) -> float:
    """Stable logistic function; extreme logits may round to 0 or 1."""
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    z = math.exp(x)
    return z / (1 + z)


def _form_counts(a: int, b: int, c: int, d: int) -> dict:
    """(hold, n) of each form on the table a: A and B, b: A and not B, c: not A and B, d: not A and not B."""
    return {"original": (a, a + b), "contrapositive": (d, b + d), "converse": (a, a + c), "inverse": (d, c + d)}


def rates(a: int, b: int, c: int, d: int) -> dict:
    """The four forms' rates on one table; None for a form with no unit to judge (empty denominator)."""
    return {f: (num / den if den else None) for f, (num, den) in _form_counts(a, b, c, d).items()}


def build(*, converse, inverse, contrapositive, n, exact=False) -> dict:
    """The 2x2 table of n synthetic units whose converse, inverse and contrapositive rates are the dials.

    Keyword-only on purpose: there is no ``original`` argument. Counts are the exact solution rounded to integers
    (largest remainder); ``dial_error`` is how far the realized rates are from the dials after that rounding.
    ``exact=True`` keeps the unrounded solution instead (fractional cells, n any finite number above 0): a table with a
    lifted cell (epsilon.py) has a cell of ε units, which no integer table can hold.
    """
    try:
        finite_n = math.isfinite(n) if isinstance(n, (int, float)) else False
    except OverflowError:
        finite_n = False
    if exact:
        if isinstance(n, bool) or not isinstance(n, (int, float)) or not finite_n or n <= 0:
            raise MoshimoError(f"n must be a finite number above 0 for an exact table, got {n!r}")
    elif type(n) is not int or n < 4:
        raise MoshimoError(f"n must be an integer of at least 4, got {n!r}")
    dials = {name: _check_dial(name, value)
             for name, value in (("converse", converse), ("inverse", inverse), ("contrapositive", contrapositive))}
    lc, li, lcp = (_logit(dials[k]) for k in DIALS)
    # a/c = odds(converse), d/c = odds(inverse), d/b = odds(contrapositive).
    # Normalize in log space: the direct ratio odds(inverse)/odds(contrapositive)
    # can overflow even though every input probability is valid.
    logs = dict(zip(CELLS, (lc, li - lcp, 0.0, li)))
    peak = max(logs.values())
    shifted = {k: logs[k] - peak for k in CELLS}
    log_total = math.log(math.fsum(math.exp(v) for v in shifted.values()))
    try:
        scale = float(n)
    except OverflowError:
        raise MoshimoError("n cannot be represented as a finite float64 table total") from None
    if not math.isfinite(scale):
        raise MoshimoError("n cannot be represented as a finite float64 table total")
    # Include n before exponentiating so a representable subnormal count is
    # not lost merely because its normalized weight underflows first.
    expected = {k: math.exp(math.log(scale) + shifted[k] - log_total) for k in CELLS}
    if exact:
        counts = expected
    else:
        try:
            counts = dict(zip(CELLS, sl._apportion([expected[k] for k in CELLS], n)))
        except ValueError:
            raise MoshimoError("float64 cell estimates cannot conserve this integer total; "
                               "use a smaller n or exact mode") from None
        if min(counts.values()) < 1:
            raise MoshimoError(f"a cell rounds to 0 units with n={n} and dials {dials}; use a larger n or dials further from 0 and 1")
    a, b, c, d = (counts[k] for k in CELLS)
    forms = _form_counts(a, b, c, d)
    if any(not math.isfinite(den) or den <= 0 for _, den in forms.values()):
        raise MoshimoError("table margins underflow to zero or overflow in float64; "
                           "these dials and n cannot represent all four forms; use less extreme dials or a different n")
    rate = {f: num / den for f, (num, den) in forms.items()}
    # Factor each product by its own margins. No count products or product of
    # four tiny margins: both can underflow (or overflow) before division.
    mcc = (math.sqrt(a / (a + b)) * math.sqrt(d / (b + d))
           * math.sqrt(a / (a + c)) * math.sqrt(d / (c + d))
           - math.sqrt(b / (a + b)) * math.sqrt(c / (a + c))
           * math.sqrt(b / (b + d)) * math.sqrt(c / (c + d)))
    return {
        "synthetic": True, "exact": exact, "n": n, "dials": dials, "cells": counts,
        "forms": {f: {"n": den, "hold": num, "rate": num / den} for f, (num, den) in forms.items()},
        "counterexamples": {"original": b, "contrapositive": b, "converse": c, "inverse": c},
        "original_rate_exact": _expit(_logit(dials["converse"]) + _logit(dials["contrapositive"]) - _logit(dials["inverse"])),
        # the ranking score of proposition generation (rule_search.py): tp = a, fp = b, fn = c, tn = d. All four sums are > 0.
        "mcc": mcc,
        # the same numerator a*d - b*c over the margins: mcc^2 = informedness * markedness
        "informedness": rate["converse"] + rate["contrapositive"] - 1,
        "markedness": rate["original"] + rate["inverse"] - 1,
        "dial_error": max(abs(num / den - dials[f]) for f, (num, den) in forms.items() if f in dials),
    }


def sweep(dial: str, values, *, converse, inverse, contrapositive, n, exact=False) -> list[dict]:
    """Turn one dial through ``values`` with the other two held. ``dial`` can only be a dial name (never 'original')."""
    base = dict(converse=converse, inverse=inverse, contrapositive=contrapositive)
    if dial not in base:
        _check_dial(dial, 0.5)  # raises the "not a dial" message
    return [build(**{**base, dial: v}, n=n, exact=exact) for v in values]


def load_record(path, proposition_id: str) -> dict:
    """One record of a propositions.jsonl (the cycle's proposition ledger output) by its id."""
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            record = json.loads(line)
            if not isinstance(record, dict):
                raise MoshimoError(f"{path}:{line_number}: ledger record must be a JSON object")
            if record.get("id") == proposition_id:
                return record
    raise MoshimoError(f"no proposition {proposition_id!r} in {path}")


def table_of(record: dict, eps: float | None = None) -> tuple[dict, dict]:
    """``(cells, lifted)`` of a real proposition's 2x2 table (metrics tp, fp, fn, tn; a rule_search row works the same).

    Counts must be non-negative Python integers (JSON integers); bool, floats and strings are refused, never coerced.
    With ``eps`` a zero cell is lifted to ε (``lifted`` says which); without it nothing changes. A table with an empty
    row or column is refused either way: 0/0 is undefined, not small, so ε does not lift it.
    """
    m = record.get("metrics") or record
    try:
        counts = {cell: m[key] for cell, key in zip(CELLS, ("tp", "fp", "fn", "tn"))}
    except (KeyError, TypeError, ValueError):
        raise MoshimoError(f"proposition {record.get('id')!r} has no 2x2 table (metrics tp, fp, fn, tn)") from None
    for cell, key in zip(CELLS, ("tp", "fp", "fn", "tn")):
        value = counts[cell]
        if type(value) is not int or value < 0:
            raise MoshimoError(f"proposition {record.get('id')!r}: count {key} must be a non-negative integer "
                               f"(bool, floats and strings are not counts), got {value!r}")
    eps = check_eps(eps)
    # all four forms, the original included: with a + b = 0 the original is 0/0, and lifting a and b by the same ε would
    # manufacture a rate of 1/2 out of nothing
    empty = [f for f in FORMS if rates(*counts.values())[f] is None]
    if empty:
        raise MoshimoError(f"proposition {record.get('id')!r}: no unit to judge its {', '.join(empty)} (a row or column "
                           "of its table is empty: 0/0 is undefined, not small, so eps does not lift it), so there is nothing to turn")
    cells, lifted = {}, {}
    for cell, v in counts.items():
        cells[cell], hit = lift(v, eps, lo=0)
        if hit and eps is not None:
            lifted[cell] = eps
    return cells, lifted


def anchor(record: dict, eps: float | None = None) -> dict:
    """The dials and n of a real proposition, read from its 2x2 table (see ``table_of``).

    Feeding the result to ``build`` gives back the table's own cells; a table with a lifted cell needs ``exact=True``.
    Refused when a form has no unit to judge.
    """
    cells, lifted = table_of(record, eps)
    r = rates(*cells.values())
    dials = {f: r[f] for f in DIALS}
    bad = [f for f, v in dials.items() if lifted and not 0 < v < 1]
    if bad:
        raise MoshimoError(f"eps={eps:g} is too small to move the {', '.join(bad)} off the boundary in float64 for "
                           "these counts; use a larger eps")
    return {**dials, "n": sum(cells.values())}


def headroom(dials: dict, threshold) -> dict:
    """The original's room above a rate threshold, and where each dial would put it on the line.

    logit(original) = logit(converse) + logit(contrapositive) - logit(inverse), so the room is one number in logit
    units (``gap``, negative when the original is below the threshold) and each dial can absorb all of it alone:
    ``breakeven[dial]`` is the value that dial would need, the other two held, for the original's rate to equal the
    threshold. Point estimate only: the verdict also asks the confidence interval to clear the threshold.
    """
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not 0 < threshold < 1:
        raise MoshimoError(f"threshold must be a number strictly between 0 and 1, got {threshold!r}")
    d = {k: _check_dial(k, dials[k]) for k in DIALS}
    logits = {k: _logit(d[k]) for k in DIALS}
    original = sum(SIGN[k] * logits[k] for k in DIALS)
    gap = original - _logit(threshold)
    return {"threshold": float(threshold), "original_rate_exact": _expit(original), "gap": gap,
            "breakeven": {k: _expit(logits[k] - SIGN[k] * gap) for k in DIALS}}


def units(table: dict) -> list[dict]:
    """The table as synthetic units with 0/1 columns A and B, in the shape PythDRagoras' evaluator reads."""
    if table.get("exact"):
        raise MoshimoError("an exact table has fractional cells (a lifted cell is ε units): there are no units to list")
    flags = {"a": (1, 1), "b": (1, 0), "c": (0, 1), "d": (0, 0)}
    rows = []
    for cell in CELLS:
        for _ in range(table["cells"][cell]):
            name = f"moshimo{len(rows) + 1:04d}"
            rows.append({"season": 2000, "team": name, "team_name": name, "A": flags[cell][0], "B": flags[cell][1]})
    return rows


def readout(table: dict, strength: str = "usually") -> dict:
    """Read the table back through PythDRagoras (propositions.evaluate): the code the cycle itself uses.

    Needs ``PYTHONPATH=<Aoi>/pythdragoras``. Returns each form's n / hold / rate / verdict, the original's MCC
    and the judgement code.
    """
    import polars as pl
    import propositions as pr

    prop = {"id": "MOSHIMO", "statement": "if A then B (synthetic)", "strength": strength,
            "if": [{"col": "A", "op": "==", "value": 1}], "then": [{"col": "B", "op": "==", "value": 1}]}
    result = pr.evaluate(prop, pl.DataFrame(units(table)))
    return {"strength": strength, "judgement_code": result["judgement"]["code"], "mcc": result["metrics"]["mcc"],
            "forms": {f["form"]: {k: f[k] for k in ("n", "hold", "rate", "verdict")} for f in result["forms"]}}


def render(tables: list[dict], dial: str | None, readouts: list[dict] | None = None) -> str:
    head = ["n", *(f"{k} (dial)" for k in DIALS), "a", "b", "c", "d", "original (readout)", "original exact", "J", "MK", "mcc"]
    if readouts:
        head += ["original verdict", "judgement"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for i, t in enumerate(tables):
        f = (lambda v: f"{v:.8g}") if t.get("exact") else (lambda v: f"{v:.3f}")  # exact tables sit near the boundary: more digits
        mark = lambda k: f"**{f(t['dials'][k])}**" if k == dial else f(t["dials"][k])  # noqa: E731
        row = [f"{t['n']:g}" if t.get("exact") else str(t["n"]), *(mark(k) for k in DIALS),
               *((f"{t['cells'][k]:.6g}" if t.get("exact") else str(t["cells"][k])) for k in CELLS),
               f(t["forms"]["original"]["rate"]), f(t["original_rate_exact"]), f(t["informedness"]), f(t["markedness"]), f(t["mcc"])]
        if readouts:
            row += [readouts[i]["forms"]["original"]["verdict"], str(readouts[i]["judgement_code"])]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_headroom(tables: list[dict], heads: list[dict], dial: str | None) -> str:
    head = ["row", "original", "threshold", "gap (logit)", *(f"{k} at break-even (now)" for k in DIALS)]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for t, h in zip(tables, heads):
        f = (lambda v: f"{v:.8g}") if t.get("exact") else (lambda v: f"{v:.3f}")  # exact tables sit near the boundary
        label = f"{dial}={f(t['dials'][dial])}" if dial else "base"
        lines.append("| " + " | ".join([label, f(h["original_rate_exact"]), f"{h['threshold']:.3f}", f"{h['gap']:+.3f}",
                                         *(f"{f(h['breakeven'][k])} ({f(t['dials'][k])})" for k in DIALS)]) + " |")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in DIALS:
        ap.add_argument(f"--{k}", type=float, help=f"rate of the {k}, strictly between 0 and 1")
    ap.add_argument("--n", type=int, help="number of synthetic units")
    ap.add_argument("--ledger", type=Path, metavar="PROPOSITIONS_JSONL",
                    help="start the dials from a real proposition of this file (with --id) instead of giving them")
    ap.add_argument("--id", help="proposition id in --ledger, e.g. P1")
    ap.add_argument("--threshold", type=float, help="rate threshold of the strength word (0.75 for usually): also print "
                    "each dial's break-even value; taken from the proposition with --ledger")
    ap.add_argument("--eps", type=float, metavar="EPS",
                    help="with --ledger: lift a zero cell of the real table to EPS units so its dials exist. ε's value is not "
                         "decided, so nothing is lifted unless you give it. The tables are then exact (fractional cells): no --readout")
    ap.add_argument("--sweep", metavar="DIAL=V1,V2,...", help="turn one dial through these values, the other two held")
    ap.add_argument("--readout", metavar="STRENGTH", choices=("always", "almost_always", "usually", "more_often_than_not"),
                    help="also read each table back through PythDRagoras, with this strength word")
    ap.add_argument("--json", type=Path, help="write the tables (and readouts) as JSON")
    ap.add_argument("--original", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    if a.original is not None:
        ap.error("the original proposition's rate cannot be set: it is read out from the three dials")
    given = {k: getattr(a, k) for k in (*DIALS, "n")}
    if a.ledger is None and a.id is not None:
        ap.error("--id goes with --ledger")
    if a.eps is not None and a.ledger is None:
        ap.error("--eps lifts a zero cell of a real table: it goes with --ledger and --id")
    if a.eps is not None and a.readout:
        ap.error("--readout needs whole units; with --eps the tables have fractional cells")
    if a.ledger is not None and (a.id is None or any(v is not None for v in given.values())):
        ap.error("--ledger needs --id, and then the dials and n come from the proposition: leave "
                 "--converse, --inverse, --contrapositive and --n out")
    if a.ledger is None and any(v is None for v in given.values()):
        ap.error("give --converse, --inverse, --contrapositive and --n, or start from a real proposition "
                 "with --ledger and --id")
    try:
        threshold, lifted, exact = a.threshold, {}, a.eps is not None
        if a.ledger is not None:
            record = load_record(a.ledger, a.id)
            base, threshold = anchor(record, a.eps), (threshold if threshold is not None else record.get("threshold"))
            lifted = table_of(record, a.eps)[1]
        else:
            base = given
        dial = None
        if a.sweep:
            dial, _, values = a.sweep.partition("=")
            tables = sweep(dial, [float(v) for v in values.split(",")], **base, exact=exact)
        else:
            tables = [build(**base, exact=exact)]
        readouts = [readout(t, a.readout) for t in tables] if a.readout else None
        heads = [headroom(t["dials"], threshold) for t in tables] if threshold is not None else None
    except (ValueError, OSError) as exc:  # MoshimoError, a value that is not a number, or an unreadable ledger
        ap.error(str(exc))
    except ModuleNotFoundError as exc:
        ap.error(f"--readout needs polars and PythDRagoras (PYTHONPATH=<Aoi>/pythdragoras): {exc}")
    print(render(tables, dial, readouts))
    if exact:
        print(f"\nε = {a.eps:g} (units). Lifted cell(s): {', '.join(lifted) or 'none (no cell was zero)'}. "
              "The table is exact: fractional cells, so logit-based numbers (original, headroom) move with log(1/ε).")
    if heads:
        print("\n" + render_headroom(tables, heads, dial))
    if a.json:
        try:
            a.json.parent.mkdir(parents=True, exist_ok=True)
            a.json.write_text(json.dumps({"anchor": {"ledger": str(a.ledger), "id": a.id, "eps": a.eps, "lifted_cells": lifted} if a.ledger else None,
                                          "tables": tables,
                                          "readouts": readouts, "headroom": heads}, ensure_ascii=False, indent=2,
                                         allow_nan=False) + "\n", encoding="utf-8")
        except (ValueError, OSError) as exc:
            ap.error(f"cannot write JSON output {a.json}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
