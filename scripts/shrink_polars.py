#!/usr/bin/env python3
"""DRAgoWing の load_overlap が使う polars だけを、標準ライブラリの polars_min.py に縮める（実験）。

polars は Rust 拡張なので wheel を削れない。scripts/shrink_module.py の ast は
``pl.read_ndjson`` のようなモジュール属性しか数えない。DataFrame のメソッド
（``height``、``select``、``[]``）と Expr の演算子は、次で見つける。

- trace: 本物の polars のメソッドを包み、load_overlap を動かして呼び出し元を記録する。
- absent: polars を sys.modules に置かず、AttributeError のたびにその名前だけ足して同じ実コードをやり直す。

    python scripts/shrink_polars.py survey
    python scripts/shrink_polars.py analyze
    python scripts/shrink_polars.py trace
    python scripts/shrink_polars.py absent
    python scripts/shrink_polars.py generate --out shrink/polars_min.py [--check]

analyze は import した関数をたどらない。``_mask`` は ``_cond`` を ``from propositions import`` しているので、
入口に ``pythdragoras/propositions.py:_cond`` を別に渡す。c001 の load_overlap は条件を1個ずつ
``_mask`` に渡すので ``&`` は実行されない。``_cond`` がつなぐ演算子としては実装し、同値テストで確かめる。
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
import traceback
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shrink_module as sm  # noqa: E402

# _cond は import 越しなので、load_overlap の解析だけでは列に出ない。
DEFAULT_ENTRIES = [
    "dragowing/overlap.py:load_overlap",
    "pythdragoras/propositions.py:_cond",
]
KNOWN = {"DataFrame", "Expr", "Series", "col", "lit", "read_ndjson"}
# ast では見えない。c001 が実際に踏むものと、_cond の演算子。
METHOD_SURFACE = (
    "DataFrame.height",
    "DataFrame.columns",
    "DataFrame.__getitem__",
    "DataFrame.select",
    "Series.to_list",
    "Expr.__lt__",
    "Expr.__le__",
    "Expr.__gt__",
    "Expr.__ge__",
    "Expr.__eq__",
    "Expr.__ne__",
    "Expr.__and__",
)

POLARS_BODY = r'''
import json
from pathlib import Path


def _cmp(a, b, op):
    if a is None or b is None:
        return None
    # polars は bool と文字列を "true" / "false" にして比べる。数値と文字列はエラー。
    if type(a) is bool and type(b) is str:
        a = "true" if a else "false"
    elif type(b) is bool and type(a) is str:
        b = "true" if b else "false"
    if isinstance(a, str) or isinstance(b, str):
        if isinstance(a, str) and isinstance(b, str):
            return op(a, b)
        raise TypeError(f"polars_min は文字列と数値を比べない: {a!r} と {b!r}")
    if isinstance(a, (bool, int, float)) and isinstance(b, (bool, int, float)):
        return op(a, b)
    raise TypeError(f"polars_min が比べない型: {type(a).__name__} と {type(b).__name__}")


def _kleene_and(a, b):
    """polars の bool の &。偽が片方なら偽、それ以外で null なら null。"""
    if a is False or b is False:
        return False
    if a is None or b is None:
        return None
    if a is True and b is True:
        return True
    raise TypeError(f"polars_min の & は bool か null だけ: {a!r} & {b!r}")


class Expr:
    """列か定数か、その比較・積。行の辞書を受け取って Python の値を返す。"""

    __slots__ = ("_fn", "_scalar")

    def __init__(self, fn, scalar):
        self._fn = fn
        self._scalar = scalar

    def _bin(self, other, op):
        other = other if isinstance(other, Expr) else lit(other)
        return Expr(
            lambda row, a=self._fn, b=other._fn, op=op: _cmp(a(row), b(row), op),
            self._scalar and other._scalar,
        )

    def __lt__(self, other):
        return self._bin(other, lambda x, y: x < y)

    def __le__(self, other):
        return self._bin(other, lambda x, y: x <= y)

    def __gt__(self, other):
        return self._bin(other, lambda x, y: x > y)

    def __ge__(self, other):
        return self._bin(other, lambda x, y: x >= y)

    def __eq__(self, other):
        return self._bin(other, lambda x, y: x == y)

    def __ne__(self, other):
        return self._bin(other, lambda x, y: x != y)

    def __and__(self, other):
        other = other if isinstance(other, Expr) else lit(other)
        return Expr(
            lambda row, a=self._fn, b=other._fn: _kleene_and(a(row), b(row)),
            self._scalar and other._scalar,
        )

    def __or__(self, other):
        raise NotImplementedError("polars_min に | はない（load_overlap は使わない）")

    def __invert__(self):
        raise NotImplementedError("polars_min に ~ はない（load_overlap は使わない）")

    def __bool__(self):
        raise TypeError("polars_min の式は真理値にしない")

    def __repr__(self):
        return "polars_min.Expr"


class Series:
    __slots__ = ("_values", "name")

    def __init__(self, values, name):
        self._values = list(values)
        self.name = name

    def to_list(self):
        return list(self._values)

    def __repr__(self):
        return f"polars_min.Series({self.name!r}, n={len(self._values)})"


class DataFrame:
    """行のリスト。列順はファイルで最初に見た順（大きな NDJSON では polars の順と違うことがある）。"""

    __slots__ = ("_columns", "_rows")

    def __init__(self, columns, rows):
        self._columns = list(columns)
        self._rows = rows

    @property
    def height(self):
        return len(self._rows)

    @property
    def columns(self):
        return list(self._columns)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise NotImplementedError("polars_min の DataFrame[] は列名だけ")
        if key not in self._columns:
            raise KeyError(key)
        return Series((row[key] for row in self._rows), key)

    def select(self, *exprs, **named):
        if exprs or not named:
            raise NotImplementedError("polars_min の select はキーワード引数の式だけ")
        items = []
        for name, expr in named.items():
            if not isinstance(expr, Expr):
                raise TypeError(f"polars_min の select は式だけ: {name}")
            items.append((name, expr))
        scalar = all(expr._scalar for _, expr in items)
        # 定数だけの select は polars と同じく 1 行。列を含む式は行数に放送する。
        n = 1 if scalar else self.height
        columns = [name for name, _ in items]
        rows = []
        for i in range(n):
            src = {} if scalar else self._rows[i]
            rows.append({name: expr._fn(src) for name, expr in items})
        return DataFrame(columns, rows)

    def __repr__(self):
        return f"polars_min.DataFrame(height={self.height}, columns={self._columns})"


def col(name):
    if not isinstance(name, str):
        raise TypeError("polars_min の col は文字列の列名だけ")
    return Expr(lambda row, name=name: row[name], False)


def lit(value):
    return Expr(lambda row, value=value: value, True)


def _kind(value):
    if type(value) is bool:
        return "bool"
    if type(value) is int:
        return "int"
    if type(value) is float:
        return "float"
    if type(value) is str:
        return "str"
    return type(value).__name__


def read_ndjson(source):
    """オブジェクトの NDJSON。空行は飛ばす。列の型は null を除いて一種類（int と float だけは float）。"""
    text = Path(source).read_text(encoding="utf-8")
    raw = []
    for line in text.splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError("polars_min の read_ndjson はオブジェクトの行だけ")
        raw.append(obj)
    if not raw:
        raise ValueError("polars_min は空の NDJSON の型を推論しない")
    columns = []
    seen = set()
    for obj in raw:
        for key in obj:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    values = {c: [] for c in columns}
    for obj in raw:
        for c in columns:
            value = obj[c] if c in obj else None
            if value is not None and _kind(value) not in {"bool", "int", "float", "str"}:
                raise NotImplementedError(f"polars_min が読まない値: {c} {_kind(value)}")
            values[c].append(value)
    for c, vals in values.items():
        kinds = {_kind(v) for v in vals if v is not None}
        if kinds <= {"int", "float"} and "float" in kinds:
            values[c] = [None if v is None else float(v) for v in vals]
        elif kinds <= {"bool"} or kinds <= {"int"} or kinds <= {"float"} or kinds <= {"str"} or not kinds:
            continue
        else:
            raise TypeError(f"polars_min は列 {c} の型を混ぜない: {sorted(kinds)}")
    rows = [{c: values[c][i] for c in columns} for i in range(len(raw))]
    return DataFrame(columns, rows)
'''


def generate_polars(names: list[str], sources: list[str]) -> str:
    missing = sorted(set(names) - KNOWN)
    if missing:
        raise SystemExit(f"polars_min の実装表にない名前: {missing}")
    head = (
        '"""polars の最小版。scripts/shrink_polars.py が生成した。手で直さない。\n\n'
        "入口: " + ", ".join(sources) + "\n"
        "使う名前: " + ", ".join(sorted(names)) + "\n"
        "AST では見えないので式と表にまとめて入れてある: " + ", ".join(METHOD_SURFACE) + "\n"
        '"""\n'
        "from __future__ import annotations\n"
    )
    exported = sorted(KNOWN)
    return head + POLARS_BODY + "\n__all__ = " + repr(exported) + '\n__version__ = "0+min"\n'


