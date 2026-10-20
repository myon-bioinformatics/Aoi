#!/usr/bin/env python3
"""Shrink the polars surface of research_digest.collect to stdlib polars_min.py.

Same shape as Aoi scripts/shrink_polars.py (PR 92), for a smaller call:

- survey / analyze reuse scripts/shrink_module.py (Aoi PR 89). ast sees DataFrame and col only.
- trace wraps real polars in a proxy, runs collect, and records every attribute the call touches.
- absent does not import polars. Each AttributeError from the traceback adds one name and collect
  is run again until the fixture succeeds.
- generate writes shrink/polars_min.py and fails if ast finds a module name without an implementation.
  ``--check`` fails when the committed file differs.

    python scripts/shrink_polars.py survey
    python scripts/shrink_polars.py analyze
    python scripts/shrink_polars.py trace
    python scripts/shrink_polars.py absent
    python scripts/shrink_polars.py generate --out shrink/polars_min.py [--check]

trace needs polars installed. absent and generate do not. Both trace and absent need this tree
overlaid on Aoi (vendor/markdown.py) because research_digest imports that helper.
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
import tempfile
import traceback
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shrink_module as sm  # noqa: E402

DEFAULT_ENTRIES = ["research_digest.py:collect"]
KNOWN = ("DataFrame", "col")
METHOD_SURFACE = (
    "DataFrame.explode",
    "DataFrame.filter",
    "DataFrame.join",
    "DataFrame.iter_rows",
    "Expr.is_not_null",
)
# Order absent-mode AttributeError tracebacks hit on the two-note fixture.
# Attribute lookup runs before arguments, so filter is seen before col().is_not_null().
DISCOVERY_ORDER = (
    "polars.DataFrame",
    "DataFrame.explode",
    "DataFrame.filter",
    "polars.col",
    "Expr.is_not_null",
    "DataFrame.join",
    "DataFrame.iter_rows",
)
EXPECTED_CALLS = {
    "polars.DataFrame": 2,
    "DataFrame.explode": 1,
    "polars.col": 1,
    "Expr.is_not_null": 1,
    "DataFrame.filter": 1,
    "DataFrame.join": 1,
    "DataFrame.iter_rows": 1,
}
EXPECTED = set(DISCOVERY_ORDER)

# Implementation emitted into shrink/polars_min.py. Keep the behavior next to the discovery
# lists above: explode drops empty lists and keeps nulls; filter is is_not_null only; join is
# left on one column and does not match null keys.
BODY = '''
__all__ = ["DataFrame", "col"]
__version__ = "0+min"


def _build():
    def _kind(value):
        if value is None:
            return None
        if type(value) is bool:
            return "bool"
        if type(value) is int:
            return "int"
        if type(value) is str:
            return "str"
        raise TypeError("polars_min does not accept " + type(value).__name__)

    def _column_kind(column, values, as_list):
        kinds = set()
        for value in values:
            if as_list:
                if value is None:
                    continue
                if not isinstance(value, list):
                    raise TypeError("polars_min column " + column + " mixes lists and scalars")
                for element in value:
                    kind = _kind(element)
                    if kind:
                        kinds.add(kind)
            else:
                if isinstance(value, list):
                    raise TypeError("polars_min column " + column + " mixes lists and scalars")
                kind = _kind(value)
                if kind:
                    kinds.add(kind)
        if len(kinds) > 1:
            raise TypeError("polars_min column " + column + " mixes " + ", ".join(sorted(kinds)))
        inner = next(iter(kinds)) if kinds else "null"
        return ("list:" + inner) if as_list else inner

    def _ingest(data):
        if isinstance(data, dict):
            columns = list(data)
            seqs = []
            width = None
            for column in columns:
                value = data[column]
                if isinstance(value, str) or not isinstance(value, (list, tuple)):
                    raise TypeError("polars_min column " + column + " must be a list")
                seq = list(value)
                if width is None:
                    width = len(seq)
                elif len(seq) != width:
                    raise ValueError(
                        "polars_min columns differ in height: "
                        + column + " has " + str(len(seq)) + ", expected " + str(width)
                    )
                seqs.append(seq)
            rows = []
            for index in range(width or 0):
                rows.append({column: seq[index] for column, seq in zip(columns, seqs)})
            kinds = {column: _column_kind(column, [row[column] for row in rows], False) for column in columns}
            return columns, rows, kinds
        if isinstance(data, list):
            if not data:
                raise ValueError("polars_min will not infer a schema from an empty list")
            if not all(isinstance(row, dict) for row in data):
                raise TypeError("polars_min list constructor expects dict rows")
            columns = []
            seen = set()
            for row in data:
                for key in row:
                    if key not in seen:
                        seen.add(key)
                        columns.append(key)
            rows = [{column: row[column] if column in row else None for column in columns} for row in data]
            kinds = {}
            for column in columns:
                as_list = any(isinstance(row[column], list) for row in rows)
                kinds[column] = _column_kind(column, [row[column] for row in rows], as_list)
            return columns, rows, kinds
        raise TypeError("polars_min DataFrame data must be a dict of columns or a list of rows")

    class Expr:
        __slots__ = ("_fn", "_kind")

        def __init__(self, fn, kind):
            self._fn = fn
            self._kind = kind

        def is_not_null(self):
            return Expr(lambda row, fn=self._fn: fn(row) is not None, "is_not_null")

        def __bool__(self):
            raise TypeError("polars_min expressions cannot be used as a boolean")

        def __getattr__(self, name):
            raise AttributeError("Expr." + name)

    class DataFrame:
        __slots__ = ("_columns", "_rows", "_kinds")

        def __init__(self, data=None, schema=None, *, schema_overrides=None, strict=True,
                     orient=None, infer_schema_length=100, nan_to_null=False, height=None):
            if (schema is not None or schema_overrides is not None or strict is not True
                    or orient is not None or infer_schema_length != 100 or nan_to_null is not False
                    or height is not None):
                raise NotImplementedError("polars_min DataFrame accepts data only")
            columns, rows, kinds = _ingest(data)
            self._columns = columns
            self._rows = rows
            self._kinds = kinds

        @classmethod
        def _from(cls, columns, rows, kinds):
            self = object.__new__(cls)
            self._columns = list(columns)
            self._rows = rows
            self._kinds = dict(kinds)
            return self

        def explode(self, columns, *more_columns, empty_as_null=False, keep_nulls=True):
            if (more_columns or type(columns) is not str or empty_as_null is not False
                    or keep_nulls is not True):
                raise NotImplementedError("polars_min explode takes one column name")
            if columns not in self._columns:
                raise KeyError(columns)
            kind = self._kinds[columns]
            if not kind.startswith("list:"):
                raise TypeError("polars_min explode expects a list column: " + columns)
            # Polars default: empty lists disappear, a null list becomes a null scalar.
            # The scalar dtype is the list element type, or Null when no element was typed.
            out = []
            for row in self._rows:
                value = row[columns]
                if value is None:
                    out.append(dict(row))
                elif isinstance(value, list):
                    for element in value:
                        copied = dict(row)
                        copied[columns] = element
                        out.append(copied)
                else:
                    raise TypeError("polars_min explode expects a list column: " + columns)
            kinds = dict(self._kinds)
            kinds[columns] = kind.split(":", 1)[1]
            return DataFrame._from(self._columns, out, kinds)

        def filter(self, *predicates, **constraints):
            if constraints or len(predicates) != 1:
                raise NotImplementedError("polars_min filter takes one expression")
            pred = predicates[0]
            if (type(pred).__module__ != type(self).__module__ or type(pred).__name__ != "Expr"
                    or pred._kind != "is_not_null"):
                raise NotImplementedError("polars_min filter only evaluates col().is_not_null()")
            return DataFrame._from(
                self._columns, [row for row in self._rows if pred._fn(row) is True], self._kinds,
            )

        def join(self, other, on=None, how="inner", *, left_on=None, right_on=None, suffix="_right",
                 validate="m:m", nulls_equal=False, coalesce=None, maintain_order=None, build_side="auto"):
            if (how != "left" or type(on) is not str or left_on is not None or right_on is not None
                    or suffix != "_right" or validate != "m:m" or nulls_equal is not False
                    or coalesce is not None or maintain_order is not None or build_side != "auto"):
                raise NotImplementedError("polars_min join is on=column, how='left' only")
            if type(other).__module__ != type(self).__module__ or type(other).__name__ != "DataFrame":
                raise TypeError("polars_min join expects a polars_min DataFrame")
            if on not in self._columns or on not in other._columns:
                raise KeyError(on)
            if self._kinds[on] != other._kinds[on]:
                raise TypeError(
                    "polars_min join keys don't match: " + on + " "
                    + self._kinds[on] + " vs " + other._kinds[on]
                )
            overlap = [column for column in other._columns if column != on and column in self._columns]
            if overlap:
                raise NotImplementedError("polars_min join does not suffix overlapping columns: " + ", ".join(overlap))
            # Null keys do not match, including null-to-null. Left row order is kept.
            buckets = {}
            for row in other._rows:
                key = row[on]
                if key is None:
                    continue
                buckets.setdefault(key, []).append(row)
            right_cols = [column for column in other._columns if column != on]
            out = []
            for row in self._rows:
                matches = buckets.get(row[on]) if row[on] is not None else None
                if not matches:
                    copied = dict(row)
                    for column in right_cols:
                        copied[column] = None
                    out.append(copied)
                else:
                    for match in matches:
                        copied = dict(row)
                        for column in right_cols:
                            copied[column] = match[column]
                        out.append(copied)
            kinds = dict(self._kinds)
            for column in right_cols:
                kinds[column] = other._kinds[column]
            return DataFrame._from(list(self._columns) + right_cols, out, kinds)

        def iter_rows(self, *, named=False, buffer_size=512):
            if named is not True or buffer_size != 512:
                raise NotImplementedError("polars_min iter_rows is named=True only")
            for row in self._rows:
                yield {column: row[column] for column in self._columns}

        def __getattr__(self, name):
            raise AttributeError("DataFrame." + name)

    def col(name):
        if type(name) is not str:
            raise TypeError("polars_min col expects a string column name")

        def fn(row, name=name):
            if name not in row:
                raise KeyError(name)
            return row[name]

        return Expr(fn, "col")

    return DataFrame, col


DataFrame, col = _build()
del _build


def __getattr__(name):
    raise AttributeError(name)
'''


def generate_text(ast_names: list[str], sources: list[str]) -> str:
    if set(ast_names) != set(KNOWN):
        raise SystemExit(
            f"polars_min implements {list(KNOWN)}; ast reached {sorted(ast_names) or '(none)'}"
        )
    head = (
        '"""Minimal stdlib polars for research_digest.collect.\n'
        "Generated by scripts/shrink_polars.py. Do not edit by hand.\n\n"
        "Entry: " + ", ".join(sources) + "\n"
        "AST names: " + ", ".join(sorted(ast_names)) + "\n"
        "Methods the AST cannot see (proxy and absent-polars tracebacks): "
        + ", ".join(METHOD_SURFACE) + "\n"
        "Limits: explode is one column name (empty lists dropped, nulls kept); "
        "filter is col().is_not_null() only; join is left on one string key, null keys do not match, "
        "and overlapping non-key columns are rejected; iter_rows(named=True) only. "
        "Scalars are str, int, bool, or None, and one column cannot mix those kinds "
        "(polars 2.0.0 coerces bool into an int column; this module rejects that mix). "
        "A join key whose values never showed a scalar type (empty lists, or only nulls) "
        "does not match a typed key. "
        "Any other polars name raises AttributeError. research_digest.py still imports polars.\n"
        '"""\n'
    )
    return head + BODY


