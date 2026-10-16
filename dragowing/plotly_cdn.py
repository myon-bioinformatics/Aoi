"""Plotly.js CDN URL and optional embed fetch (stdlib only).

TODO(myon-bioinformatics/web-ui#59): vendor ``remote_scripts`` / ``plotly_figure`` from web-ui
when PR 59 merges; keep DRAgoWing's JSON-in-``application/json`` figure blocks unless we
align on web-ui's inline initializer shape.
"""
from __future__ import annotations

import html
import urllib.error
import urllib.request

PLOTLY_JS_CDN = "https://cdn.plot.ly/plotly-latest.min.js"
_FETCH_TIMEOUT_SECONDS = 60.0

_PLOTLY_JS_CACHE: str | None = None


def reset_plotly_js_cache() -> None:
    """Clear the in-process embed cache (tests only)."""
    global _PLOTLY_JS_CACHE
    _PLOTLY_JS_CACHE = None


def fetch_plotly_js() -> str:
    """Download unpinned plotly-latest for ``--embed`` (cached in-process)."""
    global _PLOTLY_JS_CACHE
    if _PLOTLY_JS_CACHE is not None:
        return _PLOTLY_JS_CACHE
    request = urllib.request.Request(
        PLOTLY_JS_CDN,
        headers={"User-Agent": "DRAgoWing/1.0 (embed fetch)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT_SECONDS) as response:
            status = response.status if hasattr(response, "status") else response.getcode()
            if status != 200:
                raise RuntimeError(f"Plotly.js CDN returned HTTP {status} for {PLOTLY_JS_CDN}")
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"Plotly.js CDN request failed: HTTP {exc.code} {exc.reason} ({PLOTLY_JS_CDN})"
        ) from exc
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, TimeoutError):
            raise RuntimeError(
                f"Plotly.js CDN request timed out after {_FETCH_TIMEOUT_SECONDS}s ({PLOTLY_JS_CDN})"
            ) from exc
        raise RuntimeError(f"Plotly.js CDN request failed: {reason} ({PLOTLY_JS_CDN})") from exc
    except TimeoutError as exc:
        raise RuntimeError(
            f"Plotly.js CDN request timed out after {_FETCH_TIMEOUT_SECONDS}s ({PLOTLY_JS_CDN})"
        ) from exc
    body = raw.decode("utf-8")
    if not body.strip():
        raise RuntimeError(f"Plotly.js CDN returned an empty body ({PLOTLY_JS_CDN})")
    _PLOTLY_JS_CACHE = body
    return body


def plotly_script_tags(*, embed: bool) -> str:
    config = "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
    if embed:
        return config + f"<script>{fetch_plotly_js()}</script>"
    src = html.escape(PLOTLY_JS_CDN, quote=True)
    return config + f'<script charset="utf-8" src="{src}"></script>'
