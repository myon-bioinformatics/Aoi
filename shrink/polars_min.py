"""polars の最小版。scripts/shrink_polars.py が生成した。手で直さない。

入口: dragowing/overlap.py:load_overlap, pythdragoras/propositions.py:_cond
使う名前: DataFrame, Expr, col, lit, read_ndjson
AST では見えないので式と表にまとめて入れてある: DataFrame.height, DataFrame.columns, DataFrame.__getitem__, DataFrame.select, Series.to_list, Expr.__lt__, Expr.__le__, Expr.__gt__, Expr.__ge__, Expr.__eq__, Expr.__ne__, Expr.__and__
"""
from __future__ import annotations

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

__all__ = ['DataFrame', 'Expr', 'Series', 'col', 'lit', 'read_ndjson']
__version__ = "0+min"
