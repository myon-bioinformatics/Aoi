"""DRAgoWing uses the locked web-ui distribution, including failed-cache retries."""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import urllib.error
from unittest.mock import patch

import pytest

from dragowing import plotly_cdn
from vendor import web_ui


class Response(io.BytesIO):
    status = 200


@pytest.fixture(autouse=True)
def clear_cache():
    plotly_cdn.reset_plotly_js_cache()
    yield
    plotly_cdn.reset_plotly_js_cache()


@pytest.fixture
def fixture_bytes(monkeypatch):
    raw = b'/* small unit fixture */ window.Plotly={version:"4.1.1"};'
    monkeypatch.setattr(web_ui, 'PLOTLY_JS_SHA256', hashlib.sha256(raw).hexdigest())
    return raw


def test_fetch_and_successful_byte_cache(fixture_bytes):
    with patch('urllib.request.urlopen', return_value=Response(fixture_bytes)) as opener:
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()
        opener.assert_called_once()
        assert opener.call_args.args[0].full_url == web_ui.PLOTLY_JS_URL
        assert opener.call_args.kwargs['timeout'] == 60.0
        assert plotly_cdn._PLOTLY_JS_CACHE == fixture_bytes


def test_external_script_uses_shared_sri_and_embed_preserves_json(fixture_bytes):
    from dragowing.htmlout import figure_block, spec_from, standalone
    spec = {'data': [{'type': 'scatter', 'x': [1], 'y': [2]}], 'layout': {'title': {'text': '<exact>'}}}
    body = figure_block(spec, 'g')
    external = standalone('test', body, plotly=True)
    assert web_ui.remote_script_tag(web_ui.remote_scripts('plotly.js')[0]) in external
    assert f'integrity="{web_ui.PLOTLY_JS_SRI}"' in external
    assert 'crossorigin="anonymous"' in external
    with patch('urllib.request.urlopen', return_value=Response(fixture_bytes)):
        embedded = standalone('test', body, plotly=True, embed=True)
    assert fixture_bytes.decode() in embedded
    assert web_ui.PLOTLY_JS_URL not in embedded
    assert spec_from(external, 'g') == spec_from(embedded, 'g') == spec


@pytest.mark.parametrize('bad', [b'/* another release */', b'window.pwned=true;', b' ', b''])
def test_cdn_mismatch_does_not_poison_cache(bad, fixture_bytes):
    with patch('urllib.request.urlopen', side_effect=[Response(bad), Response(fixture_bytes)]) as opener:
        with pytest.raises(RuntimeError, match='mismatch|empty body'):
            plotly_cdn.fetch_plotly_js()
        assert plotly_cdn._PLOTLY_JS_CACHE is None
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()
        assert opener.call_count == 2


@pytest.mark.parametrize('error', [
    urllib.error.HTTPError(web_ui.PLOTLY_JS_URL, 503, 'Unavailable', None, None),
    urllib.error.URLError('offline'), TimeoutError('timed out'),
])
def test_acquisition_failure_does_not_poison_cache(error, fixture_bytes):
    with patch('urllib.request.urlopen', side_effect=[error, Response(fixture_bytes)]):
        with pytest.raises(RuntimeError, match='request failed'):
            plotly_cdn.fetch_plotly_js()
        assert plotly_cdn._PLOTLY_JS_CACHE is None
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()


def test_oversized_response_is_bounded_and_not_cached():
    class LargeResponse(Response):
        def read(self, size=-1):
            assert size == web_ui.PLOTLY_JS_MAX_BYTES + 1
            return b'x' * size
    with patch('urllib.request.urlopen', return_value=LargeResponse()):
        with pytest.raises(RuntimeError, match='byte limit'):
            plotly_cdn.fetch_plotly_js()
    assert plotly_cdn._PLOTLY_JS_CACHE is None


def test_inline_raw_text_terminator_is_rejected(monkeypatch):
    raw = b'window.Plotly={};/* </script> */'
    monkeypatch.setattr(web_ui, 'PLOTLY_JS_SHA256', hashlib.sha256(raw).hexdigest())
    with patch('urllib.request.urlopen', return_value=Response(raw)):
        with pytest.raises(ValueError, match='script end tag'):
            plotly_cdn.fetch_plotly_js()
    assert plotly_cdn._PLOTLY_JS_CACHE is None


def test_real_fixed_bundle_success_and_tamper_rejection():
    source = os.environ.get('DRAGOWING_PINNED_PLOTLY_JS')
    if not source:
        pytest.skip('real pinned CDN bytes supplied by Chrome CI')
    raw = Path(source).read_bytes()
    web_ui.verify_plotly_js(raw)
    with patch('urllib.request.urlopen', side_effect=[Response(raw + b';window.pwned=true;'), Response(raw)]):
        with pytest.raises(RuntimeError, match='SHA-256 mismatch'):
            plotly_cdn.fetch_plotly_js()
        assert plotly_cdn._PLOTLY_JS_CACHE is None
        assert plotly_cdn.fetch_plotly_js() == raw.decode('utf-8')
