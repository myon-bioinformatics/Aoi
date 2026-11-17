"""stdlib_min: 標準ライブラリだけの代わり（*_min.py）で Aoi の本物のコードを動かし、使う面を数える実験の入口。

  python scripts/stdlib_min.py COMMAND [ARGS...]   # COMMAND と旧ファイルの対応は各関数の説明

"""
from __future__ import annotations

import argparse
import ast
import builtins
import functools
import hashlib
import importlib.machinery
import importlib.util
import inspect
import json
import math
import os
import re
import runpy
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import traceback
import types
from collections import Counter, defaultdict
from fnmatch import fnmatchcase
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


# ==== 共通


def py_files(root: Path, skip: set[str]):
    """root の下の .py を名前順に並べる（skip の名前を部分に含むパスは除く）。"""
    for path in sorted(root.rglob("*.py")):
        if not skip & set(path.relative_to(root).parts):
            yield path


def inject(name: str, filename: Path) -> None:
    """標準ライブラリだけの代わり（filename）を、本物の name として sys.modules に置く。"""
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


# ==== survey（旧 survey_third_party.py）

SURVEY_DOC = """Count third-party imports across Aoi and its child subtrees.

Standard library only. The count is static: ``import`` / ``from`` and string
literals passed to ``importlib.import_module`` or ``__import__``. Attribute
uses are ``alias.attr`` chains and names brought in with ``from pkg import``.
Methods on values (``frame.height``, ``series.to_list()``, ``a > b``) are not
visible here; ``scripts/stdlib_min.py trace-surface`` records those from a live run.

    python scripts/stdlib_min.py survey
    python scripts/stdlib_min.py survey --json docs/evidence/third-party-survey.json
    python scripts/stdlib_min.py survey --check docs/evidence/third-party-survey.json

A name is third-party when it is not in the standard library and either it is
declared in a pyproject/requirements file, or no project file or directory has
that name. Declared dependencies win over a same-named project file
(``vendor/markdown.py`` is not the PyPI package ``markdown``).

Python 3.12 accepts ``f'{row['name']}'``. When that form fails to parse, the
f-string is widened to triple quotes and the file is parsed again, so the
inventory does not change with the interpreter.
"""

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", "build", ".cdn-cache", ".deps"}
# Harnesses import the packages on purpose. Leave them out of the inventory so
# the counts stay the product tree, not the measurement scripts.
# scripts/stdlib_min.py holds the study's own commands (survey, trace-surface,
# trace-drivers) and the sibling experiments merged with it (#91 selectolax /
# httpx / coverage, #94 numpy linalg, and the numpy_min / polars_min overlap
# runs). #92 polars_min and #95 requests / tqdm / biopython keep their own files.
SKIP_FILES = {
    "scripts/stdlib_min.py",
    "scripts/shrink_polars.py",
    "pkgmin/run_paths.py",
    "tests/test_survey_third_party.py",
    "tests/test_numpy_linalg_min.py",
    "tests/test_pkgmin_surface.py",
    "tests/test_shrink_polars.py",
    "tests/test_third_party_min.py",
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


def survey__uses(tree: ast.AST, modules: dict[str, tuple[str, str]], names: dict[str, tuple[str, str]]) -> dict[str, Counter]:
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


def relax_fstring_quotes(source: str) -> str:
    """Rewrite f-strings that reuse their delimiter inside ``{}``.

    ``f'{row['name']}'`` is legal from Python 3.12. The 3.11 parser ends the
    literal at the inner quote, and that quote cannot appear anywhere inside the
    literal. Widening the delimiter (``f'''{row['name']}'''``) keeps the
    expression and stays inside the quotes of a surrounding f-string.
    """
    text, _ = _scan_code(source, 0, len(source))
    return text


def _widen_fstring_delimiter(delimiter: str, body: str) -> str:
    if len(delimiter) != 1 or delimiter not in body or body.endswith("\\"):
        return delimiter
    other = '"' if delimiter == "'" else "'"
    for candidate in (delimiter * 3, other, other * 3):
        if candidate not in body:
            return candidate
    return delimiter


def _valid_string_prefix(prefix: str) -> bool:
    if len(prefix) > 2:
        return False
    letters = [char.lower() for char in prefix]
    if len(set(letters)) != len(letters):
        return False
    if "u" in letters and letters != ["u"]:
        return False
    if "b" in letters and "f" in letters:
        return False
    return all(char in "rbuf" for char in letters)


def _string_open(source: str, i: int, end: int) -> tuple[str, int, str] | None:
    """Return ``(prefix, body_index, delimiter)`` when a string starts at ``i``."""
    if i >= end:
        return None
    if i > 0 and (source[i - 1].isalnum() or source[i - 1] == "_"):
        return None
    for length in (2, 1, 0):
        quote_at = i + length
        if quote_at >= end or source[quote_at] not in "'\"":
            continue
        prefix = source[i:quote_at]
        if not _valid_string_prefix(prefix):
            continue
        quote = source[quote_at]
        if source.startswith(quote * 3, quote_at):
            delimiter = quote * 3
        else:
            delimiter = quote
        return prefix, quote_at + len(delimiter), delimiter
    return None


def _retarget_string(delimiter: str, content: str, banned: frozenset[str]) -> str:
    if delimiter[0] not in banned:
        return delimiter + content + delimiter
    other = '"' if delimiter[0] == "'" else "'"
    candidates = []
    if other not in banned:
        candidates.append(other * len(delimiter) if len(delimiter) == 3 else other)
        candidates.append(other * 3)
    for opener in candidates:
        if opener in content or content.endswith("\\"):
            continue
        return opener + content + opener
    return delimiter + content + delimiter


def _plain_string(source: str, start: int, body: int, delimiter: str, end: int, raw: bool, banned: frozenset[str]) -> tuple[str, int]:
    i = body
    content: list[str] = []
    while i < end:
        if source.startswith(delimiter, i):
            text = _retarget_string(delimiter, "".join(content), banned)
            prefix = source[start:body - len(delimiter)]
            return prefix + text, i + len(delimiter)
        if source[i] == "\\" and i + 1 < end:
            nxt = source[i + 1]
            if raw and source.startswith(delimiter, i + 1):
                content.append(source[i:i + 1 + len(delimiter)])
                i += 1 + len(delimiter)
                continue
            if not raw:
                content.append(source[i:i + 2])
                i += 2
                continue
            content.append(source[i:i + 2] if nxt != "\n" else source[i])
            i += 2 if nxt != "\n" else 1
            continue
        content.append(source[i])
        i += 1
    return source[start:end], end


def _scan_string(source: str, i: int, end: int, banned: frozenset[str]) -> tuple[str, int] | None:
    opened = _string_open(source, i, end)
    if opened is None:
        return None
    prefix, body, delimiter = opened
    raw = "r" in prefix.lower()
    if "f" not in prefix.lower():
        return _plain_string(source, i, body, delimiter, end, raw, banned)
    # Nested f-strings are rewritten first. This delimiter is widened only when
    # the quote still occurs in the body, which is what Python 3.11 rejects.
    rewritten, close = _scan_fstring_body(source, body, delimiter, end, frozenset())
    if close == end and not source.startswith(delimiter, max(0, close - len(delimiter))):
        return source[i:end], end
    opener = _widen_fstring_delimiter(delimiter, rewritten)
    return prefix + opener + rewritten + opener, close


def _scan_fstring_body(source: str, i: int, delimiter: str, end: int, banned: frozenset[str]) -> tuple[str, int]:
    parts: list[str] = []
    while i < end:
        if source.startswith(delimiter, i):
            return "".join(parts), i + len(delimiter)
        if source[i] == "\\" and i + 1 < end:
            parts.append(source[i:i + 2])
            i += 2
            continue
        if source.startswith("{{", i) or source.startswith("}}", i):
            parts.append(source[i:i + 2])
            i += 2
            continue
        if source[i] == "{":
            expr, i = _scan_interpolation(source, i + 1, end, banned)
            parts.append("{" + expr + "}")
            continue
        parts.append(source[i])
        i += 1
    return "".join(parts), i


def _scan_interpolation(source: str, i: int, end: int, banned: frozenset[str]) -> tuple[str, int]:
    parts: list[str] = []
    brace = paren = bracket = 0
    while i < end:
        nested = _scan_string(source, i, end, banned)
        if nested is not None:
            text, i = nested
            parts.append(text)
            continue
        char = source[i]
        if char == "#":
            newline = source.find("\n", i, end)
            if newline < 0:
                parts.append(source[i:end])
                return "".join(parts), end
            parts.append(source[i:newline + 1])
            i = newline + 1
            continue
        if char == "{":
            brace += 1
        elif char == "}":
            if brace == paren == bracket == 0:
                return "".join(parts), i + 1
            if brace:
                brace -= 1
        elif char == "(":
            paren += 1
        elif char == ")":
            if paren:
                paren -= 1
        elif char == "[":
            bracket += 1
        elif char == "]":
            if bracket:
                bracket -= 1
        parts.append(char)
        i += 1
    return "".join(parts), i


def _scan_code(source: str, i: int, end: int) -> tuple[str, int]:
    parts: list[str] = []
    while i < end:
        if source[i] == "#":
            newline = source.find("\n", i, end)
            if newline < 0:
                parts.append(source[i:end])
                return "".join(parts), end
            parts.append(source[i:newline + 1])
            i = newline + 1
            continue
        nested = _scan_string(source, i, end, frozenset())
        if nested is not None:
            text, i = nested
            parts.append(text)
            continue
        parts.append(source[i])
        i += 1
    return "".join(parts), i


def parse_source(source: str, filename: str) -> ast.AST:
    """Parse ``source``, relaxing f-string quotes when this interpreter must."""
    try:
        return ast.parse(source, filename)
    except SyntaxError as exc:
        if "f-string" not in (exc.msg or ""):
            raise
        relaxed = relax_fstring_quotes(source)
        if relaxed == source:
            raise
        return ast.parse(relaxed, filename)


def selected_files(root: Path, matches=(), excludes=()) -> list[Path]:
    """Select eligible sources by root-relative POSIX glob; excludes win."""
    if not root.is_dir():
        raise ValueError(f"not a directory: {root}")
    if any(not pattern.strip() for pattern in (*matches, *excludes)):
        raise ValueError("patterns must not be empty")
    paths = [p for p in iter_py_files(root) if p.is_file()
             if (not matches or any(fnmatchcase(p.relative_to(root).as_posix(), pat)
                                    for pat in matches))
             and not any(fnmatchcase(p.relative_to(root).as_posix(), pat)
                         for pat in excludes)]
    if not paths and (matches or excludes):
        raise ValueError("no eligible Python sources selected")
    return paths


def survey_survey(root: Path = ROOT, *, matches=(), excludes=()) -> dict:
    paths = selected_files(root, matches, excludes)
    declared = declared_dependencies(root)
    declared_norms = set(declared)
    stems = project_names(root)
    stdlib = sys.stdlib_module_names
    sites = []
    unparsed = []
    nonliteral = []
    for path in paths:
        rel = path.relative_to(root).as_posix()
        try:
            tree = parse_source(path.read_text(encoding="utf-8"), rel)
        except SyntaxError:
            unparsed.append(rel)
            continue
        _tag_parents(tree)
        modules, names = _aliases(tree)
        uses = survey__uses(tree, modules, names)
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
    result = {
        "schema": SCHEMA,
        "packages": _rollup(sites, declared),
        "declared_without_imports": _undeclared_unused(declared, sites),
        "dynamic_nonliteral": nonliteral,
        "unparsed": unparsed,
        "sites": sites,
    }
    if matches or excludes:
        result["selection"] = {"match": list(matches), "exclude": list(excludes),
                               "files": len(paths), "context": "whole_root",
                               "declared_without_imports_scope": "selected_sources"}
    return result


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
    if "selection" in data:
        lines.insert(0, f"selected sources: {data['selection']['files']} (declarations and local names: whole root)")
        lines = [line.replace("declared but never imported:", "declared but not imported in selected sources:") for line in lines]
    return "\n".join(lines)


def survey(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=SURVEY_DOC.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", type=Path, help="write the inventory")
    parser.add_argument("--check", type=Path, help="fail if this file differs from a fresh survey")
    parser.add_argument("--match", action="append", default=[], help="root-relative POSIX glob (repeat: OR; * includes /)")
    parser.add_argument("--exclude", action="append", default=[], help="exclude glob (repeat: OR; overrides --match)")
    parser.add_argument("--list", action="store_true", help="print selected source paths as JSON without reading source or declarations")
    args = parser.parse_args(argv)
    if args.list and (args.json or args.check):
        parser.error("--list cannot be combined with --json or --check")
    try:
        if args.list:
            print(json.dumps([p.relative_to(args.root).as_posix()
                              for p in selected_files(args.root, args.match, args.exclude)], indent=2))
            return 0
        data = survey_survey(args.root, matches=args.match, excludes=args.exclude)
    except (ValueError, OSError) as error:
        print(f"survey: {error}", file=sys.stderr)
        return 2
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


# ==== trace-surface（旧 trace_surface.py）

TRACE_SURFACE_DOC = """Run a command with a third-party import blocked, stubbed, or wrapped.

AST surveys only see ``pkg.attr`` written on the import alias. This tool runs
the real call and records what that survey cannot see.

absent
    A meta-path finder raises ``ModuleNotFoundError`` for the package and its
    submodules. The traceback is the same import failure a missing wheel gives.
stub
    ``import pkg`` succeeds. Every attribute is another stub. The first
    operation that needs a real value (truth, length, iteration, a number)
    raises ``StubGap``. The events are the prefix of the surface; the
    traceback is the first hole.
wrap
    The installed package is delegated to. Attribute access is logged only
    when the nearest caller outside this file is project code, and only
    objects that belong to the package stay wrapped. The command can finish.
    Names logged here but absent from ``survey_third_party.py`` are the ones
    the AST missed (methods and operators on returned objects).

    python scripts/stdlib_min.py trace-surface absent polars -- python scripts/stdlib_min.py trace-drivers load_overlap
    python scripts/stdlib_min.py trace-surface stub polars -- python scripts/stdlib_min.py trace-drivers load_overlap
    python scripts/stdlib_min.py trace-surface wrap polars -- python scripts/stdlib_min.py trace-drivers load_overlap
    python scripts/stdlib_min.py trace-surface collect --out docs/evidence/trace-surfaces.json

``--apply`` is the in-process hook used by the commands above. Exit status of
``wrap`` is the command's status. ``absent`` and ``stub`` exit 0 when they
captured a traceback.
"""
TOOL = Path(__file__).resolve()

# Drivers the summary report re-runs. Each entry is one live observation.
COLLECT = [
    ("absent", "polars", "load_overlap"),
    ("stub", "polars", "load_overlap"),
    ("wrap", "polars", "load_overlap"),
    ("wrap", "numpy", "load_overlap"),
    ("wrap", "numpy", "suggest_index"),
    ("wrap", "numpy", "littlebit_svd"),
    ("absent", "selectolax", "selectolax_css"),
    ("stub", "selectolax", "selectolax_css"),
    ("wrap", "selectolax", "selectolax_css"),
    ("absent", "httpx", "httpx_get"),
    ("stub", "httpx", "httpx_get"),
    ("wrap", "httpx", "httpx_get"),
    ("absent", "ortools", "ortools_import"),
    ("stub", "ortools", "ortools_import"),
    ("absent", "pandas", "pandas_surface"),
    ("stub", "pandas", "pandas_surface"),
]


class StubGap(TypeError):
    """The stub proxy was asked for a real value."""


class Log:
    def __init__(self, package: str, root: Path):
        self.package = package
        self.root = str(root)
        self.counts: Counter = Counter()
        self.first: list[dict] = []
        self._seen: set[tuple] = set()

    def project_caller(self) -> str | None:
        """Nearest frame that is neither this tool nor an import bootstrap."""
        frame = sys._getframe(1)
        while frame is not None:
            filename = frame.f_code.co_filename
            if frame.f_globals is globals() or filename.startswith("<"):
                frame = frame.f_back
                continue
            if filename.startswith(self.root) and "site-packages" not in filename:
                rel = os.path.relpath(filename, self.root)
                return f"{rel}:{frame.f_lineno}"
            return None
        return None

    def record(self, op: str, qual: str, name: str) -> None:
        where = self.project_caller()
        if where is None:
            return
        key = (op, qual, name)
        self.counts[key] += 1
        if key in self._seen:
            return
        self._seen.add(key)
        file, line = where.rsplit(":", 1)
        self.first.append({"op": op, "qual": qual, "name": name, "file": file, "line": int(line)})

    def payload(self) -> list[dict]:
        rows = []
        for row in self.first:
            key = (row["op"], row["qual"], row["name"])
            rows.append({**row, "count": self.counts[key]})
        return rows


def _from_package(obj, package: str) -> bool:
    if isinstance(obj, (bool, int, float, str, bytes, type(None))):
        return False
    module = getattr(obj, "__module__", None)
    if not isinstance(module, str):
        module = getattr(type(obj), "__module__", "") or ""
    if not (module == package or module.startswith(package + ".")):
        return False
    # A numpy 0-d scalar stays bare so ``1 + np.log(x)`` does not need a proxy.
    # Do not probe ``ndim`` on other packages: a Polars Expr treats ``==`` as data.
    if package == "numpy":
        try:
            ndim = getattr(obj, "ndim", None)
        except Exception:
            ndim = None
        if ndim == 0:
            return False
    return True


class Proxy:
    """Delegates to a real package object and logs project-side access."""

    __slots__ = ("_obj", "_qual", "_log")

    def __init__(self, obj, qual: str, log: Log):
        object.__setattr__(self, "_obj", obj)
        object.__setattr__(self, "_qual", qual)
        object.__setattr__(self, "_log", log)

    def __getattr__(self, name):
        self._log.record("getattr", self._qual, name)
        value = getattr(self._obj, name)
        # Bound methods of extension types often report a non-package __module__.
        # Wrap every callable so the call still unwraps proxies before delegation.
        if callable(value):
            return Proxy(value, f"{self._qual}.{name}", self._log)
        return expose(value, f"{self._qual}.{name}", self._log)

    def __call__(self, *args, **kwargs):
        self._log.record("call", self._qual, "")
        out = self._obj(*[_unwrap(arg) for arg in args], **{key: _unwrap(value) for key, value in kwargs.items()})
        return expose(out, f"{self._qual}()", self._log)

    def __repr__(self):
        return repr(self._obj)

    def __str__(self):
        return str(self._obj)


def _bind(name: str):
    def op(self, *args, **kwargs):
        self._log.record("dunder", self._qual, name)
        fn = getattr(self._obj, name)
        out = fn(*[_unwrap(arg) for arg in args], **{key: _unwrap(value) for key, value in kwargs.items()})
        if name in {"__bool__", "__int__", "__float__", "__index__", "__len__", "__hash__", "__exit__"}:
            return out
        return expose(out, f"{self._qual}.{name}", self._log)

    op.__name__ = name
    return op


for _name in (
    "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__add__", "__radd__", "__sub__", "__rsub__", "__mul__", "__rmul__",
    "__truediv__", "__rtruediv__", "__floordiv__", "__rfloordiv__",
    "__mod__", "__rmod__", "__matmul__", "__rmatmul__", "__pow__", "__rpow__",
    "__and__", "__rand__", "__or__", "__ror__", "__xor__", "__rxor__",
    "__invert__", "__neg__", "__pos__", "__abs__",
    "__getitem__", "__setitem__", "__contains__",
    "__len__", "__bool__", "__int__", "__float__", "__index__",
    "__enter__", "__exit__",
):
    setattr(Proxy, _name, _bind(_name))


def __iter__(self):
    self._log.record("dunder", self._qual, "__iter__")
    for item in self._obj:
        yield expose(item, f"{self._qual}[]", self._log)


Proxy.__iter__ = __iter__  # type: ignore[method-assign]


def _unwrap(obj):
    if isinstance(obj, Proxy):
        return obj._obj
    if type(obj) is list:
        return [_unwrap(item) for item in obj]
    if type(obj) is tuple:
        return tuple(_unwrap(item) for item in obj)
    if type(obj) is dict:
        return {key: _unwrap(value) for key, value in obj.items()}
    return obj


_CACHE: dict[int, Proxy] = {}
_ARMED: set[int] = set()


def expose(obj, qual: str, log: Log):
    if type(obj) is list:
        return [expose(item, qual, log) for item in obj]
    if type(obj) is tuple:
        return tuple(expose(item, qual, log) for item in obj)
    if isinstance(obj, Proxy) or not _from_package(obj, log.package):
        return obj
    if inspect.ismodule(obj):
        return arm_module(obj, log)
    cached = _CACHE.get(id(obj))
    if cached is None:
        cached = Proxy(obj, qual, log)
        _CACHE[id(obj)] = cached
    return cached


def arm_module(module, log: Log):
    if id(module) in _ARMED:
        return module
    _ARMED.add(id(module))
    package = log.package
    origin = module.__class__

    class Logged(origin):
        def __getattribute__(self, name, _log=log, _pkg=package):
            value = super().__getattribute__(name)
            if name.startswith("_") or not _log.project_caller():
                return value
            _log.record("getattr", self.__name__, name)
            return expose(value, f"{self.__name__}.{name}", _log)

    try:
        module.__class__ = Logged
    except TypeError:
        for key, value in list(vars(module).items()):
            if key.startswith("_"):
                continue
            wrapped = expose(value, f"{module.__name__}.{key}", log)
            if wrapped is not value:
                try:
                    setattr(module, key, wrapped)
                except (AttributeError, TypeError):
                    pass
    return module


class AbsentLoader:
    def __init__(self, fullname: str):
        self.fullname = fullname

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise ModuleNotFoundError(
            f"No module named {self.fullname!r} (trace_surface absent: import blocked)"
        )


class Stub:
    def __init__(self, qual: str, log: Log):
        object.__setattr__(self, "_qual", qual)
        object.__setattr__(self, "_log", log)

    def __getattr__(self, name):
        self._log.record("getattr", self._qual, name)
        return Stub(f"{self._qual}.{name}", self._log)

    def __call__(self, *args, **kwargs):
        self._log.record("call", self._qual, "")
        return Stub(f"{self._qual}()", self._log)

    def __getitem__(self, key):
        self._log.record("dunder", self._qual, "__getitem__")
        return Stub(f"{self._qual}[]", self._log)

    def __setitem__(self, key, value):
        self._log.record("dunder", self._qual, "__setitem__")
        raise StubGap(f"stub proxy cannot perform __setitem__ on {self._qual}")

    def __iter__(self):
        self._log.record("dunder", self._qual, "__iter__")
        raise StubGap(f"stub proxy cannot iterate {self._qual}")

    def __enter__(self):
        self._log.record("dunder", self._qual, "__enter__")
        return self

    def __exit__(self, *args):
        self._log.record("dunder", self._qual, "__exit__")
        return False

    def __repr__(self):
        return f"Stub({self._qual})"

    def __str__(self):
        return self._qual


def _stub_gap(name: str):
    def op(self, *args, **kwargs):
        self._log.record("dunder", self._qual, name)
        raise StubGap(f"stub proxy cannot perform {name} on {self._qual}")

    return op


def _stub_chain(name: str):
    def op(self, *args, **kwargs):
        self._log.record("dunder", self._qual, name)
        return Stub(f"{self._qual}.{name}", self._log)

    return op


for _gap_name in ("__bool__", "__len__", "__int__", "__float__", "__index__", "__hash__"):
    setattr(Stub, _gap_name, _stub_gap(_gap_name))
for _chain_name in (
    "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__add__", "__radd__", "__sub__", "__rsub__", "__mul__", "__rmul__",
    "__truediv__", "__matmul__", "__and__", "__rand__", "__or__", "__ror__",
    "__invert__", "__neg__", "__contains__",
):
    setattr(Stub, _chain_name, _stub_chain(_chain_name))


class StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name in {"_log", "_qual"}:
            raise AttributeError(name)
        log = self.__dict__["_log"]
        qual = self.__dict__["_qual"]
        log.record("getattr", qual, name)
        return Stub(f"{qual}.{name}", log)


class StubLoader:
    def __init__(self, log: Log):
        self.log = log

    def create_module(self, spec):
        module = StubModule(spec.name)
        module.__dict__["_log"] = self.log
        module.__dict__["_qual"] = spec.name
        # Submodule imports (``selectolax.lexbor``, ``ortools.sat``) require a package.
        module.__path__ = []
        module.__package__ = spec.name.rpartition(".")[0] or spec.name
        return module

    def exec_module(self, module):
        return None


class WrapLoader:
    def __init__(self, real, log: Log):
        self.real = real
        self.log = log

    def create_module(self, spec):
        create = getattr(self.real, "create_module", None)
        return None if create is None else create(spec)

    def exec_module(self, module):
        self.real.exec_module(module)
        name = module.__name__
        if name == self.log.package or name.startswith(self.log.package + "."):
            arm_module(module, self.log)


class Finder:
    def __init__(self, mode: str, package: str, log: Log):
        self.mode = mode
        self.package = package
        self.log = log
        self._busy: set[str] = set()

    def find_spec(self, fullname, path, target=None):
        if fullname != self.package and not fullname.startswith(self.package + "."):
            return None
        if fullname in self._busy:
            return None
        if self.mode == "absent":
            return importlib.machinery.ModuleSpec(fullname, AbsentLoader(fullname))
        if self.mode == "stub":
            return importlib.machinery.ModuleSpec(fullname, StubLoader(self.log))
        self._busy.add(fullname)
        try:
            spec = None
            for finder in sys.meta_path:
                if finder is self:
                    continue
                find = getattr(finder, "find_spec", None)
                if find is None:
                    continue
                spec = find(fullname, path, target)
                if spec is not None:
                    break
        finally:
            self._busy.discard(fullname)
        if spec is None or spec.loader is None:
            return None
        spec.loader = WrapLoader(spec.loader, self.log)
        return spec


def install(mode: str, package: str, root: Path) -> Log:
    log = Log(package, root)
    for name in list(sys.modules):
        if name == package or name.startswith(package + "."):
            del sys.modules[name]
    sys.meta_path.insert(0, Finder(mode, package, log))
    return log


def surface_names(events: list[dict], package: str) -> list[str]:
    """Attribute and operator names touched from project code.

    Call paths (``read_ndjson().select``) stay in the event log. The name set
    is the attribute itself, which is what an AST survey would have to count.
    """
    del package
    names = {event["name"] for event in events if event["op"] in {"getattr", "dunder"} and event["name"]}
    return sorted(names)


_AST_CACHE: dict[tuple[str, str], list[str]] = {}


def ast_names(package: str, root: Path) -> list[str]:
    key = (package, str(root))
    if key in _AST_CACHE:
        return _AST_CACHE[key]
    data = survey_survey(root)
    pkg = data["packages"].get(package)
    found = sorted(pkg["attributes"]) if pkg else []
    _AST_CACHE[key] = found
    return found


def _explained(token: str, known: set[str]) -> bool:
    """``svd`` is already counted when the AST saw ``linalg.svd``."""
    if token in known:
        return True
    return any(key == token or key.endswith("." + token) or key.startswith(token + ".") for key in known)


def missed(events: list[dict], package: str, root: Path) -> list[str]:
    known = set(ast_names(package, root))
    return [name for name in surface_names(events, package) if not _explained(name, known)]


def _result(mode: str, package: str, command: list[str], log: Log, status: int, error: str | None, root: Path) -> dict:
    events = log.payload()
    return {
        "mode": mode,
        "package": package,
        "command": command,
        "status": status,
        "exception": (error.splitlines()[-1] if error else None),
        "traceback": error,
        "events": events,
        "dynamic_attributes": surface_names(events, package),
        "ast_attributes": ast_names(package, root),
        "missed_by_ast": missed(events, package, root),
    }


def _split_dd(argv: list[str]) -> tuple[list[str], list[str]]:
    """Options stay on the left of ``--``. argparse REMAINDER swallows them."""
    if "--" not in argv:
        return argv, []
    index = argv.index("--")
    return argv[:index], argv[index + 1:]


def apply_main(argv: list[str]) -> int:
    left, command = _split_dd(argv)
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("mode", choices=["absent", "stub", "wrap"])
    parser.add_argument("package")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(left)
    kind, target, rest = _split_command(command)
    log = install(args.mode, args.package, args.root)
    status = 0
    error = None
    try:
        if kind == "c":
            sys.argv = ["-c", *rest]
            exec(compile(target, "<trace>", "exec"), {"__name__": "__main__"})
        elif kind == "m":
            sys.argv = [target, *rest]
            runpy.run_module(target, run_name="__main__")
        else:
            sys.argv = [target, *rest]
            # ``python script.py`` puts the script directory on sys.path. runpy does not.
            script_dir = str(Path(target).resolve().parent)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            runpy.run_path(target, run_name="__main__")
    except SystemExit as exc:
        status = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except BaseException:
        status = 1
        error = traceback.format_exc()
    args.out.write_text(json.dumps(_result(args.mode, args.package, command, log, status, error, args.root), indent=2) + "\n", encoding="utf-8")
    return status


def _split_command(command: list[str]) -> tuple[str, str, list[str]]:
    if not command:
        raise SystemExit("trace_surface: command is missing (use -- python script.py)")
    parts = list(command)
    if Path(parts[0]).name.startswith("python"):
        parts = parts[1:]
    if not parts:
        raise SystemExit("trace_surface: command is missing")
    if parts[0] == "-c":
        return "c", parts[1], parts[2:]
    if parts[0] == "-m":
        return "m", parts[1], parts[2:]
    return "path", str(Path(parts[0]).resolve()), parts[1:]


def _launch(mode: str, package: str, command: list[str], out: Path, root: Path) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, str(TOOL), "trace-surface", "--apply", mode, package, "--out", str(out), "--root", str(root), "--", *command],
        cwd=root,
    )
    if not out.exists():
        raise SystemExit(f"trace_surface: no output from {mode} {package} (status {proc.returncode})")
    data = json.loads(out.read_text(encoding="utf-8"))
    data["launcher_status"] = proc.returncode
    if mode == "wrap" and proc.returncode != 0:
        tail = (data.get("traceback") or "")[-1500:]
        print(tail, file=sys.stderr)
        raise SystemExit(proc.returncode)
    if mode == "absent" and not data.get("traceback"):
        print(f"absent {package} finished without a traceback", file=sys.stderr)
        raise SystemExit(proc.returncode or 1)
    if mode == "stub" and not data.get("traceback") and not data.get("events"):
        print(f"stub {package} recorded neither events nor a traceback", file=sys.stderr)
        raise SystemExit(proc.returncode or 1)
    _print_summary(data)
    return data


