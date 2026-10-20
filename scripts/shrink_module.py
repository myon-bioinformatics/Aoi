#!/usr/bin/env python3
"""依存の重いパッケージを、プロジェクトが実際に使う分だけの pure-Python `<pkg>_min.py` に縮める（実験）。

標準ライブラリだけで動く。ast で次を数える。

- survey: ソース全体で ``import <pkg> as X`` / ``from <pkg> import y`` を探し、``X.attr`` の参照をファイルごとに数える。
- analyze: 入口の関数（``path.py:func``）から、同じモジュールの関数呼び出しと、``mod.func(...)``
  （``mod`` がプロジェクトのモジュール名）をたどり、到達した関数の中の ``X.attr`` だけを集める。
- generate: 集めた名前ごとに、下の実装表から pure-Python の実装を取り出して ``<pkg>_min.py`` を書く。
  numpy は C なので、実装表は標準ライブラリでの忠実な書き直し。表にない名前があれば失敗して名前を出す。

    python scripts/shrink_module.py survey numpy
    python scripts/shrink_module.py analyze numpy dragowing/overlap.py:load_overlap
    python scripts/shrink_module.py generate numpy dragowing/overlap.py:load_overlap --out shrink/numpy_min.py [--check]

制限: 配列のメソッドや演算子（``a.sum()``、``~a``、``a[i, j]``）は型がわからないので ast では拾えない。
それらは最小の ndarray（1 次元と 2 次元）にまとめて常に入れる。動的な import や getattr は追わない。
"""
from __future__ import annotations

import argparse
import ast
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__"}


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
        return {n.name: n for n in tree_of(path).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

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


# ---- numpy の実装表（標準ライブラリだけ）。名前 -> ソース ----

NUMPY_CORE = '''
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
'''

NUMPY_IMPLS = {
    "ndarray": "",
    "uint8": "",
    "int64": "",
    "float64": "",
    "bool_": "",
    "asarray": '''
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
''',
    "array": '''
def array(obj, dtype=None):
    out = asarray(obj, dtype)
    return ndarray(out._data, out.shape, out.dtype)
''',
    "zeros": '''
def zeros(shape, dtype=float):
    shape = (shape,) if isinstance(shape, int) else tuple(shape)
    kind = _norm_dtype(dtype)
    return ndarray([_cast(0, kind)] * _math.prod(shape), shape, kind)
''',
    "ones": '''
def ones(shape, dtype=float):
    shape = (shape,) if isinstance(shape, int) else tuple(shape)
    kind = _norm_dtype(dtype)
    return ndarray([_cast(1, kind)] * _math.prod(shape), shape, kind)
''',
    "flatnonzero": '''
def flatnonzero(a):
    a = asarray(a)
    return ndarray([i for i, v in enumerate(a._data) if v], (sum(1 for v in a._data if v),), "int64")
''',
    "frombuffer": '''
def frombuffer(buffer, dtype=float):
    if _norm_dtype(dtype) != "uint8":
        raise NotImplementedError("numpy_min の frombuffer は uint8 だけ")
    data = bytes(buffer)
    return ndarray(list(data), (len(data),), "uint8")
''',
    "unpackbits": '''
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
''',
}

NEEDS = {"array": ["asarray"], "flatnonzero": ["asarray"]}


def generate_numpy(names: list[str], sources: list[str]) -> str:
    missing = sorted(n for n in names if n not in NUMPY_IMPLS)
    if missing:
        raise SystemExit(f"numpy_min の実装表にない名前: {missing}")
    want = set(names)
    for n in list(want):
        want.update(NEEDS.get(n, []))
    order = [n for n in NUMPY_IMPLS if n in want]
    head = (
        '"""numpy の最小版。scripts/shrink_module.py が生成した。手で直さない。\n\n'
        "入口: " + ", ".join(sources) + "\n"
        "使う名前: " + ", ".join(sorted(names)) + '\n"""\n'
        "from __future__ import annotations\n"
    )
    body = NUMPY_CORE + "".join(NUMPY_IMPLS[n] for n in order)
    exported = sorted({n for n in order} | {"ndarray"})
    return head + body + "\n__all__ = " + repr(exported) + "\n__version__ = \"0+min\"\n"


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
