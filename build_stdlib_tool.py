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
sakanalytics-boundary = "sakanalytics:main"

[tool.setuptools]
py-modules = ["sakanalytics"]
'''
CLI = '''
def main(argv=None):
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Check a numeric boundary and optionally move inside by epsilon.")
    parser.add_argument("value", type=float)
    parser.add_argument("--lo", type=float)
    parser.add_argument("--hi", type=float)
    parser.add_argument("--eps", type=float)
    args = parser.parse_args(argv)
    if not math.isfinite(args.value) or any(x is not None and not math.isfinite(x) for x in (args.lo, args.hi)):
        parser.error("value and bounds must be finite")
    if args.lo is not None and args.hi is not None and args.lo >= args.hi:
        parser.error("lo must be less than hi")
    try:
        result, hit = lift(args.value, args.eps, lo=args.lo, hi=args.hi)
    except EpsilonError as exc:
        parser.error(str(exc))
    print(json.dumps({"original": args.value, "value": result, "boundary": hit}, allow_nan=False))
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
