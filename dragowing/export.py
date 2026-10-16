"""Optional PNG/SVG export for a Plotly figure. HTML stays the default output.

The browser is dragowing._chrome_pipe. This module only loads the pinned
plotly.js and calls Plotly.toImage.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from base64 import b64decode
from urllib.parse import unquote_to_bytes

from ._chrome_pipe import Chrome

# plotly.py 7.1.0 bundles plotly.js 4.1.1.
PLOTLY_JS = "https://cdn.plot.ly/plotly-4.1.1.min.js"
_PAGE = "<!doctype html><meta charset=utf-8><script src=%s></script>"
_WAIT = (
    "new Promise(function(ok,bad){var t0=Date.now();(function tick(){"
    "if(window.Plotly)ok(true);else if(Date.now()-t0>%d)bad(new Error('plotly.js did not load'));"
    "else setTimeout(tick,20)})()})"
)


def decode_data_url(url: str) -> bytes:
    head, sep, data = url.partition(",")
    if not sep or not head.startswith("data:"):
        raise ValueError("not a data URL")
    if ";base64" in head:
        return b64decode(data, validate=True)
    return unquote_to_bytes(data)


class Session:
    """One Chrome. export() reuses it for every figure."""

    def __init__(self, chrome: str | None = None, timeout: float = 60, plotly_src: str = PLOTLY_JS):
        self.browser = Chrome(chrome=chrome, timeout=timeout)
        self.plotly_src = plotly_src
        self._sid = None
        self._dir = None

    def __enter__(self) -> Session:
        self.start()
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def start(self) -> None:
        if self._sid is not None:
            return
        self._dir = tempfile.mkdtemp(prefix="dragowing-plot-")
        html = os.path.join(self._dir, "page.html")
        try:
            with open(html, "w", encoding="utf-8") as handle:
                handle.write(_PAGE % json.dumps(self.plotly_src))
            self._sid = self.browser.open("file://" + html)
            limit = max(1, int(self.browser.timeout * 1000) - 500)
            self.browser.evaluate(_WAIT % limit, self._sid)
        except Exception:
            self.close()
            raise

    def export(self, fig_json, fmt: str = "png", width: int = 700, height: int = 500, scale: float = 1) -> bytes:
        if fmt not in ("png", "svg"):
            raise ValueError("fmt must be png or svg")
        if self._sid is None:
            self.start()
        spec = fig_json if isinstance(fig_json, str) else json.dumps(fig_json, separators=(",", ":"))
        json.loads(spec)
        expression = "Plotly.toImage(JSON.parse(%s),{format:%s,width:%s,height:%s,scale:%s})" % (
            json.dumps(spec), json.dumps(fmt), json.dumps(width), json.dumps(height), json.dumps(scale))
        value = self.browser.evaluate(expression, self._sid)
        if not isinstance(value, str):
            raise RuntimeError("Plotly.toImage did not return a data URL")
        return decode_data_url(value)

    def close(self) -> None:
        self.browser.close()
        if self._dir:
            shutil.rmtree(self._dir, ignore_errors=True)
            self._dir = None
        self._sid = None


def export_figure(fig_json, path, fmt: str = "png", *, session: Session | None = None,
                  chrome: str | None = None, timeout: float = 60, width: int = 700,
                  height: int = 500, scale: float = 1) -> bytes:
    """Write fig_json to path as png or svg. Pass session to reuse one browser."""
    own = session is None
    if own:
        session = Session(chrome=chrome, timeout=timeout)
    try:
        data = session.export(fig_json, fmt=fmt, width=width, height=height, scale=scale)
        path = os.fspath(path)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        return data
    finally:
        if own:
            session.close()
