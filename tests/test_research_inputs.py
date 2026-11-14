"""Research inputs: food-share classification snapshots, recovered input identity checks and the standalone subscription-pack regressions."""

import copy
import csv
import hashlib
import importlib.util
import io
import json
import re
import runpy
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from scripts.research_inputs import validate_member_path, validated_zip


# ═══ · food share data ═══════════════════════════════════════════════════════════════════════════════════
# Snapshot and adversarial regressions for research food-share classification.

spec = importlib.util.spec_from_file_location('food_share_check', ROOT / 'scripts/research_inputs.py')
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


# ═══ · recovered inputs ══════════════════════════════════════════════════════════════════════════════════
# Offline identity/classification checks, not independent NPB source verification.

RECOVERY = ROOT / "cycles/c001-chunichi/recovered-inputs"
CATALOG = json.loads((RECOVERY / "manifest.json").read_text(encoding="utf-8"))


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _reject_constant(value):
    raise ValueError(f"Non-standard JSON constant: {value}")


def _json(content):
    return json.loads(content, parse_constant=_reject_constant)


def _rows(content):
    return [_json(line) for line in content.splitlines()]


def test_original_archives_and_supplement_member_manifest():
    for item in CATALOG["archives"]:
        content = (ROOT / item["repository_path"]).read_bytes()
        assert len(content) == item["bytes"]
        assert _sha(content) == item["sha256"]
        with validated_zip(io.BytesIO(content)) as archive:
            assert archive.testzip() is None
            assert len(archive.namelist()) == item["members"]
            assert len(set(archive.namelist())) == len(archive.namelist())
            assert not any("synthetic" in name.lower() for name in archive.namelist())
            if item["classification"] == "real_observation_source_package":
                seen = set()
                for line in archive.read("MANIFEST.sha256").decode().splitlines():
                    match = re.fullmatch(r"([0-9a-f]{64})  (.+)  \((\d+) bytes\)", line)
                    assert match is not None
                    digest, name, size = match.groups()
                    payload = archive.read(name)
                    assert _sha(payload) == digest
                    assert len(payload) == int(size)
                    seen.add(name)
                assert len(seen) == 35
                assert seen == set(archive.namelist()) - {"MANIFEST.sha256"}


def test_preserved_games_are_not_silently_cleaned_or_renamed():
    item = CATALOG["archives"][0]
    selected = item["selected_member"]
    payload = (ROOT / selected["repository_path"]).read_bytes()
    with validated_zip(ROOT / item["repository_path"]) as archive:
        assert payload == archive.read(selected["path"])
    assert len(payload) == selected["bytes"]
    assert _sha(payload) == selected["sha256"]
    records = _json(payload)
    assert isinstance(records, list) and len(records) == 12574
    assert min(row["date"] for row in records) == "20130329"
    assert max(row["date"] for row in records) == "20261003"
    assert len({row["url"] for row in records}) == len(records)
    counts = {status: sum(row["status"] == status for row in records)
              for status in ("final", "cancelled", "noGame")}
    assert counts == {"final": 12111, "cancelled": 389, "noGame": 72}
    assert sum(row["status"].startswith("other:") for row in records) == 2
    assert sum(row["home"] is None or row["away"] is None for row in records) == 420
    assert CATALOG["queryu_observation_games_jsonl_recovered"] is False
    assert CATALOG["game_page_html_cache_recovered"] is False
    assert CATALOG["raw_html_published_by_this_change"] is False
    assert CATALOG["annual_page_html_in_excluded_mixed_archives"] is True


def test_annual_panel_reuses_exact_existing_bytes_and_saved_totals_match():
    item = CATALOG["archives"][1]
    selected = item["selected_member"]
    payload = (ROOT / selected["existing_repository_path"]).read_bytes()
    assert _sha(payload) == selected["sha256"]
    assert len(payload) == selected["bytes"]
    with validated_zip(ROOT / item["repository_path"]) as archive:
        for member in selected["paths"]:
            assert archive.read(member) == payload
        original = _json(archive.read("input-manifest.json"))
        assert original["inputs"]["season.jsonl"] == _sha(payload)
        assert original["raw_source_replayed"] is False
        acquisition = _rows(archive.read(item["linescore_provenance_member"]["path"]))
        assert len(acquisition) == 858
        assert all(set(row) == {"url", "status", "bytes", "fetched_at", "key", "group", "sha256"}
                   for row in acquisition)
    rows = _rows(payload)
    assert len(rows) == 168 and all(len(row) == 409 for row in rows)
    index = {(row["season"], row["team"]): row for row in rows}
    assert len(index) == 168
    assert {year for year, _ in index} == set(range(2012, 2026))
    assert all(sum(y == year for y, _ in index) == 12 for year in range(2012, 2026))
    with validated_zip(ROOT / CATALOG["archives"][0]["repository_path"]) as archive:
        summary = csv.DictReader(io.StringIO(
            archive.read("data/part2/team_season_summary.csv").decode("utf-8-sig")))
        comparisons = 0
        for row in summary:
            key = (int(row["year"]), row["team"])
            if key not in index:
                continue
            for source, target in [("G", "G"), ("W", "W"), ("L", "L"), ("T", "T"), ("R", "RF"), ("RA", "RA")]:
                assert int(row[source]) == index[key][target]
                comparisons += 1
        assert comparisons == 936


def test_synthetic_archive_has_only_classified_preserved_synthetic_members():
    item = CATALOG["synthetic_separation"]
    payload = (ROOT / item["repository_path"]).read_bytes()
    assert _sha(payload) == item["sha256"] and len(payload) == item["bytes"]
    with validated_zip(io.BytesIO(payload)) as archive:
        assert archive.testzip() is None
        manifest = _json(archive.read("MANIFEST.json"))
        assert manifest["classification"] == "synthetic_experiments_only_not_observed_NPB_games"
        assert len(manifest["files"]) == 330
        seen = set()
        game_files = game_records = 0
        for entry in manifest["files"]:
            validate_member_path(entry["source_member"])
            validate_member_path(entry["source_archive"])
            assert entry["source_member"].startswith("data/synthetic/")
            assert entry["unchanged_from_source"] is True
            assert entry["path"] == Path(entry["source_archive"]).stem + "/" + entry["source_member"]
            content = archive.read(entry["path"])
            assert len(content) == entry["bytes"] and _sha(content) == entry["sha256"]
            seen.add(entry["path"])
            if entry["path"].endswith(".games.jsonl"):
                game_files += 1
                rows = _rows(content)
                assert all(row["synthetic"] is True for row in rows)
                game_records += len(rows)
            elif entry["path"].endswith(".json"):
                parsed = _json(content)
                if entry["path"].endswith(".annual.json"):
                    assert parsed["synthetic"] is True
        assert seen == set(archive.namelist()) - {"README.txt", "MANIFEST.json"}
        assert game_files == 162 and game_records == 110016


# ═══ · staple subscription evidence ══════════════════════════════════════════════════════════════════════
# Collect the standalone subscription-pack regressions in ordinary repository CI.

_PACK = (Path(__file__).resolve().parents[1] / 'research' / 'staple-price-survey'
         / 'adjacent_subscription_engel_shares')
EvidenceTests = runpy.run_path(str(_PACK / 'test_subscription_engel_shares.py'))['EvidenceTests']
