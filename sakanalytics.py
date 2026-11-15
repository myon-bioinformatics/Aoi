"""SakAnalytics — データから、まだ見ぬ構造を。 汎用版（標準ライブラリだけ・この 1 ファイルで動く）

題材を問わない計算だけを置く。チーム×シーズンの指標（試合の記録から作る表）は npb/team_season.py。

  📐 check_eps / lift   値がちょうど境界にあるかを見つけ、頼まれたときだけ ε だけ持ち上げる（下の説明）
  📊 describe            件数・和・平均・中央値・最小・最大・母標準偏差
  ⚖️ compare / boundary  2 組の比較と、境界の判定（CLI）

  python sakanalytics.py describe 1 2 3
  python sakanalytics.py compare --before 1 2 --after 2 3
  python sakanalytics.py boundary 0 --lo 0 --eps 1e-6

ε as a symbol: one place that detects a value sitting exactly on a boundary and, only when asked, lifts it by ε.

The value of ε and how to treat a lifted value afterwards are not decided. So:

* nothing here chooses a number: ``eps`` is always passed in by the caller, and ``None`` (the default everywhere) means
  "do not lift". With ``eps=None`` every output is what it was before; the boundary is still detected and counted.
* a lifted value is always reported next to the original (``lift`` returns ``(value, hit)``; the sites keep the cells or
  rows that were lifted), so the result can be re-read, or redone with another ε, once the handling is decided.

What is lifted: a value that is a *boundary of a parameter or of a table* and sits there exactly, so that a formula
further on degenerates. Today that is the undamped wave λ = 0 (sakanalytics.wave_basis) and a zero cell of a real 2x2
table (moshimo_box.anchor, where it makes a rate exactly 0 or 1 and its logit infinite).

What is not lifted, on purpose:

* 0/0, an empty row or column: the quantity is undefined, not small. It stays null / "no unit".
* a true zero in the data, or a value that is correctly 0 (sin(0) = 0 for the first point of a wave: the angle is not a
  boundary of anything).
* the denominator of a noisy ratio (k_eff = logit / log(RF/RA)): lifting it pulls the value toward a fake number, so it
  stays null behind a named threshold (K_EFF_MIN_LOG_RATIO).

``lift`` tests ``x == bound`` exactly. A near-zero that is not exactly on the bound is the business of the named
tolerances (sakanalytics.TOLERANCES), not of ε.
"""
from __future__ import annotations

import math


class EpsilonError(ValueError):
    pass


def check_eps(eps, name: str = "eps") -> float | None:
    """``None`` (do not lift) or a finite number strictly greater than 0. There is no default value."""
    if eps is None:
        return None
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) or not math.isfinite(eps) or eps <= 0:
        raise EpsilonError(f"{name} must be None or a finite number greater than 0, got {eps!r}")
    return float(eps)


def lift(x: float, eps: float | None, *, lo: float | None = None, hi: float | None = None) -> tuple[float, bool]:
    """``(value, hit)``: ``hit`` is True when ``x`` is exactly on ``lo`` or ``hi``.

    With ``eps`` the value is moved inside by ε (``lo + eps`` or ``hi - eps``); with ``eps=None`` it is returned as it
    was, so a caller can detect the boundary without lifting. Other values pass through untouched.
    """
    eps = check_eps(eps)
    if lo is None and hi is None:
        raise EpsilonError("lift needs a bound: lo, hi or both")
    if None not in (lo, hi) and eps is not None and not 2 * eps < hi - lo:
        raise EpsilonError(f"eps={eps:g} does not fit inside [{lo}, {hi}]")
    if lo is not None and x == lo:
        return (lo if eps is None else lo + eps), True
    if hi is not None and x == hi:
        return (hi if eps is None else hi - eps), True
    return x, False

def parse_numbers(chunks):
    values = []
    # Rejoin shell-split arguments so `1, 2` works without quotes.
    for line in " ".join(chunks).splitlines():
        for field in line.split(","):
            if not field.strip():
                raise ValueError("empty value in input; remove missing fields")
            for token in field.split():
                try:
                    number = float(token)
                except ValueError:
                    raise ValueError("invalid number: " + repr(token)) from None
                if not math.isfinite(number):
                    raise ValueError("number must be finite: " + repr(token))
                values.append(number)
    if not values:
        raise ValueError("provide at least one number")
    return values