def _print_summary(data: dict) -> None:
    missed_names = ", ".join(data.get("missed_by_ast") or []) or "(none)"
    print(
        f"{data['mode']} {data['package']}: status={data['status']} "
        f"events={len(data['events'])} missed_by_ast={missed_names}"
    )
    if data.get("exception"):
        print(f"  {data['exception']}")


def _summary(data: dict) -> dict:
    """Drop per-event rows so the committed evidence stays a surface, not a log."""
    command = list(data["command"])
    if command and Path(command[0]).name.startswith("python"):
        command = ["python", *command[1:]]
    return {
        "mode": data["mode"],
        "package": data["package"],
        "command": command,
        "status": data["status"],
        "exception": data["exception"],
        "dynamic_attributes": data["dynamic_attributes"],
        "ast_attributes": data["ast_attributes"],
        "missed_by_ast": data["missed_by_ast"],
        "first_events": [
            {"op": event["op"], "qual": event["qual"], "name": event["name"], "file": event["file"], "line": event["line"]}
            for event in data["events"]
        ],
    }


def _comparable(payload: dict) -> list[dict]:
    rows = []
    for run in payload["runs"]:
        exception = run.get("exception") or ""
        rows.append({
            "driver": run["driver"],
            "dynamic_attributes": run["dynamic_attributes"],
            "exception_type": exception.split(":", 1)[0],
            "missed_by_ast": run["missed_by_ast"],
            "mode": run["mode"],
            "package": run["package"],
            "status": run["status"],
        })
    return rows


