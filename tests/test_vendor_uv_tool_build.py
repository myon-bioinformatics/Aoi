"""vendor/uv_tool_build.py: 親の共通 uv tool ビルダーの Aoi 側コピーが動くこと。

バイトの一致は tests/test_vendor_lock.py と scripts/repo_checks.py shared_tools_lock が見る。
ここは Aoi の子エントリで build できることと、大文字のエントリを拒むことだけ確かめる。
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "vendor" / "uv_tool_build.py"


def _load():
    spec = importlib.util.spec_from_file_location("aoi_vendor_uv_tool_build", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builds_lowercase_child_entry(tmp_path):
    out = tmp_path / "nagoyaction-tool"
    result = _load().build([ROOT / "nagoyaction" / "nagoyaction.py"], out)
    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["name"] == "nagoyaction"
    assert data["project"]["dependencies"] == []
    assert data["project"]["scripts"] == {"nagoyaction": "nagoyaction:main"}
    assert result["scripts"] == {"nagoyaction": "nagoyaction:main"}
    assert (out / "nagoyaction.py").read_bytes() == (ROOT / "nagoyaction" / "nagoyaction.py").read_bytes()


def test_builds_blueprobe_entry_without_its_removed_local_builder(tmp_path):
    """BlueProbe #53 dropped build_stdlib_tool.py; the shared builder packages blueprobe.py."""
    out = tmp_path / "blueprobe-tool"
    result = _load().build([ROOT / "blueprobe" / "blueprobe.py"], out)
    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["name"] == "blueprobe"
    assert data["project"]["dependencies"] == []
    assert data["project"]["scripts"] == {"blueprobe": "blueprobe:main"}
    assert result["scripts"] == {"blueprobe": "blueprobe:main"}
    assert (out / "blueprobe.py").read_bytes() == (ROOT / "blueprobe" / "blueprobe.py").read_bytes()


def test_rejects_camelcase_entry_name(tmp_path):
    camel = tmp_path / "NagoyAction.py"
    camel.write_text("def main():\n    return 0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="lowercase"):
        _load().build([camel], tmp_path / "out")


def test_cli_runs_without_site(tmp_path):
    run = subprocess.run([sys.executable, "-S", str(BUILDER), str(ROOT / "nagoyaction" / "nagoyaction.py"),
                          "--out", str(tmp_path / "o"), "--json"], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
