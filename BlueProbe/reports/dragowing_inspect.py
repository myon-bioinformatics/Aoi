"""Read only embedded report observations; never execute HTML or fetch URLs."""
import json
from html.parser import HTMLParser


class Report(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []
        self.count = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('id') == 'report-data':
            self.count += 1
            self.active = True
    def handle_endtag(self, tag):
        if tag == 'script':
            self.active = False
    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def inspect(html, previous=None):
    parser = Report()
    parser.feed(html)
    if parser.count != 1:
        raise ValueError('DRAgoWing report-data が一意に存在しません')
    raw = json.loads(''.join(parser.parts))
    data = raw.get('research_observations')
    if not isinstance(data, dict) or data.get('version') != 1 or not isinstance(data.get('pairs'), list):
        raise ValueError('未知の研究観測形式。前回値を更新しません')
    rows = {}
    for pair in data['pairs']:
        if not isinstance(pair, dict) or not isinstance(pair.get('units'), list) or len(pair['units']) != 2 or not all(isinstance(u, str) for u in pair['units']):
            raise ValueError('未知の球団年ペア形式')
        key = '|'.join(sorted(pair['units']))
        if key in rows:
            raise ValueError('球団年ペアの重複')
        rows[key] = pair
    old = previous.get('rows', {}) if previous else {}
    return {'version': 1, 'input': data.get('input'), 'rows': rows,
            'baseline': previous is None,
            'discoveries': data.get('discoveries', []),
            'discoveries_changed': (previous.get('discoveries', []) if previous else []) != data.get('discoveries', []),
            'added': sorted(set(rows)-set(old)), 'removed': sorted(set(old)-set(rows)),
            'changed': sorted(k for k in rows.keys() & old.keys() if rows[k] != old[k])}
