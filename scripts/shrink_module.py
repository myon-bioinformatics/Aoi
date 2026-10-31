#!/usr/bin/env python3
"""依存の重いパッケージを、プロジェクトが実際に使う分だけの pure-Python `<pkg>_min.py` に縮める（実験）。

標準ライブラリだけで動く。ast で次を数える。

- survey: ソース全体で ``import <pkg> as X`` / ``from <pkg> import y`` を探し、``X.attr`` の参照をファイルごとに数える。
- analyze: 入口の関数かクラス（``path.py:func``）から、同じモジュールの関数呼び出しと、``mod.func(...)``
  （``mod`` がプロジェクトのモジュール名）をたどり、到達した関数の中の ``X.attr`` だけを集める。
- generate: 集めた名前ごとに、下の実装表から pure-Python の実装を取り出して ``<pkg>_min.py`` を書く。
  numpy は C なので、実装表（NUMPY_IMPLS）は標準ライブラリでの忠実な書き直し。
  使う名前から ast で依存をたどり、必要なトップレベルの定義だけを切り出す。表にない名前があれば失敗して名前を出す。

    python scripts/shrink_module.py survey numpy
    python scripts/shrink_module.py analyze numpy dragowing/overlap.py:load_overlap
    python scripts/shrink_module.py generate numpy dragowing/overlap.py:load_overlap queryu/ask/suggest.py:suggest \\
        --out shrink/numpy_min.py [--check]

制限: 配列のメソッドや演算子（``a.sum()``、``~a``、``a[i, j]``）は型がわからないので ast では拾えない。
それらは ndarray（1 次元と 2 次元）にまとめて常に入れる。クラスは中のメソッド全体をたどる。動的な import や getattr は追わない。
"""
from __future__ import annotations

import argparse
import ast
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", ".pytest_cache"}


def _py_files(root: Path):
    for p in sorted(root.rglob("*.py")):
        if not SKIP & set(p.relative_to(root).parts):
            yield p


def _aliases(tree: ast.AST, pkg: str) -> tuple[set[str], dict[str, str]]:
    """モジュールの別名（np など）と、from import した名前 -> 属性名。"""
    mods, names = set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == pkg:
                    mods.add(a.asname or pkg)
        elif isinstance(node, ast.ImportFrom) and node.module == pkg:
            for a in node.names:
                names[a.asname or a.name] = a.name
    return mods, names


def _attr_chain(node: ast.AST) -> list[str] | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return [node.id, *reversed(parts)]
    return None


def _uses(node: ast.AST, mods: set[str], names: dict[str, str]) -> Counter:
    found = Counter()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and not isinstance(getattr(sub, "_parent", None), ast.Attribute):
            chain = _attr_chain(sub)
            if chain and chain[0] in mods and len(chain) > 1:
                found[".".join(chain[1:])] += 1
        elif isinstance(sub, ast.Name) and sub.id in names:
            found[names[sub.id]] += 1
    return found


def _parse(path: Path) -> ast.Module:
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node  # 連鎖の途中の Attribute を二重に数えない
    return tree


def survey(pkg: str, root: Path = ROOT) -> dict[str, Counter]:
    out = {}
    for p in _py_files(root):
        try:
            tree = _parse(p)
        except SyntaxError:
            continue
        mods, names = _aliases(tree, pkg)
        if mods or names:
            out[str(p.relative_to(root))] = _uses(tree, mods, names)
    return out


