#!/usr/bin/env python3
"""Count third-party imports across Aoi and its child subtrees.

Standard library only. The count is static: ``import`` / ``from`` and string
literals passed to ``importlib.import_module`` or ``__import__``. Attribute
uses are ``alias.attr`` chains and names brought in with ``from pkg import``.
Methods on values (``frame.height``, ``series.to_list()``, ``a > b``) are not
visible here; ``scripts/trace_surface.py`` records those from a live run.

    python scripts/survey_third_party.py
    python scripts/survey_third_party.py --json docs/evidence/third-party-survey.json
    python scripts/survey_third_party.py --check docs/evidence/third-party-survey.json

A name is third-party when it is not in the standard library and either it is
declared in a pyproject/requirements file, or no project file or directory has
that name. Declared dependencies win over a same-named project file
(``vendor/markdown.py`` is not the PyPI package ``markdown``).
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
SKIP_PARTS = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", "build", ".cdn-cache", ".deps"}
# This study's own harness imports the packages on purpose. Leave it out of the inventory.
SKIP_FILES = {
    "scripts/survey_third_party.py",
    "scripts/trace_surface.py",
    "scripts/trace_drivers.py",
    "tests/test_survey_third_party.py",
    "tests/test_trace_surface.py",
    "tests/test_trace_surface_live.py",
}
REQ_NAME = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)")
SCHEMA = 1


def norm(name: str) -> str:
    return name.lower().replace("-", "_")


def iter_py_files(root: Path):
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        if rel.as_posix() in SKIP_FILES:
            continue
        yield path


def project_names(root: Path) -> set[str]:
    """File stems and directory names that a local import could refer to."""
    names = set()
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        if path.is_dir() or path.suffix == ".py":
            names.add(path.stem if path.suffix == ".py" else path.name)
    return names


def _dep_list(text: str) -> list[str]:
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


def declared_dependencies(root: Path) -> dict[str, list[dict]]:
    """Normalized distribution name -> where it was declared."""
    found: dict[str, list[dict]] = {}

    def add(name: str, file: str, kind: str) -> None:
        found.setdefault(norm(name), []).append({"file": file, "kind": kind, "name": name})

    for path in sorted(root.rglob("pyproject.toml")):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            continue
        project = data.get("project") or {}
        rel_s = rel.as_posix()
        for spec in project.get("dependencies") or []:
            for name in _dep_list(spec):
                add(name, rel_s, "runtime")
        for group, specs in (data.get("dependency-groups") or {}).items():
            for spec in specs or []:
                for name in _dep_list(spec):
                    add(name, rel_s, f"group:{group}")
        for group, specs in (project.get("optional-dependencies") or {}).items():
            for spec in specs or []:
                for name in _dep_list(spec):
                    add(name, rel_s, f"optional:{group}")
    for path in sorted(root.rglob("*requirements*.txt")):
        rel = path.relative_to(root)
        if SKIP_PARTS & set(rel.parts):
            continue
        for name in _dep_list(path.read_text(encoding="utf-8")):
            add(name, rel.as_posix(), "requirements")
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


def _aliases(tree: ast.AST) -> tuple[dict[str, tuple[str, str]], dict[str, tuple[str, str]]]:
    """Local name -> (top-level package, attribute prefix).

    ``import numpy.linalg as la`` maps ``la`` to ``("numpy", "linalg")``.
    ``from numpy.linalg import svd`` maps ``svd`` to ``("numpy", "linalg.svd")``.
    """
    modules: dict[str, tuple[str, str]] = {}
    names: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".", 1)[0]
                rest = alias.name[len(top) + 1:]
                if alias.asname:
                    modules[alias.asname] = (top, rest)
                else:
                    modules[top] = (top, "")
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            top = node.module.split(".", 1)[0]
            rest = node.module[len(top) + 1:]
            for alias in node.names:
                if alias.name == "*":
                    continue
                full = f"{rest}.{alias.name}" if rest else alias.name
                names[alias.asname or alias.name] = (top, full)
    return modules, names


def _dynamic_imports(tree: ast.AST) -> list[tuple[str, int]]:
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        is_dynamic = (isinstance(func, ast.Name) and func.id == "__import__") or (
            isinstance(func, ast.Attribute) and func.attr == "import_module"
        )
        if not is_dynamic:
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value:
            found.append((arg.value.split(".", 1)[0], node.lineno))
        else:
            found.append(("*", node.lineno))
    return found


def _uses(tree: ast.AST, modules: dict[str, tuple[str, str]], names: dict[str, tuple[str, str]]) -> dict[str, Counter]:
    found: dict[str, Counter] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and not isinstance(getattr(node, "_parent", None), ast.Attribute):
            chain = _attr_chain(node)
            if not chain or chain[0] not in modules or len(chain) < 2:
                continue
            top, prefix = modules[chain[0]]
            attrs = ".".join(part for part in (prefix, *chain[1:]) if part)
            found.setdefault(top, Counter())[attrs] += 1
        elif isinstance(node, ast.Name) and node.id in names and not isinstance(getattr(node, "_parent", None), ast.Attribute):
            # ``from pkg import name`` counts when ``name`` is used, not when it is only stored.
            if isinstance(getattr(node, "_parent", None), ast.alias):
                continue
            top, full = names[node.id]
            found.setdefault(top, Counter())[full] += 1
    return found


def _import_tops(tree: ast.AST) -> Counter:
    tops: Counter = Counter()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                tops[alias.name.split(".", 1)[0]] += 1
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            tops[node.module.split(".", 1)[0]] += 1
    return tops


def tree_of(rel: Path) -> str:
    return rel.parts[0] if len(rel.parts) > 1 else "aoi"


def survey(root: Path = ROOT) -> dict:
    declared = declared_dependencies(root)
    declared_norms = set(declared)
    stems = project_names(root)
    stdlib = sys.stdlib_module_names
    sites = []
    unparsed = []
    nonliteral = []
    for path in iter_py_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), rel)
        except SyntaxError:
            unparsed.append(rel)
            continue
        _tag_parents(tree)
        modules, names = _aliases(tree)
        uses = _uses(tree, modules, names)
        imports = _import_tops(tree)
        dynamic = _dynamic_imports(tree)
        for name, line in dynamic:
            if name == "*":
                nonliteral.append({"file": rel, "line": line})
        tops = set(imports) | set(uses) | {name for name, _ in dynamic if name != "*"}
        for top in sorted(tops):
            kind = "stdlib" if top in stdlib else (
                "third_party" if norm(top) in declared_norms or top not in stems else "local"
            )
            if kind != "third_party":
                continue
            attrs = uses.get(top, Counter())
            dyn = [line for name, line in dynamic if name == top]
            sites.append({
                "file": rel,
                "tree": tree_of(Path(rel)),
                "package": top,
                "import_sites": imports.get(top, 0),
                "dynamic_lines": dyn,
                "attributes": dict(sorted(attrs.items())),
            })
    return {
        "schema": SCHEMA,
        "packages": _rollup(sites, declared),
        "declared_without_imports": _undeclared_unused(declared, sites),
        "dynamic_nonliteral": nonliteral,
        "unparsed": unparsed,
        "sites": sites,
    }


def _undeclared_unused(declared: dict, sites: list[dict]) -> list[dict]:
    used = {norm(site["package"]) for site in sites}
    rows = []
    for key in sorted(set(declared) - used):
        rows.append({"name": key, "declared": declared[key]})
    return rows


def _rollup(sites: list[dict], declared: dict) -> dict:
    packages: dict[str, dict] = {}
    for site in sites:
        pkg = packages.setdefault(site["package"], {
            "import_sites": 0,
            "dynamic_import_sites": 0,
            "attribute_uses": 0,
            "attributes": Counter(),
            "files": set(),
            "by_tree": {},
        })
        pkg["import_sites"] += site["import_sites"]
        pkg["dynamic_import_sites"] += len(site["dynamic_lines"])
        pkg["files"].add(site["file"])
        attrs = Counter(site["attributes"])
        pkg["attributes"] += attrs
        pkg["attribute_uses"] += sum(attrs.values())
        tree = pkg["by_tree"].setdefault(site["tree"], {
            "import_sites": 0, "dynamic_import_sites": 0, "attribute_uses": 0,
            "attributes": Counter(), "files": set(),
        })
        tree["import_sites"] += site["import_sites"]
        tree["dynamic_import_sites"] += len(site["dynamic_lines"])
        tree["attribute_uses"] += sum(attrs.values())
        tree["attributes"] += attrs
        tree["files"].add(site["file"])
    out = {}
    for name in sorted(packages):
        pkg = packages[name]
        out[name] = {
            "attribute_uses": pkg["attribute_uses"],
            "attributes": dict(sorted(pkg["attributes"].items())),
            "by_tree": {
                tree: {
                    "attribute_uses": row["attribute_uses"],
                    "attributes": dict(sorted(row["attributes"].items())),
                    "dynamic_import_sites": row["dynamic_import_sites"],
                    "files": len(row["files"]),
                    "import_sites": row["import_sites"],
                }
                for tree, row in sorted(pkg["by_tree"].items())
            },
            "declared": declared.get(norm(name), []),
            "distinct_attributes": len(pkg["attributes"]),
            "dynamic_import_sites": pkg["dynamic_import_sites"],
            "files": len(pkg["files"]),
            "import_sites": pkg["import_sites"],
        }
    return out


def dumps(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def render(data: dict) -> str:
    lines = []
    for name, pkg in data["packages"].items():
        lines.append(
            f"{name}: files={pkg['files']} import_sites={pkg['import_sites']} "
            f"dynamic={pkg['dynamic_import_sites']} attr_uses={pkg['attribute_uses']} "
            f"names={pkg['distinct_attributes']}"
        )
        trees = ", ".join(
            f"{tree} files={row['files']} uses={row['attribute_uses']}"
            for tree, row in pkg["by_tree"].items()
        )
        lines.append(f"  trees: {trees}")
        top = ", ".join(f"{key}×{pkg['attributes'][key]}" for key in list(pkg["attributes"])[:12])
        if top:
            lines.append(f"  attrs: {top}")
    if data["declared_without_imports"]:
        lines.append("declared but never imported: " + ", ".join(row["name"] for row in data["declared_without_imports"]))
    if data["dynamic_nonliteral"]:
        lines.append(f"non-literal import_module/__import__: {len(data['dynamic_nonliteral'])}")
    if data["unparsed"]:
        lines.append("unparsed: " + ", ".join(data["unparsed"]))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", type=Path, help="write the inventory")
    parser.add_argument("--check", type=Path, help="fail if this file differs from a fresh survey")
    args = parser.parse_args(argv)
    data = survey(args.root)
    text = dumps(data)
    if args.check:
        current = args.check.read_text(encoding="utf-8") if args.check.exists() else ""
        if current != text:
            print(f"{args.check} is stale. Re-run with --json {args.check}", file=sys.stderr)
            return 1
        print(f"{args.check} ok ({len(data['packages'])} packages)")
        return 0
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")
        print(f"wrote {args.json}")
    print(render(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
