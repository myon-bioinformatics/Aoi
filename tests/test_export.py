"""Framing and data URLs always run. Chrome runs only when it is installed."""

import ast
import base64
import sys
from pathlib import Path
from urllib.parse import quote

import pytest

from dragowing._chrome_pipe import find_chrome, frame_message, pop_message
from dragowing.export import Session, decode_data_url, export_figure

_PIPE = Path(__file__).resolve().parents[1] / "_chrome_pipe.py"


def test_frame_message_is_nul_delimited_and_pop_keeps_a_partial_tail():
    framed = frame_message({"id": 1, "method": "Browser.close", "params": {}})
    assert framed.endswith(b"\0")
    assert b"\0" not in framed[:-1]
    pending, rest = pop_message(b'{"id":')
    assert pending is None and rest == b'{"id":'
    first, rest = pop_message(framed + b'{"id":2}\0{"id":')
    assert first == {"id": 1, "method": "Browser.close", "params": {}}
    second, rest = pop_message(rest)
    assert second == {"id": 2} and rest == b'{"id":'
    pending, rest = pop_message(rest)
    assert pending is None and rest == b'{"id":'


def test_decode_data_url_base64_and_percent_encoding():
    png = decode_data_url("data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n").decode())
    assert png == b"\x89PNG\r\n"
    svg = decode_data_url("data:image/svg+xml," + quote("<svg>a b</svg>"))
    assert svg == b"<svg>a b</svg>"
    assert decode_data_url("data:image/svg+xml,%E2%9C%93") == "✓".encode()


def test_decode_data_url_rejects_non_data_urls():
    with pytest.raises(ValueError):
        decode_data_url("https://example.test/a.png")


def test_chrome_pipe_imports_nothing_from_this_package():
    tree = ast.parse(_PIPE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0
            assert not (node.module or "").startswith("dragowing")
        elif isinstance(node, ast.Import):
            assert all(not alias.name.startswith("dragowing") for alias in node.names)


def test_missing_chrome_and_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    with pytest.raises(RuntimeError, match="not supported"):
        find_chrome("/usr/bin/google-chrome")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("CHROME", raising=False)
    monkeypatch.delenv("CHROMIUM", raising=False)
    monkeypatch.setattr("dragowing._chrome_pipe.shutil.which", lambda _name: None)
    with pytest.raises(RuntimeError, match="not found on PATH"):
        find_chrome()
    monkeypatch.setenv("CHROME", str(tmp_path / "missing-chrome"))
    with pytest.raises(RuntimeError, match="not found"):
        find_chrome()
    exe = tmp_path / "chrome"
    exe.write_text("#!/bin/sh\n", encoding="utf-8")
    assert find_chrome(str(exe)) == str(exe)


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
def test_one_session_exports_three_figures(tmp_path):
    figures = [
        {
            "data": [{"type": "scatter", "x": [1, 2, 3], "y": [index, 1, 4]}],
            "layout": {"width": 320, "height": 240, "title": {"text": str(index)}},
        }
        for index in range(3)
    ]
    with Session(timeout=60) as session:
        pid = session.browser._proc.pid
        blobs = []
        for index, fig in enumerate(figures):
            fmt = "svg" if index == 2 else "png"
            path = tmp_path / ("fig-%s.%s" % (index, fmt))
            blobs.append(export_figure(fig, path, fmt, session=session, width=320, height=240))
            assert path.read_bytes() == blobs[-1]
            assert session.browser._proc.pid == pid
            assert session.browser._proc.poll() is None
    assert blobs[0].startswith(b"\x89PNG")
    assert blobs[1].startswith(b"\x89PNG")
    assert blobs[0] != blobs[1]
    assert b"<svg" in blobs[2]
