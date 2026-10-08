import socket
from unittest.mock import Mock

import pytest

from blueprobe import inspect
from html_source import HtmlSource


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    blocked = Mock(side_effect=AssertionError('unexpected network'))
    monkeypatch.setattr(socket.socket, 'connect', blocked)
    monkeypatch.setattr(socket, 'create_connection', blocked)


def test_saved_pages_delegate_selector_and_preserve_observations():
    extractor = Mock(return_value={'text': '1日 2日', 'scope_count': 2,
                                  'links': [], 'headings': []})
    source = HtmlSource(selector='#calendar > .day', extractor=extractor)
    records = []
    pages = [('month', 'https://example.test/month', '2026', '<main>saved</main>')]
    for _ in range(2):
        rows = inspect(source, pages, records)
        assert rows[0]['records'] == 1
        assert rows[0]['unknown'] == 0
    assert extractor.call_count == 2
    extractor.assert_called_with('<main>saved</main>', 'https://example.test/month',
                                 selector='#calendar > .day')
    assert records[0]['raw'] == '<main>saved</main>'
    assert records[0]['derived']['scope_count'] == 2


def test_markup_drift_is_unknown_not_empty_success():
    source = HtmlSource(selector='#missing', extractor=Mock(side_effect=ValueError('no match')))
    report = source.parse('<main>changed</main>', 'https://example.test')
    assert report['records'] == []
    assert report['counts']['extraction_failed'] == 1
    assert report['unknown'] == [{'raw': '<main>changed</main>',
                                 'url': 'https://example.test', 'reason': 'no match'}]


def test_transport_or_programming_errors_are_not_reclassified_as_drift():
    source = HtmlSource(extractor=Mock(side_effect=RuntimeError('unexpected failure')))
    with pytest.raises(RuntimeError, match='unexpected failure'):
        source.parse('<main>x</main>', 'https://example.test')


def test_optional_real_lab_extractor_reuses_all_calendar_rows():
    module = pytest.importorskip('mcp_toolcall_lab.adapters.html_snapshot',
                                reason='optional cross-repository integration')
    html = '<main id="calendar">' + ''.join(
        f'<div class="day"><a href="/d/{i}">{i}日</a></div>' for i in range(1, 32)) + '</main>'
    source = HtmlSource(selector='#calendar > .day', extractor=module.extract)
    for _ in range(2):
        records = []
        rows = inspect(source, [('month', 'https://example.test/month', '2026', html)], records)
        assert rows[0]['unknown'] == 0
        assert records[0]['derived']['scope_count'] == 31
        assert len(records[0]['derived']['links']) == 31
    drift = HtmlSource(selector='#missing', extractor=module.extract).parse(
        html, 'https://example.test/month')
    assert drift['counts']['extraction_failed'] == 1