def _entries(given: list[str]) -> list[str]:
    return given or list(DEFAULT_ENTRIES)


def _require_aoi() -> None:
    markdown = ROOT.parent / "vendor" / "markdown.py"
    if not markdown.is_file():
        raise SystemExit(f"overlay this tree onto Aoi/nagoyaction; missing {markdown}")


def build_fixture(root: Path) -> Path:
    """Two research notes plus propositions jsonl. One id is missing a judgement."""
    cycle = root / "cycle"
    (cycle / "research").mkdir(parents=True)
    (cycle / "outputs").mkdir()
    (cycle / "research" / "R2-plain.md").write_text(
        "# R2: 表のない記録\n\n記録: 2026-10-01\n\n本文だけ。\n",
        encoding="utf-8",
    )
    (cycle / "research" / "R18-example.md").write_text(
        "# R18: 2026年での確かめ（手順の事前登録）\n\n"
        "記録: 2026-10-04。計算を始める前に書いた。\n\n"
        "## 主に見る命題と、読み方（先に決める）\n\n"
        "| 命題 | 内容 | 読み方 |\n"
        "|---|---|---|\n"
        "| **P52**（式1） | 条件 | 逆の判例が**2件以上**、判例が**3件以上** |\n"
        "| P999 | unknown | 判例を記録 |\n",
        encoding="utf-8",
    )
    (cycle / "propositions.toml").write_text('[[proposition]]\nid = "P52"\n', encoding="utf-8")
    (cycle / "outputs" / "propositions.jsonl").write_text(
        '{"id": "P52", "judgement": {"code": 1}}\n',
        encoding="utf-8",
    )
    (cycle / "FINDINGS.md").write_text("# Findings\n\nP52: exit 1\n", encoding="utf-8")
    return cycle


