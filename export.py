"""Thin adapters: Plotly figures and Mermaid diagrams on top of render.RenderSession."""

from __future__ import annotations

import html as html_lib
import json
import os
import shutil
import tempfile
from base64 import b64decode
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote_to_bytes
from urllib.request import urlopen

from .chrome_pipe import Chrome
from .render import RenderSession, Timeouts

PLOTLY_JS_NAME = "plotly.min.js"
MERMAID_VERSION = "10.9.3"
MERMAID_JS_URL = "https://cdn.jsdelivr.net/npm/mermaid@%s/dist/mermaid.min.js" % MERMAID_VERSION
MERMAID_SHA256 = "5a8ec91820bd55afef049068489369910e5d6ce70c8103952f27e29d3e76e8bc"


def plotlyjs_path() -> Path:
    import plotly

    path = Path(plotly.__file__).resolve().parent / "package_data" / PLOTLY_JS_NAME
    if not path.is_file():
        raise FileNotFoundError("plotly.min.js is missing: %s" % path)
    return path


def decode_data_url(url: str) -> bytes:
    head, sep, data = url.partition(",")
    if not sep or not head.startswith("data:"):
        raise ValueError("not a data URL")
    if ";base64" in head:
        return b64decode(data, validate=True)
    return unquote_to_bytes(data)


def _plotly_ready_js(timeout: Timeouts) -> str:
    limit = max(1, int(timeout.ready * 1000) - 500)
    return (
        "new Promise(function(ok,bad){var t0=Date.now();(function tick(){"
        "if(window.Plotly)ok(true);else if(Date.now()-t0>%d)bad(new Error('plotly.js did not load'));"
        "else setTimeout(tick,20)})()})" % limit
    )


def _materialize_mermaid_js(dest: Path) -> None:
    data = urlopen(MERMAID_JS_URL, timeout=60).read()
    digest = sha256(data).hexdigest()
    if digest != MERMAID_SHA256:
        raise RuntimeError("mermaid.js sha256 mismatch (got %s)" % digest)
    dest.write_bytes(data)


def mermaid_page(source: str, workdir: str, js_uri: str | None = None) -> str:
    if js_uri is None:
        js_path = os.path.join(workdir, "mermaid.min.js")
        _materialize_mermaid_js(Path(js_path))
        js_uri = "file://" + js_path
    diagram = html_lib.escape(source.strip())
    return (
        "<!doctype html><meta charset=utf-8>"
        '<pre class="mermaid">%s</pre>'
        "<script src=%s></script>"
        "<script>mermaid.initialize({startOnLoad:true});</script>"
    ) % (diagram, json.dumps(js_uri))


class Session:
    """One Chrome with Plotly loaded from the installed package bundle."""

    def __init__(self, chrome: str | None = None, timeouts: Timeouts | None = None):
        self.timeouts = timeouts or Timeouts()
        self.browser = Chrome(chrome=chrome, timeout=self.timeouts.launch)
        self._sid: str | None = None
        self._dir: str | None = None

    def __enter__(self) -> Session:
        self.start()
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def start(self) -> None:
        if self._sid is not None:
            return
        self._dir = tempfile.mkdtemp(prefix="dragowing-plotly-")
        js = os.path.join(self._dir, PLOTLY_JS_NAME)
        shutil.copyfile(plotlyjs_path(), js)
        html = os.path.join(self._dir, "page.html")
        with open(html, "w", encoding="utf-8") as handle:
            handle.write("<!doctype html><meta charset=utf-8><script src=%s></script>" % json.dumps("file://" + js))
        try:
            self.browser.timeout = self.timeouts.launch
            self.browser.start()
            target = self.browser.call("Target.createTarget", {"url": "about:blank"}, timeout=self.timeouts.launch)["targetId"]
            self._sid = self.browser.call(
                "Target.attachToTarget", {"targetId": target, "flatten": True}, timeout=self.timeouts.launch,
            )["sessionId"]
            self.browser.call("Page.enable", session=self._sid, timeout=self.timeouts.load)
            self.browser.call("Page.navigate", {"url": "file://" + html}, session=self._sid, timeout=self.timeouts.load)
            self.browser.wait_event("Page.loadEventFired", session=self._sid, timeout=self.timeouts.load)
            self.browser.evaluate(_plotly_ready_js(self.timeouts), self._sid, timeout=self.timeouts.ready)
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
        value = self.browser.evaluate(expression, self._sid, timeout=self.timeouts.capture)
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
                  chrome: str | None = None, timeouts: Timeouts | None = None,
                  width: int = 700, height: int = 500, scale: float = 1) -> bytes:
    own = session is None
    if own:
        session = Session(chrome=chrome, timeouts=timeouts)
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


def export_mermaid(source: str, path, fmt: str = "svg", *, session: RenderSession | None = None,
                   chrome: str | None = None, timeouts: Timeouts | None = None) -> bytes:
    own = session is None
    if own:
        session = RenderSession(chrome=chrome, timeouts=timeouts)
    try:
        if session.browser._proc is None:
            session.start()
        html = mermaid_page(source, session._workdir)
        data = session.render(
            html,
            fmt,
            ready_selector=".mermaid svg",
            capture_selector=".mermaid svg",
        )
        path = os.fspath(path)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        return data
    finally:
        if own:
            session.close()
