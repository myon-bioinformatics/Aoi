import socket
from unittest.mock import Mock

import pytest

from blueprobe import inspect
from html_source import HtmlSource


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    blocked = Mock(side_effect=AssertionError('unexpected network'))
    monkeypatch.setattr(socket.socket, 'connect', blocked)
    monkeypatch.setattr(socket.socket, 'connect_ex', blocked)
    monkeypatch.setattr(socket, 'create_connection', blocked)
    monkeypatch.setattr(socket, 'getaddrinfo', blocked)


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


def test_optional_real_lab_extractor_reuses_all_calendar_rows(lab_html_snapshot):
    module = lab_html_snapshot
    html = '<main id="calendar">' + ''.join(
        f'<div class="day"><a href="/d/{i}">{i}日</a></div>' for i in range(1, 32)) + '</main>'
    source = HtmlSource(selector='#calendar > .day', extractor=module.extract)
    observations = []
    for _ in range(2):
        records = []
        rows = inspect(source, [('month', 'https://example.test/month', '2026', html)], records)
        assert rows[0]['unknown'] == 0
        assert records[0]['raw'] == html
        assert records[0]['derived']['scope_count'] == 31
        assert records[0]['derived']['links'] == [
            {'text': f'{day}日', 'url': f'https://example.test/d/{day}'}
            for day in range(1, 32)
        ]
        observations.append(records)
    assert observations[0] == observations[1]
    drift = HtmlSource(selector='#missing', extractor=module.extract).parse(
        html, 'https://example.test/month')
    assert drift['counts']['extraction_failed'] == 1
    assert drift['records'] == []
    unsupported = HtmlSource(selector='.day:hover', extractor=module.extract).parse(
        html, 'https://example.test/month')
    assert unsupported['counts']['extraction_failed'] == 1
    assert unsupported['records'] == []
    assert unsupported['unknown'][0]['reason'] == 'unsupported selector syntax'


def test_cache_snapshot_uses_separate_injected_validator(tmp_path):
    from blueprobe import inspect_cache
    from queryu import Cache

    cache = Cache(tmp_path)
    entry = cache.put('month', 'https://example.test/month', '2026', 200,
                      '<main>日本語🙂</main>'.encode(), {})
    snapshot = cache.snapshot(entry)
    result = {'snapshot': {key: snapshot[key] for key in
                          ('schema', 'url', 'fetched_at', 'response_sha256',
                           'content_sha256', 'encoding')},
              'extraction': {'text': '日本語🙂', 'links': []}}
    extractor = Mock(return_value=result)
    source = HtmlSource(selector='main', snapshot_extractor=extractor,
                        extractor=Mock(side_effect=AssertionError('raw bypass')),
                        include_css=True, stylesheets={})
    records = []
    rows = inspect_cache(source, cache, [entry], records)
    extractor.assert_called_once_with(snapshot, selector='main', include_css=True, stylesheets={})
    assert rows[0]['records'] == 1
    assert records[0]['raw'] == snapshot['html']
    assert records[0]['snapshot'] == result['snapshot']
    assert records[0]['cache_entry'] == entry
    assert records[0]['derived'] == result['extraction']


def test_cache_tamper_stops_before_extractor_and_never_refetches(tmp_path):
    import gzip
    from blueprobe import inspect_cache
    from queryu import Cache, CacheIntegrityError

    cache = Cache(tmp_path)
    entry = cache.put('month', 'https://example.test/month', '2026', 200, b'original', {})
    (tmp_path / entry['file']).write_bytes(gzip.compress(b'modified'))
    extractor = Mock()
    with pytest.raises(CacheIntegrityError):
        inspect_cache(HtmlSource(snapshot_extractor=extractor), cache)
    extractor.assert_not_called()


def test_snapshot_extraction_failure_preserves_envelope():
    snapshot = {'schema': 'html-snapshot/1', 'url': 'https://example.test',
                'html': '<main>x</main>', 'cache_entry': {'extra': None}}
    source = HtmlSource(snapshot_extractor=Mock(side_effect=ValueError('snapshot content hash mismatch')))
    report = source.parse_snapshot(snapshot)
    assert report['records'] == []
    assert report['counts']['extraction_failed'] == 1
    assert report['unknown'][0]['snapshot'] == snapshot
    with pytest.raises(RuntimeError, match='unexpected failure'):
        HtmlSource(snapshot_extractor=Mock(side_effect=RuntimeError('unexpected failure'))).parse_snapshot(snapshot)


