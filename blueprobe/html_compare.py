"""Compare structural HTML coverage with existing NPB observations, offline.

The original document goes to the semantic parser intact: reconstructing HTML
from links would lose competition headings and cancellation context.
"""
from collections import Counter

from html_source import HtmlSource


def compare_calendar(html, url, *, selector='.calendar a', extractor=None,
                     semantic_parser=None, include_css=False, stylesheets=None):
    if semantic_parser is None:
        from npb_calendar import parse
        semantic_parser = parse
    semantic = semantic_parser(html, url)
    structural = HtmlSource(selector=selector, extractor=extractor, include_css=include_css,
                            stylesheets=stylesheets).parse(html, url)
    links = structural['records'][0]['derived']['links'] if structural['records'] else []
    observed = Counter(link['url'] for link in links)
    adopted = {record['href'] for record in semantic['records']}
    missing = sorted(adopted - observed.keys())
    return {'schema': 'blueprobe-html-comparison/1', 'source_url': url, 'selector': selector,
            'semantic': semantic, 'structural': structural,
            'coverage': {'adopted_games': len(semantic['records']), 'link_occurrences': len(links),
                         'unique_links': len(observed), 'missing_adopted_urls': missing,
                         'duplicate_urls': {key: count for key, count in observed.items() if count > 1},
                         'complete_for_adopted_games': bool(structural['records']) and not missing}}
