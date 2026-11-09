"""scripts/child_checks.py（子へ配る検査の本体）が、各子が今持っている同じ検査と同じ答えを出す。

子が採用（tests を数行にする）する前に、Aoi 側で各 prefix に対して結果の一致を確かめておく。
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import child_checks  # noqa: E402

PIN = "9e3da7ae1846e9604ebc24bb5178f7de094a4e77"
PIN_CHILDREN = ("blueprobe", "queryu", "sakanalytics", "pythdragoras", "nagoyaction", "dragowing")
# 子の tests/test_no_sibling_imports.py の定数（採用後は子にこれだけが残る）
SIBLING_CHILDREN = {
    "sakanalytics": dict(third_party={"polars", "pytest", "ortools"}),
    "pythdragoras": dict(third_party={"polars", "numpy", "pytest"}),
    "dragowing": dict(third_party={"polars", "numpy", "markdown", "pytest"}, aoi_provided=(),
                      extra_local=("dragowing", "reports")),
}
LIVE_REF = "${{ steps.parent.outputs.sha }}"  # pythdragoras だけが親の main を実行時に解決する


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem + "_" + path.parent.parent.name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("child", PIN_CHILDREN)
def test_parent_pins_match_each_child_copy(child):
    pins = child_checks.parent_workflow_pins(ROOT / child)
    live = [p for p in pins if p == LIVE_REF]
    pins = [p for p in pins if p != LIVE_REF]
    assert pins and set(pins) == {PIN}, pins
    assert live == ([LIVE_REF] if child == "pythdragoras" else [])


@pytest.mark.parametrize("child", sorted(SIBLING_CHILDREN))
def test_sibling_uses_match_each_child_copy(child):
    own = _load(ROOT / child / "tests" / "test_no_sibling_imports.py")
    found = child_checks.sibling_uses(ROOT / child, me=child, skip_dirs=own.SKIP_DIRS,
                                     exclude=(ROOT / child / "tests" / "test_no_sibling_imports.py").resolve(),
                                     **SIBLING_CHILDREN[child])
    assert found == own.find_uses()
    assert found - own.KNOWN_EXCEPTIONS == set()
    assert own.KNOWN_EXCEPTIONS - found == set()


def test_aoi_root_from_env_accepts_only_aoi(tmp_path):
    assert child_checks.aoi_root_from_env({"AOI_ROOT": str(ROOT)}) == ROOT
    with pytest.raises(ValueError):
        child_checks.aoi_root_from_env({})
    with pytest.raises(ValueError):
        child_checks.aoi_root_from_env({"AOI_ROOT": str(tmp_path)})


def test_export_path_touches_sys_path_and_pythonpath_once(tmp_path, monkeypatch):
    env = {}
    monkeypatch.setattr(sys, "path", list(sys.path))
    child_checks.export_path(tmp_path, env)
    child_checks.export_path(tmp_path, env)
    assert sys.path.count(str(tmp_path)) == 1
    assert env["PYTHONPATH"].split(os.pathsep) == [str(tmp_path)]


def test_launch_env_sets_tool_python_and_drops_error_format():
    env = child_checks.launch_env("score_sensitivity", "py", {"PY_LAUNCH_ERROR_FORMAT": "x", "KEEP": "1"})
    assert env == {"SCORE_SENSITIVITY_PYTHON": "py", "KEEP": "1"}


def test_find_node_rejects_old_major(tmp_path):
    fake = tmp_path / "node"
    fake.write_text("#!/bin/sh\necho v24.0.0\n", encoding="utf-8")
    fake.chmod(0o755)
    assert child_checks.find_node(env={"NODE": str(fake)}) is None
    assert child_checks.find_node(min_major=24, env={"NODE": str(fake)}) == str(fake)


def test_cli_lists_pins_and_uses(capsys):
    assert child_checks.main(["pins", str(ROOT / "queryu")]) == 0
    assert set(capsys.readouterr().out.split()) == {PIN}
    assert child_checks.main(["uses", str(ROOT / "pythdragoras")]) == 0
    assert "import:sakanalytics" in capsys.readouterr().out
    assert child_checks.main(["nope"]) == 2


def test_shared_tools_lock_lists_child_checks():
    lock = json.loads((ROOT / "shared-tools.lock.json").read_text(encoding="utf-8"))
    assert any(e["path"] == "scripts/child_checks.py" for e in lock["files"])
