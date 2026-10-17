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
    with pytest.raises(RuntimeError, match="not executable"):
        find_chrome(str(exe))
    exe.chmod(0o755)
    assert find_chrome(str(exe)) == str(exe)


def test_render_static_svg_text_not_png_bytes(tmp_path, chrome_executable):
    html = '<!doctype html><svg><text id="w">page-weight-42</text></svg>'
    svg = render_html(
        html,
        "svg",
        chrome=chrome_executable,
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
        chrome=chrome_executable,
        ready_selector="svg",
        capture_selector="svg",
        timeouts=Timeouts(launch=30, load=20, ready=10, capture=10),
    )
    assert png[:8] != svg[:8]


def test_render_session_reuses_one_browser(chrome_executable):
    html = '<!doctype html><svg><text>reuse-%d</text></svg>'
    with RenderSession(chrome=chrome_executable, timeouts=Timeouts(launch=30, load=20, ready=10, capture=10)) as session:
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


@pytest.mark.parametrize("failure", [None, "attach", "capture", "navigate"])
def test_each_target_is_closed_on_success_and_failures(tmp_path, failure):
    from dragowing import render
    class Browser:
        _proc = object()
        def __init__(self):
            self.calls = []
        def call(self, method, params=None, **kwargs):
            self.calls.append(method)
            if method == "Target.createTarget":
                return {"targetId": "target"}
            if method == "Target.attachToTarget":
                if failure == "attach":
                    raise RuntimeError("attach failed")
                return {"sessionId": "session"}
            if method == "Page.navigate" and failure == "navigate":
                return {"errorText": "navigation failed"}
            if method == "Target.closeTarget":
                assert params == {"targetId": "target"}
                return {"success": True}
            return {}
        def evaluate(self, *args, **kwargs):
            if failure == "capture":
                raise RuntimeError("capture failed")
            return "<svg><text>complete</text></svg>"
        def wait_event(self, *args, **kwargs):
            return {}
        def forget_session(self, *args):
            pass
    session = render.RenderSession()
    session.browser = Browser()
    session._workdir = str(tmp_path)
    if failure:
        with pytest.raises(RuntimeError, match="failed"):
            session.render("<svg/>", "svg")
    else:
        assert b"complete" in session.render("<svg/>", "svg")
    assert session.browser.calls.count("Target.closeTarget") == 1


@pytest.mark.parametrize("ready", [{"ready_selector": "#never"}, {"ready_expression": "new Promise(()=>{})"}])
def test_ready_timeout_releases_target_and_session_is_reusable(chrome_executable, ready):
    with RenderSession(chrome=chrome_executable, offline=True, timeouts=Timeouts(ready=0.1)) as session:
        def pages():
            return {t["targetId"] for t in session.browser.call("Target.getTargets")["targetInfos"] if t["type"] == "page"}
        baseline = pages()
        with pytest.raises((RuntimeError, TimeoutError), match="timeout"):
            session.render("<!doctype html><div>not ready</div>", "svg", **ready)
        assert pages() == baseline
        assert b"recovered" in session.render("<svg><text>recovered</text></svg>", "svg")


def test_browser_termination_during_session_cleans_all_resources(chrome_executable):
    session = RenderSession(chrome=chrome_executable, offline=True)
    with session:
        workdir = Path(session._workdir)
        browserdir = Path(session.browser._tmp)
        proc = session.browser._proc
        proc.kill()
        proc.wait()
        with pytest.raises(RuntimeError, match="closed the pipe"):
            session.render("<svg/>", "svg")
    assert not workdir.exists() and not browserdir.exists()
    assert session.browser._proc is session.browser._reader is None