def trace_surface_collect(out: Path, root: Path, check: bool = False) -> int:
    runs = []
    work = Path(tempfile.mkdtemp(prefix="trace-surface-"))
    for mode, package, driver in COLLECT:
        target = work / f"{mode}-{package}-{driver}.json"
        command = [sys.executable, "scripts/stdlib_min.py", "trace-drivers", driver]
        data = _launch(mode, package, command, target, root)
        runs.append({"driver": driver, **_summary(data)})
    payload = {"schema": 1, "runs": runs}
    if check:
        previous = json.loads(out.read_text(encoding="utf-8"))
        if _comparable(previous) != _comparable(payload):
            print(f"{out} does not match a fresh collect. Re-run without --check.", file=sys.stderr)
            return 1
        print(f"{out} ok ({len(runs)} runs)")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(runs)} runs)")
    return 0


def trace_surface(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--apply"]:
        return apply_main(argv)
    left, command = _split_dd(argv)
    parser = argparse.ArgumentParser(description=TRACE_SURFACE_DOC.splitlines()[0])
    parser.add_argument("mode", choices=["absent", "stub", "wrap", "collect"])
    parser.add_argument("package", nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="re-run collect and compare surfaces to --out")
    args = parser.parse_args(left)
    if args.mode == "collect":
        return trace_surface_collect(args.out or (args.root / "docs" / "evidence" / "trace-surfaces.json"), args.root, check=args.check)
    if not args.package:
        raise SystemExit("package is required")
    out = args.out or (args.root / "docs" / "evidence" / f"trace-{args.mode}-{args.package}.json")
    _launch(args.mode, args.package, command, out, args.root)
    return 0


# ==== trace-drivers（旧 trace_drivers.py）

def load_overlap() -> None:
    """DRAgoWing load_overlap on the c001 season file."""
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras"), str(ROOT / "pythdragoras" / "core")]
    from dragowing.overlap import default_conditions, load_overlap as overlap
    from dragowing.records import read_jsonl

    season = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
    props = ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"
    rows = read_jsonl(season)
    result = overlap(season, default_conditions(read_jsonl(props), rows))
    if not result["regions"] or sum(region["count"] for region in result["regions"]) != len(rows):
        raise SystemExit("load_overlap regions do not cover the rows")
    print(f"load_overlap rows={len(rows)} regions={len(result['regions'])}")


def suggest_index() -> None:
    """Production QueRyu Index uses private shipped mini; installed NumPy stays untouched."""
    sys.path[:0] = [str(ROOT / "queryu" / "ask")]
    from suggest import Index

    docs = [
        ("P1", "得点順位が低い球団は失点順位も低いか"),
        ("P2", "ピタゴラス勝率との差が残るか"),
        ("E3", "順位が上がった年の得点"),
    ]
    found = Index(docs, dim=8)
    if found.P.shape[0] < 1:
        raise SystemExit("suggest index has no projection")
    print(f"suggest_index vocab={len(found.vocab)} rank={found.P.shape[1]}")


def littlebit_svd() -> None:
    """PythDRagoras littlebit_prune.littlebit: svd, lstsq, norm."""
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras"), str(ROOT / "pythdragoras" / "core")]
    import numpy as np
    from littlebit_prune import littlebit

    matrix = np.array([[(i * 5 + j) / 40 for j in range(5)] for i in range(8)], dtype=float)
    parts = littlebit(matrix, rank=2, stages=1, als_iters=1)
    if not parts:
        raise SystemExit("littlebit returned no parts")
    print(f"littlebit parts={len(parts)}")


def selectolax_css() -> None:
    """The Lexbor calls BlueProbe's parity tests make: css, text, attributes, tag."""
    from selectolax.lexbor import LexborHTMLParser

    html = "<table><tbody><tr><td><a id='n' href='/x'>A</a></td></tr></tbody></table>"
    parser = LexborHTMLParser(html)
    nodes = list(parser.css("a"))
    if len(nodes) != 1:
        raise SystemExit(f"expected one anchor, got {len(nodes)}")
    node = nodes[0]
    href = (node.attributes or {}).get("href")
    text = node.text(deep=True)
    if href != "/x" or text != "A" or node.tag != "a":
        raise SystemExit(f"unexpected node {href!r} {text!r} {node.tag!r}")
    if len(parser.css("tr")) != 1 or len(parser.css("tbody")) != 1:
        raise SystemExit("row or body selector missed")
    print("selectolax_css ok")


def httpx_get() -> None:
    """PoliteFetcher.get with an httpx.Client, against a local response."""
    import tempfile
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    sys.path[:0] = [str(ROOT), str(ROOT / "queryu")]
    import httpx
    from queryu import Cache, PoliteFetcher

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("ETag", "abc")
            self.send_header("Last-Modified", "Mon, 01 Jan 2024 00:00:00 GMT")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            with httpx.Client(headers={"User-Agent": "aoi-trace"}, timeout=5, follow_redirects=True) as client:
                fetcher = PoliteFetcher(Cache(Path(tmp)), wait=0, client=client)
                body = fetcher.get("k", f"http://127.0.0.1:{port}/page", "g")
            if body != "ok" or fetcher.requests != 1:
                raise SystemExit(f"httpx_get failed: {body!r} requests={fetcher.requests}")
    finally:
        server.shutdown()
    print("httpx_get ok")


def ortools_import() -> None:
    """The optional exact solver imported inside sakanalytics.season_exact.solve."""
    import ortools
    from ortools.sat.python import cp_model

    if not hasattr(cp_model, "CpModel"):
        raise SystemExit("cp_model.CpModel is missing")
    print(f"ortools {ortools.__version__}")


def pandas_surface() -> None:
    """Operations from research/.../verify_prediction_independent.py, without its files.

    That script parses arguments and reads a season file at import time, so the
    trace runs the same method chain on a tiny frame instead of executing it.
    """
    import pandas as pd

    frame = pd.DataFrame({
        "season": [2013, 2013, 2014],
        "league": ["c", "c", "c"],
        "team": ["d", "g", "d"],
        "bat_iso": [0.1, 0.2, 0.15],
        "bat_obp": [0.3, 0.4, 0.35],
        "inn_R": [10.0, 12.0, 11.0],
        "inn_S": [20.0, 18.0, 19.0],
    })
    frame = frame[frame.season >= 2013].copy()
    grouped = frame.groupby(["season", "league"])
    size = grouped.team.transform("size")
    frame["iso"] = frame.bat_iso - (grouped.bat_iso.transform("sum") - frame.bat_iso) / (size - 1)
    values = frame.team.to_numpy()
    row = frame.iloc[0]
    if len(values) != 3 or row.team != "d":
        raise SystemExit("pandas_surface drifted from the research script's operations")
    print(f"pandas_surface rows={len(frame)}")


DRIVERS = {
    "load_overlap": load_overlap,
    "suggest_index": suggest_index,
    "littlebit_svd": littlebit_svd,
    "selectolax_css": selectolax_css,
    "httpx_get": httpx_get,
    "ortools_import": ortools_import,
    "pandas_surface": pandas_surface,
}


def drivers(argv: list[str] | None = None) -> int:
    """Real call paths for scripts/stdlib_min.py trace-surface.

    Each driver is a function the study runs with a package blocked, stubbed, or
    wrapped. They call project code (or, where that code cannot start without
    extra inputs, the same operations the project file performs). They are not
    part of a pipeline.
    """
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1 or argv[0] not in DRIVERS:
        names = ", ".join(sorted(DRIVERS))
        raise SystemExit(f"usage: stdlib_min.py trace-drivers <{'|'.join(sorted(DRIVERS))}>\nknown: {names}")
    DRIVERS[argv[0]]()
    return 0


# ==== trace-third-party（旧 trace_third_party.py）

TRACE_THIRD_PARTY_DOC = """selectolax / httpx / そのほかの第三者 import を ast と「パッケージが無い」実行で見る（実験）。

polars と numpy のlinalg、調査レポートは別の作業。ここでは残りを数える。

    python scripts/stdlib_min.py trace-third-party
"""
TRACE_THIRD_PARTY_SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", ".cdn-cache", ".venv-min"}
STDLIB = set(sys.stdlib_module_names) | {"__future__"}


def _local_names() -> set[str]:
    names = set()
    for path in py_files(ROOT, TRACE_THIRD_PARTY_SKIP):
        names.add(path.stem)
        names.update(path.relative_to(ROOT).parts[:-1])
    return names


def trace_third_party_survey() -> dict:
    """第三者の import と、selectolax / httpx の静的な属性参照。"""
    local = _local_names()
    imports: dict[str, list[str]] = defaultdict(list)
    attrs = {"selectolax": Counter(), "httpx": Counter()}
    dynamic = []
    for path in py_files(ROOT, TRACE_THIRD_PARTY_SKIP):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        except SyntaxError:
            continue
        rel = str(path.relative_to(ROOT))
        aliases = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".", 1)[0]
                    if top not in STDLIB and top not in local:
                        imports[top].append(f"{rel}:{node.lineno}")
                    if top in attrs:
                        aliases[alias.asname or alias.name.split(".", 1)[0]] = top
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".", 1)[0]
                if top not in STDLIB and top not in local:
                    names = ", ".join(alias.name for alias in node.names)
                    imports[top].append(f"{rel}:{node.lineno} from {node.module} import {names}")
                if top in attrs:
                    for alias in node.names:
                        aliases[alias.asname or alias.name] = top
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                func = node.func
                if isinstance(func.value, ast.Name) and func.value.id == "importlib" and func.attr == "import_module":
                    if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        dynamic.append(f"{rel}:{node.lineno} import_module({node.args[0].value!r})")
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child._parent = node  # type: ignore[attr-defined]

        def chain(node):
            parts = []
            while isinstance(node, ast.Attribute):
                parts.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                return [node.id, *reversed(parts)]
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in aliases:
                origin = aliases[node.func.id]
                keys = [kw.arg or "**" for kw in node.keywords]
                attrs[origin][f"call {node.func.id}({', '.join(keys)})"] += 1
            elif isinstance(node, ast.Attribute) and not isinstance(getattr(node, "_parent", None), ast.Attribute):
                parts = chain(node)
                if parts and parts[0] in aliases and len(parts) > 1:
                    attrs[aliases[parts[0]]][".".join(parts[1:])] += 1
    return {"imports": {key: imports[key] for key in sorted(imports)},
            "attrs": {key: dict(attrs[key]) for key in attrs},
            "dynamic": dynamic}


