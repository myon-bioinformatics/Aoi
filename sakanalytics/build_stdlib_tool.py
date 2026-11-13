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
