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
* a proposition with an empty row or column in its table (the condition holds for every unit, so there is no
  converse or inverse to turn), or a form at exactly 0 or 1, is refused: that boundary is the ε question.

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
    return math.log(p / (1 - p))


def _expit(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def _form_counts(a: int, b: int, c: int, d: int) -> dict:
    """(hold, n) of each form on the table a: A and B, b: A and not B, c: not A and B, d: not A and not B."""
    return {"original": (a, a + b), "contrapositive": (d, b + d), "converse": (a, a + c), "inverse": (d, c + d)}


def rates(a: int, b: int, c: int, d: int) -> dict:
    """The four forms' rates on one table; None for a form with no unit to judge (empty denominator)."""
    return {f: (num / den if den else None) for f, (num, den) in _form_counts(a, b, c, d).items()}


def build(*, converse, inverse, contrapositive, n) -> dict:
    """The 2x2 table of n synthetic units whose converse, inverse and contrapositive rates are the dials.

    Keyword-only on purpose: there is no ``original`` argument. Counts are the exact solution rounded to integers
    (largest remainder); ``dial_error`` is how far the realized rates are from the dials after that rounding.
    """
    if type(n) is not int or n < 4:
        raise MoshimoError(f"n must be an integer of at least 4, got {n!r}")
    dials = {name: _check_dial(name, value)
             for name, value in (("converse", converse), ("inverse", inverse), ("contrapositive", contrapositive))}
    oc, oi, ocp = (_odds(dials[k]) for k in DIALS)
    # a/c = oc, d/c = oi, d/b = ocp. Scale c = 1.
    relative = {"a": oc, "b": oi / ocp, "c": 1.0, "d": oi}
    total = sum(relative.values())
    counts = dict(zip(CELLS, sl._apportion([n * relative[k] / total for k in CELLS], n)))
    if min(counts.values()) < 1:
        raise MoshimoError(f"a cell rounds to 0 units with n={n} and dials {dials}; use a larger n or dials further from 0 and 1")
    a, b, c, d = (counts[k] for k in CELLS)
    forms = _form_counts(a, b, c, d)
    rate = {f: num / den for f, (num, den) in forms.items()}
    odds_original = oc * ocp / oi
    return {
        "synthetic": True, "n": n, "dials": dials, "cells": counts,
        "forms": {f: {"n": den, "hold": num, "rate": num / den} for f, (num, den) in forms.items()},
        "counterexamples": {"original": b, "contrapositive": b, "converse": c, "inverse": c},
        "original_rate_exact": odds_original / (1 + odds_original),
        # the ranking score of proposition generation (rule_search.py): tp = a, fp = b, fn = c, tn = d. All four sums are > 0.
        "mcc": (a * d - b * c) / math.sqrt((a + b) * (a + c) * (b + d) * (c + d)),
        # the same numerator a*d - b*c over the margins: mcc^2 = informedness * markedness
        "informedness": rate["converse"] + rate["contrapositive"] - 1,
        "markedness": rate["original"] + rate["inverse"] - 1,
        "dial_error": max(abs(num / den - dials[f]) for f, (num, den) in forms.items() if f in dials),
    }


def sweep(dial: str, values, *, converse, inverse, contrapositive, n) -> list[dict]:
    """Turn one dial through ``values`` with the other two held. ``dial`` can only be a dial name (never 'original')."""
    base = dict(converse=converse, inverse=inverse, contrapositive=contrapositive)
    if dial not in base:
        _check_dial(dial, 0.5)  # raises the "not a dial" message
    return [build(**{**base, dial: v}, n=n) for v in values]


def load_record(path, proposition_id: str) -> dict:
    """One record of a propositions.jsonl (the cycle's proposition ledger output) by its id."""
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            if record.get("id") == proposition_id:
                return record
    raise MoshimoError(f"no proposition {proposition_id!r} in {path}")


def anchor(record: dict) -> dict:
    """The dials and n of a real proposition, read from its 2x2 table (metrics tp, fp, fn, tn).

    Feeding the result to ``build`` gives back the proposition's own cells. Refused when a form has no unit to judge.
    """
    m = record.get("metrics") or {}
    try:
        a, b, c, d = (int(m[k]) for k in ("tp", "fp", "fn", "tn"))
    except (KeyError, TypeError, ValueError):
        raise MoshimoError(f"proposition {record.get('id')!r} has no 2x2 table (metrics tp, fp, fn, tn)") from None
    r = rates(a, b, c, d)
    empty = [f for f in DIALS if r[f] is None]
    if empty:
        raise MoshimoError(f"proposition {record.get('id')!r}: no unit to judge its {', '.join(empty)} "
                           "(a row or column of its table is empty), so there is nothing to turn")
    return {**{f: r[f] for f in DIALS}, "n": a + b + c + d}


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
        mark = lambda k: f"**{t['dials'][k]:.3f}**" if k == dial else f"{t['dials'][k]:.3f}"  # noqa: E731
        row = [str(t["n"]), *(mark(k) for k in DIALS), *(str(t["cells"][k]) for k in CELLS),
               f"{t['forms']['original']['rate']:.3f}", f"{t['original_rate_exact']:.3f}",
               f"{t['informedness']:.3f}", f"{t['markedness']:.3f}", f"{t['mcc']:.3f}"]
        if readouts:
            row += [readouts[i]["forms"]["original"]["verdict"], str(readouts[i]["judgement_code"])]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_headroom(tables: list[dict], heads: list[dict], dial: str | None) -> str:
    head = ["row", "original", "threshold", "gap (logit)", *(f"{k} at break-even (now)" for k in DIALS)]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for t, h in zip(tables, heads):
        label = f"{dial}={t['dials'][dial]:.3f}" if dial else "base"
        lines.append("| " + " | ".join([label, f"{h['original_rate_exact']:.3f}", f"{h['threshold']:.3f}", f"{h['gap']:+.3f}",
                                         *(f"{h['breakeven'][k]:.3f} ({t['dials'][k]:.3f})" for k in DIALS)]) + " |")
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
    if a.ledger is not None and (a.id is None or any(v is not None for v in given.values())):
        ap.error("--ledger needs --id, and then the dials and n come from the proposition: leave "
                 "--converse, --inverse, --contrapositive and --n out")
    if a.ledger is None and any(v is None for v in given.values()):
        ap.error("give --converse, --inverse, --contrapositive and --n, or start from a real proposition "
                 "with --ledger and --id")
    try:
        threshold = a.threshold
        if a.ledger is not None:
            record = load_record(a.ledger, a.id)
            base, threshold = anchor(record), (threshold if threshold is not None else record.get("threshold"))
        else:
            base = given
        dial = None
        if a.sweep:
            dial, _, values = a.sweep.partition("=")
            tables = sweep(dial, [float(v) for v in values.split(",")], **base)
        else:
            tables = [build(**base)]
        readouts = [readout(t, a.readout) for t in tables] if a.readout else None
        heads = [headroom(t["dials"], threshold) for t in tables] if threshold is not None else None
    except (ValueError, OSError) as exc:  # MoshimoError, a value that is not a number, or an unreadable ledger
        ap.error(str(exc))
    except ModuleNotFoundError as exc:
        ap.error(f"--readout needs polars and PythDRagoras (PYTHONPATH=<Aoi>/pythdragoras): {exc}")
    print(render(tables, dial, readouts))
    if heads:
        print("\n" + render_headroom(tables, heads, dial))
    if a.json:
        a.json.parent.mkdir(parents=True, exist_ok=True)
        a.json.write_text(json.dumps({"anchor": {"ledger": str(a.ledger), "id": a.id} if a.ledger else None, "tables": tables,
                                      "readouts": readouts, "headroom": heads}, ensure_ascii=False, indent=2,
                                     allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
