"""numpy の最小版。scripts/shrink_module.py が生成した。手で直さない。

入口: dragowing/overlap.py:load_overlap
使う名前: asarray, flatnonzero, frombuffer, ndarray, ones, uint8, unpackbits, zeros
"""
from __future__ import annotations

import builtins as _b
import math as _math

uint8 = "uint8"
int64 = "int64"
float64 = "float64"
bool_ = "bool"


def _norm_dtype(dtype):
    if dtype in (bool, bool_, "bool"):
        return "bool"
    if dtype in (int, int64, "int64"):
        return "int64"
    if dtype in (float, float64, "float64"):
        return "float64"
    if dtype in (uint8, "uint8"):
        return "uint8"
    raise TypeError(f"numpy_min が扱わない dtype: {dtype!r}")


def _cast(v, dtype):
    if dtype == "bool":
        return _b.bool(v)
    if dtype == "int64":
        return _b.int(v)
    if dtype == "uint8":
        return _b.int(v) & 0xFF
    return _b.float(v)


def _infer(values):
    if all(isinstance(v, _b.bool) for v in values):
        return "bool"
    if all(isinstance(v, int) for v in values):
        return "int64"
    return "float64"


class ndarray:
    """1 次元と 2 次元だけの最小の配列。値は平らな list で持つ。"""

    __slots__ = ("_data", "shape", "dtype")

    def __init__(self, data, shape, dtype):
        self._data = list(data)
        self.shape = tuple(shape)
        self.dtype = dtype
        if _math.prod(self.shape) != len(self._data):
            raise ValueError("shape と要素数が合わない")

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def size(self):
        return len(self._data)

    def __len__(self):
        return self.shape[0]

    def tolist(self):
        if self.ndim == 1:
            return list(self._data)
        r, c = self.shape
        return [self._data[i * c:(i + 1) * c] for i in range(r)]

    def __iter__(self):
        if self.ndim == 1:
            return iter(self._data)
        return (self[i] for i in range(self.shape[0]))

    @staticmethod
    def _index(i, n):
        if i < 0:
            i += n
        if not 0 <= i < n:
            raise IndexError("index out of range")
        return i

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        if self.ndim == 1:
            (k,) = key
            if isinstance(k, slice):
                return ndarray(self._data[k], (len(range(*k.indices(self.shape[0]))),), self.dtype)
            return self._data[self._index(k, self.shape[0])]
        r, c = self.shape
        if len(key) == 1:
            key = (key[0], slice(None))
        rk, ck = key
        rows = range(*rk.indices(r)) if isinstance(rk, slice) else None
        cols = range(*ck.indices(c)) if isinstance(ck, slice) else None
        if rows is None and cols is None:
            return self._data[self._index(rk, r) * c + self._index(ck, c)]
        if rows is None:
            i = self._index(rk, r)
            return ndarray([self._data[i * c + j] for j in cols], (len(cols),), self.dtype)
        if cols is None:
            j = self._index(ck, c)
            return ndarray([self._data[i * c + j] for i in rows], (len(rows),), self.dtype)
        return ndarray([self._data[i * c + j] for i in rows for j in cols], (len(rows), len(cols)), self.dtype)

    def reshape(self, *shape):
        if len(shape) == 1 and isinstance(shape[0], tuple):
            shape = shape[0]
        shape = list(shape)
        if -1 in shape:
            k = shape.index(-1)
            rest = _math.prod(s for s in shape if s != -1)
            shape[k] = len(self._data) // rest if rest else 0
        return ndarray(self._data, shape, self.dtype)

    def astype(self, dtype):
        dtype = _norm_dtype(dtype)
        return ndarray([_cast(v, dtype) for v in self._data], self.shape, dtype)

    def sum(self, axis=None):
        if axis is None:
            if self.dtype == "float64":
                return _math.fsum(self._data)
            return _b.sum(_b.int(v) for v in self._data)
        raise NotImplementedError("numpy_min の sum は axis=None だけ")

    def _binary(self, other, op, dtype):
        if isinstance(other, ndarray):
            if other.shape != self.shape:
                raise ValueError("numpy_min はブロードキャストしない")
            vals = [op(a, b) for a, b in zip(self._data, other._data)]
        else:
            vals = [op(a, other) for a in self._data]
        return ndarray(vals, self.shape, dtype)

    def __and__(self, other):
        if self.dtype != "bool":
            raise NotImplementedError("numpy_min の & は bool だけ")
        return self._binary(other, lambda a, b: a and _b.bool(b), "bool")

    def __iand__(self, other):
        res = self & other
        self._data = res._data
        return self

    def __invert__(self):
        if self.dtype != "bool":
            raise NotImplementedError("numpy_min の ~ は bool だけ")
        return ndarray([not v for v in self._data], self.shape, "bool")

    def __eq__(self, other):
        return self._binary(other, lambda a, b: a == b, "bool")

    def __repr__(self):
        return f"numpy_min.ndarray({self.tolist()!r}, dtype={self.dtype})"

def asarray(obj, dtype=None):
    if isinstance(obj, ndarray):
        return obj if dtype is None else obj.astype(dtype)
    rows = list(obj)
    if rows and isinstance(rows[0], (list, tuple, ndarray)):
        rows = [list(r) for r in rows]
        width = len(rows[0])
        if any(len(r) != width for r in rows):
            raise ValueError("numpy_min は不揃いの行を扱わない")
        flat = [v for r in rows for v in r]
        shape = (len(rows), width)
    else:
        flat, shape = rows, (len(rows),)
    kind = _norm_dtype(dtype) if dtype is not None else _infer(flat)
    return ndarray([_cast(v, kind) for v in flat], shape, kind)

def zeros(shape, dtype=float):
    shape = (shape,) if isinstance(shape, int) else tuple(shape)
    kind = _norm_dtype(dtype)
    return ndarray([_cast(0, kind)] * _math.prod(shape), shape, kind)

def ones(shape, dtype=float):
    shape = (shape,) if isinstance(shape, int) else tuple(shape)
    kind = _norm_dtype(dtype)
    return ndarray([_cast(1, kind)] * _math.prod(shape), shape, kind)

def flatnonzero(a):
    a = asarray(a)
    return ndarray([i for i, v in enumerate(a._data) if v], (sum(1 for v in a._data if v),), "int64")

def frombuffer(buffer, dtype=float):
    if _norm_dtype(dtype) != "uint8":
        raise NotImplementedError("numpy_min の frombuffer は uint8 だけ")
    data = bytes(buffer)
    return ndarray(list(data), (len(data),), "uint8")

def unpackbits(a, axis=None, bitorder="big"):
    if a.dtype != "uint8":
        raise TypeError("unpackbits は uint8 だけ")
    order = range(8) if bitorder == "little" else range(7, -1, -1)
    bits = lambda byte: [(byte >> k) & 1 for k in order]
    if axis is None or a.ndim == 1:
        return ndarray([b for byte in a._data for b in bits(byte)], (a.size * 8,), "uint8")
    if axis in (1, -1) and a.ndim == 2:
        r, c = a.shape
        return ndarray([b for byte in a._data for b in bits(byte)], (r, c * 8), "uint8")
    raise NotImplementedError("numpy_min の unpackbits は axis=None か最後の軸だけ")

__all__ = ['asarray', 'flatnonzero', 'frombuffer', 'ndarray', 'ones', 'uint8', 'unpackbits', 'zeros']
__version__ = "0+min"