def _project_frames(extracted) -> list[str]:
    frames = []
    for frame in extracted:
        try:
            rel = Path(frame.filename).resolve().relative_to(ROOT)
        except ValueError:
            continue
        frames.append(f"{rel.as_posix()}:{frame.lineno}:{frame.name}")
    return frames


def _print_uses(title: str, files: dict[str, Counter]) -> None:
    print(title)
    if not files:
        print("  (none)")
        return
    for name, counts in files.items():
        body = ", ".join(f"{key}×{value}" for key, value in counts.most_common())
        print(f"  {name}: {sum(counts.values())} uses, {len(counts)} names: {body}")


def cmd_survey() -> int:
    found = sm.survey("polars")
    _print_uses("module attributes (methods on returned values are invisible to ast):", found)
    digest = found.get("research_digest.py", Counter())
    print(
        "research_digest.py AST: "
        + (", ".join(f"{key}×{value}" for key, value in digest.most_common()) or "(none)")
    )
    return 0


def cmd_analyze(entries: list[str]) -> int:
    used, visited = sm.analyze("polars", entries)
    print("entries:", ", ".join(entries))
    print("  reached:", ", ".join(visited) or "(none)")
    print("  uses:", ", ".join(f"{key}×{value}" for key, value in sorted(used.items())) or "(none)")
    return 0


