"""Export a JS-drawn page from headless Chrome using a small library config."""

from __future__ import annotations

import html as html_lib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .plotly_cdn import fetch_plotly_js
from .render import RenderSession, Timeouts


@dataclass(frozen=True)
class DrawConfig:
    """How to load a drawing library and where to read the result from the DOM."""

    script_urls: tuple[str, ...]
    template: str
    ready_selector: str | None = None
    ready_expression: str | None = None
    capture_selector: str | None = None
    local_scripts: tuple[Callable[[], Path], ...] = ()
    svg_expression: str | None = None

    def page(self, content: str, directory: Path | None = None) -> str:
        urls = list(self.script_urls)
        for resolve in self.local_scripts:
            source = resolve()
            if directory is not None:
                dest = directory / source.name
                shutil.copyfile(source, dest)
                source = dest
            urls.append(source.resolve().as_uri())
        scripts = "".join('<script src="%s"></script>' % html_lib.escape(url, quote=True) for url in urls)
        return self.template.replace("{{scripts}}", scripts).replace("{{content}}", content)


def page_html(config: DrawConfig, content: str) -> str:
    return config.page(content)


def export_draw(
    config: DrawConfig,
    content: str,
    path,
    fmt: str = "png",
    *,
    session: RenderSession | None = None,
    chrome: str | None = None,
    timeouts: Timeouts | None = None,
    scale: float = 1.0,
) -> bytes:
    """Build a page from ``config`` + ``content``, render in Chrome, write to ``path``."""
    own = session is None
    if fmt not in ("png", "svg"):
        raise ValueError("fmt must be png or svg")
    if own:
        session = RenderSession(chrome=chrome, timeouts=timeouts)
    try:
        # A fresh copy per export cannot retain a bundle from an older installed
        # Plotly. Keep the file alive until Chrome has completed capture.
        with tempfile.TemporaryDirectory(prefix="dragowing-export-") as workdir:
            data = session.render(
                config.page(content, Path(workdir)),
                fmt,
                ready_selector=config.ready_selector,
                ready_expression=config.ready_expression,
                capture_selector=config.capture_selector,
                svg_expression=config.svg_expression,
                scale=scale,
            )
        path = os.fspath(path)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
        return data
    finally:
        if own:
            session.close()


# --- example configs (not library-specific modules) ---

def plotlyjs_bundle_path() -> Path:
    """On-disk Plotly.js for file:// loading (same jsDelivr bundle as HTML)."""
    pinned = os.environ.get("DRAGOWING_PINNED_PLOTLY_JS")
    if pinned:
        path = Path(pinned)
        if path.is_file():
            return path
        raise FileNotFoundError(f"plotly.min.js is missing: {path}")
    cache = Path(tempfile.gettempdir()) / "dragowing-plotly.min.js"
    body = fetch_plotly_js()
    if not cache.is_file() or cache.read_text(encoding="utf-8") != body:
        cache.write_text(body, encoding="utf-8")
    return cache


# Backward-compatible alias for callers that imported the old helper name.
plotlyjs_path = plotlyjs_bundle_path


PLOTLY = DrawConfig(
    script_urls=(),
    local_scripts=(plotlyjs_bundle_path,),
    template=("<!doctype html><meta charset=utf-8><style>body{margin:0}</style>"
              "<script>window.PlotlyConfig={MathJaxConfig:'local'};</script>"
              "{{scripts}}<div id=g></div>{{content}}"),
    ready_expression="window.__dragowing_ready.then(()=>true)",
    capture_selector="#g .svg-container",
    # Plotly has multiple sibling SVG layers. The first svg.main-svg omits
    # titles/legends; toImage serializes the complete figure using local JS.
    svg_expression=("Plotly.toImage(document.getElementById('g'),{format:'svg'})"
                    ".then(url=>decodeURIComponent(url.slice(url.indexOf(',')+1)))"),
)


def plotly_figure_content(fig_json) -> str:
    spec = fig_json if isinstance(fig_json, str) else json.dumps(fig_json, separators=(",", ":"))
    json.loads(spec)
    spec = spec.replace("<", "\\u003c")
    return ("<script>window.__dragowing_ready=(()=>{const spec=%s;"
            "return Plotly.newPlot('g',spec.data,spec.layout,{displayModeBar:false})})();</script>") % spec


MERMAID = DrawConfig(
    script_urls=("https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js",),
    template=(
        "<!doctype html><meta charset=utf-8>"
        '<pre class="mermaid">{{content}}</pre>{{scripts}}'
        "<script>mermaid.initialize({startOnLoad:true});</script>"
    ),
    ready_selector=".mermaid svg",
    capture_selector=".mermaid svg",
)


def mermaid_diagram_content(source: str) -> str:
    return html_lib.escape(source.strip())
