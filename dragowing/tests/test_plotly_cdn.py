"""DRAgoWing Plotly.js CDN adapter (jsDelivr, no hash pin)."""
from __future__ import annotations

import io
import os
from pathlib import Path
import urllib.error
from unittest.mock import patch

import pytest

from dragowing import plotly_cdn


class Response(io.BytesIO):
    status = 200


@pytest.fixture(autouse=True)
def clear_cache():
    plotly_cdn.reset_plotly_js_cache()
    yield
    plotly_cdn.reset_plotly_js_cache()


@pytest.fixture
def fixture_bytes():
    return b'/* small unit fixture */ window.Plotly={version:"9.9.9"};'


def test_fetch_and_successful_byte_cache(fixture_bytes):
    with patch('urllib.request.urlopen', return_value=Response(fixture_bytes)) as opener:
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()
        opener.assert_called_once()
        assert opener.call_args.args[0].full_url == plotly_cdn.PLOTLY_JS_CDN
        assert opener.call_args.kwargs['timeout'] == 60.0
        assert plotly_cdn._PLOTLY_JS_CACHE == fixture_bytes


def test_external_script_without_sri_and_embed_preserves_json(fixture_bytes):
    from dragowing.htmlout import figure_block, spec_from, standalone
    spec = {'data': [{'type': 'scatter', 'x': [1], 'y': [2]}], 'layout': {'title': {'text': '<exact>'}}}
    body = figure_block(spec, 'g')
    external = standalone('test', body, plotly=True)
    assert plotly_cdn.PLOTLY_JS_CDN in external
    assert 'integrity=' not in external
    assert 'crossorigin="anonymous"' in external
    with patch('urllib.request.urlopen', return_value=Response(fixture_bytes)):
        embedded = standalone('test', body, plotly=True, embed=True)
    assert fixture_bytes.decode() in embedded
    assert plotly_cdn.PLOTLY_JS_CDN not in embedded
    assert spec_from(external, 'g') == spec_from(embedded, 'g') == spec


def test_failed_fetch_does_not_poison_cache(fixture_bytes):
    with patch('urllib.request.urlopen', side_effect=[urllib.error.URLError('offline'), Response(fixture_bytes)]):
        with pytest.raises(RuntimeError, match='request failed'):
            plotly_cdn.fetch_plotly_js()
        assert plotly_cdn._PLOTLY_JS_CACHE is None
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()


@pytest.mark.parametrize('error', [
    urllib.error.HTTPError(plotly_cdn.PLOTLY_JS_CDN, 503, 'Unavailable', None, None),
    urllib.error.URLError('offline'), TimeoutError('timed out'),
])
def test_acquisition_failure_does_not_poison_cache(error, fixture_bytes):
    with patch('urllib.request.urlopen', side_effect=[error, Response(fixture_bytes)]):
        with pytest.raises(RuntimeError, match='request failed|HTTP 503|timed out'):
            plotly_cdn.fetch_plotly_js()
        assert plotly_cdn._PLOTLY_JS_CACHE is None
        assert plotly_cdn.fetch_plotly_js() == fixture_bytes.decode()


def test_oversized_response_is_bounded_and_not_cached():
    class LargeResponse(Response):
        def read(self, size=-1):
            assert size == plotly_cdn.PLOTLY_JS_MAX_BYTES + 1
            return b'x' * size
    with patch('urllib.request.urlopen', return_value=LargeResponse()):
        with pytest.raises(RuntimeError, match='byte limit'):
            plotly_cdn.fetch_plotly_js()
    assert plotly_cdn._PLOTLY_JS_CACHE is None


def test_inline_raw_text_terminator_is_rejected():
    raw = b'window.Plotly={};/* </script> */'
    with patch('urllib.request.urlopen', return_value=Response(raw)):
        with pytest.raises(ValueError, match='script end tag'):
            plotly_cdn.fetch_plotly_js()
    assert plotly_cdn._PLOTLY_JS_CACHE is None


def test_pinned_bundle_used_for_offline_export_fixture():
    source = os.environ.get('DRAGOWING_PINNED_PLOTLY_JS')
    if not source:
        pytest.skip('pinned Plotly bundle supplied by Chrome CI')
    raw = Path(source).read_bytes()
    assert raw
    with patch('urllib.request.urlopen', return_value=Response(raw)):
        assert plotly_cdn.fetch_plotly_js() == raw.decode('utf-8')