def _load_collect():
    sys.path.insert(0, str(ROOT))
    import research_digest
    return research_digest


def cmd_trace() -> int:
    """Proxy real polars, run the fixture through collect, print attribute tracebacks."""
    _require_aoi()
    real = importlib.import_module("polars")
    events: list[tuple[str, str]] = []

    def record(name: str) -> None:
        stack = " <- ".join(_project_frames(traceback.extract_stack()[:-2]))
        events.append((name, stack))

    class Guard:
        __slots__ = ("_inner",)

        def __init__(self, inner):
            object.__setattr__(self, "_inner", inner)

        def __getattr__(self, name):
            if name.startswith("__"):
                raise AttributeError(name)
            inner = object.__getattribute__(self, "_inner")
            record(f"{type(inner).__name__}.{name}")
            attr = getattr(inner, name)
            if not callable(attr):
                return wrap(attr)

            def wrapper(*args, **kwargs):
                return wrap(attr(*[unwrap(arg) for arg in args], **{key: unwrap(val) for key, val in kwargs.items()}))

            return wrapper

    def unwrap(value):
        if isinstance(value, Guard):
            return object.__getattribute__(value, "_inner")
        return value

    def wrap(value):
        if isinstance(value, (str, int, float, bool, list, tuple, dict, type(None), bytes)):
            return value
        if inspect.isgenerator(value):
            return value
        return Guard(value)

    def _from_collect() -> bool:
        # polars constructs list columns by calling polars.Series. That lookup must see the
        # real class; only attribute reads whose caller is research_digest are part of the surface.
        for frame in inspect.stack(0):
            path = frame.filename.replace("\\", "/")
            if path.endswith("/scripts/shrink_polars.py"):
                continue
            if "/site-packages/polars/" in path or path.endswith("/polars/__init__.py"):
                return False
            return path.endswith("/research_digest.py")
        return False

    class Proxy(types.ModuleType):
        def __getattr__(self, name):
            if name.startswith("__"):
                raise AttributeError(name)
            attr = getattr(real, name)
            if not _from_collect():
                return attr
            record(f"polars.{name}")
            if not callable(attr):
                return wrap(attr)

            def wrapper(*args, **kwargs):
                return wrap(attr(*[unwrap(arg) for arg in args], **{key: unwrap(val) for key, val in kwargs.items()}))

            return wrapper

    proxy = Proxy("polars")
    proxy.__file__ = getattr(real, "__file__", None)
    proxy.__path__ = list(getattr(real, "__path__", []))
    proxy.__package__ = "polars"
    sys.modules["polars"] = proxy
    digest = _load_collect()
    with tempfile.TemporaryDirectory() as tmp:
        notes, _, _ = digest.collect(build_fixture(Path(tmp)))
    counts = Counter(name for name, _ in events)
    print(f"fixture notes={len(notes)}")
    seen = []
    for name, stack in events:
        if name in seen:
            continue
        seen.append(name)
        print(name)
        print("  " + stack)
    print("calls:", ", ".join(f"{key}×{counts[key]}" for key in EXPECTED_CALLS))
    missed = [name for name in seen if not name.startswith("polars.")]
    print("missed by ast: " + ", ".join(missed))
    if counts != Counter(EXPECTED_CALLS) or set(seen) != EXPECTED:
        print(f"trace surface {dict(counts)} != {EXPECTED_CALLS}", file=sys.stderr)
        return 1
    return 0


