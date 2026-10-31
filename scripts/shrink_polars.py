#!/usr/bin/env python3
"""DRAgoWing の load_overlap と NagoyAction の research_digest.collect が使う polars を、標準ライブラリの polars_min.py に縮める（実験）。

polars は Rust 拡張なので wheel を削れない。scripts/shrink_module.py の ast は
``pl.read_ndjson`` のようなモジュール属性しか数えない。DataFrame のメソッド
（``height``、``select``、``[]``、``explode``）と Expr の演算子は、次で見つける。

- trace: 本物の polars のメソッドを包み、load_overlap を動かして呼び出し元を記録する。
- absent: polars を sys.modules に置かず、AttributeError のたびにその名前だけ足して同じ実コードをやり直す。

    python scripts/shrink_polars.py survey
    python scripts/shrink_polars.py analyze
    python scripts/shrink_polars.py trace
    python scripts/shrink_polars.py absent
    python scripts/shrink_polars.py generate --out shrink/polars_min.py [--check]

analyze は import した関数をたどらない。``_mask`` は ``_cond`` を ``from propositions import`` しているので、
入口に ``pythdragoras/propositions.py:_cond`` を別に渡す（入口と trace / absent の仕事は shrink/shrink_polars.json に書く）。c001 の load_overlap は条件を1個ずつ
``_mask`` に渡すので ``&`` は実行されない。``_cond`` がつなぐ演算子としては実装し、同値テストで確かめる。
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import sys
import traceback
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import shrink_module as sm  # noqa: E402

# 入口と実行する仕事はリポジトリごとの設定に置く（このスクリプトには特定のリポジトリの名前を書かない）。
# 既定は <リポジトリ>/shrink/shrink_polars.json。--config か SHRINK_POLARS_CONFIG で差し替える。
#   {"entries": ["pkg/mod.py:func", ...],      analyze / generate / trace の入口
#    "survey_prefix": "pkg/",                  survey で polars_min の対象として分ける接頭辞
#    "sys_path": ["", "sub"],                 trace / absent で ROOT からの相対で sys.path に足す
#    "workload": "shrink.polars_workload:run"}  trace / absent で動かす関数。run(root) -> {"regions", "units"}
CONFIG_PATH = ROOT / "shrink" / "shrink_polars.json"
CONFIG: dict = {}
_LOADED: list[Path] = []  # いま CONFIG に入っている設定ファイル（同じファイルを読み直さない）


def load_config(path: Path | str | None = None) -> dict:
    import os

    target = Path(path or os.environ.get("SHRINK_POLARS_CONFIG") or CONFIG_PATH)
    if not target.is_absolute():
        target = ROOT / target
    if _LOADED == [target]:
        return CONFIG
    _LOADED[:] = [target]
    data = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    CONFIG.clear()
    CONFIG.update(data)
    DEFAULT_ENTRIES[:] = list(data.get("entries", []))
    return CONFIG


DEFAULT_ENTRIES: list[str] = []
load_config()
KNOWN = {"DataFrame", "Expr", "Series", "col", "lit", "read_ndjson"}
# ast では見えない。c001 が実際に踏むものと、_cond の演算子。
METHOD_SURFACE = (
    "DataFrame.height",
    "DataFrame.columns",
    "DataFrame.__getitem__",
    "DataFrame.select",
    "DataFrame.explode",
    "DataFrame.filter",
    "DataFrame.join",
    "DataFrame.iter_rows",
    "Series.to_list",
    "Expr.__lt__",
    "Expr.__le__",
    "Expr.__gt__",
    "Expr.__ge__",
    "Expr.__eq__",
    "Expr.__ne__",
    "Expr.__and__",
    "Expr.is_not_null",
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

    __slots__ = ("_fn", "_scalar", "_marker")

    def __init__(self, fn, scalar, marker=None):
        self._fn = fn
        self._scalar = scalar
        self._marker = marker

    def is_not_null(self):
        return Expr(lambda row, fn=self._fn: fn(row) is not None, False, "is_not_null")

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

    def __getattr__(self, name):
        raise AttributeError("Expr." + name)

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


def _cell_kind(value):
    """collect のコンストラクタが受けるスカラー。bool を int へは寄せない。"""
    if value is None:
        return None
    if type(value) is bool:
        return "bool"
    if type(value) is int:
        return "int"
    if type(value) is str:
        return "str"
    raise TypeError("polars_min が受けない値: " + type(value).__name__)


def _column_kind(column, values, as_list):
    kinds = set()
    for value in values:
        if as_list:
            if value is None:
                continue
            if not isinstance(value, list):
                raise TypeError(f"polars_min の列 {column} はリストとスカラーを混ぜない")
            for element in value:
                kind = _cell_kind(element)
                if kind:
                    kinds.add(kind)
        else:
            if isinstance(value, list):
                raise TypeError(f"polars_min の列 {column} はリストとスカラーを混ぜない")
            kind = _cell_kind(value)
            if kind:
                kinds.add(kind)
    if len(kinds) > 1:
        raise TypeError(f"polars_min の列 {column} は型を混ぜない: {', '.join(sorted(kinds))}")
    inner = next(iter(kinds)) if kinds else "null"
    return ("list:" + inner) if as_list else inner


def _ingest(data):
    """DataFrame(dict) か DataFrame(list of dict)。collect が使う形だけ。"""
    if isinstance(data, dict):
        columns = list(data)
        seqs = []
        width = None
        for column in columns:
            value = data[column]
            if isinstance(value, str) or not isinstance(value, (list, tuple)):
                raise TypeError(f"polars_min の列 {column} はリスト")
            seq = list(value)
            if width is None:
                width = len(seq)
            elif len(seq) != width:
                raise ValueError(f"polars_min の列の長さが違う: {column} は {len(seq)}、期待は {width}")
            seqs.append(seq)
        rows = [{column: seq[index] for column, seq in zip(columns, seqs)} for index in range(width or 0)]
        kinds = {column: _column_kind(column, [row[column] for row in rows], False) for column in columns}
        return columns, rows, kinds
    if isinstance(data, list):
        if not data:
            raise ValueError("polars_min は空のリストから型を推論しない")
        if not all(isinstance(row, dict) for row in data):
            raise TypeError("polars_min のリストは辞書の行だけ")
        columns, seen = [], set()
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
    raise TypeError("polars_min の DataFrame は列の辞書か行のリスト")


class DataFrame:
    """行のリスト。列順はファイルで最初に見た順（大きな NDJSON では polars の順と違うことがある）。"""

    __slots__ = ("_columns", "_rows", "_kinds")

    def __init__(self, data=None, schema=None, *, schema_overrides=None, strict=True,
                 orient=None, infer_schema_length=100, nan_to_null=False, height=None):
        if (schema is not None or schema_overrides is not None or strict is not True
                or orient is not None or infer_schema_length != 100 or nan_to_null is not False
                or height is not None):
            raise NotImplementedError("polars_min の DataFrame は data だけ")
        columns, rows, kinds = _ingest(data)
        self._columns = columns
        self._rows = rows
        self._kinds = kinds

    @classmethod
    def _frame(cls, columns, rows, kinds=None):
        self = object.__new__(cls)
        self._columns = list(columns)
        self._rows = rows
        self._kinds = dict(kinds) if kinds is not None else {}
        return self

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
        return DataFrame._frame(columns, rows)

    def explode(self, columns, *more_columns, empty_as_null=False, keep_nulls=True):
        if (more_columns or type(columns) is not str or empty_as_null is not False or keep_nulls is not True):
            raise NotImplementedError("polars_min の explode は列名ひとつ")
        if columns not in self._columns:
            raise KeyError(columns)
        kind = self._kinds[columns]
        if not str(kind).startswith("list:"):
            raise TypeError(f"polars_min の explode はリスト列だけ: {columns}")
        # 空のリストは消え、null のリストは null のスカラーになる。
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
                raise TypeError(f"polars_min の explode はリスト列だけ: {columns}")
        kinds = dict(self._kinds)
        kinds[columns] = kind.split(":", 1)[1]
        return DataFrame._frame(self._columns, out, kinds)

    def filter(self, *predicates, **constraints):
        if constraints or len(predicates) != 1:
            raise NotImplementedError("polars_min の filter は式ひとつ")
        pred = predicates[0]
        if not isinstance(pred, Expr) or pred._marker != "is_not_null":
            raise NotImplementedError("polars_min の filter は col().is_not_null() だけ")
        return DataFrame._frame(self._columns, [row for row in self._rows if pred._fn(row) is True], self._kinds)

    def join(self, other, on=None, how="inner", *, left_on=None, right_on=None, suffix="_right",
             validate="m:m", nulls_equal=False, coalesce=None, maintain_order=None, build_side="auto"):
        if (how != "left" or type(on) is not str or left_on is not None or right_on is not None
                or suffix != "_right" or validate != "m:m" or nulls_equal is not False
                or coalesce is not None or maintain_order is not None or build_side != "auto"):
            raise NotImplementedError("polars_min の join は on=列、how='left' だけ")
        if not isinstance(other, DataFrame):
            raise TypeError("polars_min の join は polars_min の DataFrame")
        if on not in self._columns or on not in other._columns:
            raise KeyError(on)
        if self._kinds[on] != other._kinds[on]:
            raise TypeError(f"polars_min の join の鍵の型が違う: {on} {self._kinds[on]} と {other._kinds[on]}")
        overlap = [column for column in other._columns if column != on and column in self._columns]
        if overlap:
            raise NotImplementedError("polars_min の join は重なる列に接尾辞を付けない: " + ", ".join(overlap))
        # null の鍵は null 同士でも一致しない。左の行順は保つ。
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
        return DataFrame._frame(list(self._columns) + right_cols, out, kinds)

    def iter_rows(self, *, named=False, buffer_size=512):
        if named is not True or buffer_size != 512:
            raise NotImplementedError("polars_min の iter_rows は named=True だけ")
        for row in self._rows:
            yield {column: row[column] for column in self._columns}

    def __getattr__(self, name):
        raise AttributeError("DataFrame." + name)

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
    kinds = {}
    for c, vals in values.items():
        found = {_kind(v) for v in vals if v is not None}
        kinds[c] = next(iter(found)) if len(found) == 1 else ("null" if not found else "mixed")
    return DataFrame._frame(columns, rows, kinds)
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
    entries = given or list(DEFAULT_ENTRIES)
    if not entries:
        raise SystemExit("入口が無い。引数で渡すか、設定ファイルの entries に書く")
    return entries


def _run_workload() -> dict:
    spec = CONFIG.get("workload")
    if not spec:
        raise SystemExit("設定ファイルに workload（module:function）が無い")
    wanted = [str(ROOT / rel) if rel else str(ROOT) for rel in CONFIG.get("sys_path", [""])]
    sys.path[:0] = [p for p in dict.fromkeys(wanted) if p not in sys.path]  # 何度呼んでも同じ項目を重ねない
    module_name, _, func = spec.partition(":")
    return getattr(importlib.import_module(module_name), func)(ROOT)


def _print_uses(title: str, files: dict[str, Counter]) -> None:
    print(title)
    if not files:
        print("  (none)")
        return
    for name, counts in files.items():
        body = ", ".join(f"{k}×{v}" for k, v in counts.most_common())
        print(f"  {name}: {sum(counts.values())} uses, {len(counts)} names: {body}")


def cmd_survey() -> int:
    prefix = CONFIG.get("survey_prefix", "")
    found = sm.survey("polars")
    drag = {k: v for k, v in found.items() if k.startswith(prefix)}
    rest = {k: v for k, v in found.items() if not k.startswith(prefix)}
    _print_uses(f"{prefix or '(all)'} (module attributes only; methods are invisible to ast):", drag)
    names = Counter()
    for counts in drag.values():
        names += counts
    print(f"{prefix or '(all)'} AST names: " + ", ".join(f"{k}×{v}" for k, v in names.most_common()))
    total = Counter()
    for counts in found.values():
        total += counts
    print(f"repo TOTAL: {sum(total.values())} uses of {len(total)} names across {len(found)} files")
    _print_uses(f"outside {prefix or '(all)'} (not in polars_min):", rest)
    return 0


def cmd_analyze(entries: list[str]) -> int:
    alone, visited = sm.analyze("polars", entries[:1])
    print(f"{entries[0]} alone does not follow imported functions")
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
        result = _run_workload()
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
    for step in range(1, 40):
        try:
            result = _run_workload()
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
    print("gave up before the workload succeeded", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["survey", "analyze", "trace", "absent", "generate"])
    parser.add_argument("entries", nargs="*")
    parser.add_argument("--out")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--config", help="入口と workload の JSON（既定 shrink/shrink_polars.json）")
    args = parser.parse_args(argv)
    load_config(args.config)
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
