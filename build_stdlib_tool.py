"""Build a standalone boundary-check CLI from the canonical epsilon module."""
import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYPROJECT = '''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "sakanalytics-stdlib"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
sakanalytics = "sakanalytics:main"
sakanalytics-boundary = "sakanalytics:main"

[tool.setuptools]
py-modules = ["sakanalytics"]
'''
CLI = '''
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
    parser = argparse.ArgumentParser(description="Summarize and compare numbers or check boundaries.")
    sub = parser.add_subparsers(dest="command", required=True)
    desc = sub.add_parser("describe")
    desc.add_argument("values", type=float, nargs="+")
    comp = sub.add_parser("compare")
    comp.add_argument("--before", type=float, nargs="+", required=True)
    comp.add_argument("--after", type=float, nargs="+", required=True)
    boundary = sub.add_parser("boundary")
    boundary.add_argument("value", type=float)
    boundary.add_argument("--lo", type=float)
    boundary.add_argument("--hi", type=float)
    boundary.add_argument("--eps", type=float)
    args = parser.parse_args(argv)
    try:
        if args.command == "describe":
            result = describe(args.values)
        elif args.command == "compare":
            before, after = describe(args.before), describe(args.after)
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
    except (ValueError, EpsilonError, OverflowError) as exc:
        parser.error(str(exc))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path, help="new directory for the generated uv tool project")
    args = parser.parse_args()
    source = (ROOT / "epsilon.py").read_text(encoding="utf-8") + "\n" + CLI
    ast.parse(source)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "sakanalytics.py").write_text(source, encoding="utf-8")
    (args.out / "pyproject.toml").write_text(PYPROJECT, encoding="utf-8")


if __name__ == "__main__":
    main()
