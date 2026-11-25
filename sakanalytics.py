"""SakAnalytics — データから、まだ見ぬ構造を。 汎用版（標準ライブラリだけ・この 1 ファイルで動く）

題材を問わない計算だけを置く。チーム×シーズンの指標（試合の記録から作る表）は npb/team_season.py。

  📐 check_eps / lift   値がちょうど境界にあるかを見つけ、頼まれたときだけ ε だけ持ち上げる（下の説明）
  📊 describe            件数・和・平均・中央値・最小・最大・母標準偏差
  ⚖️ compare / boundary  2 組の比較と、境界の判定（CLI）
  📈 scale               非負の列を対数または線形に換算（log_scale / linear_scale / adjust_narrow / round_score）

  python sakanalytics.py describe 1 2 3
  python sakanalytics.py compare --before 1 2 --after 2 3
  python sakanalytics.py boundary 0 --lo 0 --eps 1e-6
  python sakanalytics.py scale 1 10 --anchor 10
  python sakanalytics.py scale --linear --factor 0.97 3 4

ε as a symbol: one place that detects a value sitting exactly on a boundary and, only when asked, lifts it by ε.

The value of ε and how to treat a lifted value afterwards are not decided. So:

* nothing here chooses a number: ``eps`` is always passed in by the caller, and ``None`` (the default everywhere) means
  "do not lift". With ``eps=None`` every output is what it was before; the boundary is still detected and counted.
* a lifted value is always reported next to the original (``lift`` returns ``(value, hit)``; the sites keep the cells or
  rows that were lifted), so the result can be re-read, or redone with another ε, once the handling is decided.

What is lifted: a value that is a *boundary of a parameter or of a table* and sits there exactly, so that a formula
further on degenerates. Today that is the undamped wave λ = 0 (team_season.wave_basis) and a zero cell of a real 2x2
table (moshimo_box.anchor, where it makes a rate exactly 0 or 1 and its logit infinite).

What is not lifted, on purpose:

* 0/0, an empty row or column: the quantity is undefined, not small. It stays null / "no unit".
* a true zero in the data, or a value that is correctly 0 (sin(0) = 0 for the first point of a wave: the angle is not a
  boundary of anything).
* the denominator of a noisy ratio (k_eff = logit / log(RF/RA)): lifting it pulls the value toward a fake number, so it
  stays null behind a named threshold (K_EFF_MIN_LOG_RATIO).

``lift`` tests ``x == bound`` exactly. A near-zero that is not exactly on the bound is the business of the named
tolerances (team_season.TOLERANCES), not of ε.
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
    with open(path, encoding="utf-8-sig", newline="") as stream:
        return _csv_values(stream, column)


def _csv_values(stream, column):
    import csv
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



def _require_finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be a finite number")
    return value


def _require_nonneg(value, name):
    value = _require_finite(value, name)
    if value < 0:
        raise ValueError(name + " must be nonnegative")
    return value


def _numbers(values):
    if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
        raise ValueError("values must be a nonempty iterable of finite nonnegative numbers")
    items = [_require_nonneg(value, "value") for value in values]
    if not items:
        raise ValueError("values must be a nonempty iterable of finite nonnegative numbers")
    return items


def _log1p(value, base):
    if base == math.e:
        return math.log1p(value)
    if base == 10:
        return math.log10(1 + value)
    if base == 2:
        return math.log2(1 + value)
    return math.log1p(value) / math.log(base)


def round_score(score, *, step=5):
    """Round ``score`` to a multiple of ``step``, half away from zero.

    ``step=None`` returns ``score`` unchanged. ``step`` must be positive.
    """
    score = _require_finite(score, "score")
    if step is None:
        return score
    step = _require_finite(step, "step")
    if step <= 0:
        raise ValueError("step must be positive")
    quotient = score / step
    rounded = math.floor(quotient + 0.5) if quotient >= 0 else math.ceil(quotient - 0.5)
    return rounded * step


def _apply(items, scores, floor, round_to):
    result = []
    for value, score in zip(items, scores):
        if value == 0 and floor is not None:
            result.append(floor)
        else:
            result.append(round_score(score, step=round_to))
    return result


def _optional_floor(floor):
    if floor is None:
        return None
    return _require_finite(floor, "floor")


def log_scale(values, *, anchor=None, top=90, floor=None, round_to=5, base=10):
    """Scale nonnegative values: ``top * log(1+x) / log(1+anchor)``.

    ``anchor`` defaults to the maximum of ``values``. ``round_to`` is the
    step for :func:`round_score`; ``round_to=None`` disables rounding.
    ``top=None`` returns ``log(1+x)`` in the given ``base`` (``anchor`` is
    unused) so callers that need unnormalized log1p can share this helper.

    A zero value uses ``floor`` as the final score when ``floor`` is set
    (it is not rounded). When the resolved anchor is 0, every value must
    be 0: each score is 0, or ``floor`` if set. A positive value with
    anchor 0 raises ValueError, as does a negative value or a negative
    anchor.
    """
    items = _numbers(values)
    base = _require_finite(base, "base")
    if base <= 0 or base == 1:
        raise ValueError("base must be positive and not 1")
    floor = _optional_floor(floor)
    if top is None:
        scores = [_log1p(value, base) for value in items]
        return _apply(items, scores, floor, round_to)
    top = _require_finite(top, "top")
    if anchor is None:
        anchor = max(items)
    else:
        anchor = _require_nonneg(anchor, "anchor")
    if anchor == 0:
        if any(value > 0 for value in items):
            raise ValueError("anchor must be positive when a value is positive")
        scores = [0.0] * len(items)
        return _apply(items, scores, floor, round_to)
    denom = _log1p(anchor, base)
    scores = [top * _log1p(value, base) / denom for value in items]
    return _apply(items, scores, floor, round_to)


def linear_scale(values, *, factor=1.0, floor=None, round_to=None):
    """Scale nonnegative values with ``factor * x``.

    ``round_to=None`` (the default) disables rounding. A zero value uses
    ``floor`` as the final score when ``floor`` is set (it is not rounded).
    """
    items = _numbers(values)
    factor = _require_finite(factor, "factor")
    floor = _optional_floor(floor)
    scores = [factor * value for value in items]
    return _apply(items, scores, floor, round_to)


def adjust_narrow(score, count, *, below=3, factor=0.75):
    """Shrink ``score`` when ``0 < count < below`` (else return ``score``).

    Used for a narrow footprint (default: count 1 or 2). The caller decides
    whether to round before or after; the Languages bar rule applies this
    to the unrounded score, then :func:`round_score`.
    """
    score = _require_finite(score, "score")
    count = _require_finite(count, "count")
    below = _require_finite(below, "below")
    factor = _require_finite(factor, "factor")
    if 0 < count < below:
        return score * factor
    return score


def main(argv=None):
    import argparse
    import json
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in ("describe", "compare", "boundary", "scale", "-h", "--help"):
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
    desc = sub.add_parser("describe", help="📊 summary of one list of numbers")
    desc.add_argument("values", nargs="*", help="numbers separated by spaces or commas; - reads stdin")
    desc.add_argument("--file", help="read a file, or - for UTF-8 stdin")
    desc.add_argument("--column", help="CSV header to analyze (requires --file)")
    comp = sub.add_parser("compare", help="⚖️ two summaries and the change in mean")
    comp.add_argument("--before", nargs="+", required=True, help="numbers separated by spaces or commas; - reads stdin")
    comp.add_argument("--after", nargs="+", required=True, help="numbers separated by spaces or commas; - reads stdin")
    boundary = sub.add_parser("boundary", help="📐 is the value on a bound? lift it by --eps only when asked")
    boundary.add_argument("value", type=float, help="finite number to check")
    boundary.add_argument("--lo", type=float, help="lower bound (less than --hi)")
    boundary.add_argument("--hi", type=float, help="upper bound")
    boundary.add_argument("--eps", type=float, help="lift a value on a bound by this much, greater than 0 (default: detect only)")
    def _none_or_finite(token):
        if token.lower() == "none":
            return None
        try:
            value = float(token)
        except ValueError:
            raise argparse.ArgumentTypeError("must be a finite number or none") from None
        if not math.isfinite(value):
            raise argparse.ArgumentTypeError("must be a finite number or none")
        return value
    scaler = sub.add_parser("scale", help="📈 log or linear scaling of nonnegative numbers")
    scaler.add_argument("values", nargs="*", help="nonnegative numbers separated by spaces or commas; - reads stdin")
    scaler.add_argument("--anchor", type=_none_or_finite, default=argparse.SUPPRESS, help="log denominator; default is the maximum")
    scaler.add_argument("--top", type=_none_or_finite, default=argparse.SUPPRESS, help="log numerator cap (default 90; none for unnormalized log)")
    scaler.add_argument("--base", type=float, default=argparse.SUPPRESS, help="log base (default 10)")
    scaler.add_argument("--round-to", dest="round_to", type=_none_or_finite, default=argparse.SUPPRESS, help="rounding step (default 5 for log, none for linear; none disables)")
    scaler.add_argument("--floor", type=_none_or_finite, help="final score for a zero value")
    scaler.add_argument("--linear", action="store_true", help="use linear_scale instead of log_scale")
    scaler.add_argument("--factor", type=float, help="linear factor (requires --linear; default 1)")
    args = parser.parse_args(argv)
    try:
        if args.command == "describe":
            if args.file and args.values:
                parser.error("use numbers or --file, not both")
            if args.column and not args.file:
                parser.error("--column requires --file")
            if args.file:
                if args.file == "-":
                    from io import TextIOWrapper
                    stream = TextIOWrapper(sys.stdin.buffer, encoding="utf-8-sig", newline="")
                    try:
                        values = _csv_values(stream, args.column) if args.column else parse_numbers([stream.read()])
                    finally:
                        stream.detach()
                elif args.column:
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
        elif args.command == "scale":
            if args.values.count("-") > 1:
                parser.error("stdin can only be read once")
            values = parse_numbers([sys.stdin.read() if value == "-" else value for value in args.values])
            if args.linear:
                conflict = [opt for opt in ("--anchor", "--top", "--base") if hasattr(args, opt.lstrip("-"))]
                if conflict:
                    parser.error("linear mode does not take " + ", ".join(conflict))
                factor = 1.0 if args.factor is None else args.factor
                round_to = args.round_to if hasattr(args, "round_to") else None
                scores = linear_scale(values, factor=factor, floor=args.floor, round_to=round_to)
                result = {"mode": "linear", "scores": scores}
            else:
                if args.factor is not None:
                    parser.error("--factor requires --linear")
                top = args.top if hasattr(args, "top") else 90
                base = args.base if hasattr(args, "base") else 10
                round_to = args.round_to if hasattr(args, "round_to") else 5
                anchor = args.anchor if hasattr(args, "anchor") else None
                scores = log_scale(values, anchor=anchor, top=top, floor=args.floor, round_to=round_to, base=base)
                result = {"mode": "log", "scores": scores}
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