def absent_traces() -> dict[str, str]:
    """パッケージを塞いで研究スクリプトを import し、出た例外の先頭を返す。"""
    targets = {
        "selectolax": [
            "research/gpt-r001-score-allocation/fetch.py",   # observe・verify・inning_pilot
            "blueprobe/tests/test_blueprobe_html_parity.py",
        ],
        "httpx": [
            "research/gpt-r001-score-allocation/fetch.py",   # collect・verify・inning_pilot
        ],
    }
    code = r"""
import builtins, sys
from pathlib import Path
root = Path(sys.argv[1])
blocked, target = sys.argv[2], sys.argv[3]
sys.path[:0] = [str(root), str(root / "blueprobe"), str(root / "queryu"), str(root / "research/gpt-r001-score-allocation")]
real = builtins.__import__
def hook(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".", 1)[0] == blocked:
        raise ModuleNotFoundError("No module named %r" % name)
    return real(name, globals, locals, fromlist, level)
builtins.__import__ = hook
import runpy
try:
    runpy.run_path(str(root / target), run_name="trace_not_main")
except ModuleNotFoundError as exc:
    sys.stderr.write("ModuleNotFoundError: %s\n" % exc)
    raise SystemExit(0)
print("imported")
"""
    out = {}
    for blocked, files in targets.items():
        for rel in files:
            proc = subprocess.run([sys.executable, "-c", code, str(ROOT), blocked, rel],
                                  capture_output=True, text=True)
            line = (proc.stderr or proc.stdout).strip().splitlines()
            out[f"{blocked}:{rel}"] = line[-1] if line else f"exit {proc.returncode}"
    return out


def reject_fetch() -> None:
    """PyPI に聞いて、compiled と実行時依存を fetch_module が拒むことを確かめる。"""
    import fetch_module as fm

    expect = {
        "httpx": "依存",
        "selectolax": "pure-Python",
        "ortools": "依存",
        "pandas": "依存",
        "numpy": "pure-Python",
        "polars": "依存",
    }
    for package, needle in expect.items():
        try:
            spec = fm.resolve(package)
        except SystemExit as exc:
            text = str(exc)
            if needle not in text:
                raise SystemExit(f"{package}: {text}")
            print(package, text)
        else:
            raise SystemExit(f"{package} resolved unexpectedly: {spec['filename']}")
    coverage = fm.resolve("coverage", _locked_coverage_version())  # 拒まれない側（pure wheel、依存なし）
    print("coverage", coverage["version"], coverage["filename"])


def trace_third_party(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=TRACE_THIRD_PARTY_DOC.splitlines()[0])
    parser.add_argument("--resolve", action="store_true", help="PyPI で fetch_module の拒否を確かめる")
    args = parser.parse_args(argv)
    found = trace_third_party_survey()
    print("imports:")
    for name, sites in found["imports"].items():
        print(f"  {name}: {len(sites)}")
        for site in sites[:6]:
            print(f"    {site}")
    print("dynamic:", *found["dynamic"], sep="\n  ")
    print("selectolax attrs:", found["attrs"]["selectolax"])
    print("httpx attrs:", found["attrs"]["httpx"])
    print("absent:")
    for key, line in absent_traces().items():
        print(f"  {key}: {line}")
    if args.resolve:
        reject_fetch()
    return 0


