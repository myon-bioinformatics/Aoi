"""Offline regressions: python3 -m unittest discover -s . -p 'test_*.py'."""
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('engel_builder', HERE / 'build_subscription_engel_shares.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class EvidenceTests(unittest.TestCase):
    def test_raw_bytes_match_pr_head(self):
        manifest = json.loads((HERE / 'raw_git_blobs.json').read_text())
        self.assertEqual(set(manifest), {p.name for p in (HERE / 'raw').iterdir() if p.is_file()})
        for name, expected in manifest.items():
            data = (HERE / 'raw' / name).read_bytes()
            self.assertEqual(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(), expected, name)

    def test_missing_tokens_and_zero(self):
        for token in ('', None, 'n.a.'):
            r = builder.row('USA', 2024, 'fixture', token, 'unit', ('source', 'fixture record 1'))
            self.assertEqual(r['value'], '')
            self.assertIn('missing published value', r['note'])
        self.assertEqual(builder.row('USA', 2024, 'fixture', '0', 'unit', ('s', 'r'))['value'], '0')

    def test_conflicting_alternatives_not_selected(self):
        report = builder.quality_report(builder.build())
        self.assertEqual(len(report['conflicts']), 3)
        expected = {'mean': {'3609.38', '3609.0'}, 'share_of_spend': {'4.5959', '4.595'}, 'share_of_income': {'3.4637', '3.463'}}
        for c in report['conflicts']:
            self.assertEqual((c['country'], c['year']), ('USA', '2024'))
            self.assertEqual({r['value'] for r in c['alternatives']}, expected[c['variable'].rsplit(':', 1)[1]])
            self.assertEqual(len({r['source'] for r in c['alternatives']}), 2)
            self.assertTrue(all('raw/' in r['note'] and 'data record' in r['note'] for r in c['alternatives']))

    def test_explicit_missing_values_and_absent_years(self):
        q = builder.quality_report(builder.build())
        self.assertEqual(len(q['missing_values']), 14)
        hbs = [r for r in q['missing_values'] if r['variable'].startswith('eurostat_hbs:')]
        self.assertEqual(len(hbs), 12)
        self.assertEqual({(r['country'], r['year']) for r in hbs}, {('NLD', '2010'), ('NOR', '2020'), ('PRT', '2020'), ('ROU', '2020')})
        series = [r for r in q['series_coverage'] if r['source'].startswith('BLS CE API')]
        self.assertEqual(len(series), 5)
        for s in series:
            self.assertEqual(len(s['observed_years']), 39)
            self.assertEqual(s['absent_years_within_observed_span'], [1994, 1995])

    def test_fixture_conflicts_include_units_and_missing(self):
        rows = [builder.row('X', 2000, 'fixture', v, u, ('s', 'fixture')) for v, u in [('1', 'USD'), ('1', 'PPS'), ('', 'USD')]]
        self.assertEqual(len(builder.quality_report(rows)['conflicts'][0]['alternatives']), 3)
        self.assertEqual(builder.quality_report([])['series_coverage'], [])

    def test_rebuild_is_byte_identical_and_gzip_matches(self):
        outputs = [f'{builder.NAME}_vertical.csv', f'{builder.NAME}_vertical.csv.gz', '_build_stats.json', '_quality_report.json']
        before = {p.name: p.read_bytes() for p in (HERE / 'raw').iterdir()}
        with tempfile.TemporaryDirectory() as tmp, patch.object(builder, 'HERE', Path(tmp)):
            with patch('sys.stdout', io.StringIO()):
                builder.main()
                first = {n: (Path(tmp) / n).read_bytes() for n in outputs}
                builder.main()
            self.assertEqual(first, {n: (Path(tmp) / n).read_bytes() for n in outputs})
            self.assertEqual(first, {n: (HERE / n).read_bytes() for n in outputs})
            self.assertEqual(gzip.decompress(first[outputs[1]]), first[outputs[0]])
            self.assertEqual(len(list(csv.DictReader(io.StringIO(first[outputs[0]].decode())))), 2012)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (HERE / 'raw').iterdir()})


if __name__ == '__main__':
    unittest.main()
