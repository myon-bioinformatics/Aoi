"""Validate the food-share snapshot using only the Python standard library."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1] / 'research/staple-price-survey'


def coverage(rows):
    countries = sorted({r['country'] for r in rows})
    years = [int(r['year']) for r in rows]
    return (f'**{len(rows)} vertical rows** · **{len(countries)} ISO3** · '
            f'year span **{min(years)}–{max(years)}**.\n\nISO3: '
            + ', '.join(countries) + '.')


def validate_rows(rows, manifest):
    seen = set()
    groups = {}
    restored = []
    partial = {tuple(x['key']): set(x['indices']) for x in manifest['partial_series']}
    for r in rows:
        key = tuple(r[k] for k in ('country', 'date', 'variable', 'unit'))
        if key in seen:
            raise ValueError(f'duplicate observation: {key}')
        seen.add(key)
        match = re.fullmatch(r'(engel_share:food(?:_at_home)?)_([qd])(\d+)', r['legacy_variable'])
        if not match:
            raise ValueError('invalid legacy variable')
        metric, letter, index = match.groups()
        contract_key = json.dumps([r['country'], r['source'], letter], ensure_ascii=False, separators=(',', ':'))
        contract = manifest['source_contracts'].get(contract_key)
        if contract is None:
            raise ValueError(f'unreviewed source: {contract_key}')
        for field in ('stratifier', 'bucket_type', 'bucket_count'):
            if str(contract[field]) != r[field]:
                raise ValueError(f'source classification mismatch: {field}: {key}')
        if r['bucket_index'] != index or not 1 <= int(index) <= int(r['bucket_count']):
            raise ValueError('invalid bucket index')
        metric += "_" + contract["series_variant"] if contract["series_variant"] else ""
        canonical = f"{metric}_{r['stratifier']}_{r['bucket_type']}_{index}"
        if r['variable'] != canonical:
            raise ValueError('noncanonical variable')
        group = (r['country'], r['date'], r['source'], canonical.rsplit('_', 1)[0])
        indices, count = groups.setdefault(group, (set(), int(r['bucket_count'])))
        if int(index) in indices:
            raise ValueError('duplicate group bucket')
        indices.add(int(index))
        restored.append({f: r['legacy_variable'] if f == 'variable' else r[f]
                         for f in manifest['original_fields']})
    for key, (indices, count) in groups.items():
        if indices != partial.get(key, set(range(1, count + 1))):
            raise ValueError(f'incomplete or unexpected series: {key}')
    if not set(partial) <= set(groups):
        raise ValueError('missing partial series')
    digest = hashlib.sha256(json.dumps(restored, ensure_ascii=False, sort_keys=True,
                                      separators=(',', ':')).encode()).hexdigest()
    if digest != manifest['original_rows_sha256']:
        raise ValueError('original observations/source records changed')


def validate(base=BASE):
    for pack in ('adjacent_food_share_by_income', 'adjacent_food_share_urban_rural'):
        directory = base / pack
        path = directory / f'{pack}_vertical.csv'
        if gzip.decompress(path.with_suffix('.csv.gz').read_bytes()) != path.read_bytes():
            raise ValueError(f'CSV/gzip mismatch: {pack}')
        with path.open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        readme = (directory / f'{pack}_readme.md').read_text()
        expected = '<!-- coverage:start -->\n' + coverage(rows) + '\n<!-- coverage:end -->'
        if expected not in readme:
            raise ValueError(f'stale README coverage: {pack}')
        with (directory / '_coverage_by_country.csv').open(newline='') as stream:
            recorded = list(csv.DictReader(stream))
        actual = []
        for country in sorted({r['country'] for r in rows}):
            subset = [r for r in rows if r['country'] == country]
            years = [int(r['year']) for r in subset]
            actual.append({'country': country, 'n_rows': str(len(subset)),
                           'min_year': str(min(years)), 'max_year': str(max(years))})
        if actual != recorded:
            raise ValueError(f'stale coverage CSV: {pack}')
        if pack.endswith('by_income'):
            validate_rows(rows, json.loads((directory / 'classification.json').read_text()))
    return True


if __name__ == '__main__':
    validate()
    print('Food-share classification, preservation, gzip and coverage: OK')
