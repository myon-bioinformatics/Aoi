#!/usr/bin/env python3
"""check_child_heads.validate_heads を coverage で測る（実験）。

    python mindeps/run_coverage.py --impl real out.json   # 入っている coverage
    python mindeps/run_coverage.py --impl cdn  out.json   # fetch_module の pure wheel。coverage は入れない

pure wheel（py3-none-any）には C tracer が無い。Python tracer でも
analysis2 と json_report の数は、この呼び出しでは C tracer と一致する。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mindeps")]

_SUMMARY = (
    "num_statements", "missing_lines", "num_branches", "covered_branches",
    "missing_branches", "num_partial_branches",
)


def exercise() -> None:
    import check_child_heads as heads

    good = {
        "schema": "child-heads/1", "ref": "main",
        "heads": {"myon-bioinformatics/BlueProbe": {
            "sha": "a" * 40, "repository_id": 1,
            "optional": {"subtree_prefix": "blueprobe", "mirrored_from_parent": {"README.md": "README.md"}},
        }},
    }
    heads.validate_heads(good)
    samples = [
        {"schema": "no", "ref": "main", "heads": {"a/b": {}}},
        {"schema": "child-heads/1", "ref": "", "heads": {"a/b": {}}},
        {"schema": "child-heads/1", "ref": "m\n", "heads": {"a/b": {}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "bad": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "zz", "repository_id": 1, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 0, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": True, "optional": {"subtree_prefix": "x"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "/abs"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "a/../b"}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "x", "not_in_parent": []}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "x", "mirrored_from_parent": []}}}},
        {"schema": "child-heads/1", "ref": "main", "heads": {
            "a/b": {"sha": "a" * 40, "repository_id": 1, "optional": {"subtree_prefix": "x", "mirrored_from_parent": {"": "a"}}}}},
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


_EXTRA_EQ = re.compile(r"""^extra\s*==\s*['"]([^'"]+)['"]$""")


def _and_clauses(marker: str) -> list[str] | None:
    """Top-level ``and`` clauses. ``or`` is not a conjunction, so return None."""
    clauses: list[str] = []
    buf: list[str] = []
    quote = ""
    i = 0
    while i < len(marker):
        ch = marker[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = ""
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if marker.startswith(" or ", i):
            return None
        if marker.startswith(" and ", i):
            clauses.append("".join(buf).strip())
            buf = []
            i += 5
            continue
        buf.append(ch)
        i += 1
    if quote:
        return None
    clauses.append("".join(buf).strip())
    return clauses


def _unselected_extra(requirement: str) -> bool:
    """True when the marker is an AND that demands an extra.

    ``fetch_module`` fail-closes on a pre-release such as ``3.11.0a6`` before it
    can see ``extra == "toml"``. No extra is selected, so that conjunction is not
    a runtime dependency. A bare requirement, or one that uses ``or``, stays a
    dependency.
    """
    if ";" not in requirement:
        return False
    clauses = _and_clauses(requirement.split(";", 1)[1].strip())
    if not clauses:
        return False
    for clause in clauses:
        text = clause.strip()
        while text.startswith("(") and text.endswith(")") and len(text) > 1:
            text = text[1:-1].strip()
        match = _EXTRA_EQ.fullmatch(text)
        if match and match.group(1) != "":
            return True
    return False


def _listed_runtime_deps(package: str, version: str) -> list[str]:
    import fetch_module

    url = f"{fetch_module.INDEX}/{package}/{version}/json"
    meta = json.loads(fetch_module._get(url))
    return fetch_module.runtime_requirements(meta["info"])


def _resolve_coverage(version: str) -> dict:
    """Resolve the locked pure wheel.

    ``coverage`` 7.16.2 publishes one requirement,
    ``tomli; python_full_version <= "3.11.0a6" and extra == "toml"``.
    The locked resolver treats the pre-release comparison as an active
    dependency. The extra is not selected, so the wheel is still fetched.
    """
    import fetch_module

    try:
        return fetch_module.resolve("coverage", version)
    except SystemExit as exc:
        deps = _listed_runtime_deps("coverage", version)
        if deps and all(_unselected_extra(dep) for dep in deps):
            return fetch_module.resolve("coverage", version, allow_deps=True)
        raise exc


def _load_cdn():
    if importlib.util.find_spec("coverage") is not None:
        raise SystemExit("coverage が入っている。--impl cdn は coverage なしの環境で動かす")
    import fetch_module

    spec = _resolve_coverage(_locked_coverage_version())
    wheel = fetch_module.fetch(spec, ROOT / ".cdn-cache")
    sys.path.insert(0, str(wheel))
    return importlib.import_module("coverage")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
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


if __name__ == "__main__":
    raise SystemExit(main())
