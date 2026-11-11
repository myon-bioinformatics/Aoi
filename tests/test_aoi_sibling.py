"""DRAgoWing は QueRyu の ask と PythDRagoras の propositions / rule_search を AOI_ROOT の Aoi から探す。

PYTHONPATH は要らない。``aoi_sibling.aoi_sibling_path`` は import できないときだけ ``AOI_ROOT/<sibling>``
（AOI_ROOT がなく、このパッケージの親が Aoi の checkout のときはその ``<sibling>``）を足す。単独では隣を読まない。
"""
import os, shutil, subprocess, sys
from pathlib import Path

from dragowing import aoi_sibling

ROOT = Path(__file__).resolve().parents[1]
PROBE = r"""
import importlib.machinery, sys, types
from pathlib import Path
pkg_dir = Path(sys.argv[1])
pkg = types.ModuleType("dragowing"); pkg.__path__ = [str(pkg_dir)]
pkg.__spec__ = importlib.machinery.ModuleSpec("dragowing", loader=None, is_package=True)
pkg.__spec__.submodule_search_locations = pkg.__path__
sys.modules["dragowing"] = pkg
from dragowing import forms, overlap
try:
    print("ask", forms.registration_status({}))
    rule_search, propositions = overlap._engines()
    print("rule_search", rule_search.__file__)
    print("propositions", propositions.__file__)
except ModuleNotFoundError as error:
    print("missing", error.name, error, file=sys.stderr)
    sys.exit(3)
"""


def _aoi(tmp_path: Path, *, cycles: bool = True) -> Path:
    aoi = tmp_path / "aoi"
    (aoi / "queryu" / "ask").mkdir(parents=True)
    (aoi / "pythdragoras").mkdir()
    if cycles:
        (aoi / "cycles").mkdir()
    (aoi / "pyproject.toml").write_text("", encoding="utf-8")
    (aoi / "queryu" / "ask" / "ask.py").write_text("def registration_status(item):\n    return 'FAKE_ASK'\n")
    (aoi / "pythdragoras" / "propositions.py").write_text("")
    (aoi / "pythdragoras" / "rule_search.py").write_text("")
    return aoi


def _copy_package(target: Path) -> Path:
    target.mkdir(parents=True)
    for path in ROOT.glob("*.py"):
        shutil.copy2(path, target / path.name)
    return target


def _env(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "AOI_ROOT"}}
    env.update(extra)
    return env


def _probe(pkg: Path, cwd: Path, env: dict):
    return subprocess.run([sys.executable, "-c", PROBE, str(pkg)], cwd=cwd, env=env, capture_output=True, text=True)


def test_siblings_come_from_aoi_root_without_pythonpath(tmp_path):
    aoi = _aoi(tmp_path)
    pkg = _copy_package(tmp_path / "standalone" / "DRAgoWing")
    result = _probe(pkg, tmp_path, _env(AOI_ROOT=str(aoi)))
    assert result.returncode == 0, result.stderr
    assert "ask FAKE_ASK" in result.stdout
    assert f"rule_search {aoi / 'pythdragoras' / 'rule_search.py'}" in result.stdout
    assert f"propositions {aoi / 'pythdragoras' / 'propositions.py'}" in result.stdout


def test_embedded_in_aoi_without_aoi_root(tmp_path):
    aoi = _aoi(tmp_path)
    pkg = _copy_package(aoi / "dragowing")
    result = _probe(pkg, tmp_path, _env())
    assert result.returncode == 0, result.stderr
    assert f"rule_search {aoi / 'pythdragoras' / 'rule_search.py'}" in result.stdout


def test_missing_sibling_names_aoi_root(tmp_path):
    pkg = _copy_package(tmp_path / "standalone" / "DRAgoWing")
    shutil.copytree(_aoi(tmp_path / "x") / "queryu", tmp_path / "standalone" / "queryu")  # 隣にあっても読まない
    result = _probe(pkg, tmp_path, _env())
    assert result.returncode == 3, result.stdout + result.stderr
    assert "missing ask" in result.stderr and "AOI_ROOT" in result.stderr


def test_non_aoi_root_is_ignored(tmp_path):
    not_aoi = _aoi(tmp_path, cycles=False)
    pkg = _copy_package(tmp_path / "standalone" / "DRAgoWing")
    result = _probe(pkg, tmp_path, _env(AOI_ROOT=str(not_aoi)))
    assert result.returncode == 3, result.stdout + result.stderr


def test_importable_module_is_never_shadowed(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    before = list(sys.path)
    aoi_sibling.aoi_sibling_path("json", "pythdragoras", env={"AOI_ROOT": str(_aoi(tmp_path))})
    aoi_sibling.aoi_sibling_path("dragowing_test_missing", "pythdragoras",
                                 here=tmp_path / "w" / "DRAgoWing" / "aoi_sibling.py", env={})
    assert sys.path == before
    aoi_sibling.aoi_sibling_path("dragowing_test_missing", "pythdragoras", env={"AOI_ROOT": str(tmp_path / "aoi")})
    assert sys.path[0] == str(tmp_path / "aoi" / "pythdragoras")


def test_main_runs_as_a_file_without_pythonpath(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "__main__.py"), "--help"], cwd=tmp_path, env=_env(),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "usage" in result.stdout.lower()
