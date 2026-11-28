"""🌡️ The heatmap page (scripts/build_heatmap_page.py) is built from the vendored PySaiyanWeBoo under ``python -S``."""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_cli_spec = importlib.util.spec_from_file_location("dragowing_cli_args", ROOT / "vendor/cli_args/cli_args.py")
_cli_args = importlib.util.module_from_spec(_cli_spec)
sys.modules[_cli_spec.name] = _cli_args
_cli_spec.loader.exec_module(_cli_args)
run_cli = _cli_args.run_cli


def _page() -> str:
    page = run_cli(ROOT / "scripts/build_heatmap_page.py", cwd=ROOT)
    assert page.returncode == 0, page.stderr
    return page.stdout


def _pswb():
    """The pinned PySaiyanWeBoo the page is built from (📦 the pages group)."""
    return importlib.import_module("pysaiyanweboo")


def test_page_uses_pswb_parts():
    html = _page()
    assert html.startswith("<!doctype html>")
    assert '<body class="ui-elements" data-ui-theme="modern">' in html and '<main class="ui-page">' in html
    assert "data-ui-theme-switch" in html and 'data-ui-scroll="table"' in html
    assert '<div id="stats" hidden><div class="ui-grid ui-stats">' in html          # 📊 stat_tiles()
    assert html.count('<script type="module">') == 5                              # ui, scroll, records, imagestudio, the page
    assert "<script>" not in html                                                    # no classic copy of PySaiyanWeBoo
    assert "globalThis.webUiImageStudio" in html and "pngPayload(" in html          # 🔡 Base64 from imagestudio.js
    assert html.count("function heatmapColor(") == 1
    editor = html.rsplit('<script type="module">', 1)[-1]
    assert "ui.heatmapColor(value, low, high, levels, PALETTE)" in editor
    assert "palette: [...PALETTE]" in editor and "function heatColor(" not in editor
    assert "bindDrafts(document" in html and "localStorage" not in html.split('<script type="module">')[-1]   # 📝 records.js
    assert "https://myon-bioinformatics.github.io/tools/#image-studio" in html and "/tools/ironmate/" not in html


def test_every_draft_field_has_a_records_key():
    html = _page()
    keys = re.findall(r'data-ui-draft="([^"]+)"', html[:html.index('<script type="module">')])   # the markup, not the modules
    assert sorted(keys) == sorted({"source", "format", "palette", "steps", "zmin", "zmax", "labels", "reverse", "transpose",
                                   "flip-y", "export-axes", "size"})


def test_pswb_is_pinned_by_commit_and_not_vendored():
    import tomllib
    pages = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["dependency-groups"]["pages"]
    assert len(pages) == 1 and re.fullmatch(r"pysaiyanweboo @ git\+https://github\.com/myon-bioinformatics/PySaiyanWeBoo@main", pages[0])  # 🔁 follows main; uv.lock records the commit
    assert not [f for f in json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))["files"]
                if f["repository"] == "myon-bioinformatics/PySaiyanWeBoo"]
    assert not (ROOT / "vendor/pysaiyanweboo").exists()


def test_built_page_accepts_portfolio_back_nav():
    ui = _pswb()
    with_nav = ui.add_back_nav(_page(), [{"label": "← 🧰 Tools", "href": "../../index.html#tools"}], test_id="portfolio-back")
    assert '<main class="ui-page"><nav class="ui-back"' in with_nav and 'data-testid="portfolio-back"' in with_nav
