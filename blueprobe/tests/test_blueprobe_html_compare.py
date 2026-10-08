from pathlib import Path
import socket
from unittest.mock import Mock

import pytest

from html_compare import compare_calendar
from html_source import HtmlSource


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    blocked = Mock(side_effect=AssertionError('unexpected network'))
    monkeypatch.setattr(socket.socket, 'connect', blocked)
    monkeypatch.setattr(socket, 'create_connection', blocked)


def test_comparison_uses_original_html_and_reports_missing_adopted_urls():
    parser = Mock(return_value={'records': [{'href': 'https://npb.jp/game'}],
                               'counts': {'cancelled': 1}, 'unknown': []})
    extractor = Mock(return_value={'links': [{'url': 'https://npb.jp/other'}]})
    result = compare_calendar('<table>original</table>', 'https://npb.jp/month',
                              extractor=extractor, semantic_parser=parser)
    parser.assert_called_once_with('<table>original</table>', 'https://npb.jp/month')
    assert result['coverage']['missing_adopted_urls'] == ['https://npb.jp/game']
    assert result['coverage']['complete_for_adopted_games'] is False
    assert result['semantic']['counts']['cancelled'] == 1


def test_css_options_are_delegated_without_loading_assets():
    extractor = Mock(return_value={'links': [], 'css': {'computed_styles': False}})
    result = HtmlSource(include_css=True, stylesheets={'saved.css': '.day{color:#fff}'},
                        extractor=extractor).parse('<main>x</main>', 'https://example.test')
    extractor.assert_called_once_with('<main>x</main>', 'https://example.test', selector=None,
                                      include_css=True, stylesheets={'saved.css': '.day{color:#fff}'})
    assert result['records'][0]['derived']['css']['computed_styles'] is False


def test_real_saved_npb_fixture_coverage_and_css():
    module = pytest.importorskip('mcp_toolcall_lab.adapters.html_snapshot',
                                reason='optional shared extractor integration')
    html = (Path(__file__).parent / 'fixtures/npb_calendar_sample.html').read_text()
    html = '<style>.calendar a{color:#123456}.missing:hover{display:none}</style>' + html
    url = 'https://npb.jp/bis/2024/calendar/index_04.html'
    results = [compare_calendar(html, url, extractor=module.extract, include_css=True) for _ in range(2)]
    assert results[0] == results[1]
    result = results[0]
    assert result['coverage']['adopted_games'] == 4
    assert result['coverage']['complete_for_adopted_games']
    assert result['coverage']['missing_adopted_urls'] == []
    assert result['coverage']['duplicate_urls'] == {'https://npb.jp/bis/2024/games/s2024040201097.html': 2}
    assert result['semantic']['counts']['cancelled'] == 1
    assert result['semantic']['counts']['non_regular'] == 1
    css = result['structural']['records'][0]['derived']['css']
    assert css['sources'][0]['inspection']['rules'][0]['declarations'][0]['hex_colors'] == ['#123456']
    assert css['selector_matches'][0]['matched'] == result['coverage']['link_occurrences']
    assert css['selector_matches'][1]['status'] == 'unsupported'
    drift = compare_calendar(html, url, selector='#changed', extractor=module.extract)
    assert not drift['coverage']['complete_for_adopted_games']
    assert len(drift['coverage']['missing_adopted_urls']) == 4
