from hashlib import sha256
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
    monkeypatch.setattr(socket.socket, 'connect_ex', blocked)
    monkeypatch.setattr(socket, 'create_connection', blocked)
    monkeypatch.setattr(socket, 'getaddrinfo', blocked)


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


def test_real_saved_npb_fixture_coverage_and_css(lab_html_snapshot):
    module = lab_html_snapshot
    fixtures = Path(__file__).parent / 'fixtures'
    html = (fixtures / 'npb_calendar_sample.html').read_text(encoding='utf-8')
    saved_css = (fixtures / 'npb_calendar_sample.css').read_text(encoding='utf-8')
    html = ('<style>.calendar a{color:#123456}.missing:hover{display:none}</style>'
            '<link rel="stylesheet" href="../assets/calendar.css">'
            '<link rel="stylesheet" href="../assets/not-saved.css">' + html)
    url = 'https://npb.jp/bis/2024/calendar/index_04.html'
    stylesheets = {'../assets/calendar.css': saved_css}
    results = [compare_calendar(html, url, extractor=module.extract, include_css=True,
                                stylesheets=stylesheets) for _ in range(2)]
    assert results[0] == results[1]
    result = results[0]
    assert result['coverage']['adopted_games'] == 4
    assert result['coverage']['complete_for_adopted_games']
    assert result['coverage']['missing_adopted_urls'] == []
    assert result['coverage']['duplicate_urls'] == {'https://npb.jp/bis/2024/games/s2024040201097.html': 2}
    assert result['semantic']['counts']['cancelled'] == 1
    assert result['semantic']['counts']['non_regular'] == 1
    structural = result['structural']['records'][0]
    assert structural['raw'] == html
    css = structural['derived']['css']
    assert css['computed_styles'] is False
    assert [source['kind'] for source in css['sources']] == ['embedded', 'supplied']
    assert css['sources'][0]['inspection']['rules'][0]['declarations'][0]['hex_colors'] == ['#123456']
    assert css['selector_matches'][0]['matched'] == result['coverage']['link_occurrences']
    assert css['selector_matches'][1]['status'] == 'unsupported'
    supplied = css['sources'][1]
    assert supplied['url'] == 'https://npb.jp/bis/2024/assets/calendar.css'
    assert supplied['inspection']['content_sha256'] == sha256(saved_css.encode('utf-8')).hexdigest()
    assert supplied['inspection']['computed_styles'] is False
    assert supplied['inspection']['rules'][0]['declarations'][0]['hex_colors'] == ['#abcdef']
    assert supplied['inspection']['rules'][0]['declarations'][1]['value'] == (
        'url("https://example.test/not-loaded.svg")')
    assert supplied['inspection']['unknown'] == [
        {'source': '@font-face', 'reason': 'unsupported at-rule body'}
    ]
    assert css['selector_matches'][2:] == [
        {'source': 1, 'rule': 0, 'selector': '.calendar a',
         'matched': result['coverage']['link_occurrences'], 'contexts': [], 'status': 'matched'},
        {'source': 1, 'rule': 1, 'selector': '.calendar td > a',
         'matched': result['coverage']['link_occurrences'],
         'contexts': ['@media (min-width: 800px)'], 'status': 'matched'},
    ]
    assert css['stylesheet_references'] == [
        'https://npb.jp/bis/2024/assets/calendar.css',
        'https://npb.jp/bis/2024/assets/not-saved.css',
    ]
    assert structural['derived']['stylesheets'] == css['stylesheet_references']
    assert css['unloaded_stylesheets'] == ['https://npb.jp/bis/2024/assets/not-saved.css']
    assert css['unloaded_imports'] == ['@import url("https://example.test/not-loaded.css")']
    assert stylesheets == {'../assets/calendar.css': saved_css}
    drift = compare_calendar(html, url, selector='#changed', extractor=module.extract)
    assert not drift['coverage']['complete_for_adopted_games']
    assert len(drift['coverage']['missing_adopted_urls']) == 4