def _entries(given: list[str]) -> list[str]:
    return given or list(DEFAULT_ENTRIES)


def _print_uses(title: str, files: dict[str, Counter]) -> None:
    print(title)
    if not files:
        print("  (none)")
        return
    for name, counts in files.items():
        body = ", ".join(f"{k}×{v}" for k, v in counts.most_common())
        print(f"  {name}: {sum(counts.values())} uses, {len(counts)} names: {body}")


def cmd_survey() -> int:
    found = sm.survey("polars")
    drag = {k: v for k, v in found.items() if k.startswith("dragowing/")}
    rest = {k: v for k, v in found.items() if not k.startswith("dragowing/")}
    _print_uses("dragowing/ (module attributes only; methods are invisible to ast):", drag)
    names = Counter()
    for counts in drag.values():
        names += counts
    print("dragowing AST names: " + ", ".join(f"{k}×{v}" for k, v in names.most_common()))
    total = Counter()
    for counts in found.values():
        total += counts
    print(f"repo TOTAL: {sum(total.values())} uses of {len(total)} names across {len(found)} files")
    _print_uses("outside dragowing/ (not in polars_min):", rest)
    return 0


def cmd_analyze(entries: list[str]) -> int:
    alone, visited = sm.analyze("polars", ["dragowing/overlap.py:load_overlap"])
    print("load_overlap alone does not follow `from propositions import _cond`")
    print("  reached:", ", ".join(visited))
    print("  uses:", ", ".join(f"{k}×{v}" for k, v in sorted(alone.items())) or "(none)")
    used, visited = sm.analyze("polars", entries)
    print("entries:", ", ".join(entries))
    print("  reached:", ", ".join(visited))
    print("  uses:", ", ".join(f"{k}×{v}" for k, v in sorted(used.items())) or "(none)")
    return 0


