"""Plotly.js CDN URL and optional embed fetch (stdlib + httpx only).

TODO(myon-bioinformatics/web-ui#59): vendor ``remote_scripts`` / ``plotly_figure`` from web-ui
when PR 59 merges; keep DRAgoWing's JSON-in-``application/json`` figure blocks unless we
align on web-ui's inline initializer shape.
"""
from __future__ import annotations

import html

PLOTLY_JS_CDN = "https://cdn.plot.ly/plotly-latest.min.js"

_PLOTLY_JS_CACHE: str | None = None


def fetch_plotly_js() -> str:
    """Download unpinned plotly-latest for ``--embed`` (cached in-process)."""
    global _PLOTLY_JS_CACHE
    if _PLOTLY_JS_CACHE is not None:
        return _PLOTLY_JS_CACHE
    import httpx

    response = httpx.get(PLOTLY_JS_CDN, follow_redirects=True, timeout=60.0)
    response.raise_for_status()
    body = response.text
    if not body.strip():
        raise RuntimeError("empty Plotly.js response from CDN")
    _PLOTLY_JS_CACHE = body
    return body


def plotly_script_tags(*, embed: bool) -> str:
    config = "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
    if embed:
        return config + f"<script>{fetch_plotly_js()}</script>"
    src = html.escape(PLOTLY_JS_CDN, quote=True)
    return config + f'<script charset="utf-8" src="{src}"></script>'