# ==== linalg-feasibility（旧 linalg_feasibility.py）

LINALG_FEASIBILITY_SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__"}

ENTRIES = [
    "queryu/ask/suggest.py:Index",
    "queryu/ask/suggest.py:suggest",
    "pythdragoras/core/littlebit_prune.py:littlebit",
    "pythdragoras/core/littlebit_prune.py:overlap_bounds",
    "pythdragoras/core/littlebit_prune.py:search_guaranteed",
    "pythdragoras/core/rule_search.py:_search_bitmatrix",
    "pythdragoras/core/littlebit_holdout.py:fit",
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


def _parse(path: Path) -> ast.Module:
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node
    return tree


def _vendored_numpy_loader(tree: ast.Module) -> bool:
    """Recognize the supported explicit vendor loader, not arbitrary _load_numpy* names.

    This is static reachability classification, not runtime provenance validation.
    """
    loader = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_load_numpy_min"), None)
    if loader is None:
        return False
    # Deliberately support this one loader contract, not arbitrary dynamic Python.
    # Exact statement structure rejects decoy constants/calls in dead branches.
    expected = ast.parse("""
name = "queryu_numpy_min"
if name in sys.modules:
    return sys.modules[name]
path = Path(__file__).resolve().parents[1] / "vendor" / "aoi" / "shrink" / "numpy_min.py"
spec = importlib.util.spec_from_file_location(name, path)
module = importlib.util.module_from_spec(spec)
sys.modules[name] = module
spec.loader.exec_module(module)
return module
""").body
    body = loader.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]  # The loader's explanatory docstring does not affect binding.
    return ([ast.dump(n) for n in body] == [ast.dump(n) for n in expected]
            and not loader.args.args and not loader.args.kwonlyargs
            and loader.args.vararg is None and loader.args.kwarg is None)


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
            elif (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "_load_numpy_min"
                and not node.value.args and not node.value.keywords
                and _vendored_numpy_loader(tree)
            ):
                # 同梱の numpy 代替を読み込む `np = _load_numpy_min()` も numpy として扱う。
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.numpy_aliases.add(target.id)


def _index(root: Path) -> dict[str, list[_Module]]:
    found: dict[str, list[_Module]] = {}
    for path in py_files(root, LINALG_FEASIBILITY_SKIP):
        try:
            module = _Module(path, _parse(path))
        except SyntaxError:
            continue
        found.setdefault(path.stem, []).append(module)
    return found


def linalg_feasibility__uses(module: _Module, node: ast.AST) -> Counter:
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
            used += linalg_feasibility__uses(current, node)
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
    """numpy を使えない proxy に差し替えても QueRyu の Index が動くことを確かめる。

    QueRyu は同梱の numpy_min を使うので、本物の numpy に触れたら失敗にする。
    """
    touched: list[str] = []

    class _Watch(_Proxy):
        def __getattr__(self, item):
            if not item.startswith("__"):
                touched.append(f"{self.__name__}.{item}")
            return super().__getattr__(item)

    proxy = _Watch("numpy")
    proxy.__file__ = "<absent numpy>"
    proxy.__package__ = "numpy"
    sys.modules["numpy"] = proxy
    for folder in (ROOT, ROOT / "pythdragoras", ROOT / "pythdragoras" / "core", ROOT / "queryu", ROOT / "queryu" / "ask"):
        sys.path.insert(0, str(folder))
    try:
        import suggest
        suggest.Index([("P1", "得失点差がプラスなら上位半分である")], dim=4)
    except AttributeError:
        traceback.print_exc()
        print("absent-probe: Index touched numpy", file=sys.stderr)
        return 1
    leaked = [name for name, mod in vars(suggest).items() if mod is proxy]
    if touched or leaked:
        print(f"absent-probe: Index touched numpy: {touched or leaked}", file=sys.stderr)
        return 1
    print("absent-probe: Index ran without touching numpy")
    return 0


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
    _prepare("real", allow_installed=True)        # linalg（旧 run_linalg.py）は同じファイルにある
    payload = linalg_collect(scope, "real")
    print(json.dumps({"scope": scope, "calls": log, "seconds": payload["meta"]["seconds"], "backend_evidence": payload["backend_evidence"]}, ensure_ascii=False))
    names = {row["fn"] for row in log}
    if scope == "fixture":
        need = {"linalg.svd", "linalg.lstsq", "linalg.norm", "einsum", "linalg.pinv"}
        missing = need - names
        if missing:
            print(f"trace が通らなかった: {sorted(missing)}", file=sys.stderr)
            return 1
    return 0


def linalg_feasibility(argv=None) -> int:
    """queryu と pythdragoras の重い numpy が、標準ライブラリだけで置き換えられるかを調べる（実験）。

    shrink/numpy_min.py は scripts/shrink_module.py の生成物（load_overlap と queryu の suggest が入口）。こちらは別ファイルで調べる。

        python scripts/stdlib_min.py linalg-feasibility ast
        python scripts/stdlib_min.py linalg-feasibility trace --scope fixture
        python scripts/stdlib_min.py linalg-feasibility trace --scope c001
        python scripts/stdlib_min.py linalg-feasibility absent
        python scripts/stdlib_min.py linalg-feasibility report

    ast はクラスのメソッド、``self.method``、``import mod as alias``、``from mod import func`` をたどる。
    shrink_module.analyze はモジュール直下の関数と ``mod.func`` だけなので、suggest.Index の svd を落とす。

    trace は本物の numpy の svd / lstsq / pinv / norm / einsum を包み、実際の shape と時間を出す。
    absent は使えない numpy を先に入れ、製品の QueRyu Index が numpy に触れず動くことを確かめる。
    """
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
        return subprocess.call([sys.executable, str(Path(__file__).resolve()), "linalg-feasibility", "absent"], env=env)
    return _trace(args.scope)


# ==== linalg（旧 run_linalg.py）

MIN_FILE = ROOT / "shrink" / "numpy_linalg_min.py"
SUGGEST_MIN_FILE = ROOT / "queryu" / "vendor" / "aoi" / "shrink" / "numpy_min.py"
EVIDENCE_SCHEMA = "linalg-consumers/1"
REQUIRED_CALLS = {
    "suggest": ("linalg.svd", "linalg.norm"),
    "littlebit_prune": ("linalg.svd", "linalg.lstsq", "einsum"),
    "rule_search": ("frombuffer", "unpackbits"),
    "harness": ("linalg.svd", "linalg.pinv"),
}


def _identity(module, expected: Path | None) -> dict:
    path = Path(module.__file__).resolve()
    if expected is not None:
        if path != expected.resolve():
            raise ValueError(f"unexpected backend: {path}; expected {expected}")
        kind = "shipped-min" if expected == SUGGEST_MIN_FILE else "experimental-min"
    else:
        if module.__name__ != "numpy" or path.name != "__init__.py" or path.parent.name != "numpy":
            raise ValueError(f"not real NumPy: {path}")
        kind = "real"
    return {"kind": kind, "file": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "module": module.__name__, "version": str(getattr(module, "__version__", "")),
            "backend": str(getattr(module, "BACKEND", "numpy" if kind == "real" else "stdlib"))}


class _Observed:
    """Consumer-local delegation: never mutate the shared backend or its linalg object."""
    def __init__(self, source, record, prefix=""):
        self._source, self._record, self._prefix = source, record, prefix

    def __getattr__(self, name):
        value = getattr(self._source, name)
        key = self._prefix + name
        if key == "linalg":
            return _Observed(value, self._record, "linalg.")
        monitored = {op for ops in REQUIRED_CALLS.values() for op in ops}
        if key not in monitored:
            return value
        @functools.wraps(value)
        def call(*args, **kwargs):
            result = value(*args, **kwargs)
            counts = self._record["calls"]
            counts[key] = counts.get(key, 0) + 1
            return result
        return call


def linalg_collect(scope: str, which: str) -> dict:
    import numpy as np
    import littlebit_prune as lp
    import rule_search as rs
    import suggest

    if which not in {"real", "min"}:
        raise ValueError(f"unknown arm: {which}")
    # Validate the production binding before overriding only the reference arm.
    shipped = suggest._load_numpy_min()
    _identity(shipped, SUGGEST_MIN_FILE)
    selected = np if which == "real" else shipped
    modules = {"suggest": suggest, "littlebit_prune": lp, "rule_search": rs}
    originals = {name: module.np for name, module in modules.items()}
    evidence = {"schema": EVIDENCE_SCHEMA, "arm": which, "consumers": {}}
    proxies = {}
    for name in REQUIRED_CALLS:
        backend = selected if name == "suggest" else np
        expected = None if which == "real" else (SUGGEST_MIN_FILE if name == "suggest" else MIN_FILE)
        record = {"identity": _identity(backend, expected), "calls": {}}
        evidence["consumers"][name] = record
        proxies[name] = _Observed(backend, record)
    try:
        for name, module in modules.items():
            module.np = proxies[name]
        payload = _collect(scope, proxies["harness"], lp, rs, suggest)
        payload["backend_evidence"] = evidence
        errors = _evidence_errors(payload, which)
        if errors:
            raise ValueError("; ".join(errors))
        return payload
    finally:
        for name, module in modules.items():
            module.np = originals[name]