def _project_stack() -> str:
    frames = []
    for frame in traceback.extract_stack()[:-2]:
        if "shrink_polars.py" in frame.filename or "site-packages" in frame.filename:
            continue
        try:
            rel = Path(frame.filename).resolve().relative_to(ROOT)
        except ValueError:
            continue
        frames.append(f"{rel}:{frame.lineno}:{frame.name}")
    return " <- ".join(frames[-6:])


def cmd_trace() -> int:
    """本物の polars を包んで load_overlap を走らせ、ast が見逃した属性を出す。"""
    import polars as pl

    events: list[tuple[str, str]] = []

    def rec(name: str) -> None:
        events.append((name, _project_stack()))

    saved: list[tuple[object, str, object]] = []

    def swap(obj, name, new) -> None:
        saved.append((obj, name, getattr(obj, name)))
        setattr(obj, name, new)

    def patch_fn(obj, qual, name) -> None:
        orig = getattr(obj, name)

        def wrapped(*args, **kwargs):
            rec(f"{qual}.{name}")
            return orig(*args, **kwargs)

        swap(obj, name, wrapped)

    def patch_method(cls, name) -> None:
        orig = getattr(cls, name)

        def wrapped(self, *args, **kwargs):
            rec(f"{cls.__name__}.{name}")
            return orig(self, *args, **kwargs)

        swap(cls, name, wrapped)

    def patch_prop(cls, name) -> None:
        prop = getattr(cls, name)

        def fget(self):
            rec(f"{cls.__name__}.{name}")
            return prop.fget(self)

        swap(cls, name, property(fget))

    try:
        for name in ("read_ndjson", "col", "lit"):
            patch_fn(pl, "polars", name)
        for name in ("select", "__getitem__"):
            patch_method(pl.DataFrame, name)
        for name in ("height", "columns"):
            patch_prop(pl.DataFrame, name)
        patch_method(pl.Series, "to_list")
        for name in ("__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__", "__and__"):
            patch_method(pl.Expr, name)
        sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
        from dragowing.overlap import default_conditions, load_overlap
        from dragowing.records import read_jsonl

        season = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
        props = ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"
        result = load_overlap(season, default_conditions(read_jsonl(props), read_jsonl(season)))
    finally:
        for obj, name, old in reversed(saved):
            setattr(obj, name, old)
    used, _ = sm.analyze("polars", DEFAULT_ENTRIES)
    ast_names = set(used)
    print(f"regions={len(result['regions'])} units={len(result['units'])}")
    seen = []
    for name, stack in events:
        if name not in seen:
            seen.append(name)
            print(f"{name}")
            print(f"  {stack}")
    missed = []
    for name in seen:
        head, _, attr = name.partition(".")
        if head == "polars" and attr in ast_names:
            continue
        missed.append(name)
    print("missed by ast: " + ", ".join(missed))
    return 0


