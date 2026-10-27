"""Regression checks for the seven subscription packs; no Netflix rebuild."""
import csv
import gzip
import importlib.util
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1] / 'research/staple-price-survey'
spec = importlib.util.spec_from_file_location('subscription_contract', ROOT / 'subscription_contract.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def test_committed_audit_and_compression():
    assert c.audit(ROOT) == json.loads((ROOT / 'subscription_source_audit.json').read_text())
    for name in c.PACKS:
        p = ROOT / ('adjacent_' + name + '_levels')
        f = p / (p.name + '_vertical.csv')
        assert gzip.decompress(f.with_suffix('.csv.gz').read_bytes()) == f.read_bytes()
        rows = list(csv.DictReader(f.open()))
        assert c.observations(rows) == c.observations(reversed(rows))
        assert c.cross_source_groups(rows) == c.cross_source_groups(reversed(rows))


def sample(source='a', value='1'):
    return dict(country='ARE', date='2026-10-26', variable='price', source=source,
                value=value, unit='AED per monthly subscription')


def test_duplicates_conflicts_and_explicit_selection():
    a, b = sample(), sample('b', '2')
    for other in (sample(), sample(value='2')):
        with pytest.raises(ValueError, match='duplicate'):
            c.observations([a, other])
    assert c.cross_source_groups([a, b])[0]['conflict']
    assert not c.cross_source_groups([a, sample('b')])[0]['conflict']
    assert c.select_source([b, a], 'a') == [a]
    assert c.select_source([a], 'missing') == []
    for value in ('0', '-1', 'NaN', 'Infinity'):
        with pytest.raises(ValueError):
            c.observations([sample(value=value)])
    with pytest.raises(ValueError):
        c.observations([sample(source='')])


def test_known_conflicts_retained_and_outliers_quarantined():
    audit = c.audit(ROOT)
    for pack, country, values in [('apple_music_subscription', 'ARE', {'29.99', '23.99'}),
                                  ('google_one', 'CHL', {'750.0', '1790.0'})]:
        group = next(g for g in audit['adjacent_' + pack + '_levels']['cross_source']
                     if g['key'][0:2] == [country, '2026-10-26'])
        assert {float(r['value']) for r in group['observations']} == {float(v) for v in values}
    p = ROOT / 'adjacent_youtube_premium_subscription_levels'
    bad = list(csv.DictReader((p / 'raw/quarantined_vertical.csv').open()))
    active = list(csv.DictReader(next(p.glob('*_vertical.csv')).open()))
    assert len(bad) == 5
    assert all(row not in active for row in bad)
    assert {r['country'] for r in bad} == {'MEX', 'DOM'}


def test_quarantine_exact_identity_and_raw_provenance():
    """Keep suspect observations recoverable without leaking into analysis."""
    pack = ROOT / 'adjacent_youtube_premium_subscription_levels'
    def read(path):
        with path.open(newline='', encoding='utf-8') as stream:
            return list(csv.DictReader(stream))
    bad = read(pack / 'raw/quarantined_vertical.csv')
    expected = {('DOM', date, '8.49', 'DOP') for date in
                ('2026-04-10', '2026-07-13', '2026-10-26')}
    expected |= {('MEX', date, '15.99', 'MXN') for date in
                 ('2026-07-13', '2026-10-26')}
    assert {(r['country'], r['date'], r['value'], r['unit'].split()[0])
            for r in bad} == expected
    raw = read(pack / 'raw/youtube_premium_levels.csv')
    for row in bad:
        matches = [r for r in raw if (r['iso3'], r['date'], r['local_price'],
                   r['currency'], r['source_url']) ==
                   (row['country'], row['date'], row['value'],
                    row['unit'].split()[0], row['source'])]
        assert len(matches) == 1
        original = matches[0]
        assert original['source_label'] in row['note']
        assert 'retrieved ' + original['retrieved'] in row['note']
        assert 'source_price_usd=' + original['price_usd'] in row['note']
        assert row['estimated_value'] == ''
    active = read(pack / (pack.name + '_vertical.csv'))
    bad_keys = {tuple(r[k] for k in c.KEY) for r in bad}
    assert bad_keys.isdisjoint(tuple(r[k] for k in c.KEY) for r in active)
    assert any(r['country'] == 'MEX' and r['value'] == '159.0' for r in active)
    before = c.audit(ROOT)
    # An invalid raw quarantine sentinel must not be opened by audit().
    from tempfile import TemporaryDirectory
    import shutil
    with TemporaryDirectory() as tmp:
        mirror = Path(tmp) / 'survey'
        mirror.mkdir()
        for name in c.PACKS:
            directory = ROOT / ('adjacent_' + name + '_levels')
            target = mirror / directory.name
            target.mkdir()
            filename = directory.name + '_vertical.csv'
            shutil.copyfile(directory / filename, target / filename)
            (target / 'raw').mkdir()
            (target / 'raw/quarantined_vertical.csv').write_text('invalid raw data')
        assert c.audit(mirror) == before