def _evidence_errors(payload: dict, arm: str) -> list[str]:
    evidence = payload.get("backend_evidence")
    if not isinstance(evidence, dict) or evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("arm") != arm:
        return [f"{arm}: missing or invalid backend evidence"]
    consumers = evidence.get("consumers")
    if not isinstance(consumers, dict) or set(consumers) != set(REQUIRED_CALLS):
        return [f"{arm}: missing or invalid consumers"]
    errors = []
    real_identity = None
    for name, operations in REQUIRED_CALLS.items():
        row = consumers[name]
        identity = row.get("identity") if isinstance(row, dict) else None
        calls = row.get("calls") if isinstance(row, dict) else None
        if not isinstance(identity, dict) or set(identity) != {"kind", "file", "sha256", "module", "version", "backend"} or not all(isinstance(v, str) for v in identity.values()):
            errors.append(f"{arm}.{name}: invalid identity")
            continue
        path = Path(identity["file"])
        digest = identity["sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            errors.append(f"{arm}.{name}: invalid source hash")
        if arm == "real":
            if identity["kind"] != "real" or identity["module"] != "numpy" or identity["backend"] != "numpy" or not identity["version"] or path.name != "__init__.py" or path.parent.name != "numpy":
                errors.append(f"{arm}.{name}: not real NumPy")
            if real_identity is None:
                real_identity = identity
            elif identity != real_identity:
                errors.append(f"{arm}.{name}: inconsistent real NumPy identity")
        else:
            expected = SUGGEST_MIN_FILE if name == "suggest" else MIN_FILE
            kind = "shipped-min" if name == "suggest" else "experimental-min"
            # Paths differ across CI runners; verify repository-relative suffix and exact bytes.
            if identity["kind"] != kind or not path.as_posix().endswith("/" + expected.relative_to(ROOT).as_posix()) or digest != hashlib.sha256(expected.read_bytes()).hexdigest():
                errors.append(f"{arm}.{name}: unexpected mini implementation")
            if identity["version"] != ("0+min" if name == "suggest" else "0+linalg"):
                errors.append(f"{arm}.{name}: invalid mini version")
            if identity["module"] != ("queryu_numpy_min" if name == "suggest" else "numpy"):
                errors.append(f"{arm}.{name}: invalid mini module")
            if identity["backend"] not in ({"lapack", "stdlib"} if name == "suggest" else {"stdlib"}):
                errors.append(f"{arm}.{name}: invalid mini backend")
        if not isinstance(calls, dict) or any(type(calls.get(op)) is not int or calls[op] <= 0 for op in operations):
            errors.append(f"{arm}.{name}: missing executed calls")
    return errors


# 余弦・特異値・再構成。因子の符号は一意でないので比べない。
SUGGEST_RTOL, SUGGEST_ATOL = 1e-4, 1e-4
SIGMA_RTOL, SIGMA_ATOL = 1e-5, 1e-8
RECON_RTOL, RECON_ATOL = 1e-6, 1e-6
PINV_RTOL, PINV_ATOL = 1e-5, 1e-8

QUERY = "得失点差がプラスなら上位か"
DOCS = [
    ("P46", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないという命題"),
    ("P47", "中日は得点が5位以下の年に走者ひとりあたりの得点が他より少ないという隣の命題"),
    ("P1", "得失点差がプラスなら上位半分である"),
    ("P9", "1点差の試合で勝ち越すと期待勝利数を上回る"),
    ("N1", "明日の天気とビールの売上"),
    ("N2", "監督の名前と本拠地"),
]
ROWS = [
    ("a", 40, 1, 2.0, True), ("b", 10, 3, -5.0, False), ("c", -20, 2, 4.0, True),
    ("d", -60, 5, 1.0, False), ("e", 5, 3, 0.5, True), ("f", -10, 6, -1.0, False),
    ("g", 30, 2, -6.0, False), ("h", -30, 5, 3.0, False), ("i", 60, 1, 0.0, True),
]
TARGET = [{"col": "upper_half", "op": "==", "value": False}]
CANDS = [
    {"col": "rd", "op": "<", "value": 0},
    {"col": "rank_ra", "op": ">=", "value": 4},
    {"col": "wins_vs_pythag", "op": "<", "value": -4},
    {"col": "rd", "op": "<", "value": 20},
]
# 12×5。littlebit の段と pinv の形を小さく固定する。
MATRIX = [
    [1, 0, 1, 0, 1], [1, 1, 0, 0, 1], [0, 1, 1, 1, 0], [1, 0, 0, 1, 1],
    [0, 0, 1, 1, 0], [1, 1, 1, 0, 0], [0, 1, 0, 1, 1], [1, 0, 1, 1, 0],
    [0, 1, 1, 0, 1], [1, 1, 0, 1, 0], [0, 0, 0, 1, 1], [1, 0, 0, 0, 1],
]


def _prepare(which: str, allow_installed: bool) -> None:
    if which == "min":
        if not allow_installed and importlib.util.find_spec("numpy") is not None:
            raise SystemExit("numpy が入っている。--numpy min は numpy なしの環境で動かす（手元は --allow-installed）")
        spec = importlib.util.spec_from_file_location("numpy", MIN_FILE)
        if spec is None or spec.loader is None:
            raise SystemExit(f"読み込めない: {MIN_FILE}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["numpy"] = mod
        spec.loader.exec_module(mod)
        if not str(mod.__file__).endswith("numpy_linalg_min.py"):
            raise SystemExit(f"スタンドインではない: {mod.__file__}")
    for folder in (ROOT, ROOT / "pythdragoras", ROOT / "pythdragoras" / "core", ROOT / "queryu", ROOT / "queryu" / "ask"):
        entry = str(folder)
        if entry not in sys.path:
            sys.path.insert(0, entry)


def _rule(row: dict) -> dict:
    return {
        "mcc": round(row["mcc"], 12),
        "conditions": row["conditions"],
        "tp": row["tp"],
        "fp": row["fp"],
        "if_any": row["if_any"],
    }


def _timed(bucket: dict, name: str, fn):
    start = time.perf_counter()
    value = fn()
    bucket[name] = round(time.perf_counter() - start, 6)
    return value


def _collect(scope: str, np, lp, rs, suggest) -> dict:
    import polars as pl

    seconds: dict[str, float] = {}
    if scope == "fixture":
        docs, dim = DOCS, 4
        frame = pl.DataFrame(
            [{"rd": rd, "rank_ra": ra, "wins_vs_pythag": w, "upper_half": u} for _, rd, ra, w, u in ROWS]
        )
        target, cands = TARGET, CANDS
        kw = dict(max_terms=2, max_conds=2, top=20)
        rank, stages = 2, 1
        matrix = np.array(MATRIX, dtype=np.float64)
        als = 2
        pinv_src = matrix[:4, :]
    elif scope == "c001":
        import tomllib

        import aoi_paths
        import littlebit_approx as la
        from pythdragoras import apply_exclusions

        cycle = aoi_paths.resolve_cycle_path(ROOT)
        docs = suggest.load_docs(cycle / "outputs")
        dim = 128
        cfg = tomllib.loads((cycle / "analysis.toml").read_text(encoding="utf-8"))
        spec = tomllib.loads((cycle / "rule_candidates.toml").read_text(encoding="utf-8"))
        season = pl.read_ndjson(cycle / "outputs" / "season.jsonl")
        season, _dropped = apply_exclusions(season, cfg.get("exclude", []))
        cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
        frame = season.drop_nulls(cols)
        target, cands = spec["target"], spec["candidate"]
        kw = dict(max_terms=int(spec["max_terms"]), max_conds=int(spec["max_conds"]), top=20)
        rank, stages = 8, 2
        matrix = la.indicator_matrix(frame, cands).astype(np.float64)
        als = la.ALS_ITERS
        # holdout の decoder.T と同じ (rank, 条件数)。因子の符号には依存させない。
        pinv_src = matrix[:8, :]
    else:
        raise SystemExit(f"scope が違う: {scope}")

    def _index():
        return suggest.Index(docs, dim=dim)

    index = _timed(seconds, "suggest_index", _index)
    float_hits = _timed(seconds, "suggest_query", lambda: index.query(QUERY, mode="float", k=5))
    binary_hits = index.query(QUERY, mode="binary", k=5)
    singular = _timed(
        seconds, "indicator_svd",
        lambda: np.linalg.svd(matrix, full_matrices=False, compute_uv=False),
    )

    def _recon():
        parts = lp.littlebit(matrix, rank=min(rank, matrix.shape[1]), stages=stages, als_iters=als)
        return lp._dense(parts)

    recon = _timed(seconds, "littlebit_recon", _recon)
    pseudo = _timed(seconds, "pinv", lambda: np.linalg.pinv(pinv_src, rcond=1e-12))
    bit = _timed(seconds, "bitmatrix", lambda: rs.search(frame, target, cands, backend="bitmatrix", **kw))
    guaranteed = _timed(
        seconds, "guaranteed",
        lambda: rs.search(frame, target, cands, prune="littlebit", rank=rank, stages=stages, **kw),
    )
    return {
        "scope": scope,
        "numpy_file": str(np.__file__),
        "suggest": {
            "n_docs": len(docs),
            "vocab": len(index.vocab),
            "dim": dim,
            "float": [{"id": i, "similarity": float(s)} for i, s in float_hits],
            "binary": [{"id": i, "similarity": float(s)} for i, s in binary_hits],
            "sizes": index.sizes(),
        },
        "indicator": {"shape": list(matrix.shape), "singular_values": [float(v) for v in singular.tolist()]},
        "littlebit_recon": {"shape": list(recon.shape), "values": recon.tolist()},
        "pinv": {"shape": list(pseudo.shape), "rcond": 1e-12, "values": pseudo.tolist()},
        "bitmatrix": [_rule(row) for row in bit],
        "guaranteed": [_rule(row) for row in guaranteed],
        "meta": {"seconds": seconds},
    }


def _numbers(a, b, rtol: float, atol: float, path: str) -> list[str]:
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path} の長さ {len(a)} と {len(b)}"]
        bad = []
        for i, (left, right) in enumerate(zip(a, b)):
            bad.extend(_numbers(left, right, rtol, atol, f"{path}[{i}]"))
        return bad
    if isinstance(a, bool) or isinstance(b, bool):
        return [] if a == b else [f"{path} {a!r} != {b!r}"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if math.isnan(a) and math.isnan(b):
            return []
        if math.isclose(float(a), float(b), rel_tol=rtol, abs_tol=atol):
            return []
        return [f"{path} {a} と {b}（rtol={rtol}, atol={atol}）"]
    return [] if a == b else [f"{path} {a!r} != {b!r}"]


def _hits(ref: list, got: list, path: str) -> list[str]:
    rid = [row["id"] for row in ref]
    gid = [row["id"] for row in got]
    if rid != gid:
        return [f"{path} の id {rid} と {gid}"]
    return _numbers(
        [row["similarity"] for row in ref],
        [row["similarity"] for row in got],
        SUGGEST_RTOL, SUGGEST_ATOL, path + " similarity",
    )


def compare(ref: dict, got: dict) -> list[str]:
    bad = _evidence_errors(ref, "real") + _evidence_errors(got, "min")
    if bad:
        return bad
    for name in REQUIRED_CALLS:
        left = ref["backend_evidence"]["consumers"][name]["identity"]
        right = got["backend_evidence"]["consumers"][name]["identity"]
        if left["sha256"] == right["sha256"] or left["file"] == right["file"]:
            bad.append(f"{name}: same implementation on both arms")
    if bad:
        return bad
    if ref.get("scope") != got.get("scope"):
        bad.append(f"scope {ref.get('scope')} と {got.get('scope')}")
    for key in ("n_docs", "vocab", "dim", "sizes"):
        if ref["suggest"][key] != got["suggest"][key]:
            bad.append(f"suggest.{key} {ref['suggest'][key]!r} と {got['suggest'][key]!r}")
    bad.extend(_hits(ref["suggest"]["float"], got["suggest"]["float"], "suggest.float"))
    bad.extend(_hits(ref["suggest"]["binary"], got["suggest"]["binary"], "suggest.binary"))
    if ref["indicator"]["shape"] != got["indicator"]["shape"]:
        bad.append(f"indicator shape {ref['indicator']['shape']} と {got['indicator']['shape']}")
    bad.extend(_numbers(ref["indicator"]["singular_values"], got["indicator"]["singular_values"], SIGMA_RTOL, SIGMA_ATOL, "singular_values"))
    if ref["littlebit_recon"]["shape"] != got["littlebit_recon"]["shape"]:
        bad.append("littlebit_recon の shape が違う")
    bad.extend(_numbers(ref["littlebit_recon"]["values"], got["littlebit_recon"]["values"], RECON_RTOL, RECON_ATOL, "littlebit_recon"))
    if ref["pinv"]["shape"] != got["pinv"]["shape"]:
        bad.append(f"pinv shape {ref['pinv']['shape']} と {got['pinv']['shape']}")
    bad.extend(_numbers(ref["pinv"]["values"], got["pinv"]["values"], PINV_RTOL, PINV_ATOL, "pinv"))
    if ref["bitmatrix"] != got["bitmatrix"]:
        bad.append("bitmatrix の規則（mcc を 12 桁、tp、fp、if_any）が一致しない")
    if ref["guaranteed"] != got["guaranteed"]:
        bad.append("search_guaranteed の規則が一致しない（上限が整数境界をまたいだ可能性がある）")
    return bad


def linalg(argv=None) -> int:
    """suggest は同梱 numpy_min、littlebit / ビット行列は numpy_linalg_min を本物の numpy と比べる（実験）。

        python scripts/stdlib_min.py linalg --numpy real --scope fixture out.json
        python scripts/stdlib_min.py linalg --numpy min  --scope fixture out.json
        python scripts/stdlib_min.py linalg --compare ref.json got.json

    --scope c001 が既定。c001 の SVD は pure-Python だと数十秒かかる。pytest の既定には入れない。

    --numpy min は、本物の numpy が import できる環境では失敗する。手元で両方を見るときは
    --allow-installed を付ける（スタンドインを先に注入し、``__file__`` が numpy_linalg_min.py であることを確かめる）。
    CI の numpy なしジョブは --allow-installed を付けない。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--numpy", choices=["real", "min"])
    parser.add_argument("--scope", choices=["fixture", "c001"], default="c001")
    parser.add_argument("--allow-installed", action="store_true")
    parser.add_argument("--compare", nargs=2, metavar=("REF", "GOT"))
    parser.add_argument("out", nargs="?")
    args = parser.parse_args(argv)
    if args.compare:
        ref = json.loads(Path(args.compare[0]).read_text(encoding="utf-8"))
        got = json.loads(Path(args.compare[1]).read_text(encoding="utf-8"))
        bad = compare(ref, got)
        if bad:
            print("\n".join(bad))
            return 1
        print(f"ok scope={ref['scope']} suggest={ref['suggest']['n_docs']} docs indicator={ref['indicator']['shape']}")
        return 0
    if args.numpy is None or not args.out:
        raise SystemExit("--numpy と出力先、または --compare が必要")
    _prepare(args.numpy, args.allow_installed)
    import numpy
    payload = linalg_collect(args.scope, args.numpy)
    Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    seconds = payload["meta"]["seconds"]
    print(
        f"numpy={numpy.__version__} ({numpy.__file__}) scope={args.scope} "
        f"docs={payload['suggest']['n_docs']} indicator={payload['indicator']['shape']} "
        f"seconds={seconds}"
    )
    return 0


# ==== overlap（旧 run_overlap.py）

SEASON = ROOT / "cycles/c001-chunichi/outputs/season.jsonl"
PROPS = ROOT / "cycles/c001-chunichi/outputs/propositions.jsonl"


def overlap(argv=None) -> int:
    """DRAgoWing の load_overlap を c001 の実データで動かし、結果の JSON と sha256 を出す（実験）。

        python scripts/stdlib_min.py overlap --numpy real  out.json   # 本物の numpy
        python scripts/stdlib_min.py overlap --numpy min   out.json   # shrink/numpy_min.py を numpy として使う

    --numpy min では、本物の numpy が import できる環境なら失敗する（入っていないことを確かめる）。
    """
    p = argparse.ArgumentParser()
    p.add_argument("--numpy", choices=["real", "min"], required=True)
    p.add_argument("out")
    a = p.parse_args(argv)
    if a.numpy == "min":
        if importlib.util.find_spec("numpy") is not None:
            raise SystemExit("numpy が入っている。--numpy min は numpy なしの環境で動かす")
        inject("numpy", ROOT / "shrink" / "numpy_min.py")
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras"), str(ROOT / "pythdragoras" / "core")]
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    import numpy

    rows = read_jsonl(SEASON)
    conds = default_conditions(read_jsonl(PROPS), rows)
    result = load_overlap(SEASON, conds)
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(a.out).write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(f"numpy={numpy.__version__} ({numpy.__file__}) rows={len(rows)} regions={len(result['regions'])} sha256={digest}")
    return 0


# ==== overlap-stdlib（旧 run_overlap_stdlib.py）

def overlap_stdlib(argv=None) -> int:
    """DRAgoWing の load_overlap を c001 の実データで動かし、結果の JSON と sha256 を出す（実験）。

        python scripts/stdlib_min.py overlap-stdlib --deps real out.json   # 本物の numpy と polars
        python scripts/stdlib_min.py overlap-stdlib --deps min  out.json   # numpy_min と polars_min

    --deps min では、本物の numpy か polars が import できる環境なら失敗する（両方入っていないことを確かめる）。
    本番のパイプラインは変えない。呼び出し側が min を使うときは、import より前に同じ差し替えをする。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--deps", choices=["real", "min"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.deps == "min":
        present = [name for name in ("numpy", "polars") if importlib.util.find_spec(name) is not None]
        if present:
            raise SystemExit(f"{' と '.join(present)} が入っている。--deps min は両方ない環境で動かす")
        inject("numpy", ROOT / "shrink" / "numpy_min.py")
        inject("polars", ROOT / "shrink" / "polars_min.py")
    sys.path[:0] = [str(ROOT), str(ROOT / "pythdragoras"), str(ROOT / "pythdragoras" / "core")]
    from dragowing.overlap import default_conditions, load_overlap
    from dragowing.records import read_jsonl

    import numpy
    import polars

    rows = read_jsonl(SEASON)
    result = load_overlap(SEASON, default_conditions(read_jsonl(PROPS), rows))
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(
        f"numpy={numpy.__version__} ({numpy.__file__}) polars={polars.__version__} ({polars.__file__}) "
        f"rows={len(rows)} regions={len(result['regions'])} sha256={digest}"
    )
    return 0


# ==== selectolax（旧 run_selectolax.py）

SELECTOLAX_DOC = """selectolax を使う研究コードを、本物か selectolax_min で走らせて JSON を書く（実験）。

    python scripts/stdlib_min.py selectolax --impl real out.json
    python scripts/stdlib_min.py selectolax --impl min  out.json   # selectolax が入っていない環境

--impl min では、本物の selectolax が import できる環境なら失敗する。
fetch.py は import 時に httpx も読むので、httpx が無いときだけ httpx_min を先に置く。
"""
RESEARCH = ROOT / "research" / "gpt-r001-score-allocation"


def _selectolax_paths() -> None:
    """旧 run_selectolax.py が import 時に置いた sys.path（研究コード・min を読む関数の頭で呼ぶ）。"""
    sys.path[:0] = [
        str(ROOT), str(ROOT / "mindeps"), str(ROOT / "scripts"),
        str(ROOT / "blueprobe"), str(ROOT / "queryu"), str(RESEARCH),
    ]


def selectolax_install_httpx_min() -> None:
    if importlib.util.find_spec("httpx") is not None:
        return
    inject("httpx", ROOT / "mindeps" / "httpx_min.py")


def install_selectolax_min() -> None:
    if importlib.util.find_spec("selectolax") is not None:
        raise SystemExit("selectolax が入っている。--impl min は selectolax なしの環境で動かす")
    selectolax_install_httpx_min()
    spec = importlib.util.spec_from_file_location("selectolax.lexbor", ROOT / "mindeps" / "selectolax_min.py")
    module = importlib.util.module_from_spec(spec)
    package = types.ModuleType("selectolax")
    package.__path__ = []
    package.lexbor = module
    sys.modules["selectolax"] = package
    sys.modules["selectolax.lexbor"] = module
    spec.loader.exec_module(module)


def use_min_parser() -> None:
    """既に import 済みの研究モジュール（fetch.py の observe・inning_pilot・verify）の LexborHTMLParser を min に差し替える。"""
    _selectolax_paths()
    import fetch
    import selectolax_min

    fetch.LexborHTMLParser = selectolax_min.LexborHTMLParser


def _jsonable(value):
    if isinstance(value, Counter):
        return dict(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _call(name, fn):
    try:
        return {"name": name, "value": _jsonable(fn())}
    except ValueError as exc:
        return {"name": name, "error": f"ValueError: {exc}"}


def _score_row(name, values):
    return '<tr><td class="gmscoreteam">' + name + "</td>" + "".join(
        '<td class="gmscore">' + value + "</td>" for value in values) + "</tr>"


def _cells(values):
    parts = []
    for index, value in enumerate(values):
        parts.append('<td class="gmscore">' + value + "</td>")
        if index in (2, 5):
            parts.append('<td class="gmscspan"><br /></td>')
    return "".join(parts)


def _annual_page() -> str:
    teams = [
        ("読売<br>ジャイアンツ", 143, 80, 60, 3, 520, 400),
        ("東京ヤクルトスワローズ", 143, 70, 70, 3, 500, 480),
        ("横浜DeNAベイスターズ", 143, 75, 65, 3, 510, 470),
        ("中日ドラゴンズ", 143, 60, 80, 3, 430, 560),
        ("阪神タイガース", 143, 88, 52, 3, 600, 390),
        ("広島東洋カープ", 143, 65, 75, 3, 470, 510),
    ]
    rows = []
    for name, games, wins, losses, draws, runs, runs_allowed in teams:
        rows.append(
            f"<tr><td>{name}</td><td>{games}</td><td>{wins}</td><td>{losses}</td><td>{draws}</td></tr>"
            f"<tr><td>{name}</td><td>.250</td><td>{games}</td><td>0</td><td>{runs}</td></tr>"
            f"<tr><td>{name}</td><td>0</td><td>{games}</td><td>{wins}</td><td>{losses}</td><td>{runs_allowed}</td></tr>"
        )
    return "<table>" + "".join(rows) + "</table>"


def selectolax_outcomes() -> list:
    _selectolax_paths()
    from fetch import annual, inning_pilot_parse, observe_parse

    url = "https://npb.jp/bis/2013/calendar/index_10.html"
    observe_pages = {
        "label": '''<div class="stvsteam"><div class="tescheaten">CS ファーストS</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>
        <div class="stvsteam"><div><a href="/bis/2013/games/s2013101200002.html">楽 3 - 2 オ</a></div></div>''',
        "allstar": '''<div class="stvsteam"><div class="tescheaten">オールスター</div>
        <div><a href="/bis/2013/games/s2013071900001.html">パ 2 - 2 セ</a></div></div>''',
        "unknown_label": '''<div class="stvsteam"><div class="tescheaten">未知大会</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>''',
        "climax": '''<div class="stvsteam"><div class="tescheaten">クライマックスS</div>
        <div><a href="/bis/2020/games/s2020111400001.html">ソ 2 - 1 ロ</a></div></div>''',
        "calendar_fixture": (ROOT / "blueprobe/tests/fixtures/npb_calendar_sample.html").read_text(encoding="utf-8"),
    }
    inning_pages = {
        "wrong_total": (
            '<div id="gmdivresult"><table>'
            + _score_row("中日", ["0"] * 9 + ["-", "1", "0", "0"])
            + _score_row("東京ヤクルト", ["0"] * 8 + ["X", "-", "0", "0", "0"])
            + "</table></div>",
            {"away": "d", "home": "s", "as": 1, "hs": 0},
        ),
        "board": (
            '<div id="gmdivresult"><table>'
            '<tr><td class="gmscorettl" colspan="13"><br /></td><td class="gmscorettl">Ｒ</td></tr>'
            '<tr><td class="gmscoreteam">阪　神</td>' + _cells(["0"] * 9)
            + '<td align="center" class="gmscore">-</td><td align="center" class="gmscore">0</td>'
            '<td class="gmscore">4</td><td class="gmscore">0</td></tr>'
            '<tr><td class="gmscoreteam">読　売</td>' + _cells(["0", "0", "0", "0", "3", "0", "0", "1", "X"])
            + '<td align="center" class="gmscore">-</td><td align="center" class="gmscore">4</td>'
            '<td class="gmscore">10</td><td class="gmscore">1</td></tr></table></div>',
            {"away": "t", "home": "g", "as": 0, "hs": 4},
        ),
        "marked": (
            '<div id="gmdivresult"><table>'
            '<tr><td class="gmscoreteam">中　日</td>' + _cells([" 0 ", "\n1\n", "２", "0", "0", "0", "0", "0", "<span>0</span>"])
            + '<td class="gmscore">-</td><td class="gmscore">3</td><td class="gmscore">8</td><td class="gmscore">1</td></tr>'
            '<tr><td class="gmscoreteam"> 東京ヤクルト </td>' + _cells(["0"] * 8 + ["２ｘ"])
            + '<td class="gmscore">-</td><td class="gmscore">2</td><td class="gmscore">9</td><td class="gmscore">0</td></tr>'
            "</table></div>",
            {"away": "d", "home": "s", "as": 3, "hs": 2},
        ),
    }
    calls = [_call(name, lambda html=html: observe_parse(html, url)) for name, html in observe_pages.items()]
    calls += [
        _call(name, lambda html=html, game=game: inning_pilot_parse(html, game))
        for name, (html, game) in inning_pages.items()
    ]
    calls.append(_call("annual_synthetic", lambda: annual(_annual_page())))
    fixture = (ROOT / "blueprobe/tests/fixtures/npb_annual/2005_c_std.html").read_text(encoding="utf-8")
    calls.append(_call("annual_fixture", lambda: annual(fixture)))
    return calls


def run_selectolax(argv=None) -> int:
    _selectolax_paths()
    parser = argparse.ArgumentParser(description=SELECTOLAX_DOC.splitlines()[0])
    parser.add_argument("--impl", choices=["real", "min"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.impl == "min":
        install_selectolax_min()
    elif importlib.util.find_spec("selectolax") is None:
        raise SystemExit("selectolax が無い。--impl real は selectolax のある環境で動かす")
    result = selectolax_outcomes()
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"selectolax={args.impl} cases={len(result)} bytes={len(text)}")
    return 0


# ==== httpx（旧 run_httpx.py）

HTTPX_DOC = """research/gpt-r001-score-allocation/fetch.py（collect・verify・inning_pilot）と同じ httpx.Client で PoliteFetcher を動かす（実験）。

    python scripts/stdlib_min.py httpx --impl real out.json
    python scripts/stdlib_min.py httpx --impl min  out.json   # httpx が入っていない環境

外のネットワークには出ない。127.0.0.1 の一時サーバーだけを使う。
"""
def _httpx_paths() -> None:
    """旧 run_httpx.py が import 時に置いた sys.path。"""
    sys.path[:0] = [str(ROOT), str(ROOT / "mindeps"), str(ROOT / "blueprobe"), str(ROOT / "queryu"),
                    str(ROOT / "research" / "gpt-r001-score-allocation")]


def httpx_install_httpx_min() -> None:
    if importlib.util.find_spec("httpx") is not None:
        raise SystemExit("httpx が入っている。--impl min は httpx なしの環境で動かす")
    inject("httpx", ROOT / "mindeps" / "httpx_min.py")


def install_selectolax_min_for_fetch() -> None:
    """fetch.py は import 時に selectolax も読む（まとめる前の collect.py は読まなかった）。selectolax が無いときだけ min を置く。"""
    if importlib.util.find_spec("selectolax") is None:
        install_selectolax_min()


class _Handler(BaseHTTPRequestHandler):
    seen: list[str] = []

    def do_GET(self):
        type(self).seen.append(self.headers.get("User-Agent") or "")
        if self.path.startswith("/redir"):
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
            return
        if self.path.startswith("/missing"):
            self.send_response(404)
            self.send_header("ETag", '"no"')
            self.end_headers()
            self.wfile.write(b"missing")
            return
        if self.path.startswith("/err"):
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"boom")
            return
        if self.headers.get("If-None-Match") == '"v1"':
            self.send_response(304)
            self.send_header("ETag", '"v1"')
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("ETag", '"v1"')
        self.send_header("Last-Modified", "Mon, 01 Jan 2024 00:00:00 GMT")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("<p>ok</p>".encode())

    def log_message(self, fmt, *args):
        return None


def httpx_outcomes() -> dict:
    """fetch.py の collect の with httpx.Client(...) as client を、ローカル URL に対して実行する。"""
    _httpx_paths()
    import httpx
    from queryu import Cache, PoliteFetcher, UA

    # 研究スクリプトの import が、この Client で通ることを確かめる。main は npb.jp へ行くので呼ばない。
    import fetch  # noqa: F401

    _Handler.seen = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        import tempfile
        cache = Cache(Path(tempfile.mkdtemp(prefix="httpx-min-")))
        # fetch.py の collect・verify・inning_pilot と同じ引数。
        with httpx.Client(headers={"User-Agent": UA}, timeout=45, follow_redirects=True) as client:
            fetcher = PoliteFetcher(cache, wait=0, client=client)
            pages = {
                "ok": fetcher.get("k", base + "/ok", "g"),
                "redir": fetcher.get("r", base + "/redir", "g"),
                "missing": fetcher.get("m", base + "/missing", "g"),
            }
            try:
                fetcher.get("e", base + "/err", "g")
                raised = None
            except Exception as exc:
                response = getattr(exc, "response", None)
                raised = getattr(response, "status_code", None)
            pages["conditional"] = fetcher.get("k", base + "/ok", "g", live=True)
        entry = cache.latest()["k"]
        return {
            "pages": pages,
            "requests": fetcher.requests,
            "error_status": raised,
            "etag": entry.get("etag"),
            "last_modified": entry.get("last_modified"),
            "user_agents": sorted(set(_Handler.seen)),
            "collect_imports": True,
        }
    finally:
        server.shutdown()
        thread.join(timeout=2)


def run_httpx(argv=None) -> int:
    _httpx_paths()
    parser = argparse.ArgumentParser(description=HTTPX_DOC.splitlines()[0])
    parser.add_argument("--impl", choices=["real", "min"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.impl == "min":
        httpx_install_httpx_min()
        install_selectolax_min_for_fetch()
    elif importlib.util.find_spec("httpx") is None:
        raise SystemExit("httpx が無い。--impl real は httpx のある環境で動かす")
    result = httpx_outcomes()
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"httpx={args.impl} requests={result['requests']} error={result['error_status']}")
    return 0


# ==== coverage（旧 run_coverage.py）

COVERAGE_DOC = """check_child_heads.validate_heads を coverage で測る（実験）。

    python scripts/stdlib_min.py coverage --impl real out.json   # 入っている coverage
    python scripts/stdlib_min.py coverage --impl cdn  out.json   # fetch_module の pure wheel。coverage は入れない

pure wheel（py3-none-any）には C tracer が無い。Python tracer でも
analysis2 と json_report の数は、この呼び出しでは C tracer と一致する。
"""
def _coverage_paths() -> None:
    """旧 run_coverage.py が import 時に置いた sys.path。"""
    sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mindeps")]

_SUMMARY = (
    "num_statements", "missing_lines", "num_branches", "covered_branches",
    "missing_branches", "num_partial_branches",
)


def exercise() -> None:
    _coverage_paths()
    import check_child_heads as heads

    good = {
        "schema": "child-heads/1", "ref": "main",
        "heads": {"myon-bioinformatics/BlueProbe": {
            "repository_id": 1,
            "optional": {"subtree_prefix": "blueprobe", "mirrored_from_parent": {"README.md": "README.md"}},
        }},
    }
    heads.validate_heads(good)
    samples = [
        {"schema": "no", "ref": "main", "heads": {"a/b": {}}},
        {"schema": "child-heads/1", "ref": "", "heads": {"a/b": {}}},
        {"schema": "child-heads/1", "ref": "m\n", "heads": {"a/b": {}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {}},
        {"schema": "child-heads/1", "ref": "main", "heads": {"a/b": "not-an-object"}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "bad": {"repository_id": 1, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 0, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": True, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 1, "optional": {}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 1, "optional": {"subtree_prefix": "/abs"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 1, "optional": {"subtree_prefix": "a/../b"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 1, "optional": {"subtree_prefix": "x", "not_in_parent": []}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 1, "optional": {"subtree_prefix": "x", "mirrored_from_parent": []}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"repository_id": 1, "optional": {"subtree_prefix": "x", "mirrored_from_parent": {"": "a"}}}}},
    ]
    for doc in samples:
        try:
            heads.validate_heads(doc)
        except ValueError:
            pass
    row = {"drift": True, "mirrors": {"README.md": "differs"}, "identical": False, "error": "x"}
    heads.failed({"children": [row]}, fail_on_drift=True, fail_on_diff=True)
    heads.failed(
        {"children": [{"drift": False, "mirrors": {"README.md": "identical"}, "identical": True}]},
        fail_on_drift=False, fail_on_diff=False,
    )


def measure(coverage_module) -> dict:
    directory = Path(tempfile.mkdtemp(prefix="coverage-min-"))
    data_file = directory / "coverage.dat"
    json_path = directory / "coverage.json"
    cov = coverage_module.Coverage(data_file=str(data_file), branch=True, config_file=False)
    cov.start()
    try:
        exercise()
    finally:
        cov.stop()
        cov.save()
    loaded = coverage_module.Coverage(data_file=str(data_file), branch=True, config_file=False)
    loaded.load()
    measured = [path for path in loaded.get_data().measured_files() if path.endswith("check_child_heads.py")]
    if len(measured) != 1:
        raise SystemExit(f"check_child_heads.py が測れていない: {measured}")
    _fn, statements, excluded, missing, _formatted = loaded.analysis2(measured[0])
    loaded.json_report(outfile=str(json_path), include=["*check_child_heads.py"])
    summary = json.loads(json_path.read_text(encoding="utf-8"))["files"]
    file_summary = next(iter(summary.values()))["summary"]
    return {
        "statements": list(statements),
        "missing": list(missing),
        "excluded": list(excluded),
        "summary": {key: file_summary[key] for key in _SUMMARY},
    }


def _locked_coverage_version() -> str:
    """uv.lock に書いてある版の pure wheel を取る。下限を足すのではなく、入っている版と比べる。"""
    name = None
    for line in (ROOT / "uv.lock").read_text(encoding="utf-8").splitlines():
        if line.startswith("name = "):
            name = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("version = ") and name == "coverage":
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("uv.lock に coverage が無い")


def _load_cdn():
    _coverage_paths()
    if importlib.util.find_spec("coverage") is not None:
        raise SystemExit("coverage が入っている。--impl cdn は coverage なしの環境で動かす")
    import fetch_module

    spec = fetch_module.resolve("coverage", _locked_coverage_version())
    wheel = fetch_module.fetch(spec, ROOT / ".cdn-cache")
    sys.path.insert(0, str(wheel))
    return importlib.import_module("coverage")


def run_coverage(argv=None) -> int:
    _coverage_paths()
    parser = argparse.ArgumentParser(description=COVERAGE_DOC.splitlines()[0])
    parser.add_argument("--impl", choices=["real", "cdn"], required=True)
    parser.add_argument("out")
    args = parser.parse_args(argv)
    if args.impl == "cdn":
        module = _load_cdn()
    else:
        if importlib.util.find_spec("coverage") is None:
            raise SystemExit("coverage が無い。--impl real は coverage のある環境で動かす")
        import coverage as module
    result = measure(module)
    text = json.dumps(result, ensure_ascii=False, sort_keys=True)
    Path(args.out).write_text(text, encoding="utf-8")
    origin = Path(module.__file__).as_posix()
    print(f"coverage={args.impl} statements={len(result['statements'])} missing={len(result['missing'])} from {origin}")
    return 0


# ==== 入口
COMMANDS = {
    "survey": survey,
    "trace-surface": trace_surface,
    "trace-drivers": drivers,
    "trace-third-party": trace_third_party,
    "linalg-feasibility": linalg_feasibility,
    "linalg": linalg,
    "overlap": overlap,
    "overlap-stdlib": overlap_stdlib,
    "selectolax": run_selectolax,
    "httpx": run_httpx,
    "coverage": run_coverage,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="scripts/stdlib_min.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"scripts/stdlib_min.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
