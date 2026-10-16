"""Render an HTML file or string to PNG or SVG via headless Chrome."""

from __future__ import annotations

import base64
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .chrome_pipe import Chrome


@dataclass(frozen=True)
class Timeouts:
    launch: float = 30.0
    load: float = 30.0
    ready: float = 30.0
    capture: float = 15.0


def _page_url(source: str | os.PathLike, workdir: str) -> str:
    path = os.fspath(source)
    if os.path.isfile(path):
        return "file://" + os.path.abspath(path)
    text = source if isinstance(source, str) else Path(source).read_text(encoding="utf-8")
    html = os.path.join(workdir, "page.html")
    with open(html, "w", encoding="utf-8") as handle:
        handle.write(text)
    return "file://" + os.path.abspath(html)


def _wait_ready(browser: Chrome, session: str, timeouts: Timeouts,
                ready_expression: str | None, ready_selector: str | None) -> None:
    if ready_expression:
        browser.evaluate(ready_expression, session, timeout=timeouts.ready)
        return
    if ready_selector:
        limit = max(1, int(timeouts.ready * 1000))
        expr = (
            "new Promise(function(ok,bad){var t0=Date.now();(function tick(){"
            "if(document.querySelector(%s))ok(true);"
            "else if(Date.now()-t0>%d)bad(new Error('ready timeout'));"
            "else setTimeout(tick,20)})()})"
        ) % (json.dumps(ready_selector), limit)
        browser.evaluate(expr, session, timeout=timeouts.ready)
        return
    browser.evaluate("true", session, await_promise=False, timeout=timeouts.ready)


def _capture_png(browser: Chrome, session: str, timeouts: Timeouts,
                 capture_selector: str | None, scale: float) -> bytes:
    params: dict = {"format": "png", "fromSurface": True}
    if capture_selector:
        clip = browser.evaluate(
            "(()=>{const el=document.querySelector(%s);if(!el)throw new Error('capture selector missing');"
            "const r=el.getBoundingClientRect();"
            "return {x:r.x,y:r.y,width:r.width,height:r.height,scale:%s};})()"
            % (json.dumps(capture_selector), json.dumps(scale)),
            session,
            timeout=timeouts.capture,
        )
        if not isinstance(clip, dict):
            raise RuntimeError("capture clip was not an object")
        params["clip"] = clip
    result = browser.call("Page.captureScreenshot", params, session=session, timeout=timeouts.capture)
    data = result.get("data")
    if not isinstance(data, str):
        raise RuntimeError("Page.captureScreenshot returned no data")
    return base64.b64decode(data)


def _capture_svg(browser: Chrome, session: str, timeouts: Timeouts, capture_selector: str | None) -> bytes:
    selector = capture_selector or "svg"
    markup = browser.evaluate(
        "(()=>{const el=document.querySelector(%s);if(!el)throw new Error('svg not found');"
        "return el.outerHTML;})()" % json.dumps(selector),
        session,
        timeout=timeouts.capture,
    )
    if not isinstance(markup, str) or "<svg" not in markup:
        raise RuntimeError("svg outerHTML was empty")
    return markup.encode("utf-8")


class RenderSession:
    """One Chrome process. Each render opens a fresh page in the same browser."""

    def __init__(self, chrome: str | None = None, timeouts: Timeouts | None = None):
        self.chrome = chrome
        self.timeouts = timeouts or Timeouts()
        self.browser = Chrome(chrome=chrome, timeout=self.timeouts.launch)
        self._workdir: str | None = None

    def __enter__(self) -> RenderSession:
        self.start()
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def start(self) -> None:
        if self.browser._proc is not None:
            return
        self._workdir = tempfile.mkdtemp(prefix="dragowing-render-")
        self.browser.timeout = self.timeouts.launch
        self.browser.start()

    def render(self, source: str | os.PathLike, fmt: str = "png", *,
               ready_expression: str | None = None, ready_selector: str | None = None,
               capture_selector: str | None = None, scale: float = 1.0) -> bytes:
        if fmt not in ("png", "svg"):
            raise ValueError("fmt must be png or svg")
        if self.browser._proc is None:
            self.start()
        url = _page_url(source, self._workdir)
        target = self.browser.call(
            "Target.createTarget", {"url": "about:blank"}, timeout=self.timeouts.launch,
        )["targetId"]
        session = self.browser.call(
            "Target.attachToTarget", {"targetId": target, "flatten": True}, timeout=self.timeouts.launch,
        )["sessionId"]
        self.browser.call("Page.enable", session=session, timeout=self.timeouts.load)
        self.browser.call("Page.navigate", {"url": url}, session=session, timeout=self.timeouts.load)
        self.browser.wait_event("Page.loadEventFired", session=session, timeout=self.timeouts.load)
        _wait_ready(self.browser, session, self.timeouts, ready_expression, ready_selector)
        if fmt == "png":
            return _capture_png(self.browser, session, self.timeouts, capture_selector, scale)
        return _capture_svg(self.browser, session, self.timeouts, capture_selector)

    def close(self) -> None:
        self.browser.close()
        if self._workdir:
            shutil.rmtree(self._workdir, ignore_errors=True)
            self._workdir = None


def render_html(source: str | os.PathLike, fmt: str = "png", *, chrome: str | None = None,
                timeouts: Timeouts | None = None, session: RenderSession | None = None, **kwargs) -> bytes:
    """Render HTML to bytes. Pass ``session`` to reuse one browser."""
    own = session is None
    if own:
        session = RenderSession(chrome=chrome, timeouts=timeouts)
    try:
        return session.render(source, fmt, **kwargs)
    finally:
        if own:
            session.close()