class _AbsentState:
    allow: set[str]
    order: list[str]


_STATE = _AbsentState()
_STATE.allow = set()
_STATE.order = []
_IMPL = None


def _min_impl():
    global _IMPL
    if _IMPL is None:
        spec = importlib.util.spec_from_file_location("_polars_min_impl", ROOT / "shrink" / "polars_min.py")
        if spec is None or spec.loader is None:
            raise SystemExit("shrink/polars_min.py is missing; generate it first")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _IMPL = module
    return _IMPL


def _absent_unwrap(value):
    if isinstance(value, _AbsentGuard):
        return object.__getattribute__(value, "_inner")
    return value


def _absent_wrap(value):
    if isinstance(value, (str, int, float, bool, list, tuple, dict, type(None), bytes)):
        return value
    if inspect.isgenerator(value):
        return value
    return _AbsentGuard(value)


class _AbsentGuard:
    __slots__ = ("_inner",)

    def __init__(self, inner):
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        inner = object.__getattribute__(self, "_inner")
        key = f"{type(inner).__name__}.{name}"
        if key not in _STATE.allow:
            raise AttributeError(key)
        attr = getattr(inner, name)
        if not callable(attr):
            return _absent_wrap(attr)

        def wrapper(*args, **kwargs):
            return _absent_wrap(attr(
                *[_absent_unwrap(arg) for arg in args],
                **{item: _absent_unwrap(val) for item, val in kwargs.items()},
            ))

        return wrapper


class _AbsentModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        key = f"polars.{name}"
        if key not in _STATE.allow:
            raise AttributeError(key)
        attr = getattr(_min_impl(), name)
        if not callable(attr):
            return _absent_wrap(attr)

        def wrapper(*args, **kwargs):
            return _absent_wrap(attr(
                *[_absent_unwrap(arg) for arg in args],
                **{item: _absent_unwrap(val) for item, val in kwargs.items()},
            ))

        return wrapper


def cmd_absent() -> int:
    """Grow the allowed surface from AttributeError tracebacks with polars not imported."""
    _require_aoi()
    if "polars" in sys.modules and not isinstance(sys.modules["polars"], _AbsentModule):
        raise SystemExit("absent must run in a process that has not imported polars")
    _STATE.allow = set()
    _STATE.order = []
    module = _AbsentModule("polars")
    module.__file__ = str(ROOT / "shrink" / "polars_min.py")
    sys.modules["polars"] = module
    digest = _load_collect()
    with tempfile.TemporaryDirectory() as tmp:
        cycle = build_fixture(Path(tmp))
        for step in range(1, 20):
            try:
                notes, _, _ = digest.collect(cycle)
            except AttributeError as exc:
                key = exc.args[0] if exc.args else ""
                frames = _project_frames(traceback.extract_tb(exc.__traceback__))
                print(f"step {step}: AttributeError: {key}")
                print("  " + " <- ".join(frames))
                if not isinstance(key, str) or not key or key in _STATE.allow or key.startswith("__"):
                    traceback.print_exc()
                    return 1
                _STATE.allow.add(key)
                _STATE.order.append(key)
                continue
            print(f"succeeded notes={len(notes)}")
            print("discovered: " + ", ".join(_STATE.order))
            if tuple(_STATE.order) != DISCOVERY_ORDER or _STATE.allow != EXPECTED:
                print(
                    f"discovered {_STATE.order} != {list(DISCOVERY_ORDER)}",
                    file=sys.stderr,
                )
                return 1
            return 0
    print("gave up before collect succeeded", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("survey", "analyze", "trace", "absent", "generate"))
    parser.add_argument("entries", nargs="*")
    parser.add_argument("--out")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "survey":
        return cmd_survey()
    entries = _entries(args.entries)
    if args.command == "analyze":
        return cmd_analyze(entries)
    if args.command == "trace":
        return cmd_trace()
    if args.command == "absent":
        return cmd_absent()
    used, _ = sm.analyze("polars", entries)
    text = generate_text(sorted(used), entries)
    if not args.out:
        raise SystemExit("generate needs --out")
    out = Path(args.out)
    if args.check:
        if not out.is_file() or out.read_text(encoding="utf-8") != text:
            print(f"{out} does not match generate output; run generate again", file=sys.stderr)
            return 1
        print(f"{out} ok")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}: {', '.join(sorted(used))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
