"""DRAgoWing adapter to the locked web-ui Plotly distribution contract.

Figure JSON/initialization remains DRAgoWing-owned; URL, SRI and bounded bytes
verification come from one vendored upstream module, recorded in vendor.lock.json.
"""
from __future__ import annotations

from vendor import web_ui

PLOTLY_JS_CDN = web_ui.PLOTLY_JS_URL
_PLOTLY_JS_CACHE: bytes | None = None


def reset_plotly_js_cache() -> None:
    """Clear the in-process embed cache (tests only)."""
    global _PLOTLY_JS_CACHE
    _PLOTLY_JS_CACHE = None


def fetch_plotly_js() -> str:
    """Fetch fixed, verified bytes through web-ui and cache successful bytes only."""
    global _PLOTLY_JS_CACHE
    if _PLOTLY_JS_CACHE is None:
        raw = web_ui.fetch_plotly_js()
        body = raw.decode("utf-8")
        # A trusted JS bundle still must not terminate an HTML raw-text element.
        web_ui.classic_script(body)
        _PLOTLY_JS_CACHE = raw
    return _PLOTLY_JS_CACHE.decode("utf-8")


def plotly_script_tags(*, embed: bool) -> str:
    config = "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
    if embed:
        return config + web_ui.classic_script(fetch_plotly_js())
    return config + web_ui.remote_script_tag(web_ui.remote_scripts("plotly.js")[0])
