"""Render an HTML file or string to PNG or SVG via headless Chrome."""

from __future__ import annotations

import base64, importlib.util, json, math, os, shutil, sys, tempfile
from functools import lru_cache
from html import escape
from dataclasses import dataclass; from pathlib import Path

from .chrome_pipe import Chrome, _seconds


@dataclass(frozen=True)
class Timeouts:
    launch: float = 30.0
    load: float = 30.0
    ready: float = 30.0
    capture: float = 15.0

    def __post_init__(self):
        for value in (self.launch, self.load, self.ready, self.capture):
            _seconds(value)


def _page_url(source: str | os.PathLike, workdir: str) -> str:
    path = os.fspath(source)
    try:
        if os.path.isfile(path):
            return Path(path).resolve().as_uri()
    except OSError:
        pass  # An HTML string can exceed the filesystem's maximum path length.
    text = source if isinstance(source, str) else Path(source).read_text(encoding="utf-8")
    html = os.path.join(workdir, "page.html")
    with open(html, "w", encoding="utf-8") as handle:
        handle.write(text)
    return Path(html).resolve().as_uri()


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
    params: dict = {"format": "png", "fromSurface": True, "captureBeyondViewport": True}
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


def _capture_svg(browser: Chrome, session: str, timeouts: Timeouts, capture_selector: str | None,
                 svg_expression: str | None = None) -> bytes:
    selector = capture_selector or "svg"
    markup = browser.evaluate(
        svg_expression or "(()=>{const el=document.querySelector(%s);if(!el)throw new Error('svg not found');"
        "return el.outerHTML;})()" % json.dumps(selector),
        session,
        timeout=timeouts.capture,
    )
    if not isinstance(markup, str) or "<svg" not in markup:
        raise RuntimeError("svg outerHTML was empty")
    return markup.encode("utf-8")


class RenderSession:
    """One Chrome process. Each render opens a fresh page in the same browser."""

    def __init__(self, chrome: str | None = None, timeouts: Timeouts | None = None, *, offline: bool = False):
        self.chrome = chrome
        self.timeouts = timeouts or Timeouts()
        self.browser = Chrome(chrome=chrome, timeout=self.timeouts.launch)
        self._workdir: str | None = None
        self.offline = offline

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
        try:
            self.browser.start()
            self.browser.call("Target.setDiscoverTargets", {"discover": True}, timeout=self.timeouts.launch)
        except Exception:
            self.close()
            raise

    def render(self, source: str | os.PathLike, fmt: str = "png", *,
               ready_expression: str | None = None, ready_selector: str | None = None,
               capture_selector: str | None = None, scale: float = 1.0,
               svg_expression: str | None = None) -> bytes:
        if fmt not in ("png", "svg"):
            raise ValueError("fmt must be png or svg")
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("scale must be finite and positive")
        if self.browser._proc is None:
            self.start()
        url = _page_url(source, self._workdir)
        target = self.browser.call(
            "Target.createTarget", {"url": "about:blank"}, timeout=self.timeouts.launch,
        )["targetId"]
        session = None
        try:
            session = self.browser.call(
                "Target.attachToTarget", {"targetId": target, "flatten": True}, timeout=self.timeouts.launch,
            )["sessionId"]
            self.browser.call("Page.enable", session=session, timeout=self.timeouts.load)
            if self.offline:
                self.browser.call("Network.enable", session=session, timeout=self.timeouts.load)
                self.browser.call("Network.emulateNetworkConditions", {
                    "offline": True, "latency": 0, "downloadThroughput": 0, "uploadThroughput": 0,
                }, session=session, timeout=self.timeouts.load)
            result = self.browser.call("Page.navigate", {"url": url}, session=session, timeout=self.timeouts.load)
            if result.get("errorText"):
                raise RuntimeError("Page.navigate: " + result["errorText"])
            self.browser.wait_event("Page.loadEventFired", session=session, timeout=self.timeouts.load)
            _wait_ready(self.browser, session, self.timeouts, ready_expression, ready_selector)
            if fmt == "png":
                return _capture_png(self.browser, session, self.timeouts, capture_selector, scale)
            return _capture_svg(self.browser, session, self.timeouts, capture_selector, svg_expression)
        finally:
            failed = sys.exc_info()[0] is not None
            try:
                result = self.browser.call("Target.closeTarget", {"targetId": target}, timeout=self.timeouts.capture)
                if not result.get("success"):
                    raise RuntimeError("Chrome did not close the render target")
                self.browser.wait_event("Target.targetDestroyed", timeout=self.timeouts.capture,
                                        params={"targetId": target})
            except (OSError, RuntimeError, TimeoutError):
                self.close()
                if not failed:
                    raise
            finally:
                self.browser.forget_session(session, target)

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


# FFSS SVG uses the parent renderer; HTML/PNG and existing report exports keep Chrome.
@lru_cache(maxsize=1)
def plotly_min():
    """vendor/tools/stdlib_min/plotly_min.py（親の stdlib_min を vendor.lock.json で固定）。名前は子どうしでぶつからないように。"""
    path = Path(__file__).resolve().parent / "vendor" / "tools" / "stdlib_min" / "plotly_min.py"
    if not path.is_file():
        raise FileNotFoundError(f"plotly_min が無い: {path}（DRAgoWing のリポジトリから動かす）")
    spec = importlib.util.spec_from_file_location("dragowing_plotly_min", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def figure_svg(spec: dict) -> bytes:
    """SVG for the single-axis FFSS figures covered by parent #307.

    This is separate from RenderSession: existing report exports still use
    Chromium. Reject known unsupported layouts instead of losing their axes.
    """
    layout = spec.get("layout", {})
    if (any(k.startswith(("xaxis", "yaxis")) and k not in ("xaxis", "yaxis") for k in layout)
            or any(t.get("xaxis", "x") != "x" or t.get("yaxis", "y") != "y" for t in spec["data"])
            or layout.get("barmode") in ("stack", "relative")
            or any(t.get("texttemplate") for t in spec["data"] if t.get("type") == "heatmap")):
        raise ValueError("plotly_min at parent #307 does not cover this layout; use the existing Chromium export")
    return plotly_min().Figure(spec).to_image("svg")


def write_ffss(records_path, out_dir, *, svg: bool = True) -> list[Path]:
    """📊 FFSS の記録から ffss.html（plotly.js）と svg/F<NN>_<識別子>.svg（plotly_min、Chrome なし）を書く。"""
    pm = plotly_min()
    from .figures import ffss_figures
    from .records import read_ffss

    figs = ffss_figures(read_ffss(records_path))
    if not figs:
        raise ValueError("FFSS の図にする記録が無い（run E30・E31・E32 か verify の --jsonl）")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blocks = "".join(f'<section><h2>{escape(name)}</h2>{pm.Figure(spec).to_html(include_plotlyjs=False, full_html=False, div_id=name)}</section>'
                     for name, spec in figs.items())
    page = (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>📊 FFSS の図</title>'
            f'<script src="https://cdn.plot.ly/plotly-{pm.PLOTLY_JS}.min.js" charset="utf-8"></script>'
            f'<style>body{{font-family:{pm.FONT};margin:16px}}h2{{font-size:16px}}</style></head>'
            f'<body><h1>📊 FFSS の図（記録から）</h1>{blocks}</body></html>\n')
    written = [out / "ffss.html"]
    written[0].write_text(page, encoding="utf-8")
    if svg:
        (out / "svg").mkdir(exist_ok=True)
        for name, spec in figs.items():
            path = out / "svg" / f"{name}.svg"
            path.write_bytes(figure_svg(spec))
            written.append(path)
    return written
