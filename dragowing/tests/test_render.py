"""Generic render: pure helpers and Chrome when available."""

import ast
import sys
from pathlib import Path

import pytest

from dragowing.chrome_pipe import find_chrome, frame_message, pop_message
from dragowing.export import MERMAID, mermaid_diagram_content, page_html
from dragowing.html_tag_count import count_elements
from dragowing.render import RenderSession, Timeouts, render_html

_PIPE = Path(__file__).resolve().parents[1] / "chrome_pipe.py"


def test_frame_message_and_pop_message():
    framed = frame_message({"id": 1, "method": "Browser.close", "params": {}})
    assert framed.endswith(b"\0")
    pending, rest = pop_message(b'{"id":')
    assert pending is None and rest == b'{"id":'
    first, rest = pop_message(framed + b'{"id":2}\0')
    assert first["method"] == "Browser.close"
    assert pop_message(rest)[0] == {"id": 2}


def test_chrome_pipe_has_no_dragowing_imports():
    tree = ast.parse(_PIPE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert not (node.module or "").startswith("dragowing")
        elif isinstance(node, ast.Import):
            assert all(not alias.name.startswith("dragowing") for alias in node.names)


def test_mermaid_example_page_counts_tags_without_browser():
    html = page_html(MERMAID, mermaid_diagram_content("graph TD\n  A-->B"))
    counts = count_elements(html, ("pre", "script"))
    assert counts == {"pre": 1, "script": 2}
    assert "graph TD" in html


def test_missing_chrome_and_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    with pytest.raises(RuntimeError, match="not supported"):
        find_chrome("/usr/bin/google-chrome")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("CHROME", raising=False)
    monkeypatch.delenv("CHROMIUM", raising=False)
    monkeypatch.setattr("dragowing.chrome_pipe.shutil.which", lambda _name: None)
    with pytest.raises(RuntimeError, match="not found on PATH"):
        find_chrome()
    monkeypatch.setenv("CHROME", str(tmp_path / "missing-chrome"))
    with pytest.raises(RuntimeError, match="not found"):
        find_chrome()
    exe = tmp_path / "chrome"
    exe.write_text("#!/bin/sh\n", encoding="utf-8")
    assert find_chrome(str(exe)) == str(exe)


def _installed_chrome():
    if sys.platform == "win32":
        return None
    try:
        return find_chrome()
    except RuntimeError:
        return None


@pytest.mark.skipif(_installed_chrome() is None, reason="Chrome/Chromium is not available")
def test_render_static_svg_text_not_png_bytes(tmp_path):
    html = '<!doctype html><svg><text id="w">page-weight-42</text></svg>'
    svg = render_html(
        html,
        "svg",
        ready_selector="svg",
        capture_selector="svg",
        timeouts=Timeouts(launch=30, load=20, ready=10, capture=10),
    )
    text = svg.decode("utf-8")
    assert "page-weight-42" in text
    assert count_elements(text, ("text",))["text"] == 1
    png = render_html(
        html,
        "png",
        ready_selector="svg",
        capture_selector="svg",
        timeouts=Timeouts(launch=30, load=20, ready=10, capture=10),
    )
    assert png[:8] != svg[:8]


@pytest.mark.skipif(_installed_chrome() is None, reason="Chrome/Chromium is not available")
def test_render_session_reuses_one_browser():
    html = '<!doctype html><svg><text>reuse-%d</text></svg>'
    with RenderSession(timeouts=Timeouts(launch=30, load=20, ready=10, capture=10)) as session:
        pid = session.browser._proc.pid
        for index in range(3):
            svg = session.render(
                html % index,
                "svg",
                ready_selector="svg",
                capture_selector="svg",
            ).decode("utf-8")
            assert ("reuse-%d" % index) in svg
            assert session.browser._proc.pid == pid
