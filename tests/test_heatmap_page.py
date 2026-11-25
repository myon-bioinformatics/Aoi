"""🌡️ The heatmap page (scripts/build_heatmap_page.py) is built from the vendored PySaiyanWeBoo under ``python -S``."""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _page() -> str:
    return subprocess.run([sys.executable, "-S", str(ROOT / "scripts/build_heatmap_page.py")], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def _pswb():
    """The vendored PySaiyanWeBoo the page is built from (loaded by path, beside the repository's own modules)."""
    spec = importlib.util.spec_from_file_location("dragowing_vendored_pswb", ROOT / "vendor/pysaiyanweboo/pysaiyanweboo.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_page_runs_with_python_minus_s_and_uses_pswb_parts():
    html = _page()
    assert html.startswith("<!doctype html>")
    assert '<body class="ui-elements" data-ui-theme="modern">' in html and '<main class="ui-page">' in html
    assert "data-ui-theme-switch" in html and 'data-ui-scroll="table"' in html
    assert '<div id="stats" hidden><div class="ui-grid ui-stats">' in html          # 📊 stat_tiles()
    assert html.count('<script type="module">') == 5                              # ui, scroll, records, imagestudio, the page
    assert "<script>" not in html                                                    # no classic copy of PySaiyanWeBoo
    assert "globalThis.webUiImageStudio" in html and "pngPayload(" in html          # 🔡 Base64 from imagestudio.js
    assert "bindDrafts(document" in html and "localStorage" not in html.split('<script type="module">')[-1]   # 📝 records.js
    assert "https://myon-bioinformatics.github.io/tools/image-studio/" in html and "/tools/ironmate/" not in html


def test_every_draft_field_has_a_records_key():
    html = _page()
    keys = re.findall(r'data-ui-draft="([^"]+)"', html[:html.index('<script type="module">')])   # the markup, not the modules
    assert sorted(keys) == sorted({"source", "format", "palette", "steps", "zmin", "zmax", "labels", "reverse", "transpose",
                                   "flip-y", "export-axes", "size"})


def test_the_vendored_pswb_is_the_locked_one():
    row = next(f for f in json.loads((ROOT / "vendor.lock.json").read_text(encoding="utf-8"))["files"]
               if f["repository"] == "myon-bioinformatics/PySaiyanWeBoo")
    assert row["destination"] == "vendor/pysaiyanweboo/pysaiyanweboo.py" and row["ref"] == row["commit"]
    assert 'sys.path[:0] = [str(ROOT), str(ROOT / "vendor" / "pysaiyanweboo")]' in (ROOT / "scripts/build_heatmap_page.py").read_text()


def test_built_page_accepts_portfolio_back_nav():
    ui = _pswb()
    with_nav = ui.add_back_nav(_page(), [{"label": "← 🧭 Tools & Demos", "href": "../../index.html#tools"}], test_id="portfolio-back")
    assert '<main class="ui-page"><nav class="ui-back"' in with_nav and 'data-testid="portfolio-back"' in with_nav