def _module_index(root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for p in _py_files(root):
        index.setdefault(p.stem, []).append(p)
    return index


def analyze(pkg: str, entries: list[str], root: Path = ROOT) -> tuple[Counter, list[str]]:
    """入口から到達する関数で使う属性と、たどった関数の一覧。"""
    index = _module_index(root)
    trees: dict[Path, ast.Module] = {}

    def tree_of(path: Path) -> ast.Module:
        if path not in trees:
            trees[path] = _parse(path)
        return trees[path]

    def funcs(path: Path) -> dict[str, ast.FunctionDef]:
        return {n.name: n for n in tree_of(path).body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}

    todo = []
    for e in entries:
        file, func = e.split(":")
        todo.append(((root / file).resolve(), func))
    seen, used = set(), Counter()
    while todo:
        path, name = todo.pop()
        if (path, name) in seen:
            continue
        seen.add((path, name))
        fn = funcs(path).get(name)
        if fn is None:
            continue
        mods, names = _aliases(tree_of(path), pkg)
        used += _uses(fn, mods, names)
        local = funcs(path)
        for sub in ast.walk(fn):
            if not isinstance(sub, ast.Call):
                continue
            f = sub.func
            if isinstance(f, ast.Name) and f.id in local:
                todo.append((path, f.id))
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in index:
                for cand in index[f.value.id]:
                    if f.attr in funcs(cand):
                        todo.append((cand.resolve(), f.attr))
    visited = sorted(f"{p.relative_to(root)}:{n}" for p, n in seen if n in funcs(p))
    return used, visited


# ---- numpy の実装表（標準ライブラリだけ）。名前 -> トップレベルの定義 ----
# 共有ツールは1ファイルなので、実装表もこのファイルの中に Python ソースの文字列で持つ。
# generate は使う名前から ast で依存をたどり、必要な定義だけを切り出す。ndarray は配列のメソッドや
# 演算子を ast で拾えないので常に入れる。``linalg.X`` は使う X だけを持つ ``class linalg`` を組み立てる。
# 実装は shrink/numpy_linalg_min.py（手書き）と同じ書き直しを元にしている。対象は 1 次元と 2 次元。

NUMPY_IMPLS = r'''
from __future__ import annotations

import builtins as _b
import math as _math
import array as _array
import ctypes as _ct
import ctypes.util as _ctu
import os as _os
import struct as _struct

# ---- 速さが要る所（SVD と行列積）は、apt の liblapack3 / libblas3 を ctypes で直接呼ぶ ----
# 探す順: NUMPY_MIN_PURE=1 なら探さない → NUMPY_MIN_LAPACK / NUMPY_MIN_BLAS のパス（指定したらそれだけ）
# → ctypes.util.find_library("lapack" / "blas") → liblapack.so.3 / libblas.so.3。
# 読めない（OSError）か記号が無い（AttributeError）ときは、下の標準ライブラリだけの実装で計算する。
# 確かめたのは Debian 13 の liblapack3 3.12.1-6 / libblas3 3.12.1-6（参照実装）。
def _load_lib(env, name, soname, symbols):
    if _os.environ.get("NUMPY_MIN_PURE"):
        return None
    explicit = _os.environ.get(env)
    for cand in ([explicit] if explicit else [_ctu.find_library(name), soname]):
        if not cand:
            continue
        try:
            lib = _ct.CDLL(cand)
            for symbol in symbols:
                getattr(lib, symbol)
            return lib
        except (OSError, AttributeError):
            continue
    return None


_lapack = _load_lib("NUMPY_MIN_LAPACK", "lapack", "liblapack.so.3", ("dgesdd_",))
_blas = _load_lib("NUMPY_MIN_BLAS", "blas", "libblas.so.3", ("cblas_sgemm", "cblas_dgemm"))
if _lapack is None or _blas is None:
    _lapack = _blas = None
BACKEND = "stdlib" if _lapack is None else "lapack"


_EPS = _math.ulp(1.0)
# グラム法で Vt を作るとき、これより小さい特異値は 0 ベクトルにする（増幅しない）。
_SIGMA_KEEP = 1e-12


class _dtype:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def __call__(self, value):
        return _cast(value, self.name)

    def __eq__(self, other):
        return self.name == getattr(other, "name", other)

    def __hash__(self):
        return hash(self.name)


float32 = _dtype("float32")
float64 = _dtype("float64")
int64 = _dtype("int64")
int8 = _dtype("int8")
uint8 = _dtype("uint8")
bool_ = _dtype("bool")
inf = _math.inf
nan = _math.nan
newaxis = None
pi = _math.pi


def _f32(value: float) -> float:
    return _struct.unpack("f", _struct.pack("f", float(value)))[0]


def _norm_dtype(dtype) -> str:
    if isinstance(dtype, _dtype):
        return dtype.name
    if dtype is _b.bool or dtype is bool_:
        return "bool"
    if dtype is _b.int:
        return "int64"
    if dtype is _b.float:
        return "float64"
    if dtype in ("bool", "int64", "int8", "uint8", "float32", "float64"):
        return dtype
    name = getattr(dtype, "name", None) or getattr(dtype, "__name__", None)
    if name == "bool_":
        return "bool"
    if name in ("bool", "int64", "int8", "uint8", "float32", "float64"):
        return name
    raise TypeError(f"numpy_linalg_min が扱わない dtype: {dtype!r}")


def _div(numer, denom):
    """IEEE 除算。分母 0 は ±inf、0/0 は nan。errstate(divide='ignore') と同じ。"""
    n = _b.float(numer)
    d = _b.float(denom)
    if d == 0.0:
        if n == 0.0 or _math.isnan(n):
            return _math.nan
        return _math.copysign(_math.inf, n) * _math.copysign(1.0, d)
    return n / d


def _cast(value, dtype: str):
    if dtype == "bool":
        return _b.bool(value)
    if dtype == "int64":
        return _b.int(value)
    if dtype == "uint8":
        return _b.int(value) & 0xFF
    if dtype == "int8":
        wrapped = _b.int(value) & 0xFF
        return wrapped - 256 if wrapped >= 128 else wrapped
    if dtype == "float32":
        return _f32(value)
    return _b.float(value)


def _py(value, dtype: str):
    """スカラーの取り出し。インデックスや int() にそのまま渡せる。"""
    if dtype == "bool":
        return _b.bool(value)
    if dtype in ("int64", "int8", "uint8"):
        return _b.int(value)
    return _b.float(value)


def _is_float(dtype: str) -> bool:
    return dtype in ("float32", "float64")


def _scalar_kind(value) -> str:
    if isinstance(value, _b.bool):
        return "bool"
    if isinstance(value, _b.int):
        return "pyint"
    if isinstance(value, _b.float):
        return "pyfloat"
    raise TypeError(f"数値ではない: {type(value).__name__}")


def _combine(kind_a: str, kind_b: str, truediv: bool) -> str:
    """ndarray どうし、または ndarray と Python スカラーの結果 dtype。

    NumPy 2 は ``float32 + Python float`` を float32 のままにし、``float32 + int64 配列`` は float64 に上げる。
    """
    pair = {kind_a, kind_b}
    if "float64" in pair:
        return "float64"
    if "float32" in pair:
        other = (pair - {"float32"}).pop() if len(pair) > 1 else "float32"
        if other in ("float32", "pyint", "pyfloat", "bool"):
            return "float32"
        return "float64"
    if "pyfloat" in pair:
        return "float64"
    if truediv:
        return "float64"
    if "int64" in pair or "pyint" in pair:
        return "int64"
    if "int8" in pair:
        return "int8"
    if "uint8" in pair:
        return "uint8"
    return "bool"


def _infer(values) -> str:
    saw_float = saw_int = saw_bool = False
    for value in values:
        if isinstance(value, _b.bool):
            saw_bool = True
        elif isinstance(value, _b.int):
            saw_int = True
        elif isinstance(value, _b.float):
            saw_float = True
        elif isinstance(value, ndarray):
            if _is_float(value.dtype):
                saw_float = True
            elif value.dtype == "bool":
                saw_bool = True
            else:
                saw_int = True
        else:
            saw_float = True
    if saw_float:
        return "float64"
    if saw_int:
        return "int64"
    if saw_bool:
        return "bool"
    return "float64"


def _broadcast_shape(left, right):
    if len(left) > 2 or len(right) > 2:
        raise NotImplementedError("numpy_linalg_min は 3 次元以上を放送しない")
    width = _b.max(len(left), len(right))
    a = (1,) * (width - len(left)) + tuple(left)
    b = (1,) * (width - len(right)) + tuple(right)
    out = []
    for x, y in zip(a, b):
        if x == y or x == 1 or y == 1:
            out.append(_b.max(x, y))
        else:
            raise ValueError(f"broadcast できない shape: {left} と {right}")
    return tuple(out)


def _expand(data, shape, out_shape):
    if shape == out_shape:
        return data
    dims = _b.max(len(out_shape), len(shape))
    shape = (1,) * (dims - len(shape)) + tuple(shape)
    out_shape = (1,) * (dims - len(out_shape)) + tuple(out_shape)
    if dims == 0:
        return data
    if dims == 1:
        if shape[0] == 1 and out_shape[0] != 1:
            return list(data) * out_shape[0]
        return data
    rows, cols = out_shape
    src_rows, src_cols = shape
    out = []
    for i in range(rows):
        ii = 0 if src_rows == 1 else i
        for j in range(cols):
            jj = 0 if src_cols == 1 else j
            out.append(data[ii * src_cols + jj])
    return out


class ndarray:
    """1 次元と 2 次元。値は行優先の list。"""

    __slots__ = ("_data", "shape", "dtype")

    def __init__(self, data, shape, dtype: str):
        self._data = list(data)
        self.shape = tuple(shape)
        self.dtype = dtype
        if _math.prod(self.shape) != len(self._data):
            raise ValueError(f"shape {self.shape} と要素数 {len(self._data)} が合わない")

    @property
    def ndim(self) -> int:
        return len(self.shape)

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def nbytes(self) -> int:
        width = {"bool": 1, "uint8": 1, "int8": 1, "int64": 8, "float32": 4, "float64": 8}[self.dtype]
        return self.size * width

    @property
    def T(self):
        if self.ndim == 1:
            return ndarray(self._data, self.shape, self.dtype)
        rows, cols = self.shape
        data = [self._data[i * cols + j] for j in range(cols) for i in range(rows)]
        return ndarray(data, (cols, rows), self.dtype)

    def __len__(self):
        if self.ndim == 0:
            raise TypeError("len() of unsized object")
        return self.shape[0]

    def __iter__(self):
        if self.ndim == 1:
            return (_py(value, self.dtype) for value in self._data)
        if self.ndim == 2:
            return (self[i] for i in range(self.shape[0]))
        raise TypeError("iterate")

    def __bool__(self):
        if self.size != 1:
            raise ValueError("配列の真偽は曖昧")
        return _b.bool(self._data[0])

    def copy(self):
        return ndarray(self._data, self.shape, self.dtype)

    def tolist(self):
        if self.ndim == 1:
            return [_py(value, self.dtype) for value in self._data]
        rows, cols = self.shape
        return [[_py(self._data[i * cols + j], self.dtype) for j in range(cols)] for i in range(rows)]

    def reshape(self, *shape):
        if len(shape) == 1 and isinstance(shape[0], (tuple, list)):
            shape = tuple(shape[0])
        shape = list(shape)
        if -1 in shape:
            slot = shape.index(-1)
            rest = _math.prod(item for item in shape if item != -1) or 1
            shape[slot] = len(self._data) // rest
        return ndarray(self._data, shape, self.dtype)

    def astype(self, dtype):
        dtype = _norm_dtype(dtype)
        if dtype == self.dtype:
            return ndarray(self._data, self.shape, self.dtype)
        return ndarray([_cast(value, dtype) for value in self._data], self.shape, dtype)

    def _axis(self, axis):
        if axis is None:
            return None
        if axis < 0:
            axis += self.ndim
        if axis not in range(self.ndim):
            raise ValueError(f"axis {axis}")
        return axis

    def _reduce(self, axis, how: str):
        axis = self._axis(axis)
        if self.ndim == 1 or axis is None and self.ndim == 1:
            return self._agg(self._data, how, scalar=(axis is None or self.ndim == 1 and not False))
        if axis is None:
            return self._agg(self._data, how, scalar=True)
        rows, cols = self.shape
        if axis == 0:
            cols_data = [[self._data[i * cols + j] for i in range(rows)] for j in range(cols)]
            values = [self._agg(col, how, scalar=True) for col in cols_data]
            return ndarray([_cast(value, self._reduce_dtype(how)) for value in values], (cols,), self._reduce_dtype(how))
        values = [self._agg(self._data[i * cols:(i + 1) * cols], how, scalar=True) for i in range(rows)]
        dtype = self._reduce_dtype(how)
        return ndarray([_cast(value, dtype) for value in values], (rows,), dtype)

    def _reduce_dtype(self, how: str) -> str:
        if how == "mean":
            return "float32" if self.dtype == "float32" else "float64"
        if self.dtype == "float32":
            return "float32"
        if self.dtype == "float64":
            return "float64"
        return "int64"

    def _agg(self, values, how: str, scalar: bool):
        dtype = self._reduce_dtype(how)
        if how == "sum":
            if _is_float(self.dtype):
                total = _math.fsum(float(value) for value in values)
            else:
                total = _b.sum(_b.int(_b.bool(value) if self.dtype == "bool" else value) for value in values)
            return _cast(total, dtype) if scalar else total
        if not values:
            return _math.nan
        total = self._agg(values, "sum", scalar=True)
        return _cast(float(total) / len(values), dtype)

    def sum(self, axis=None):
        if self.ndim == 1 and axis in (None, 0, -1):
            return self._agg(self._data, "sum", scalar=True)
        if axis is None and self.ndim == 2:
            return self._agg(self._data, "sum", scalar=True)
        return self._reduce(axis, "sum")

    def mean(self, axis=None):
        if self.ndim == 1 and axis in (None, 0, -1):
            return self._agg(self._data, "mean", scalar=True)
        if axis is None and self.ndim == 2:
            return self._agg(self._data, "mean", scalar=True)
        return self._reduce(axis, "mean")

    def __getitem__(self, key):
        if isinstance(key, ndarray) and key.dtype == "bool":
            if key.shape != self.shape:
                raise IndexError("bool インデックスの shape が違う")
            picked = [self._data[i] for i, flag in enumerate(key._data) if flag]
            return ndarray(picked, (len(picked),), self.dtype)
        if isinstance(key, ndarray) and key.dtype == "int64" and self.ndim == 1:
            data = [self._data[_at(int(i), self.shape[0])] for i in key._data]
            return ndarray(data, (len(data),), self.dtype)
        if not isinstance(key, tuple):
            key = (key,)
        if _b.any(item is None for item in key):
            return self._newaxis(key)
        if len(key) == 2 and _b.all(isinstance(item, ndarray) and item.dtype == "int64" for item in key):
            if self.ndim != 2:
                raise IndexError
            rows, cols = self.shape
            data = [self._data[_at(int(i), rows) * cols + _at(int(j), cols)] for i, j in zip(key[0]._data, key[1]._data)]
            return ndarray(data, (len(data),), self.dtype)
        if len(key) == 1 and isinstance(key[0], ndarray) and key[0].dtype == "int64" and self.ndim == 2:
            rows, cols = self.shape
            chosen = [_at(int(i), rows) for i in key[0]._data]
            data = [self._data[i * cols + j] for i in chosen for j in range(cols)]
            return ndarray(data, (len(chosen), cols), self.dtype)
        offsets, out_shape, scalar = self._basic(key)
        if scalar:
            return _py(self._data[offsets[0]], self.dtype)
        return ndarray([self._data[i] for i in offsets], out_shape, self.dtype)

    def __setitem__(self, key, value):
        if isinstance(key, ndarray) and key.dtype == "bool":
            slots = [i for i, flag in enumerate(key._data) if flag]
            if isinstance(value, ndarray):
                if value.size != len(slots):
                    raise ValueError("代入する要素数が違う")
                for dest, src in zip(slots, value._data):
                    self._data[dest] = _cast(src, self.dtype)
            else:
                casted = _cast(value, self.dtype)
                for dest in slots:
                    self._data[dest] = casted
            return
        if not isinstance(key, tuple):
            key = (key,)
        if _b.any(isinstance(item, ndarray) for item in key):
            raise NotImplementedError("配列インデックスへの代入")
        offsets, _shape, _scalar = self._basic(key)
        if isinstance(value, ndarray):
            flat = value._data
            if len(flat) != len(offsets):
                raise ValueError("代入する要素数が違う")
            for dest, src in zip(offsets, flat):
                self._data[dest] = _cast(src, self.dtype)
        else:
            casted = _cast(value, self.dtype)
            for dest in offsets:
                self._data[dest] = casted

    def _newaxis(self, key):
        if self.ndim != 1:
            raise NotImplementedError("newaxis は 1 次元を 2 次元にする形だけ")
        full = slice(None)
        if key in ((None,), (None, full)):
            return ndarray(self._data, (1, self.shape[0]), self.dtype)
        if key == (full, None):
            return ndarray(self._data, (self.shape[0], 1), self.dtype)
        raise NotImplementedError(f"newaxis {key!r}")

    def _basic(self, key):
        if self.ndim == 1:
            if len(key) != 1:
                raise IndexError
            idx, scalar = _axis_index(key[0], self.shape[0])
            return idx, (len(idx),), scalar
        if len(key) == 1:
            key = (key[0], slice(None))
        if len(key) != 2:
            raise IndexError
        rows, cols = self.shape
        ii, row_scalar = _axis_index(key[0], rows)
        jj, col_scalar = _axis_index(key[1], cols)
        offsets = [i * cols + j for i in ii for j in jj]
        if row_scalar and col_scalar:
            return offsets, (), True
        if row_scalar or col_scalar:
            return offsets, (len(offsets),), False
        return offsets, (len(ii), len(jj)), False

    def _binop(self, other, op, *, reflected=False, inplace=False, truediv=False, compare=False, logical=False, bitwise=False):
        if isinstance(other, ndarray):
            kind_b = other.dtype
            data_b, shape_b = other._data, other.shape
        else:
            kind_b = _scalar_kind(other)
            data_b, shape_b = [other], ()
        out_shape = _broadcast_shape(self.shape, shape_b)
        if compare or logical:
            dtype = "bool"
        elif bitwise:
            dtype = self.dtype
        else:
            dtype = _combine(self.dtype, kind_b, truediv)
        left = _expand(self._data, self.shape, out_shape)
        right = _expand(data_b, shape_b, out_shape)
        out = []
        for a, b in zip(left, right):
            x, y = (b, a) if reflected else (a, b)
            out.append(op(x, y))
        if inplace:
            if out_shape != self.shape:
                raise ValueError("in-place 演算の shape が変わる")
            self._data = [_cast(value, self.dtype) for value in out]
            return self
        return ndarray([_cast(value, dtype) for value in out], out_shape, dtype)

    def __add__(self, other):
        return self._binop(other, lambda a, b: float(a) + float(b) if _needs_float(self, other) else int(a) + int(b))

    def __radd__(self, other):
        return self._binop(other, lambda a, b: float(b) + float(a) if _needs_float(self, other) else int(b) + int(a), reflected=False)

    def __sub__(self, other):
        return self._binop(other, lambda a, b: float(a) - float(b) if _needs_float(self, other) else int(a) - int(b))

    def __rsub__(self, other):
        return self._binop(other, lambda a, b: float(b) - float(a) if _needs_float(self, other) else int(b) - int(a))

    def __mul__(self, other):
        return self._binop(other, lambda a, b: float(a) * float(b) if _needs_float(self, other) else int(a) * int(b))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self._binop(other, _div, truediv=True)

    def __rtruediv__(self, other):
        return self._binop(other, lambda a, b: _div(b, a), truediv=True)

    def __iadd__(self, other):
        return self._binop(other, lambda a, b: float(a) + float(b), inplace=True)

    def __isub__(self, other):
        return self._binop(other, lambda a, b: float(a) - float(b), inplace=True)

    def __imul__(self, other):
        return self._binop(other, lambda a, b: float(a) * float(b), inplace=True)

    def __neg__(self):
        dtype = "int64" if self.dtype == "bool" else self.dtype
        return ndarray([_cast(-float(value), dtype) for value in self._data], self.shape, dtype)

    def __and__(self, other):
        if self.dtype == "bool":
            return self._binop(other, lambda a, b: _b.bool(a) and _b.bool(b), logical=True)
        if self.dtype == "uint8":
            return self._binop(other, lambda a, b: (int(a) & int(b)) & 0xFF, bitwise=True)
        raise NotImplementedError("numpy_linalg_min の & は bool と uint8 だけ")

    def __or__(self, other):
        if self.dtype == "bool":
            return self._binop(other, lambda a, b: _b.bool(a) or _b.bool(b), logical=True)
        if self.dtype == "uint8":
            return self._binop(other, lambda a, b: (int(a) | int(b)) & 0xFF, bitwise=True)
        raise NotImplementedError("numpy_linalg_min の | は bool と uint8 だけ")

    def __iand__(self, other):
        result = self & other
        self._data = result._data
        return self

    def __invert__(self):
        if self.dtype == "bool":
            return ndarray([not value for value in self._data], self.shape, "bool")
        if self.dtype == "uint8":
            return ndarray([value ^ 0xFF for value in self._data], self.shape, "uint8")
        raise NotImplementedError("numpy_linalg_min の ~ は bool と uint8 だけ")

    def _compare(self, other, op):
        return self._binop(other, op, compare=True)

    def __eq__(self, other):
        return self._compare(other, lambda a, b: a == b)

    def __ne__(self, other):
        return self._compare(other, lambda a, b: a != b)

    def __lt__(self, other):
        return self._compare(other, lambda a, b: float(a) < float(b))

    def __le__(self, other):
        return self._compare(other, lambda a, b: float(a) <= float(b))

    def __gt__(self, other):
        return self._compare(other, lambda a, b: float(a) > float(b))

    def __ge__(self, other):
        return self._compare(other, lambda a, b: float(a) >= float(b))

    def __matmul__(self, other):
        if not isinstance(other, ndarray):
            other = asarray(other)
        return _matmul(self, other)

    def __rmatmul__(self, other):
        return asarray(other).__matmul__(self)

    def __repr__(self):
        return f"numpy_linalg_min.ndarray({self.tolist()!r}, dtype={self.dtype})"


def _needs_float(left: ndarray, other) -> bool:
    if _is_float(left.dtype):
        return True
    if isinstance(other, ndarray):
        return _is_float(other.dtype)
    return isinstance(other, _b.float)


def _at(index: int, length: int) -> int:
    if index < 0:
        index += length
    if not 0 <= index < length:
        raise IndexError("index out of range")
    return index


def _axis_index(spec, length: int):
    if isinstance(spec, slice):
        return list(range(*spec.indices(length))), False
    if isinstance(spec, ndarray):
        raise TypeError("配列インデックスは別経路")
    return [_at(int(spec), length)], True


def _buf(values, code):
    data = _array.array(code, values)
    return data, (_ct.c_float if code == "f" else _ct.c_double) * len(data)


def _matmul(left: ndarray, right: ndarray):
    if _blas is not None and left.ndim == 2 and right.ndim in (1, 2):
        dtype = _combine(left.dtype, right.dtype, False)
        if not _is_float(dtype) and dtype != "int64":
            dtype = "float64"  # 標準ライブラリ版と同じく、bool や小さい整数は float64 で積む
        if dtype in ("float32", "float64"):
            rows, shared = left.shape
            cols = right.shape[1] if right.ndim == 2 else 1
            if right.shape[0] != shared:
                raise ValueError("matmul の内側次元が違う")
            code = "f" if dtype == "float32" else "d"
            scalar = _ct.c_float if code == "f" else _ct.c_double
            a, ta = _buf([float(v) for v in left._data], code)
            b, tb = _buf([float(v) for v in right._data], code)
            out, to = _buf([0.0] * (rows * cols), code)
            gemm = _blas.cblas_sgemm if code == "f" else _blas.cblas_dgemm
            # CblasRowMajor=101, CblasNoTrans=111
            gemm(101, 111, 111, rows, cols, shared, scalar(1.0), ta.from_buffer(a), shared,
                 tb.from_buffer(b), cols, scalar(0.0), to.from_buffer(out), cols)
            return ndarray(list(out), (rows, cols) if right.ndim == 2 else (rows,), dtype)
    return _matmul_py(left, right)


def _matmul_py(left: ndarray, right: ndarray):
    if left.ndim == 1 and right.ndim == 1:
        if left.shape[0] != right.shape[0]:
            raise ValueError("内積の長さが違う")
        total = _math.fsum(float(a) * float(b) for a, b in zip(left._data, right._data))
        dtype = _combine(left.dtype, right.dtype, False)
        return _cast(total, dtype) if dtype == "float32" else float(total)
    dtype = _combine(left.dtype, right.dtype, False)
    if not _is_float(dtype) and dtype != "int64":
        dtype = "float64"
    if left.ndim == 2 and right.ndim == 2:
        rows, shared = left.shape
        shared_b, cols = right.shape
        if shared != shared_b:
            raise ValueError("matmul の内側次元が違う")
        out = [0.0] * (rows * cols)
        for i in range(rows):
            base = i * shared
            for t in range(shared):
                factor = float(left._data[base + t])
                if factor == 0.0:
                    continue
                span = t * cols
                dest = i * cols
                row = right._data
                for j in range(cols):
                    out[dest + j] += factor * float(row[span + j])
        if dtype == "float32":
            out = [_f32(value) for value in out]
        elif dtype == "int64":
            out = [int(round(value)) for value in out]
        return ndarray(out, (rows, cols), dtype)
    if left.ndim == 2 and right.ndim == 1:
        rows, shared = left.shape
        if right.shape[0] != shared:
            raise ValueError("matmul の内側次元が違う")
        out = []
        for i in range(rows):
            base = i * shared
            total = _math.fsum(float(left._data[base + t]) * float(right._data[t]) for t in range(shared))
            out.append(_cast(total, dtype))
        return ndarray(out, (rows,), dtype)
    if left.ndim == 1 and right.ndim == 2:
        shared, cols = right.shape
        if left.shape[0] != shared:
            raise ValueError("matmul の内側次元が違う")
        out = []
        for j in range(cols):
            total = _math.fsum(float(left._data[t]) * float(right._data[t * cols + j]) for t in range(shared))
            out.append(_cast(total, dtype))
        return ndarray(out, (cols,), dtype)
    raise ValueError("matmul は 1 次元と 2 次元だけ")


def array(obj, dtype=None, *, copy=True, order="K", ndmin=0, subok=False, device=None):
    del copy, order, subok, device
    if isinstance(obj, ndarray):
        out = ndarray(obj._data, obj.shape, obj.dtype)
    elif isinstance(obj, (list, tuple)):
        if not obj:
            out = ndarray([], (0,), _norm_dtype(dtype) if dtype is not None else "float64")
        elif isinstance(obj[0], (list, tuple, ndarray)):
            rows = [list(row) for row in obj]
            width = len(rows[0])
            if _b.any(len(row) != width for row in rows):
                raise ValueError("numpy_linalg_min は不揃いの行を扱わない")
            flat = []
            for row in rows:
                for value in row:
                    flat.append(value.item() if hasattr(value, "item") and not isinstance(value, (list, tuple)) else value)
            # ndarray cells
            normalized = []
            for value in flat:
                if isinstance(value, ndarray):
                    if value.size != 1:
                        raise ValueError("入れ子が深すぎる")
                    normalized.append(value._data[0])
                else:
                    normalized.append(value)
            out = ndarray(normalized, (len(rows), width), _infer(normalized))
        else:
            out = ndarray(list(obj), (len(obj),), _infer(obj))
    elif isinstance(obj, (int, float, bool)):
        kind = _infer([obj])
        out = ndarray([obj], (), kind)
    else:
        raise TypeError(f"array にできない型: {type(obj).__name__}")
    if dtype is not None:
        out = out.astype(dtype)
    if ndmin and out.ndim < ndmin:
        shape = (1,) * (ndmin - out.ndim) + out.shape
        out = out.reshape(shape)
    return out


def asarray(obj, dtype=None, order=None):
    del order
    if isinstance(obj, ndarray):
        if dtype is None or _norm_dtype(dtype) == obj.dtype:
            return obj
        return obj.astype(dtype)
    return array(obj, dtype=dtype)


def zeros(shape, dtype=float, order="C"):
    del order
    if isinstance(shape, int):
        shape = (shape,)
    else:
        shape = tuple(int(item) for item in shape)
    kind = _norm_dtype(dtype)
    return ndarray([_cast(0, kind)] * _math.prod(shape), shape, kind)


def ones(shape, dtype=float, order="C"):
    del order
    made = zeros(shape, dtype=dtype)
    made._data = [_cast(1, made.dtype)] * made.size
    return made


def empty(shape, dtype=float, order="C"):
    return zeros(shape, dtype=dtype, order=order)


def zeros_like(a, dtype=None):
    source = asarray(a)
    return zeros(source.shape, source.dtype if dtype is None else dtype)


def ones_like(a, dtype=None):
    source = asarray(a)
    return ones(source.shape, source.dtype if dtype is None else dtype)


def full_like(a, fill_value, dtype=None):
    source = asarray(a)
    kind = source.dtype if dtype is None else _norm_dtype(dtype)
    return ndarray([_cast(fill_value, kind)] * source.size, source.shape, kind)


def arange(start, stop=None, step=1, dtype=None):
    if stop is None:
        stop = start
        start = 0
    values = list(range(int(start), int(stop), int(step)))
    kind = _norm_dtype(dtype) if dtype is not None else "int64"
    return ndarray([_cast(value, kind) for value in values], (len(values),), kind)


def concatenate(arrays, axis=0):
    parts = [asarray(item) for item in arrays]
    if not parts:
        raise ValueError("concatenate に配列がない")
    if axis not in (0, -1) or _b.any(part.ndim != 1 for part in parts):
        raise NotImplementedError("concatenate は 1 次元だけ")
    data = [value for part in parts for value in part._data]
    return ndarray(data, (len(data),), parts[0].dtype)


def hstack(tup):
    parts = [asarray(item) for item in tup]
    if parts[0].ndim == 1:
        return concatenate(parts)
    rows = parts[0].shape[0]
    for part in parts:
        if part.ndim != 2 or part.shape[0] != rows:
            raise ValueError("hstack の行数が違う")
    cols = _b.sum(part.shape[1] for part in parts)
    data = []
    for i in range(rows):
        for part in parts:
            width = part.shape[1]
            data.extend(part._data[i * width:(i + 1) * width])
    return ndarray(data, (rows, cols), parts[0].dtype)


def _unary(a, op, dtype=None):
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        return op(float(a))
    source = asarray(a)
    kind = dtype or (source.dtype if _is_float(source.dtype) else "float64")
    return ndarray([_cast(op(float(value)), kind) for value in source._data], source.shape, kind)


def log(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return _math.log(float(x))
    source = asarray(x)
    kind = source.dtype if _is_float(source.dtype) else "float64"

    def one(value):
        number = float(value)
        if number > 0.0:
            return _math.log(number)
        if number == 0.0:
            return _math.inf * -1
        return _math.nan

    return ndarray([_cast(one(value), kind) for value in source._data], source.shape, kind)


def sign(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        if x > 0:
            return 1.0 if isinstance(x, float) else 1
        if x < 0:
            return -1.0 if isinstance(x, float) else -1
        return 0.0 if isinstance(x, float) else 0
    source = asarray(x)
    kind = "int64" if source.dtype in ("bool", "int64", "int8", "uint8") else source.dtype

    def one(value):
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0

    return ndarray([_cast(one(value), kind) for value in source._data], source.shape, kind)


def abs(x):
    return absolute(x)


def absolute(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return builtins_abs(x)
    source = asarray(x)
    kind = source.dtype if source.dtype != "bool" else "int64"
    return ndarray([_cast(builtins_abs(value), kind) for value in source._data], source.shape, kind)


builtins_abs = _b.abs


def sqrt(x):
    return _unary(x, _math.sqrt)


def floor(x):
    return _unary(x, _math.floor)


def ceil(x):
    return _unary(x, _math.ceil)


def isfinite(x):
    source = asarray(x)
    return ndarray([_math.isfinite(float(value)) for value in source._data], source.shape, "bool")


def round(a, decimals=0, out=None):
    del out
    source = asarray(a)
    kind = source.dtype if _is_float(source.dtype) else "float64"
    places = int(decimals)
    return ndarray([_cast(_b.round(float(value), places), kind) for value in source._data], source.shape, kind)


def maximum(x, y):
    if not isinstance(x, ndarray) and isinstance(y, ndarray):
        return y._binop(x, lambda a, b: a if float(a) >= float(b) else b, reflected=True)
    if not isinstance(x, ndarray):
        return x if float(x) >= float(y) else y
    return asarray(x)._binop(y, lambda a, b: a if float(a) >= float(b) else b)


def minimum(x, y):
    if not isinstance(x, ndarray) and isinstance(y, ndarray):
        return y._binop(x, lambda a, b: a if float(a) <= float(b) else b, reflected=True)
    if not isinstance(x, ndarray):
        return x if float(x) <= float(y) else y
    return asarray(x)._binop(y, lambda a, b: a if float(a) <= float(b) else b)


def clip(a, a_min, a_max):
    return minimum(maximum(a, a_min), a_max)


def where(cond, x=None, y=None):
    if x is None or y is None:
        raise NotImplementedError("where は 3 引数だけ")
    mask = asarray(cond)
    if not isinstance(x, ndarray) and not isinstance(y, ndarray):
        data = [x if flag else y for flag in mask._data]
        return ndarray(data, mask.shape, _infer(data))
    anchor = x if isinstance(x, ndarray) else y
    # broadcast onto the common shape
    parts = [mask.shape]
    datas = []
    shapes = []
    for piece in (x, y):
        if isinstance(piece, ndarray):
            parts.append(piece.shape)
        else:
            parts.append(())
    out_shape = parts[0]
    for part in parts[1:]:
        out_shape = _broadcast_shape(out_shape, part)
    flags = _expand(mask._data, mask.shape, out_shape)
    if isinstance(x, ndarray):
        xs = _expand(x._data, x.shape, out_shape)
        x_dtype = x.dtype
    else:
        xs = [x] * _math.prod(out_shape)
        x_dtype = _scalar_kind(x)
    if isinstance(y, ndarray):
        ys = _expand(y._data, y.shape, out_shape)
        y_dtype = y.dtype
    else:
        ys = [y] * _math.prod(out_shape)
        y_dtype = _scalar_kind(y)
    kind = _combine(x_dtype if isinstance(x, ndarray) else x_dtype, y_dtype if isinstance(y, ndarray) else y_dtype, False)
    if kind in ("pyint", "pyfloat", "bool"):
        kind = "float64" if kind == "pyfloat" else ("int64" if kind == "pyint" else "bool")
    data = [xs[i] if flags[i] else ys[i] for i in range(len(flags))]
    return ndarray([_cast(value, kind) for value in data], out_shape, kind)


def nan_to_num(x, copy=True, nan=0.0, posinf=None, neginf=None):
    del copy
    source = asarray(x)
    if posinf is None:
        posinf = 1.7976931348623157e+308
    if neginf is None:
        neginf = -1.7976931348623157e+308
    out = []
    for value in source._data:
        number = float(value)
        if _math.isnan(number):
            out.append(nan)
        elif _math.isinf(number):
            out.append(posinf if number > 0 else neginf)
        else:
            out.append(number)
    return ndarray([_cast(value, source.dtype) for value in out], source.shape, source.dtype)


def any(a, axis=None):
    if axis is not None:
        raise NotImplementedError("any は軸なしだけ")
    return _b.any(_b.bool(value) for value in asarray(a)._data)


def all(a, axis=None):
    if axis is not None:
        raise NotImplementedError("all は軸なしだけ")
    return _b.all(_b.bool(value) for value in asarray(a)._data)


class errstate:
    def __init__(self, **kwargs):
        del kwargs

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def divide(x, y, out=None, where=True):
    if out is None and where is True:
        if isinstance(x, ndarray):
            return x / y
        return asarray(y).__rtruediv__(x)
    left = asarray(x)
    right = asarray(y) if isinstance(y, ndarray) else y
    if isinstance(right, ndarray):
        out_shape = _broadcast_shape(left.shape, right.shape)
        right_data, right_shape = right._data, right.shape
    else:
        out_shape = left.shape
        right_data, right_shape = [right], ()
    if out is None:
        kind = _combine(left.dtype, right.dtype if isinstance(right, ndarray) else _scalar_kind(right), True)
        out = zeros(out_shape, kind)
    else:
        out_shape = out.shape
    xs = _expand(left._data, left.shape, out_shape)
    ys = _expand(right_data, right_shape, out_shape)
    if where is True:
        flags = [True] * len(xs)
    else:
        mask = asarray(where)
        flags = _expand(mask._data, mask.shape, out_shape)
    for i, flag in enumerate(flags):
        if flag:
            out._data[i] = _cast(_div(xs[i], ys[i]), out.dtype)
    return out


def argsort(a, axis=-1, kind=None):
    del kind
    source = asarray(a)
    if source.ndim != 1 or axis not in (-1, 0):
        raise NotImplementedError("argsort は 1 次元だけ")
    order = sorted(range(source.size), key=lambda i: source._data[i])
    return ndarray(order, (source.size,), "int64")


def sort(a, axis=-1, kind=None):
    del kind
    source = asarray(a)
    if source.ndim != 1 or axis not in (-1, 0):
        raise NotImplementedError("sort は 1 次元だけ")
    return ndarray(sorted(source._data), source.shape, source.dtype)


def partition(a, kth, axis=-1):
    del kth, axis
    source = asarray(a)
    if source.ndim != 1:
        raise NotImplementedError("partition は 1 次元だけ")
    # 完全なソートは partition の条件（kth の位置にその順位の値）を満たす。
    return ndarray(sorted(source._data), source.shape, source.dtype)


def argpartition(a, kth, axis=-1):
    del kth, axis
    source = asarray(a)
    if source.ndim != 1:
        raise NotImplementedError("argpartition は 1 次元だけ")
    order = sorted(range(source.size), key=lambda i: source._data[i])
    return ndarray(order, (source.size,), "int64")


def nonzero(a):
    source = asarray(a)
    if source.ndim == 1:
        idx = [i for i, value in enumerate(source._data) if value]
        return (ndarray(idx, (len(idx),), "int64"),)
    if source.ndim != 2:
        raise NotImplementedError
    rows, cols = source.shape
    ii, jj = [], []
    for i in range(rows):
        for j in range(cols):
            if source._data[i * cols + j]:
                ii.append(i)
                jj.append(j)
    return ndarray(ii, (len(ii),), "int64"), ndarray(jj, (len(jj),), "int64")


def flatnonzero(a):
    source = asarray(a)
    idx = [i for i, value in enumerate(source._data) if value]
    return ndarray(idx, (len(idx),), "int64")


def triu_indices(n, k=0, m=None):
    cols = n if m is None else m
    ii, jj = [], []
    for i in range(n):
        for j in range(cols):
            if j >= i + k:
                ii.append(i)
                jj.append(j)
    return ndarray(ii, (len(ii),), "int64"), ndarray(jj, (len(jj),), "int64")


def frombuffer(buffer, dtype=float, count=-1, offset=0):
    del count, offset
    if _norm_dtype(dtype) != "uint8":
        raise NotImplementedError("frombuffer は uint8 だけ")
    data = list(bytes(buffer))
    return ndarray(data, (len(data),), "uint8")


def unpackbits(a, axis=None, count=None, bitorder="big"):
    del count
    source = asarray(a)
    if source.dtype != "uint8":
        raise TypeError("unpackbits は uint8 だけ")
    shifts = range(8) if bitorder == "little" else range(7, -1, -1)

    def bits(byte):
        return [(int(byte) >> shift) & 1 for shift in shifts]

    if axis is None or source.ndim == 1:
        data = [bit for byte in source._data for bit in bits(byte)]
        return ndarray(data, (source.size * 8,), "uint8")
    if axis in (1, -1) and source.ndim == 2:
        rows, cols = source.shape
        data = [bit for byte in source._data for bit in bits(byte)]
        return ndarray(data, (rows, cols * 8), "uint8")
    raise NotImplementedError("unpackbits は axis=None か最後の軸だけ")


def packbits(a, axis=None, bitorder="big"):
    source = asarray(a).astype("bool")
    little = bitorder == "little"

    def pack(bits):
        out = []
        for start in range(0, len(bits), 8):
            chunk = bits[start:start + 8]
            if len(chunk) < 8:
                chunk = chunk + [False] * (8 - len(chunk))
            value = 0
            for shift, bit in enumerate(chunk):
                if bit:
                    value |= 1 << (shift if little else 7 - shift)
            out.append(value)
        return out

    if axis is None or source.ndim == 1:
        data = pack(source._data if source.ndim == 1 else source.reshape(-1)._data)
        return ndarray(data, (len(data),), "uint8")
    if axis in (1, -1) and source.ndim == 2:
        rows, cols = source.shape
        data = []
        for i in range(rows):
            data.extend(pack(source._data[i * cols:(i + 1) * cols]))
        width = (cols + 7) // 8
        return ndarray(data, (rows, width), "uint8")
    raise NotImplementedError("packbits は axis=None か最後の軸だけ")


def bitwise_count(a):
    source = asarray(a)
    if source.dtype not in ("uint8", "int8", "int64"):
        raise TypeError("bitwise_count の dtype")
    counts = [int(value).bit_count() for value in source._data]
    # NumPy は uint8 の popcount を uint8 で返す（この後の sum が幅を広げる）。
    kind = "uint8" if source.dtype == "uint8" else "int64"
    return ndarray([_cast(value, kind) for value in counts], source.shape, kind)


def einsum(subscripts, *operands, optimize=None, **kwargs):
    del optimize, kwargs
    text = subscripts.replace(" ", "")
    if text != "ik,ij,jk->k":
        raise NotImplementedError(f"einsum は ik,ij,jk->k だけ（受けたもの: {subscripts}）")
    hu, mat, gv = (asarray(item, dtype="float64") for item in operands)
    rows, rank = hu.shape
    if mat.shape[0] != rows or gv.shape[0] != mat.shape[1] or gv.shape[1] != rank:
        raise ValueError(f"einsum の shape: {hu.shape} {mat.shape} {gv.shape}")
    out = []
    for col in range(rank):
        total = 0.0
        for i in range(rows):
            acc = 0.0
            base = i * mat.shape[1]
            for j in range(mat.shape[1]):
                acc += mat._data[base + j] * gv._data[j * rank + col]
            total += hu._data[i * rank + col] * acc
        out.append(total)
    return ndarray(out, (rank,), "float64")


def norm(x, ord=None, axis=None, keepdims=False):
    if ord not in (None, 2):
        raise NotImplementedError(f"norm の ord={ord} は未対応")
    source = asarray(x)
    kind = "float32" if source.dtype == "float32" else "float64"

    def length(values):
        return _cast(_math.sqrt(_math.fsum(float(value) * float(value) for value in values)), kind)

    if axis is None:
        value = length(source._data)
        if not keepdims:
            return value
        dims = _b.max(source.ndim, 1)
        return ndarray([value], (1,) * dims, kind)
    axis = source._axis(axis)
    if source.ndim == 1:
        value = length(source._data)
        return ndarray([value], (1,), kind) if keepdims else value
    rows, cols = source.shape
    if axis == 1:
        values = [length(source._data[i * cols:(i + 1) * cols]) for i in range(rows)]
        return ndarray(values, (rows, 1) if keepdims else (rows,), kind)
    values = [length([source._data[i * cols + j] for i in range(rows)]) for j in range(cols)]
    return ndarray(values, (1, cols) if keepdims else (cols,), kind)


def _jacobi(gram):
    """対称行列の Jacobi 法。固有値（降順）と、列が固有ベクトルの直交行列を返す。"""
    n = len(gram)
    matrix = [float(gram[i][j]) for i in range(n) for j in range(n)]
    vectors = [0.0] * (n * n)
    for i in range(n):
        vectors[i * n + i] = 1.0
    for _sweep in range(60):
        rotations = 0
        off = 0.0
        for p in range(n - 1):
            for q in range(p + 1, n):
                apq = matrix[p * n + q]
                magnitude = abs(apq)
                if magnitude > off:
                    off = magnitude
                app = matrix[p * n + p]
                aqq = matrix[q * n + q]
                if magnitude <= _EPS * (abs(app) + abs(aqq) + 1.0):
                    continue
                rotations += 1
                tau = (aqq - app) / (2.0 * apq)
                tangent = _math.copysign(1.0, tau) / (abs(tau) + _math.sqrt(1.0 + tau * tau))
                cosine = 1.0 / _math.sqrt(1.0 + tangent * tangent)
                sine = tangent * cosine
                matrix[p * n + p] = app - tangent * apq
                matrix[q * n + q] = aqq + tangent * apq
                matrix[p * n + q] = matrix[q * n + p] = 0.0
                for k in range(n):
                    if k == p or k == q:
                        continue
                    aik = matrix[k * n + p]
                    aiq = matrix[k * n + q]
                    matrix[k * n + p] = matrix[p * n + k] = cosine * aik - sine * aiq
                    matrix[k * n + q] = matrix[q * n + k] = sine * aik + cosine * aiq
                for k in range(n):
                    vip = vectors[k * n + p]
                    viq = vectors[k * n + q]
                    vectors[k * n + p] = cosine * vip - sine * viq
                    vectors[k * n + q] = sine * vip + cosine * viq
        if rotations == 0 or off <= 1e-14:
            break
    diagonal = [matrix[i * n + i] for i in range(n)]
    order = sorted(range(n), key=lambda i: (-diagonal[i], i))
    values = [diagonal[i] for i in order]
    basis = [0.0] * (n * n)
    for new, old in enumerate(order):
        for row in range(n):
            basis[row * n + new] = vectors[row * n + old]
    return values, basis


def _svd_onesided(data, rows: int, cols: int):
    """片側 Jacobi。小さい特異値も潰さない（lstsq / pinv の階数判定、c001 の 200 未満）。"""
    transposed = rows < cols
    if transposed:
        original = data
        data = [original[r * cols + c] for c in range(cols) for r in range(rows)]
        rows, cols = cols, rows
    else:
        data = list(data)
    vectors = [0.0] * (cols * cols)
    for i in range(cols):
        vectors[i * cols + i] = 1.0
    for _sweep in range(40):
        rotations = 0
        for p in range(cols - 1):
            for q in range(p + 1, cols):
                app = aqq = apq = 0.0
                for i in range(rows):
                    base = i * cols
                    cp = data[base + p]
                    cq = data[base + q]
                    app += cp * cp
                    aqq += cq * cq
                    apq += cp * cq
                scale = _math.sqrt(app * aqq) if app > 0.0 and aqq > 0.0 else 0.0
                if abs(apq) <= _EPS * scale:
                    continue
                rotations += 1
                tau = (aqq - app) / (2.0 * apq)
                tangent = _math.copysign(1.0, tau) / (abs(tau) + _math.sqrt(1.0 + tau * tau))
                cosine = 1.0 / _math.sqrt(1.0 + tangent * tangent)
                sine = tangent * cosine
                for i in range(rows):
                    base = i * cols
                    cp = data[base + p]
                    cq = data[base + q]
                    data[base + p] = cosine * cp - sine * cq
                    data[base + q] = sine * cp + cosine * cq
                for i in range(cols):
                    base = i * cols
                    vp = vectors[base + p]
                    vq = vectors[base + q]
                    vectors[base + p] = cosine * vp - sine * vq
                    vectors[base + q] = sine * vp + cosine * vq
        if rotations == 0:
            break
    norms = []
    for comp in range(cols):
        total = 0.0
        for i in range(rows):
            value = data[i * cols + comp]
            total += value * value
        norms.append(_math.sqrt(total))
    order = sorted(range(cols), key=lambda i: (-norms[i], i))
    singular = [norms[i] for i in order]
    k = cols
    left = [0.0] * (rows * k)
    vt = [0.0] * (k * cols)
    for new, old in enumerate(order):
        sigma = singular[new]
        scale = 1.0 / sigma if sigma > 0.0 else 0.0
        for i in range(rows):
            left[i * k + new] = data[i * cols + old] * scale
        for j in range(cols):
            vt[new * cols + j] = vectors[j * cols + old]
    _positive_columns(left, vt, rows, cols, k)
    if transposed:
        # 転置の SVD を戻す。元の形は (cols, rows) だったので U と Vt を入れ替える。
        return _transpose_flat(vt, k, cols), singular, _transpose_flat(left, rows, k)
    return left, singular, vt


def _transpose_flat(data, rows: int, cols: int):
    return [data[i * cols + j] for j in range(cols) for i in range(rows)]


def _svd_economy(data, rows: int, cols: int):
    """float64 の行優先データ。U (rows, k)、S (k,)、Vt (k, cols)。k = min(rows, cols)。

    片側が 400 を超える細い行列（suggest の 145×3247）だけグラム行列。それ以外は片側 Jacobi。
    """
    if rows == 0 or cols == 0:
        return [], [], []
    if max(rows, cols) > 400 and min(rows, cols) <= 200:
        return _svd_gram(data, rows, cols)
    return _svd_onesided(data, rows, cols)


def _svd_gram(data, rows: int, cols: int):
    if rows <= cols:
        gram = [[0.0] * rows for _ in range(rows)]
        for i in range(rows):
            ii = i * cols
            for j in range(i, rows):
                jj = j * cols
                total = 0.0
                for t in range(cols):
                    total += data[ii + t] * data[jj + t]
                gram[i][j] = gram[j][i] = total
        values, basis = _jacobi(gram)
        singular = [_math.sqrt(value) if value > 0.0 else 0.0 for value in values]
        k = rows
        left = basis  # rows × rows、列が U
        largest = singular[0] if singular else 0.0
        vt = [0.0] * (k * cols)
        for comp in range(k):
            if singular[comp] <= largest * _SIGMA_KEEP:
                continue
            scale = 1.0 / singular[comp]
            for j in range(cols):
                total = 0.0
                for i in range(rows):
                    total += left[i * k + comp] * data[i * cols + j]
                vt[comp * cols + j] = total * scale
        _positive_columns(left, vt, rows, cols, k)
        return left, singular, vt
    gram = [[0.0] * cols for _ in range(cols)]
    for i in range(cols):
        for j in range(i, cols):
            total = 0.0
            for r in range(rows):
                total += data[r * cols + i] * data[r * cols + j]
            gram[i][j] = gram[j][i] = total
    values, basis = _jacobi(gram)
    singular = [_math.sqrt(value) if value > 0.0 else 0.0 for value in values]
    k = cols
    largest = singular[0] if singular else 0.0
    left = [0.0] * (rows * k)
    for comp in range(k):
        if singular[comp] <= largest * _SIGMA_KEEP:
            continue
        scale = 1.0 / singular[comp]
        for i in range(rows):
            total = 0.0
            base = i * cols
            for j in range(cols):
                total += data[base + j] * basis[j * k + comp]
            left[i * k + comp] = total * scale
    vt = [0.0] * (k * cols)
    for comp in range(k):
        for j in range(cols):
            vt[comp * cols + j] = basis[j * k + comp]
    _positive_columns(left, vt, rows, cols, k)
    return left, singular, vt


def _positive_columns(left, vt, rows, cols, k):
    """U の各列で絶対値最大の成分を正にする（Vt の対応する行も反転する）。"""
    for comp in range(k):
        best = 0
        for i in range(rows):
            if abs(left[i * k + comp]) > abs(left[best * k + comp]):
                best = i
        if left[best * k + comp] < 0.0:
            for i in range(rows):
                left[i * k + comp] = -left[i * k + comp]
            for j in range(cols):
                vt[comp * cols + j] = -vt[comp * cols + j]


def svd(a, full_matrices=True, compute_uv=True, hermitian=False):
    source = asarray(a)
    if _lapack is not None and not hermitian and source.ndim == 2 and not full_matrices and source.size:
        return _svd_lapack(source, compute_uv)
    return _svd_py(source, full_matrices, compute_uv, hermitian)


def _svd_lapack(source, compute_uv):
    """numpy の svd_s と同じ dgesdd（jobz='S'）。float32 の入力も float64 で解いて戻す。"""
    rows, cols = source.shape
    k = min(rows, cols)
    kind = "float32" if source.dtype == "float32" else "float64"
    # 行優先の A（rows×cols）は、列優先では Aᵀ（cols×rows）。Aᵀ = U′SV′ᵀ なので
    # A の U は VT′ の並び、A の Vt は U′ の並びのまま読める（転置のコピーが要らない）
    m, n = cols, rows
    a, ta = _buf([float(v) for v in source._data], "d")
    s, ts = _buf([0.0] * k, "d")
    u, tu = _buf([0.0] * (m * k), "d")
    vt, tvt = _buf([0.0] * (k * n), "d")
    iwork = (_ct.c_int * (8 * k))()
    info = _ct.c_int()
    i = lambda v: _ct.byref(_ct.c_int(v))

    def call(work, lwork):
        # Fortran の文字引数は参照で渡し、最後に隠れた長さ引数を付ける
        _lapack.dgesdd_(_ct.c_char_p(b"S"), i(m), i(n), ta.from_buffer(a), i(m), ts.from_buffer(s),
                        tu.from_buffer(u), i(m), tvt.from_buffer(vt), i(k), work, i(lwork),
                        iwork, _ct.byref(info), _ct.c_size_t(1))

    query = _ct.c_double()
    call(_ct.byref(query), -1)
    lwork = int(query.value)
    call((_ct.c_double * lwork)(), lwork)
    if info.value:
        raise ValueError(f"SVD did not converge (dgesdd info={info.value})")
    cast = lambda values: [_cast(v, kind) for v in values]
    sing = ndarray(cast(s), (k,), kind)
    if not compute_uv:
        return sing
    return ndarray(cast(vt), (rows, k), kind), sing, ndarray(cast(u), (k, cols), kind)


def _svd_py(a, full_matrices=True, compute_uv=True, hermitian=False):
    if hermitian:
        raise NotImplementedError("svd の hermitian=True は未対応")
    source = asarray(a)
    if source.ndim != 2:
        raise ValueError("svd は 2 次元だけ")
    rows, cols = source.shape
    if full_matrices and rows != cols:
        raise NotImplementedError("svd は full_matrices=False（非正方で True は未対応）")
    data = [float(value) for value in source._data]
    left, singular, vt = _svd_economy(data, rows, cols)
    kind = "float32" if source.dtype == "float32" else "float64"
    k = min(rows, cols)
    s = ndarray([_cast(value, kind) for value in singular], (k,), kind)
    if not compute_uv:
        return s
    u = ndarray([_cast(value, kind) for value in left], (rows, k), kind)
    v = ndarray([_cast(value, kind) for value in vt], (k, cols), kind)
    return u, s, v


def lstsq(a, b, rcond=None):
    matrix = asarray(a, dtype="float64")
    rhs = asarray(b, dtype="float64")
    if matrix.ndim != 2 or rhs.ndim != 1:
        raise NotImplementedError("lstsq は A が 2 次元、b が 1 次元だけ")
    rows, cols = matrix.shape
    if rhs.shape[0] != rows:
        raise ValueError("lstsq の行数が違う")
    left, singular, vt = _svd_economy([float(value) for value in matrix._data], rows, cols)
    largest = singular[0] if singular else 0.0
    cutoff = (_EPS * max(rows, cols) if rcond is None else float(rcond)) * largest
    # NumPy: rcond * 最大特異値より小さい特異値を 0 とみなす（未満）。
    k = len(singular)
    coeff = []
    rank = 0
    for comp in range(k):
        if singular[comp] < cutoff or singular[comp] == 0.0:
            coeff.append(0.0)
            continue
        rank += 1
        total = 0.0
        for i in range(rows):
            total += left[i * k + comp] * float(rhs._data[i])
        coeff.append(total / singular[comp])
    solution = []
    for j in range(cols):
        total = 0.0
        for comp in range(k):
            total += vt[comp * cols + j] * coeff[comp]
        solution.append(total)
    residuals = []
    if rank == cols and rows > cols:
        rss = 0.0
        for i in range(rows):
            predicted = 0.0
            base = i * cols
            for j in range(cols):
                predicted += float(matrix._data[base + j]) * solution[j]
            diff = float(rhs._data[i]) - predicted
            rss += diff * diff
        residuals = [rss]
    return (
        ndarray(solution, (cols,), "float64"),
        ndarray(residuals, (len(residuals),), "float64"),
        rank,
        ndarray(singular, (k,), "float64"),
    )


def pinv(a, rcond=1e-15, hermitian=False):
    if hermitian:
        raise NotImplementedError("pinv の hermitian=True は未対応")
    matrix = asarray(a, dtype="float64")
    if matrix.ndim != 2:
        raise ValueError("pinv は 2 次元だけ")
    rows, cols = matrix.shape
    left, singular, vt = _svd_economy([float(value) for value in matrix._data], rows, cols)
    largest = singular[0] if singular else 0.0
    cutoff = float(rcond) * largest
    # NumPy: rcond * 最大特異値以下を 0 にする。
    k = len(singular)
    out = [0.0] * (cols * rows)
    for comp in range(k):
        if singular[comp] <= cutoff or singular[comp] == 0.0:
            continue
        scale = 1.0 / singular[comp]
        for j in range(cols):
            factor = vt[comp * cols + j] * scale
            dest = j * rows
            for i in range(rows):
                out[dest + i] += factor * left[i * k + comp]
    return ndarray(out, (cols, rows), "float64")
'''
ALWAYS = ["ndarray", "BACKEND"]  # メソッドや演算子は ast で拾えない。BACKEND は lapack か stdlib かを示す


def _top_defs(tree: ast.Module) -> list[tuple[set[str], ast.stmt]]:
    out = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            out.append(({node.name}, node))
        elif isinstance(node, ast.Assign):
            out.append(({t.id for t in node.targets if isinstance(t, ast.Name)}, node))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            out.append(({node.target.id}, node))
        else:
            out.append((set(), node))  # import や docstring
    return out


def generate_numpy(names: list[str], sources: list[str], impls: str = NUMPY_IMPLS) -> str:
    text = impls
    tree = ast.parse(text)
    defs = _top_defs(tree)
    by_name = {n: node for ns, node in defs for n in ns}
    linalg = sorted(n.split(".", 1)[1] for n in names if n.startswith("linalg."))
    roots = [n for n in names if not n.startswith("linalg.")] + linalg + ALWAYS
    missing = sorted(n for n in names if n != "linalg" and (n.split(".", 1)[1] if n.startswith("linalg.") else n) not in by_name)
    if "linalg" in names and not linalg:
        missing.append("linalg")
    if missing:
        raise SystemExit(f"numpy_min の実装表にない名前: {missing}")
    keep: set[str] = set()
    todo = [n for n in roots if n in by_name]
    while todo:
        n = todo.pop()
        if n in keep:
            continue
        keep.add(n)
        for sub in ast.walk(by_name[n]):
            if isinstance(sub, ast.Name) and sub.id in by_name and sub.id not in keep:
                todo.append(sub.id)
    lines = text.splitlines(keepends=True)
    chunks = []
    for ns, node in defs:
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            continue  # 実装表の docstring
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            continue
        if ns and not ns & keep:
            continue
        start = node.decorator_list[0].lineno if getattr(node, "decorator_list", None) else node.lineno
        chunks.append("".join(lines[start - 1:node.end_lineno]).rstrip() + "\n")
    if linalg:
        chunks.append("class linalg:\n" + "".join(f"    {n} = staticmethod({n})\n" for n in linalg))
    head = (
        '"""numpy の最小版。scripts/shrink_module.py が生成した。手で直さない。\n\n'
        "入口: " + ", ".join(sources) + "\n"
        "使う名前: " + ", ".join(sorted(names)) + '\n"""\n'
        "from __future__ import annotations\n\n"
    )
    exported = sorted({n for n in names if "." not in n} | {"ndarray"} | ({"linalg"} if linalg else set()))
    return head + "\n\n".join(chunks) + "\n\n__all__ = " + repr(exported) + "\n__version__ = \"0+min\"\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command", choices=["survey", "analyze", "generate"])
    p.add_argument("package")
    p.add_argument("entries", nargs="*")
    p.add_argument("--out")
    p.add_argument("--check", action="store_true")
    a = p.parse_args(argv)
    if a.command == "survey":
        total = Counter()
        for f, c in survey(a.package).items():
            total += c
            print(f"{f}: {sum(c.values())} uses, {len(c)} names: " + ", ".join(f"{k}×{v}" for k, v in c.most_common()))
        print(f"TOTAL: {sum(total.values())} uses of {len(total)} names")
        return 0
    used, visited = analyze(a.package, a.entries)
    if a.command == "analyze":
        print("reached:", *visited, sep="\n  ")
        print("uses:", ", ".join(f"{k}×{v}" for k, v in sorted(used.items())))
        return 0
    if a.package != "numpy":
        raise SystemExit("generate は今は numpy だけ")
    text = generate_numpy(sorted(used), a.entries)
    out = Path(a.out)
    if a.check:
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
