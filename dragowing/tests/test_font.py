"""文字はメイリオを先頭にして、図・ページ・研究用レポートで揃える。

figures.FONT が基準。research_report.py と reports/build_reports.py は単独で配布・実行されるので
import せずに同じ文字列を書き、ここで一致を確かめる。
"""
from dragowing import research_report
from dragowing.figures import FONT, heatmap_figure
from dragowing.htmlout import figure_block, standalone
from reports.build_reports import page

TIGHT = FONT.replace(" ", "")  # CSS で詰めて書いている形: Meiryo,メイリオ,sans-serif


def test_font_puts_meiryo_first():
    assert FONT == "Meiryo, メイリオ, sans-serif"


def test_page_and_figure_use_the_font():
    fig = heatmap_figure([{"league": "C", "team": "d", "team_name": "中日", "season": 2020, "value": 1}], "value")
    assert fig["layout"]["font"]["family"] == FONT
    assert f"font-family: {FONT};" in standalone("t", figure_block(fig, "f"), plotly=True)


def test_research_report_template_uses_the_font_and_keeps_it_when_a_figure_sets_its_own_font():
    t = research_report.TEMPLATE
    assert f"font:16px/1.65 {TIGHT}" in t and f"family:'{FONT}'" in t
    assert "system-ui" not in t
    # 図が layout.font（大きさだけなど）を持っても、既定の family と色を失わない
    assert "...p.layout,font:{family:" in t and "...(p.layout||{}).font}" in t


def test_report_pages_use_the_font():
    class Md:
        default_stylesheet = staticmethod(lambda: "")
    out = page("t", "<p>x</p>", Md)
    assert f"font-family:{TIGHT}" in out and "system-ui" not in out


def test_committed_research_reports_use_the_font(aoi_root):
    pages = sorted(aoi_root.glob("research/*/outputs/*.html"))
    assert pages  # 検証が空振りしない
    for path in pages:
        text = path.read_text(encoding="utf-8")
        if "Plotly.newPlot" in text:  # DRAgoWing の研究用レポート（取得した原本の HTML は対象外）
            assert f"font:16px/1.65 {TIGHT}" in text and f"family:'{FONT}'" in text, path
            assert "system-ui" not in text, path
