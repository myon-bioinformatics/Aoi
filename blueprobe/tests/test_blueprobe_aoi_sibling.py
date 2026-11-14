"""BlueProbe は QueRyu（--cache）を AOI_ROOT の Aoi から探す。PYTHONPATH は要らない。

``aoi_sibling_path`` は import できないときだけ ``AOI_ROOT/queryu``（または、このファイルの親が Aoi の
checkout のときはその ``queryu/``）を足す。単独の BlueProbe では隣を読まない。
"""
import os, shutil, subprocess, sys
from pathlib import Path

import pytest

import blueprobe

ROOT = Path(__file__).resolve().parents[1]
FAKE_QUERYU = (
    "import sys\n"
    "class Cache:\n"
    "    def __init__(self, path):\n"
    "        print('FAKE_QUERYU_CACHE', __file__)\n"
    "        sys.exit(5)\n"
)


def _aoi(tmp_path: Path, *, cycles: bool = True) -> Path:
    aoi = tmp_path / "aoi"
    (aoi / "queryu").mkdir(parents=True)
    (aoi / "blueprobe").mkdir()
    if cycles:
        (aoi / "cycles").mkdir()
    (aoi / "pyproject.toml").write_text("", encoding="utf-8")
    (aoi / "queryu" / "queryu.py").write_text(FAKE_QUERYU, encoding="utf-8")
    (aoi / "queryu" / "cache_core.py").write_text("class Cache:\n    pass\n", encoding="utf-8")
    return aoi


def _standalone_copy(tmp_path: Path) -> Path:
    work = tmp_path / "standalone" / "BlueProbe"
    work.mkdir(parents=True)
    for path in ROOT.glob("*.py"):
        shutil.copy2(path, work / path.name)
    return work


def _env(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "AOI_ROOT"}}
    env.update(extra)
    return env


def _cache(tmp_path: Path) -> Path:
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "manifest.jsonl").write_text("", encoding="utf-8")
    return cache


def test_cli_finds_queryu_through_aoi_root_without_pythonpath(tmp_path):
    aoi = _aoi(tmp_path)
    work = _standalone_copy(tmp_path)
    result = subprocess.run([sys.executable, str(work / "blueprobe.py"), "--source", "html_source",
                             "--cache", str(_cache(tmp_path))],
                            cwd=tmp_path, env=_env(AOI_ROOT=str(aoi)), capture_output=True, text=True)
    assert result.returncode == 5, result.stderr
    assert f"FAKE_QUERYU_CACHE {aoi / 'queryu' / 'queryu.py'}" in result.stdout


def test_cli_without_aoi_root_or_pythonpath_reports_how_to_fix(tmp_path):
    work = _standalone_copy(tmp_path)
    (tmp_path / "standalone" / "queryu").mkdir()  # 単独の BlueProbe の隣にあっても読まない
    (tmp_path / "standalone" / "queryu" / "queryu.py").write_text(FAKE_QUERYU, encoding="utf-8")
    result = subprocess.run([sys.executable, str(work / "blueprobe.py"), "--source", "html_source",
                             "--cache", str(_cache(tmp_path))],
                            cwd=tmp_path, env=_env(), capture_output=True, text=True)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "AOI_ROOT" in result.stderr
    assert "FAKE_QUERYU_CACHE" not in result.stdout


def test_sibling_comes_from_aoi_root(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    aoi = _aoi(tmp_path)
    blueprobe.aoi_sibling_path("blueprobe_test_missing_module", here=tmp_path / "x" / "BlueProbe" / "blueprobe.py",
                               env={"AOI_ROOT": str(aoi)})
    assert sys.path[0] == str(aoi / "queryu")


def test_embedded_in_aoi_without_aoi_root(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    aoi = _aoi(tmp_path)
    blueprobe.aoi_sibling_path("blueprobe_test_missing_module", here=aoi / "blueprobe" / "blueprobe.py", env={})
    assert sys.path[0] == str(aoi / "queryu")


def test_standalone_and_non_aoi_roots_add_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    before = list(sys.path)
    standalone = tmp_path / "work"
    (standalone / "BlueProbe").mkdir(parents=True)
    (standalone / "queryu").mkdir()
    blueprobe.aoi_sibling_path("blueprobe_test_missing_module", here=standalone / "BlueProbe" / "blueprobe.py", env={})
    not_aoi = _aoi(tmp_path, cycles=False)
    blueprobe.aoi_sibling_path("blueprobe_test_missing_module", here=standalone / "BlueProbe" / "blueprobe.py",
                               env={"AOI_ROOT": str(not_aoi)})
    assert sys.path == before


def test_importable_module_is_never_shadowed(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    before = list(sys.path)
    blueprobe.aoi_sibling_path("json", env={"AOI_ROOT": str(_aoi(tmp_path))})
    assert sys.path == before


@pytest.mark.parametrize("missing", ["queryu"])
def test_main_returns_2_when_queryu_is_missing(tmp_path, monkeypatch, capsys, missing):
    monkeypatch.setitem(sys.modules, missing, None)
    monkeypatch.delenv("AOI_ROOT", raising=False)
    assert blueprobe.main(["--source", "html_source", "--cache", str(_cache(tmp_path))]) == 2
    assert "AOI_ROOT" in capsys.readouterr().err
