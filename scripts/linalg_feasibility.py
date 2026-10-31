#!/usr/bin/env python3
"""queryu と pythdragoras の重い numpy が、標準ライブラリだけで置き換えられるかを調べる（実験）。

shrink/numpy_min.py は scripts/shrink_module.py の生成物（load_overlap と queryu の suggest が入口）。こちらは別ファイルで調べる。

    python scripts/linalg_feasibility.py ast
    python scripts/linalg_feasibility.py trace --scope fixture
    python scripts/linalg_feasibility.py trace --scope c001
    python scripts/linalg_feasibility.py absent
    python scripts/linalg_feasibility.py report

ast はクラスのメソッド、``self.method``、``import mod as alias``、``from mod import func`` をたどる。
shrink_module.analyze はモジュール直下の関数と ``mod.func`` だけなので、suggest.Index の svd を落とす。

trace は本物の numpy の svd / lstsq / pinv / norm / einsum を包み、実際の shape と時間を出す。
absent は中身のない numpy を先に入れ、最初に足りない属性のトレースバックを出して終了する
（足りない numpy 属性なら終了コード 0）。
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import subprocess
import sys
import time
import traceback
import types
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__"}

ENTRIES = [
    "queryu/ask/suggest.py:Index",
    "queryu/ask/suggest.py:suggest",
    "pythdragoras/littlebit_prune.py:littlebit",
    "pythdragoras/littlebit_prune.py:overlap_bounds",
    "pythdragoras/littlebit_prune.py:search_guaranteed",
    "pythdragoras/rule_search.py:_search_bitmatrix",
    "pythdragoras/littlebit_holdout.py:fit",
]

REPORT = """\
Feasibility at the sizes actually used (cycles/c001-chunichi). Pure Python, stdlib only.
Tolerances are for this run, not a claim of bit-identity with LAPACK.

CAN
- linalg.svd, full_matrices=False.
  suggest builds a centered TF-IDF of (145, 3247) float32, vocab 3247, and keeps dim=128.
  That matrix is wide, so the stand-in uses a Gram matrix and symmetric Jacobi.
  On c001 the float-mode ids matched NumPy and the largest similarity gap was 1.5e-7
  (binary 7e-8). The index took 13.4 s versus 77 ms. Signs differ and cancel in the cosine.
  The Gram matrix squares the condition number, so a singular value below about 1e-6 of the largest
  is not reliable. dim=128 stays above that (the kept spectrum is O(1), not 1e-8).
  dim >= n_docs would keep a garbage tail.
  littlebit and the Ty/Tn blocks are (156, 17) and about (139, 156). Those use one-sided Jacobi.
  Indicator singular values matched to 6e-14. LittleBit reconstruction of the indicator matched to 5e-15.
- linalg.lstsq on the ALS systems actually built, (r, r) with r <= 8, including rank-deficient ones.
  One-sided Jacobi matches NumPy's rcond=None cutoff (a constructed rank-7 8×8 keeps rank 7).
  The Gram SVD is the wrong tool here: it reports a true sigma near 1e-16 as about 1e-8,
  which stays above NumPy's cutoff, so the numerical rank and the solution are wrong.
- linalg.pinv of indicator[:8, :], shape (8, 17), rcond=1e-12. Same shape as holdout's decoder.T.
  c001 matched NumPy to 1e-15. holdout.fit() end to end is not replayed: factor signs are not unique,
  and an exact sign tie uses np.random.Generator(PCG64), which is not reimplemented.
  The pinv input is a slice of the indicator, so it does not depend on SVD signs.
- einsum with the single subscript used, "ik,ij,jk->k", at the ALS shapes.
- linalg.norm with axis=-1 and keepdims, and the 1-d norm. float32 in stays float32 out.
- rule_search bitmatrix at 139 terms × 156 units. The matmul is 0/1 in float64, exact while
  the unit count stays <= 8192. The c001 top-20 rules matched exactly (mcc to 12 digits, tp, fp, if_any).
  Pure Python took 0.13 s versus 17 ms.
- search_guaranteed on this table matched the same top-20 rules exactly. It took 48.7 s versus 23 ms.
  With real NumPy it is already slower than the exact bitmatrix. Pure Python is a correctness check.

Measured on c001 with NumPy 2.5.4, one local run. CI repeats that compare without NumPy installed.

CANNOT
- Bit-identical SVD or lstsq against LAPACK. Compare singular values, reconstruction, and the solution.
- full_matrices=True on a non-square matrix, arrays with ndim > 2, a general einsum, hermitian=True.
- np.random.Generator(PCG64). pattern_sign tie-breaks and holdout.fit / derived masks are not replayed.
- suggest when dim >= n_docs. The Gram path drops the tiny tail of a full decomposition.
- The synthetic size mentioned in littlebit_prune (about 5000 units by 1000 conditions).
  A pure-Python Jacobi of that size is minutes to hours, not an acceptable stand-in.
