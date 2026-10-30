"""Source-preserving subscription observations; stdlib only. Run for audit JSON."""
import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

KEY = ('country', 'date', 'variable', 'source')
PACKS = ('spotify_subscription', 'apple_music_subscription', 'youtube_premium_subscription',
         'icloud_plus', 'microsoft_365', 'google_one', 'apple_tv_plus')


def observations(rows):
    """Validate before indexing: even identical duplicate keys are rejected."""
    indexed = {}
    for original in rows:
        row = dict(original)
        key = tuple(row[field] for field in KEY)
        if any(not value.strip() for value in key):
            raise ValueError('empty observation dimension')
        value = Decimal(row['value'])
        if not value.is_finite() or value <= 0 or not row['unit'].strip():
            raise ValueError('expected finite positive price and explicit unit')
        if key in indexed:
            raise ValueError(f'duplicate source observation: {key}')
        indexed[key] = row
    return [indexed[key] for key in sorted(indexed)]


def cross_source_groups(rows):
    """Report all multi-source keys, including equal-price duplicates."""
    groups = defaultdict(list)
    for row in observations(rows):
        groups[tuple(row[f] for f in KEY[:3])].append(row)
    return [dict(key=list(key), conflict=len({(Decimal(r['value']), r['unit']) for r in group}) > 1,
                 observations=group) for key, group in sorted(groups.items()) if len(group) > 1]


def select_source(rows, source):
    """Explicit exact-URL selection; no fallback, averaging or last-row wins."""
    return [row for row in observations(rows) if row['source'] == source]


def audit(root):
    result = {}
    for name in PACKS:
        pack = root / ('adjacent_' + name + '_levels')
        path = pack / (pack.name + '_vertical.csv')
        with path.open(newline='', encoding='utf-8') as stream:
            rows = observations(csv.DictReader(stream))
        result[pack.name] = dict(rows=len(rows), cross_source=cross_source_groups(rows))
    return result


if __name__ == '__main__':
    print(json.dumps(audit(Path(__file__).parent), indent=2, sort_keys=True))