def read_csv_column(path, column):
    import csv
    with open(path, encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream)
        if not rows.fieldnames or column not in rows.fieldnames:
            raise ValueError("CSV column not found: " + repr(column))
        if len(set(rows.fieldnames)) != len(rows.fieldnames):
            raise ValueError("duplicate CSV column names")
        values = []
        for line, row in enumerate(rows, 2):
            cell = row.get(column)
            if cell is None or not cell.strip():
                raise ValueError("missing value in CSV row " + str(line))
            try:
                number = float(cell.strip())
            except ValueError:
                raise ValueError("invalid number in CSV row " + str(line) + ": " + repr(cell)) from None
            if not math.isfinite(number):
                raise ValueError("non-finite number in CSV row " + str(line))
            values.append(number)
        return values


def describe(values):
    import statistics
    if not values or any(not math.isfinite(v) for v in values):
        raise ValueError("provide at least one finite number")
    return {"count": len(values), "sum": sum(values), "mean": statistics.mean(values),
            "median": statistics.median(values), "min": min(values), "max": max(values),
            "population_stddev": statistics.pstdev(values)}


def main(argv=None):
    import argparse
    import json
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("describe", "compare", "boundary", "-h", "--help"):
        argv.insert(0, "boundary")
    class NumericArgumentParser(argparse.ArgumentParser):
        def _parse_optional(self, token):
            # argparse only recognizes a narrow set of negative-number spellings.
            # Keep finite numeric lists (including scientific notation) as values,
            # without swallowing unknown flags such as --befor or -x.
            # A trailing comma can continue in the next shell argument; the
            # complete joined input is still validated after argument parsing.
            if token.startswith("-") and not token.startswith("--"):
                try:
                    parse_numbers([token.rstrip(",")])
                except ValueError:
                    pass
                else:
                    return None
            return super()._parse_optional(token)

    parser = NumericArgumentParser(description="Summarize and compare numbers or check boundaries.")
    sub = parser.add_subparsers(dest="command", required=True)
    desc = sub.add_parser("describe")
    desc.add_argument("values", nargs="*", help="numbers separated by spaces or commas; - reads stdin")
    desc.add_argument("--file", help="read a CSV file")
    desc.add_argument("--column", help="CSV header to analyze (requires --file)")
    comp = sub.add_parser("compare")
    comp.add_argument("--before", nargs="+", required=True)
    comp.add_argument("--after", nargs="+", required=True)
    boundary = sub.add_parser("boundary")
    boundary.add_argument("value", type=float)
    boundary.add_argument("--lo", type=float)
    boundary.add_argument("--hi", type=float)
    boundary.add_argument("--eps", type=float)
    args = parser.parse_args(argv)
    try:
        if args.command == "describe":
            if args.file and args.values:
                parser.error("use numbers or --file, not both")
            if args.column and not args.file:
                parser.error("--column requires --file")
            if args.file:
                if args.column:
                    values = read_csv_column(args.file, args.column)
                else:
                    with open(args.file, encoding="utf-8-sig") as stream:
                        values = parse_numbers([stream.read()])
            else:
                if args.values.count("-") > 1:
                    parser.error("stdin can only be read once")
                values = parse_numbers([sys.stdin.read() if value == "-" else value for value in args.values])
            result = describe(values)
        elif args.command == "compare":
            if (args.before + args.after).count("-") > 1:
                parser.error("stdin can only be read once")
            before = describe(parse_numbers([sys.stdin.read() if x == "-" else x for x in args.before]))
            after = describe(parse_numbers([sys.stdin.read() if x == "-" else x for x in args.after]))
            delta = after["mean"] - before["mean"]
            result = {"before": before, "after": after, "mean_difference": delta,
                      "mean_relative_change": delta / before["mean"] if before["mean"] else None,
                      "none_reason": None if before["mean"] else "before_mean_zero"}
        else:
            if not math.isfinite(args.value) or any(x is not None and not math.isfinite(x) for x in (args.lo, args.hi)):
                parser.error("value and bounds must be finite")
            if args.lo is not None and args.hi is not None and args.lo >= args.hi:
                parser.error("lo must be less than hi")
            value, hit = lift(args.value, args.eps, lo=args.lo, hi=args.hi)
            result = {"original": args.value, "value": value, "boundary": hit}
        print(json.dumps(result, allow_nan=False))
    except (ValueError, EpsilonError, OverflowError, OSError) as exc:
        parser.error(str(exc))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