- A faster replacement for NumPy. This module is for one equivalence run at c001 size.
"""


def _py_files(root: Path):
    for path in sorted(root.rglob("*.py")):
        if not SKIP & set(path.relative_to(root).parts):
            yield path


def _parse(path: Path) -> ast.Module:
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node
    return tree


def _attr_chain(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return [node.id, *reversed(parts)]
    return None


class _Module:
    def __init__(self, path: Path, tree: ast.Module):
        self.path = path
        self.functions: dict[str, ast.AST] = {}
        self.classes: dict[str, dict[str, ast.AST]] = {}
        self.modules: dict[str, str] = {}
        self.imported: dict[str, tuple[str, str]] = {}
        self.numpy_aliases: set[str] = set()
        self.numpy_names: dict[str, str] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[node.name] = node
            elif isinstance(node, ast.ClassDef):
                methods = {}
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods[item.name] = item
                self.classes[node.name] = methods
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    stem = alias.name.split(".")[0]
                    self.modules[alias.asname or stem] = stem
                    if stem == "numpy":
                        self.numpy_aliases.add(alias.asname or stem)
            elif isinstance(node, ast.ImportFrom) and node.module:
                stem = node.module.split(".")[0]
                for alias in node.names:
                    local = alias.asname or alias.name
                    self.imported[local] = (stem, alias.name)
                    if stem == "numpy":
                        attr = alias.name if node.module == "numpy" else f"{node.module.split('.', 1)[1]}.{alias.name}"
                        self.numpy_names[local] = attr


def _index(root: Path) -> dict[str, list[_Module]]:
    found: dict[str, list[_Module]] = {}
    for path in _py_files(root):
        try:
            module = _Module(path, _parse(path))
        except SyntaxError:
            continue
        found.setdefault(path.stem, []).append(module)
    return found


def _uses(module: _Module, node: ast.AST) -> Counter:
    found: Counter = Counter()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and not isinstance(getattr(sub, "_parent", None), ast.Attribute):
            chain = _attr_chain(sub)
            if chain and chain[0] in module.numpy_aliases and len(chain) > 1:
                found[".".join(chain[1:])] += 1
        elif isinstance(sub, ast.Name) and sub.id in module.numpy_names:
            found[module.numpy_names[sub.id]] += 1
    return found


def _lookup(index: dict[str, list[_Module]], stem: str) -> list[_Module]:
    return index.get(stem, [])


def analyze(entries: list[str] | None = None, root: Path = ROOT) -> dict[str, dict]:
    """入口ごとに、到達した関数と numpy の属性。"""
    index = _index(root)
    entries = entries or ENTRIES
    out: dict[str, dict] = {}
    for entry in entries:
        file, name = entry.split(":")
        start = (root / file).resolve()
        module = next((item for item in index.get(start.stem, []) if item.path.resolve() == start), None)
        if module is None:
            out[entry] = {"uses": {}, "visited": [], "missing": True}
            continue
        todo: list[tuple[_Module, str, str | None]] = []
        if name in module.classes:
            for method in module.classes[name]:
                todo.append((module, name, method))
        else:
            todo.append((module, name, None))
        seen: set[tuple[str, str]] = set()
        used: Counter = Counter()
        while todo:
            current, qual, method = todo.pop()
            key = f"{current.path}:{qual}" if method is None else f"{current.path}:{qual}.{method}"
            if key in seen:
                continue
            seen.add(key)
            if method is None:
                node = current.functions.get(qual)
                class_name = None
            else:
                node = current.classes.get(qual, {}).get(method)
                class_name = qual
            if node is None:
                continue
            used += _uses(current, node)
            for sub in ast.walk(node):
                if not isinstance(sub, ast.Call):
                    continue
                func = sub.func
                if isinstance(func, ast.Name):
                    ident = func.id
                    if ident in current.functions:
                        todo.append((current, ident, None))
                    elif ident in current.classes:
                        for item in current.classes[ident]:
                            todo.append((current, ident, item))
                    elif ident in current.imported:
                        stem, attr = current.imported[ident]
                        for foreign in _lookup(index, stem):
                            if attr in foreign.functions:
                                todo.append((foreign, attr, None))
                            elif attr in foreign.classes:
                                for item in foreign.classes[attr]:
                                    todo.append((foreign, attr, item))
                elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    base = func.value.id
                    if base in ("self", "cls") and class_name and func.attr in current.classes.get(class_name, {}):
                        todo.append((current, class_name, func.attr))
                    elif base in current.modules:
                        stem = current.modules[base]
                        if stem == "numpy":
                            continue
                        for foreign in _lookup(index, stem):
                            if func.attr in foreign.functions:
                                todo.append((foreign, func.attr, None))
                            elif func.attr in foreign.classes:
                                for item in foreign.classes[func.attr]:
                                    todo.append((foreign, func.attr, item))
        visited = sorted(
            f"{Path(key.split(':', 1)[0]).relative_to(root)}:{key.split(':', 1)[1]}" for key in seen
            if Path(key.split(":", 1)[0]).is_relative_to(root)
        )
        out[entry] = {"uses": dict(used), "visited": visited}
    return out


def _print_ast(found: dict[str, dict]) -> None:
    for entry, info in found.items():
        print(f"## {entry}")
        if info.get("missing"):
            print("  (file not found)")
            continue
        uses = info["uses"]
        if not uses:
            print("  numpy: (none)")
        for name in sorted(uses):
            print(f"  numpy.{name}  ×{uses[name]}")
        print("  visited:")
        for item in info["visited"]:
            print(f"    {item}")


class _Proxy(types.ModuleType):
    """属性を取るたびに子を返し、呼ぶと AttributeError にする。"""

    def __getattr__(self, item):
        if item.startswith("__"):
            raise AttributeError(item)
        child = _Proxy(f"{self.__name__}.{item}")
        setattr(self, item, child)
        return child

    def __call__(self, *args, **kwargs):
        raise AttributeError(self.__name__)


def _absent_child() -> int:
    proxy = _Proxy("numpy")
    proxy.__file__ = "<absent numpy>"
    proxy.__package__ = "numpy"
    sys.modules["numpy"] = proxy
    for folder in (ROOT, ROOT / "pythdragoras", ROOT / "queryu", ROOT / "queryu" / "ask"):
        sys.path.insert(0, str(folder))
    try:
        import suggest
        suggest.Index([("P1", "得失点差がプラスなら上位半分である")], dim=4)
    except AttributeError:
        traceback.print_exc()
        text = traceback.format_exc()
        if "numpy." in text:
            print("absent-probe: first failure is a missing numpy attribute")
            return 0
        return 1
    print("absent-probe: Index ran without touching numpy", file=sys.stderr)
    return 1


def _wrap(np, log: list[dict]) -> None:
    def around(name, fn, *, skip=0):
        def wrapped(*args, **kwargs):
            start = time.perf_counter()
            out = fn(*args, **kwargs)
            elapsed = time.perf_counter() - start
            operands = args[skip:]
            shapes = [list(getattr(item, "shape", ()) or ()) for item in operands]
            dtypes = [str(getattr(item, "dtype", type(item).__name__)) for item in operands]
            extra = {key: kwargs[key] for key in ("full_matrices", "compute_uv", "rcond") if key in kwargs}
            log.append({
                "fn": name, "shape": shapes[0] if len(shapes) == 1 else shapes,
                "dtype": dtypes[0] if len(dtypes) == 1 else dtypes,
                "seconds": round(elapsed, 6), **extra,
            })
            print(f"trace {name} shape={shapes} dtype={dtypes} {extra} {elapsed:.4f}s", flush=True)
            return out
        return wrapped

    np.linalg.svd = around("linalg.svd", np.linalg.svd)
    np.linalg.lstsq = around("linalg.lstsq", np.linalg.lstsq)
    np.linalg.pinv = around("linalg.pinv", np.linalg.pinv)
    np.linalg.norm = around("linalg.norm", np.linalg.norm)
    np.einsum = around("einsum", np.einsum, skip=1)


def _trace(scope: str) -> int:
    import numpy as np
    log: list[dict] = []
    _wrap(np, log)
    spec = importlib.util.spec_from_file_location("run_linalg", ROOT / "shrink" / "run_linalg.py")
    if spec is None or spec.loader is None:
        raise SystemExit("run_linalg を読めない")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._prepare("real", allow_installed=True)
    payload = mod.collect(scope)
    print(json.dumps({"scope": scope, "calls": log, "seconds": payload["meta"]["seconds"]}, ensure_ascii=False))
    names = {row["fn"] for row in log}
    if scope == "fixture":
        need = {"linalg.svd", "linalg.lstsq", "linalg.norm", "einsum", "linalg.pinv"}
        missing = need - names
        if missing:
            print(f"trace が通らなかった: {sorted(missing)}", file=sys.stderr)
            return 1
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["ast", "trace", "absent", "report"])
    parser.add_argument("--scope", choices=["fixture", "c001"], default="fixture")
    args = parser.parse_args(argv)
    if args.cmd == "report":
        print(REPORT)
        _print_ast(analyze())
        return 0
    if args.cmd == "ast":
        _print_ast(analyze())
        return 0
    if args.cmd == "absent":
        if os.environ.get("AOI_LINALG_ABSENT_CHILD") == "1":
            return _absent_child()
        env = os.environ.copy()
        env["AOI_LINALG_ABSENT_CHILD"] = "1"
        return subprocess.call([sys.executable, str(Path(__file__).resolve()), "absent"], env=env)
    return _trace(args.scope)


if __name__ == "__main__":
    raise SystemExit(main())
