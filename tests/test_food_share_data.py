"""Snapshot and adversarial regressions for research food-share classification."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('food_share_check', ROOT / 'scripts/check_food_share_data.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class FoodShareTests(unittest.TestCase):
    def setUp(self):
        directory = check.BASE / 'adjacent_food_share_by_income'
        with (directory / 'adjacent_food_share_by_income_vertical.csv').open(newline='') as f:
            self.rows = list(csv.DictReader(f))
        self.manifest = json.loads((directory / 'classification.json').read_text())

    def test_snapshot(self):
        self.assertTrue(check.validate())

    def test_zaf_both_decile_observations_survive(self):
        values = {r['variable']: r['value'] for r in self.rows
                  if r['country'] == 'ZAF' and r['year'] == '2023'}
        self.assertEqual(len(values), 20)
        self.assertEqual(values['engel_share:food_income_decile_1'], '30.5')
        self.assertEqual(values['engel_share:food_expenditure_decile_1'], '32.1')
        self.assertEqual(values['engel_share:food_income_decile_10'], '8.4')
        self.assertEqual(values['engel_share:food_expenditure_decile_10'], '7.9')

    def test_hkg_is_four_quartiles(self):
        rows = [r for r in self.rows if r['country'] == 'HKG']
        self.assertEqual(len(rows), 4)
        self.assertEqual({r['bucket_index'] for r in rows}, {'1', '2', '3', '4'})
        self.assertTrue(all(r['stratifier'] == 'expenditure' and r['bucket_type'] == 'quartile'
                            and r['bucket_count'] == '4' for r in rows))

    def test_consumption_and_expenditure_are_distinct(self):
        for country, expected in [('PAK', 'consumption'), ('MDA', 'expenditure'), ('IDN', 'expenditure')]:
            self.assertEqual({r['stratifier'] for r in self.rows if r['country'] == country}, {expected})

    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate observation'):
            check.validate_rows(self.rows + [self.rows[0]], self.manifest)

    def test_wrong_source_grain_rejected(self):
        for field, value in [('stratifier', 'income'), ('bucket_type', 'quintile'), ('bucket_count', '5')]:
            rows = copy.deepcopy(self.rows)
            next(r for r in rows if r['country'] == 'HKG')[field] = value
            with self.assertRaisesRegex(ValueError, 'source classification mismatch'):
                check.validate_rows(rows, self.manifest)

    def test_missing_quintile_rejected(self):
        rows = [r for r in self.rows if not (r['country'] == 'IDN' and r['year'] == '2022'
                                            and r['bucket_index'] == '5')]
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            check.validate_rows(rows, self.manifest)

    def test_original_value_and_source_preserved(self):
        for field in ('value', 'note'):
            rows = copy.deepcopy(self.rows)
            rows[0][field] += 'changed'
            with self.assertRaisesRegex(ValueError, 'original observations'):
                check.validate_rows(rows, self.manifest)

    def test_readme_country_count_and_year_drift_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / 'survey'
            for pack in ('adjacent_food_share_by_income', 'adjacent_food_share_urban_rural'):
                target = base / pack
                target.mkdir(parents=True)
                for path in (check.BASE / pack).iterdir():
                    if path.is_file():
                        shutil.copyfile(path, target / path.name)
            path = base / 'adjacent_food_share_urban_rural/adjacent_food_share_urban_rural_readme.md'
            original = path.read_text()
            for old, new in [('**531 vertical rows**', '**523 vertical rows**'),
                             ('**109 ISO3**', '**107 ISO3**'), ('WSM, XKX, YEM', 'WSM, YEM'),
                             ('**1988–2025**', '**1989–2025**')]:
                self.assertIn(old, original)
                path.write_text(original.replace(old, new))
                with self.assertRaisesRegex(ValueError, 'stale README'):
                    check.validate(base)
            path.write_text(original)
            csvpath = base / 'adjacent_food_share_urban_rural/adjacent_food_share_urban_rural_vertical.csv'
            csvpath.write_bytes(csvpath.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'CSV/gzip mismatch'):
                check.validate(base)