def test_verified_cache_real_lab_snapshot_replay(tmp_path, lab_source_access):
    import hashlib
    import npb_calendar
    from pathlib import Path
    from blueprobe import inspect_cache
    from queryu import Cache

    raw = (Path(__file__).parent / 'fixtures' / 'npb_calendar_sample.html').read_bytes()
    cache = Cache(tmp_path)
    first = cache.put('month', 'https://npb.jp/bis/2024/calendar/index_04.html', '2024', 200, raw, {})
    second = cache.put('month', first['url'], '2024', 200, b'<main>changed</main>', {})
    snapshot = cache.snapshot(first)
    assert snapshot['response_sha256'] == hashlib.sha256(raw).hexdigest()
    assert snapshot['content_sha256'] == hashlib.sha256(snapshot['html'].encode()).hexdigest()
    # Default path must import source_access.extract_snapshot, not the raw adapter.
    source = HtmlSource(selector='.calendar a', include_css=True)
    observations = []
    for _ in range(2):
        records = []
        rows = inspect_cache(source, cache, [first], records)
        assert rows[0]['unknown'] == 0
        assert records[0]['snapshot']['fetched_at'] == first['fetched_at']
        assert records[0]['cache_entry'] == first
        assert records[0]['raw'].encode() == raw
        assert records[0]['derived']['links']
        observations.append(records)
    assert observations[0] == observations[1]
    assert cache.body(second) == '<main>changed</main>'
    semantic_records = []
    inspect_cache(npb_calendar, cache, [first], semantic_records)
    assert semantic_records == npb_calendar.parse(snapshot['html'], first['url'])['records']
    assert len(semantic_records) == 4
    invalid = {**snapshot, 'content_sha256': '0' * 64}
    report = source.parse_snapshot(invalid)
    assert report['records'] == []
    assert report['unknown'][0]['reason'] == 'snapshot content hash mismatch'
    for field, value in [('schema', 'unsupported'), ('url', 'file:///tmp/page'),
                         ('html', 'x' * (2 * 1024 * 1024 + 1))]:
        assert source.parse_snapshot({**snapshot, field: value})['counts']['extraction_failed'] == 1


def test_blueprobe_cache_cli_uses_verified_snapshots(tmp_path, monkeypatch, capsys):
    import blueprobe
    from queryu import Cache, CacheIntegrityError

    cache = Cache(tmp_path)
    entry = cache.put('page', 'https://example.test', 'g', 200, b'<p>x</p>', {})
    snapshot = cache.snapshot(entry)
    extractor = Mock(return_value={'snapshot': {'schema': 'html-snapshot/1'}, 'extraction': {'text': 'x'}})
    source = HtmlSource(snapshot_extractor=extractor)
    monkeypatch.setattr(blueprobe, 'load_source', lambda name: source)
    assert blueprobe.main(['--source', 'html_source', '--cache', str(tmp_path)]) == 0
    extractor.assert_called_once_with(snapshot, selector=None)
    assert 'records' in capsys.readouterr().out
    (tmp_path / entry['file']).unlink()
    with pytest.raises((CacheIntegrityError, FileNotFoundError)):
        blueprobe.main(['--source', 'html_source', '--cache', str(tmp_path)])


def test_empty_404_cache_is_counted_without_parsing(tmp_path):
    from blueprobe import inspect_cache
    from queryu import Cache

    cache = Cache(tmp_path)
    cache.put('absent', 'https://example.test/absent', 'g', 404, b'', {})
    source = HtmlSource(snapshot_extractor=Mock(side_effect=AssertionError('empty page')))
    rows = inspect_cache(source, cache)
    assert rows[0]['empty_pages'] == 1
    assert rows[0]['pages'] == rows[0]['records'] == rows[0]['unknown'] == 0
    source.snapshot_extractor.assert_not_called()
