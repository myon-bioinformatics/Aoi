"""Aoi-owned committed research outputs follow DRAgoWing fonts."""
from pathlib import Path
from dragowing.figures import FONT

ROOT = Path(__file__).resolve().parents[1]
TIGHT = FONT.replace(" ", "")


def test_committed_research_reports_use_the_font():
    pages = sorted(ROOT.glob("research/*/outputs/*.html"))
    assert pages  # 検証が空振りしない
    for path in pages:
        text = path.read_text(encoding="utf-8")
        if "Plotly.newPlot" in text:  # DRAgoWing の研究用レポート（取得した原本の HTML は対象外）
            assert f"font:16px/1.65 {TIGHT}" in text and f"family:'{FONT}'" in text, path
            assert "system-ui" not in text, path
