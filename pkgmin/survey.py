#!/usr/bin/env python3
"""AST inventory of requests, tqdm, and biopython across Aoi and the child subtrees.

Standard library only. Counts ``import`` / ``from`` and string literals passed
to ``importlib.import_module`` or ``__import__``. Attribute uses are
``alias.attr`` chains and names brought in with ``from pkg import``. This
file's own tree (``pkgmin/`` and its test) is excluded, same rule as the
feasibility harness: the study does not count itself.

    python pkgmin/survey.py
    python pkgmin/survey.py --check pkgmin/evidence/used-surface.json
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", "build", ".cdn-cache", ".deps", "pkgmin"}
SKIP_FILES = {"tests/test_pkgmin_surface.py"}
# Distribution name -> import names a file would actually use.
TARGETS = {
    "requests": ("requests",),
    "tqdm": ("tqdm",),
    "biopython": ("Bio", "biopython"),
}
IMPORT_TO_DIST = {name: dist for dist, names in TARGETS.items() for name in names}
REQ_NAME = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)")


def iter_py_files(root: Path):
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        if rel.as_posix() in SKIP_FILES:
            continue
        yield path


def _dep_names(text: str) -> list[str]:
    names = []
    for line in text.splitlines():
        body = line.split("#", 1)[0].strip()
        if not body:
            continue
        body = body.split(";", 1)[0].strip().strip("\"'")
        match = REQ_NAME.match(body)
        if match:
            names.append(match.group(1))
    return names


def declared(root: Path) -> dict[str, list[dict]]:
    """Where a target distribution is declared. Empty for these three today."""
    found = {dist: [] for dist in TARGETS}
    # Match the wheel name. Bio is the import name, not the distribution.
    wanted = {dist: {dist, dist.replace("_", "-")} for dist in TARGETS}

    def add(dist: str, file: str, kind: str, name: str) -> None:
        found[dist].append({"file": file, "kind": kind, "name": name})

    for path in sorted(root.rglob("pyproject.toml")):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            continue
        project = data.get("project") or {}
        specs = [(spec, "runtime") for spec in (project.get("dependencies") or [])]
        for group, group_specs in (data.get("dependency-groups") or {}).items():
            specs.extend((spec, f"group:{group}") for spec in (group_specs or []))
        for group, group_specs in (project.get("optional-dependencies") or {}).items():
            specs.extend((spec, f"optional:{group}") for spec in (group_specs or []))
        for spec, kind in specs:
            for name in _dep_names(spec if isinstance(spec, str) else str(spec)):
                key = name.lower().replace("-", "_")
                for dist, aliases in wanted.items():
                    if key in {alias.lower().replace("-", "_") for alias in aliases}:
                        add(dist, rel.as_posix(), kind, name)
    for path in sorted(root.rglob("*requirements*.txt")):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        for name in _dep_names(path.read_text(encoding="utf-8")):
            key = name.lower().replace("-", "_")
            for dist, aliases in wanted.items():
                if key in {alias.lower().replace("-", "_") for alias in aliases}:
                    add(dist, rel.as_posix(), "requirements", name)
    return found


def _tag_parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node  # type: ignore[attr-defined]


def _attr_chain(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return [node.id, *reversed(parts)]
    return None


def scan_file(path: Path, rel: str) -> tuple[list[dict], Counter, list[dict]]:
    """Import sites, attribute counts by distribution, and non-literal dynamic imports."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), rel)
    except SyntaxError:
        return [], Counter(), [{"file": rel, "line": 0, "kind": "unparsed"}]
    _tag_parents(tree)
    sites: list[dict] = []
    attrs: Counter = Counter()
    nonliteral: list[dict] = []
    modules: dict[str, tuple[str, str]] = {}
    names: dict[str, tuple[str, str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".", 1)[0]
                rest = alias.name[len(top) + 1:]
                if top not in IMPORT_TO_DIST:
                    continue
                dist = IMPORT_TO_DIST[top]
                sites.append({"file": rel, "line": node.lineno, "module": alias.name, "kind": "import"})
                if rest:
                    attrs[(dist, rest)] += 1
                # ``import pkg.sub`` binds the name ``pkg``. ``import pkg.sub as sub`` binds ``sub``.
                if alias.asname:
                    modules[alias.asname] = (dist, rest)
                else:
                    modules[top] = (dist, "")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            top = node.module.split(".", 1)[0]
            rest = node.module[len(top) + 1:]
            if top not in IMPORT_TO_DIST:
                continue
            dist = IMPORT_TO_DIST[top]
            for alias in node.names:
                if alias.name == "*":
                    sites.append({"file": rel, "line": node.lineno, "module": node.module, "kind": "from"})
                    continue
                full = f"{rest}.{alias.name}" if rest else alias.name
                sites.append({"file": rel, "line": node.lineno, "module": f"{node.module}.{alias.name}", "kind": "from"})
                attrs[(dist, full)] += 1
                names[alias.asname or alias.name] = (dist, full)
        elif isinstance(node, ast.Call) and node.args:
            func = node.func
            dynamic = (isinstance(func, ast.Name) and func.id == "__import__") or (
                isinstance(func, ast.Attribute) and func.attr == "import_module"
            )
            if not dynamic:
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value:
                top = arg.value.split(".", 1)[0]
                if top in IMPORT_TO_DIST:
                    dist = IMPORT_TO_DIST[top]
                    sites.append({"file": rel, "line": node.lineno, "module": arg.value, "kind": "dynamic"})
                    rest = arg.value[len(top) + 1:]
                    if rest:
                        attrs[(dist, rest)] += 1
            else:
                nonliteral.append({"file": rel, "line": node.lineno})

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and not isinstance(getattr(node, "_parent", None), ast.Attribute):
            chain = _attr_chain(node)
            if not chain or chain[0] not in modules or len(chain) < 2:
                continue
            dist, prefix = modules[chain[0]]
            dotted = ".".join(part for part in (prefix, *chain[1:]) if part)
            attrs[(dist, dotted)] += 1
        elif isinstance(node, ast.Name) and node.id in names and not isinstance(getattr(node, "_parent", None), (ast.Attribute, ast.alias)):
            dist, full = names[node.id]
            attrs[(dist, full)] += 1
    return sites, attrs, nonliteral


def scan(root: Path = ROOT) -> dict:
    files = 0
    by_dist_sites: dict[str, list[dict]] = {dist: [] for dist in TARGETS}
    by_dist_attrs: dict[str, Counter] = {dist: Counter() for dist in TARGETS}
    nonliteral: list[dict] = []
    for path in iter_py_files(root):
        files += 1
        rel = path.relative_to(root).as_posix()
        sites, attrs, dynamic = scan_file(path, rel)
        for site in sites:
            top = site["module"].split(".", 1)[0]
            by_dist_sites[IMPORT_TO_DIST[top]].append(site)
        for (dist, name), count in attrs.items():
            by_dist_attrs[dist][name] += count
        nonliteral.extend(item for item in dynamic if item not in nonliteral)
    decls = declared(root)
    packages = {}
    for dist, import_names in TARGETS.items():
        packages[dist] = {
            "attributes": dict(sorted(by_dist_attrs[dist].items())),
            "declared": decls[dist],
            "import_names": list(import_names),
            "import_sites": by_dist_sites[dist],
        }
    return {
        "dynamic_nonliteral": nonliteral,
        "files_scanned": files,
        "packages": packages,
        "schema": 1,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", type=Path, help="fail if the package surface disagrees with this JSON")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    data = scan(args.root)
    if args.check:
        previous = json.loads(args.check.read_text(encoding="utf-8"))
        fresh = {"dynamic_nonliteral": data["dynamic_nonliteral"], "packages": data["packages"]}
        saved = {"dynamic_nonliteral": previous["dynamic_nonliteral"], "packages": previous["packages"]}
        if fresh != saved:
            print(f"{args.check} does not match the tree. Re-run without --check.", file=sys.stderr)
            return 1
        print(f"{args.check} ok ({data['files_scanned']} files, no requests/tqdm/biopython imports)")
        return 0
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
