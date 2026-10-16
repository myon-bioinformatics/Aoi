"""Plotly and Mermaid adapters."""

import base64
import json
import sys
from urllib.parse import quote

import pytest

from dragowing.chrome_pipe import find_chrome
from dragowing.export import Session, decode_data_url, export_figure, export_mermaid, plotlyjs_path
from dragowing.render import Timeouts


def test_decode_data_url_base64_and_percent_encoding():
    png = decode_data_url("data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n").decode())
    assert png == b"\x89PNG\r\n"
    svg = decode_data_url("data:image/svg+xml," + quote("<svg>a b</svg>"))
    assert svg == b"<svg>a b</svg>"


def test_plotlyjs_path_is_bundled_file():
    path = plotlyjs_path()
    assert path.name == "plotly.min.js"
    assert path.is_file()


def test_fmt_is_png_or_svg(tmp_path):
    with pytest.raises(ValueError, match="png or svg"):
        export_figure({"data": []}, tmp_path / "out.gif", "gif")


def _installed_chrome():
    if sys.platform == "win32":
        return None
    try:
        return find_chrome()
    except RuntimeError:
        return None


@pytest.mark.skipif(_installed_chrome() is None, reason="Chrome/Chromium is not available")
def test_plotly_session_exports_three_figures_by_svg_text(tmp_path):
    figures = [
        {
            "data": [{"type": "scatter", "x": [1, 2, 3], "y": [index, 1, 4]}],
            "layout": {"width": 320, "height": 240, "title": {"text": "title-%d" % index}},
        }
        for index in range(3)
    ]
    with Session(timeouts=Timeouts(launch=30, load=30, ready=30, capture=30)) as session:
        pid = session.browser._proc.pid
        for index, fig in enumerate(figures):
            fmt = "svg" if index == 2 else "png"
            path = tmp_path / ("fig-%s.%s" % (index, fmt))
            export_figure(fig, path, fmt, session=session, width=320, height=240)
            assert session.browser._proc.pid == pid
            if fmt == "svg":
                text = path.read_text(encoding="utf-8")
                assert "title-%d" % index in text
                assert "<svg" in text
            else:
                assert path.stat().st_size > 100


@pytest.mark.skipif(_installed_chrome() is None, reason="Chrome/Chromium is not available")
def test_mermaid_export_contains_node_labels(tmp_path):
    out = tmp_path / "flow.svg"
    export_mermaid("graph TD\n  Alpha-->Beta", out, "svg", timeouts=Timeouts(launch=30, load=30, ready=45, capture=20))
    text = out.read_text(encoding="utf-8")
    assert "Alpha" in text or "Beta" in text
    assert "<svg" in text
