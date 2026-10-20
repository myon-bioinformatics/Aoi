#!/usr/bin/env python3
"""Count polars names with the ast survey/analyze from Aoi scripts/shrink_module.py (PR 89).

survey walks every project file and counts ``import polars as pl`` / ``from polars import name``
uses (``pl.DataFrame``, ``pl.col``). analyze keeps only the uses reachable from an entry
function, following same-module calls and ``module.func(...)`` calls whose module file is in
this tree.

Methods on returned values (``df.explode()``, ``expr.is_not_null()``) are not visible: the
receiver is a call, not the polars alias. scripts/shrink_polars.py finds those by running
``research_digest.collect``.
"""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", ".pytest_cache"}


def py_files(root: Path = ROOT):
    for path in sorted(root.rglob("*.py")):
        if not SKIP & set(path.relative_to(root).parts):
            yield path


def aliases(tree: ast.AST, pkg: str) -> tuple[set[str], dict[str, str]]:
    """Module aliases (``pl``) and ``from polars import name`` bindings."""
    mods, names = set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == pkg:
                    mods.add(alias.asname or pkg)
        elif isinstance(node, ast.ImportFrom) and node.module == pkg:
            for alias in node.names:
                names[alias.asname or alias.name] = alias.name
    return mods, names


def _attr_chain(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return [node.id, *reversed(parts)]
    return None


def uses(node: ast.AST, mods: set[str], names: dict[str, str]) -> Counter:
    found: Counter = Counter()
    for sub in ast.walk(node):
        parent = getattr(sub, "_parent", None)
        if isinstance(sub, ast.Attribute) and not isinstance(parent, ast.Attribute):
            chain = _attr_chain(sub)
            if chain and chain[0] in mods and len(chain) > 1:
                found[".".join(chain[1:])] += 1
        elif isinstance(sub, ast.Name) and sub.id in names and not isinstance(parent, ast.Attribute):
            found[names[sub.id]] += 1
    return found


def parse(path: Path) -> ast.Module:
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node  # do not count the middle of an attribute chain twice
    return tree


def survey(pkg: str, root: Path = ROOT) -> dict[str, Counter]:
    found = {}
    for path in py_files(root):
        try:
            tree = parse(path)
        except SyntaxError:
            continue
        mods, names = aliases(tree, pkg)
        if mods or names:
            found[str(path.relative_to(root))] = uses(tree, mods, names)
    return found


def _module_index(root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for path in py_files(root):
        index.setdefault(path.stem, []).append(path)
    return index


def analyze(pkg: str, entries: list[str], root: Path = ROOT) -> tuple[Counter, list[str]]:
    """Names used by functions reachable from ``path.py:func`` entries, and those functions."""
    index = _module_index(root)
    trees: dict[Path, ast.Module] = {}

    def tree_of(path: Path) -> ast.Module:
        if path not in trees:
            trees[path] = parse(path)
        return trees[path]

    def funcs(path: Path) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
        return {
            node.name: node
            for node in tree_of(path).body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    todo: list[tuple[Path, str]] = []
    for entry in entries:
        file, func = entry.split(":")
        todo.append(((root / file).resolve(), func))
    seen: set[tuple[Path, str]] = set()
    used: Counter = Counter()
    while todo:
        path, name = todo.pop()
        if (path, name) in seen or not path.is_file():
            continue
        seen.add((path, name))
        fn = funcs(path).get(name)
        if fn is None:
            continue
        mods, bound = aliases(tree_of(path), pkg)
        used += uses(fn, mods, bound)
        local = funcs(path)
        for sub in ast.walk(fn):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            if isinstance(func, ast.Name) and func.id in local:
                todo.append((path, func.id))
            elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in index:
                    for cand in index[func.value.id]:
                        if func.attr in funcs(cand):
                            todo.append((cand.resolve(), func.attr))
    visited = sorted(
        f"{path.relative_to(root)}:{name}" for path, name in seen if name in funcs(path)
    )
    return used, visited
