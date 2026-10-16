"""Config-driven export (Plotly and Mermaid are example configs only)."""

import json
import sys

import pytest

from dragowing.chrome_pipe import find_chrome
from dragowing.export import MERMAID, PLOTLY, export_draw, mermaid_diagram_content, page_html, plotly_figure_content
from dragowing.html_tag_count import count_elements
from dragowing.render import RenderSession, Timeouts


def test_page_html_builds_plotly_and_mermaid_without_browser():
    plotly = page_html(PLOTLY, plotly_figure_content({"data": [], "layout": {"title": {"text": "t"}}}))
    assert "plotly-latest.min.js" in plotly
    assert "Plotly.newPlot" in plotly
    assert count_elements(plotly, ("script", "div")) == {"script": 2, "div": 1}

    mermaid = page_html(MERMAID, mermaid_diagram_content("graph TD\n  A-->B"))
    assert "mermaid.min.js" in mermaid
    assert "graph TD" in mermaid
    assert count_elements(mermaid, ("pre", "script")) == {"pre": 1, "script": 2}


def test_fmt_is_png_or_svg(tmp_path):
    with pytest.raises(ValueError, match="png or svg"):
        export_draw(PLOTLY, plotly_figure_content({"data": []}), tmp_path / "out.gif", "gif")


def _installed_chrome():
    if sys.platform == "win32":
        return None
    try:
        return find_chrome()
    except RuntimeError:
        return None


@pytest.mark.skipif(_installed_chrome() is None, reason="Chrome/Chromium is not available")
def test_export_draw_plotly_three_figures_in_one_session(tmp_path):
    figures = [
        {
            "data": [{"type": "scatter", "x": [1, 2, 3], "y": [index, 1, 4]}],
            "layout": {"width": 320, "height": 240, "title": {"text": "title-%d" % index}},
        }
        for index in range(3)
    ]
    timeouts = Timeouts(launch=45, load=45, ready=45, capture=20)
    with RenderSession(timeouts=timeouts) as session:
        pid = session.browser._proc.pid
        for index, fig in enumerate(figures):
            fmt = "svg" if index == 2 else "png"
            path = tmp_path / ("fig-%s.%s" % (index, fmt))
            export_draw(
                PLOTLY,
                plotly_figure_content(fig),
                path,
                fmt,
                session=session,
                scale=1.0,
            )
            assert session.browser._proc.pid == pid
            if fmt == "svg":
                text = path.read_text(encoding="utf-8")
                assert "<svg" in text and "scatterlayer" in text
            else:
                assert path.stat().st_size > 100


@pytest.mark.skipif(_installed_chrome() is None, reason="Chrome/Chromium is not available")
def test_export_draw_mermaid_svg_contains_labels(tmp_path):
    out = tmp_path / "flow.svg"
    export_draw(
        MERMAID,
        mermaid_diagram_content("graph TD\n  Alpha-->Beta"),
        out,
        "svg",
        timeouts=Timeouts(launch=45, load=45, ready=60, capture=20),
    )
    text = out.read_text(encoding="utf-8")
    assert "Alpha" in text or "Beta" in text
    assert "<svg" in text
