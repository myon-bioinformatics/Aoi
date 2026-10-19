"""Plotly.js for DRAgoWing HTML and Chrome export (jsDelivr, no SRI/hash pin).

Figure JSON/initialization remains DRAgoWing-owned. web-ui alignment is tracked
separately; this module uses the versionless jsDelivr dist URL directly.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from html import escape
PLOTLY_JS_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-dist-min/plotly.min.js"
PLOTLY_JS_MAX_BYTES = 8 * 1024 * 1024
_PLOTLY_JS_CACHE: bytes | None = None


def reset_plotly_js_cache() -> None:
    """Clear the in-process embed cache (tests only)."""
    global _PLOTLY_JS_CACHE
    _PLOTLY_JS_CACHE = None


def _classic_script(source: str) -> str:
    if re.search(r"</script(?=[\s/>])", source, re.IGNORECASE):
        raise ValueError("script contains HTML script end tag")
    return "<script>%s</script>" % source


def fetch_plotly_js() -> str:
    """Fetch Plotly.js bytes from jsDelivr and cache successful responses only."""
    global _PLOTLY_JS_CACHE
    if _PLOTLY_JS_CACHE is None:
        request = urllib.request.Request(
            PLOTLY_JS_CDN,
            headers={"User-Agent": "dragowing/plotly_cdn (Plotly embed)"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60.0) as response:
                status = getattr(response, "status", None)
                if status is None:
                    getcode = getattr(response, "getcode", None)
                    status = getcode() if getcode is not None else 200
                if status != 200:
                    raise RuntimeError(
                        "Plotly.js CDN returned HTTP %s for %s" % (status, PLOTLY_JS_CDN)
                    )
                raw = response.read(PLOTLY_JS_MAX_BYTES + 1)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                "Plotly.js CDN returned HTTP %s for %s" % (exc.code, PLOTLY_JS_CDN)
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError("Plotly.js request failed: %s" % exc.reason) from exc
        except TimeoutError as exc:
            raise RuntimeError("Plotly.js request failed: timed out") from exc
        if not raw:
            raise RuntimeError("Plotly.js CDN returned an empty body")
        if len(raw) > PLOTLY_JS_MAX_BYTES:
            raise RuntimeError("Plotly.js exceeds %s byte limit" % PLOTLY_JS_MAX_BYTES)
        _classic_script(raw.decode("utf-8"))
        _PLOTLY_JS_CACHE = raw
    return _PLOTLY_JS_CACHE.decode("utf-8")


def plotly_script_tags(*, embed: bool) -> str:
    config = "<script>window.PlotlyConfig = {MathJaxConfig: 'local'};</script>\n"
    if embed:
        return config + _classic_script(fetch_plotly_js())
    return (
        config
        + '<script src="%s" crossorigin="anonymous"></script>' % escape(PLOTLY_JS_CDN, quote=True)
    )
