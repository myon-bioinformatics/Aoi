"""plotly_cdn embed fetch (stdlib urllib; no network in tests)."""
from __future__ import annotations

import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from dragowing.plotly_cdn import PLOTLY_JS_CDN, fetch_plotly_js, reset_plotly_js_cache


def _urlopen_response(body: bytes, *, status: int = 200) -> MagicMock:
    response = MagicMock()
    response.read.return_value = body
    response.status = status
    response.getcode.return_value = status
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


@pytest.fixture(autouse=True)
def _clear_plotly_cache():
    reset_plotly_js_cache()
    yield
    reset_plotly_js_cache()


def test_fetch_plotly_js_reads_cdn_body_via_urlopen():
    body = b"window.Plotly=" + b"x" * 120
    with patch("urllib.request.urlopen", return_value=_urlopen_response(body)) as urlopen:
        assert fetch_plotly_js().startswith("window.Plotly=")
        urlopen.assert_called_once()
        request = urlopen.call_args[0][0]
        assert request.full_url == PLOTLY_JS_CDN
        assert urlopen.call_args.kwargs.get("timeout") == 60.0


def test_fetch_plotly_js_caches_after_first_fetch():
    body = b"cached-plotly-body"
    with patch("urllib.request.urlopen", return_value=_urlopen_response(body)) as urlopen:
        assert fetch_plotly_js() == "cached-plotly-body"
        assert fetch_plotly_js() == "cached-plotly-body"
        urlopen.assert_called_once()


def test_fetch_plotly_js_http_error_is_clear():
    error = urllib.error.HTTPError(PLOTLY_JS_CDN, 503, "Unavailable", None, None)
    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(RuntimeError, match="HTTP 503 Unavailable"):
            fetch_plotly_js()


def test_fetch_plotly_js_rejects_empty_body():
    with patch("urllib.request.urlopen", return_value=_urlopen_response(b"   \n")):
        with pytest.raises(RuntimeError, match="empty body"):
            fetch_plotly_js()
