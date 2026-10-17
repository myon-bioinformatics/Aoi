"""単独の QueRyu では、隣のディレクトリ（../blueprobe など）を相対パスで読まない。

BlueProbe は固定 SHA の checkout を PYTHONPATH で渡す。隣の ``blueprobe/`` を読むのは、親が Aoi の checkout
（pyproject.toml と cycles/ がある）のときだけで、その処理は ``queryu.aoi_sibling_path`` 一か所に限る。
"""
import ast
import os
from pathlib import Path
import subprocess
import sys

import pytest

import queryu

ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted(p for p in ROOT.rglob("*.py")
                 if not {"tests", "vendor", ".test-deps", ".venv", "build"} & set(p.relative_to(ROOT).parts))
SIBLINGS = {"blueprobe", "sakanalytics", "pythdragoras", "nagoyaction", "dragowing"}


def _sibling_path_uses(path: Path):
    """``.parent`` / ``.parents[...]`` と兄弟名の文字列を ``/`` でつなぐ式、と sys.path の操作を探す。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    allowed = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "aoi_sibling_path":
            allowed |= set(range(node.lineno, node.end_lineno + 1))
    for node in ast.walk(tree):
        if getattr(node, "lineno", None) in allowed:
            continue
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            text = ast.unparse(node)
            if ".parent" in text and any(f"'{s}'" in text or f'"{s}"' in text for s in SIBLINGS):
                yield node.lineno, text
        if isinstance(node, ast.Call) and "sys.path" in ast.unparse(node.func):
            text = ast.unparse(node)
            if any(s in text for s in SIBLINGS) or "parents[" in text or ".parent" in text:
                yield node.lineno, text


def test_sources_do_not_reach_siblings_by_relative_path():
    found = {str(p.relative_to(ROOT)): list(_sibling_path_uses(p)) for p in SOURCES}
    assert {k: v for k, v in found.items() if v} == {}


def test_sibling_is_added_only_inside_an_aoi_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    standalone = tmp_path / "work"
    (standalone / "QueRyu").mkdir(parents=True)
    (standalone / "blueprobe").mkdir()  # 単独の QueRyu の隣に blueprobe/ があっても読まない
    queryu.aoi_sibling_path(standalone / "QueRyu", "queryu_test_missing_module")
    assert str(standalone / "blueprobe") not in sys.path

    aoi = tmp_path / "aoi"
    for d in ("queryu", "blueprobe", "cycles"):
        (aoi / d).mkdir(parents=True)
    (aoi / "pyproject.toml").write_text("", encoding="utf-8")
    queryu.aoi_sibling_path(aoi / "queryu", "queryu_test_missing_module")
    assert sys.path[0] == str(aoi / "blueprobe")


def test_importable_module_is_never_shadowed_by_a_sibling(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    aoi = tmp_path / "aoi"
    for d in ("queryu", "blueprobe", "cycles"):
        (aoi / d).mkdir(parents=True)
    (aoi / "pyproject.toml").write_text("", encoding="utf-8")
    queryu.aoi_sibling_path(aoi / "queryu", "blueprobe")
    assert str(aoi / "blueprobe") not in sys.path


def test_blueprobe_modules_come_from_the_pinned_checkout_not_a_sibling():
    import blueprobe
    import npb_calendar
    import npb_team_annual
    pinned = [Path(p).resolve() for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
    for module in (blueprobe, npb_calendar, npb_team_annual):
        origin = Path(module.__file__).resolve()
        assert origin.parent != (ROOT.parent / "blueprobe").resolve(), origin
        # PYTHONPATH で渡した BlueProbe の checkout（CI では .test-deps/blueprobe）から読まれている
        assert origin.parent in pinned, (origin, pinned)


def test_cli_entry_point_does_not_add_a_sibling(tmp_path):
    # __main__ の経路（python queryu.py）でも、隣の ../blueprobe を足さずに PYTHONPATH の BlueProbe を使う
    code = (
        "import runpy, sys\n"
        f"sys.argv = [{str(ROOT / 'queryu.py')!r}, '--help']\n"
        "try:\n"
        "    runpy.run_path(sys.argv[0], run_name='__main__')\n"
        "except SystemExit:\n"
        "    pass\n"
        "import blueprobe\n"
        "print('BLUEPROBE=' + blueprobe.__file__)\n"
        "print('\\n'.join(sys.path))\n"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True, cwd=tmp_path)
    lines = out.stdout.splitlines()
    assert str(ROOT.parent / "blueprobe") not in lines
    origin = Path(next(l for l in lines if l.startswith("BLUEPROBE="))[len("BLUEPROBE="):]).resolve()
    assert origin.parent != (ROOT.parent / "blueprobe").resolve()
