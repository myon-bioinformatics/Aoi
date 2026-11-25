"""ヒートマップページ（scripts/build_heatmap_page.py）と PSWB バンドルの整合性テスト。"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pysaiyanweboo

ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_heatmap_bundle_matches_pinned_pysaiyanweboo():
    builder = _load("scripts/build_heatmap_bundle.py", "dragowing_build_heatmap_bundle")
    assert builder.check_bundle_module(ROOT / "scripts/heatmap_bundle.py") == []


def test_build_heatmap_page_runs_with_python_minus_s():
    proc = subprocess.run(
        [sys.executable, "-S", str(ROOT / "scripts/build_heatmap_page.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    html = proc.stdout
    assert html.startswith("<!doctype html>")
    assert '<body class="ui-elements" data-ui-theme="modern">' in html
    assert '<main class="ui-page">' in html
    assert "data-ui-theme-switch" in html
    assert 'data-ui-scroll="table"' in html
    assert "ui-panel" in html
    assert "ui-stats" in html
    assert "https://myon-bioinformatics.github.io/tools/ironmate/" in html


def test_built_page_accepts_portfolio_back_nav():
    html = subprocess.check_output(
        [sys.executable, "-S", str(ROOT / "scripts/build_heatmap_page.py")],
        cwd=ROOT,
        text=True,
    )
    with_nav = pysaiyanweboo.add_back_nav(
        html,
        [{"label": "← 🧭 Tools & Demos", "href": "../../index.html#tools"}],
        test_id="portfolio-back",
    )
    assert '<main class="ui-page"><nav class="ui-back"' in with_nav
    assert 'data-testid="portfolio-back"' in with_nav