class _Guard:
    """内側の polars_min を呼ぶ前に、まだ許していない属性なら AttributeError にする。"""

    __slots__ = ("_inner",)

    def __init__(self, inner):
        object.__setattr__(self, "_inner", inner)

    def __getattr__(self, name):
        inner = object.__getattribute__(self, "_inner")
        key = f"{type(inner).__name__}.{name}"
        if key not in _ALLOW:
            raise AttributeError(key)
        attr = getattr(inner, name)
        if not callable(attr):
            return _wrap(attr)

        def wrapper(*args, **kwargs):
            return _wrap(attr(*[_unwrap(a) for a in args], **{k: _unwrap(v) for k, v in kwargs.items()}))

        return wrapper

    def __getitem__(self, key):
        inner = object.__getattribute__(self, "_inner")
        attr = f"{type(inner).__name__}.__getitem__"
        if attr not in _ALLOW:
            raise AttributeError(attr)
        return _wrap(inner[_unwrap(key)])


def _bind_ops() -> None:
    def make(op):
        def fn(self, other):
            inner = object.__getattribute__(self, "_inner")
            key = f"{type(inner).__name__}.{op}"
            if key not in _ALLOW:
                raise AttributeError(key)
            return _wrap(getattr(inner, op)(_unwrap(other)))

        fn.__name__ = op
        return fn

    for op in ("__lt__", "__le__", "__gt__", "__ge__", "__eq__", "__ne__", "__and__"):
        setattr(_Guard, op, make(op))


_bind_ops()
_ALLOW: set[str] = set()


def _unwrap(value):
    if isinstance(value, _Guard):
        return object.__getattribute__(value, "_inner")
    return value


def _wrap(value):
    if isinstance(value, (int, float, str, bool, list, tuple, dict, type(None))):
        return value
    return _Guard(value)


class _PolarsModule(types.ModuleType):
    def __getattr__(self, name):
        key = f"polars.{name}"
        if key not in _ALLOW:
            raise AttributeError(key)
        attr = getattr(_impl(), name)
        if not callable(attr):
            return _wrap(attr)

        def wrapper(*args, **kwargs):
            return _wrap(attr(*[_unwrap(a) for a in args], **{k: _unwrap(v) for k, v in kwargs.items()}))

        return wrapper


_IMPL = None


def _impl():
    global _IMPL
    if _IMPL is None:
        spec = importlib.util.spec_from_file_location("_polars_min_impl", ROOT / "shrink" / "polars_min.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _IMPL = module
    return _IMPL


def cmd_absent() -> int:
    """polars が無い状態から AttributeError を足していき、load_overlap が通る面を出す。"""
    if "polars" in sys.modules and not isinstance(sys.modules["polars"], _PolarsModule):
        raise SystemExit("absent は polars を import する前のプロセスで動かす")
    _ALLOW.clear()
    module = _PolarsModule("polars")
    module.__file__ = str(ROOT / "shrink" / "polars_min.py")
    sys.modules["polars"] = module
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras")]
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    season = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
    props = ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"
    rows = read_jsonl(season)
    conds = default_conditions(read_jsonl(props), rows)
    for step in range(1, 40):
        try:
            result = load_overlap(season, conds)
        except AttributeError as exc:
            key = exc.args[0] if exc.args else ""
            if not isinstance(key, str) or key in _ALLOW:
                traceback.print_exc()
                return 1
            _ALLOW.add(key)
            frames = []
            for frame in traceback.extract_tb(exc.__traceback__):
                try:
                    rel = Path(frame.filename).resolve().relative_to(ROOT)
                except ValueError:
                    continue
                frames.append(f"{rel}:{frame.lineno}:{frame.name}")
            print(f"step {step}: AttributeError: {key}")
            print("  " + " <- ".join(frames))
            continue
        print(f"succeeded regions={len(result['regions'])} units={len(result['units'])}")
        print("discovered: " + ", ".join(sorted(_ALLOW)))
        return 0
    print("gave up before load_overlap succeeded", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["survey", "analyze", "trace", "absent", "generate"])
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
    text = generate_polars(sorted(used), entries)
    if not args.out:
        raise SystemExit("generate には --out が要る")
    out = Path(args.out)
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != text:
            print(f"{out} が生成結果と違う。generate し直す", file=sys.stderr)
            return 1
        print(f"{out} ok")
        return 0
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}: {', '.join(sorted(used))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
