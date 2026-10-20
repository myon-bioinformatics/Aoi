#!/usr/bin/env python3
"""selectolax / httpx / そのほかの第三者 import を ast と「パッケージが無い」実行で見る（実験）。

polars と numpy のlinalg、調査レポートは別の作業。ここでは残りを数える。

    python scripts/trace_third_party.py
"""
from __future__ import annotations

import ast
import builtins
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".venv", ".git", ".test-deps", "node_modules", "__pycache__", ".cdn-cache", ".venv-min"}
STDLIB = set(sys.stdlib_module_names) | {"__future__"}


def _py_files():
    for path in sorted(ROOT.rglob("*.py")):
        if not SKIP & set(path.relative_to(ROOT).parts):
            yield path


def _local_names() -> set[str]:
    names = set()
    for path in _py_files():
        names.add(path.stem)
        names.update(path.relative_to(ROOT).parts[:-1])
    return names


def survey() -> dict:
    """第三者の import と、selectolax / httpx の静的な属性参照。"""
    local = _local_names()
    imports: dict[str, list[str]] = defaultdict(list)
    attrs = {"selectolax": Counter(), "httpx": Counter()}
    dynamic = []
    for path in _py_files():
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
            "research/gpt-r001-score-allocation/observe.py",
            "research/gpt-r001-score-allocation/verify.py",
            "research/gpt-r001-score-allocation/inning_pilot.py",
            "blueprobe/tests/test_blueprobe_html_parity.py",
        ],
        "httpx": [
            "research/gpt-r001-score-allocation/collect.py",
            "research/gpt-r001-score-allocation/verify.py",
            "research/gpt-r001-score-allocation/inning_pilot.py",
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
    markdown = fm.resolve("markdown")
    print("markdown", markdown["version"], markdown["filename"])


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--resolve", action="store_true", help="PyPI で fetch_module の拒否を確かめる")
    args = parser.parse_args(argv)
    found = survey()
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


if __name__ == "__main__":
    raise SystemExit(main())
