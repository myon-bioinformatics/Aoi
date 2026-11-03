"""The narrow lab lane must preserve its plugins, lock and complete test guard."""
import importlib.util
import contextlib
import io
import json
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('lab_nano_check', ROOT / 'scripts/check_lab_nano_environment.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class LabEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.lock = {'package': [{'name': name, 'version': '1.0'}
                                for name in CHECK.EXPECTED | CHECK.OMITTED]}
        self.installed = [(name, '1.0') for name in CHECK.EXPECTED]

    def test_matching_locked_environment(self):
        self.assertTrue(CHECK.inspect_environment(self.lock, self.installed)['valid'])

    def test_missing_plugin_fails(self):
        self.assertFalse(CHECK.inspect_environment(self.lock, [r for r in self.installed if r[0] != 'anyio'])['valid'])

    def test_newly_added_dependency_fails_even_when_locked(self):
        self.lock['package'].append({'name': 'future-runtime', 'version': '1.0'})
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed + [('future-runtime', '1.0')])['valid'])

    def test_restored_heavy_package_fails(self):
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed + [('numpy', '1.0')])['valid'])

    def test_unlocked_version_fails(self):
        self.installed = [(n, '2.0' if n == 'pytest' else v) for n, v in self.installed]
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed)['valid'])

    def test_duplicate_distribution_fails(self):
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed + [('pytest', '1.0')])['valid'])

    def test_package_name_normalization(self):
        rows = [('PyTest' if n == 'pytest' else n, v) for n, v in self.installed]
        self.assertTrue(CHECK.inspect_environment(self.lock, rows)['valid'])

    def test_removed_lock_omission_requires_review(self):
        self.lock['package'] = [p for p in self.lock['package'] if p['name'] != 'numpy']
        self.assertFalse(CHECK.inspect_environment(self.lock, self.installed)['valid'])

    def _run_cli(self, platform, python_version):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock = root / 'uv.lock'
            lock.write_text(''.join(
                f'[[package]]\nname = "{p["name"]}"\nversion = "{p["version"]}"\n'
                for p in self.lock['package']))
            output = root / 'evidence' / 'inventory.json'
            distributions = [SimpleNamespace(metadata={'Name': n}, version=v)
                             for n, v in self.installed]
            with patch.object(CHECK.metadata, 'distributions', return_value=distributions), \
                 patch.object(CHECK.sys, 'platform', platform), \
                 patch.object(CHECK.sys, 'version_info', python_version), \
                 patch.object(CHECK.sys, 'prefix', str(root / 'environment')), \
                 contextlib.redirect_stdout(io.StringIO()):
                status = CHECK.main(['--lock', str(lock), '--output', str(output)])
            return status, json.loads(output.read_text())

    def test_cli_writes_success_evidence(self):
        status, report = self._run_cli('linux', (3, 15))
        self.assertEqual(status, 0)
        self.assertTrue(report['valid'])
        self.assertEqual(len(report['lock_sha256']), 64)
        self.assertEqual(report['environment_regular_file_bytes'], 0)

    def test_cli_rejects_unreviewed_runtime_with_evidence(self):
        for platform, version in [('darwin', (3, 15)), ('linux', (3, 14))]:
            with self.subTest(platform=platform, version=version):
                status, report = self._run_cli(platform, version)
                self.assertEqual(status, 1)
                self.assertFalse(report['valid'])
                self.assertTrue(report['errors'])

    def test_workflow_locks_once_then_runs_without_resync(self):
        text = (ROOT / '.github/workflows/ci.yml').read_text()
        lane = text.split('  lab-integration:', 1)[1].split('  chrome-export:', 1)[0]
        omitted = re.findall(r'--no-install-package ([\w-]+)', lane)
        self.assertEqual(set(omitted), CHECK.OMITTED)
        self.assertEqual(len(omitted), len(CHECK.OMITTED))
        self.assertEqual(lane.count('uv sync --locked --python 3.15'), 1)
        self.assertEqual(lane.count('uv run --locked --no-sync --python 3.15 pytest'), 1)
        self.assertNotIn('uv run --locked --python', lane)
        self.assertIn('--require-blueprobe-lab-integration', lane)
        for node in ('test_optional_real_lab_extractor_reuses_all_calendar_rows',
                     'test_real_saved_npb_fixture_coverage_and_css',
                     'test_verified_cache_real_lab_snapshot_replay'):
            self.assertIn('::' + node, lane)
        self.assertIn('scripts/check_lab_nano_environment.py --output', lane)
        self.assertIn('uv pip check --offline', lane)
        self.assertLess(lane.index('uv sync'), lane.index('check_lab_nano_environment.py'))
        self.assertLess(lane.index('check_lab_nano_environment.py'), lane.index('uv run'))
        self.assertIn('timeout-minutes: 10', lane)
        self.assertIn('AOI_LAB_SOURCE_ROOT', lane)
        self.assertIn('if-no-files-found: error', lane)


if __name__ == '__main__':
    unittest.main()
