"""Export a JS-drawn page from headless Chrome using a small library config."""

from __future__ import annotations

import html as html_lib
import json
import os
from dataclasses import dataclass

from .render import RenderSession, Timeouts


@dataclass(frozen=True)
class DrawConfig:
    """How to load a drawing library and where to read the result from the DOM."""

    script_urls: tuple[str, ...]
    template: str
    ready_selector: str | None = None
    ready_expression: str | None = None
    capture_selector: str | None = None

    def page(self, content: str) -> str:
        scripts = "".join('<script src=%s></script>' % json.dumps(url) for url in self.script_urls)
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
    if own:
        session = RenderSession(chrome=chrome, timeouts=timeouts)
    try:
        data = session.render(
            page_html(config, content),
            fmt,
            ready_selector=config.ready_selector,
            ready_expression=config.ready_expression,
            capture_selector=config.capture_selector,
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

PLOTLY = DrawConfig(
    script_urls=("https://cdn.plot.ly/plotly-latest.min.js",),
    template="<!doctype html><meta charset=utf-8>{{scripts}}<div id=g></div>{{content}}",
    ready_selector="svg.main-svg",
    capture_selector="svg.main-svg",
)


def plotly_figure_content(fig_json) -> str:
    spec = fig_json if isinstance(fig_json, str) else json.dumps(fig_json, separators=(",", ":"))
    json.loads(spec)
    return "<script>Plotly.newPlot('g',%s);</script>" % spec


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
