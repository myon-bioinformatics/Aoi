"""Overlap benchmark checks survive -O in both controller and worker."""
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/benchmark_overlap.py'

class BenchmarkValidationTests(unittest.TestCase):
    def test_parity_in_both_interpreter_modes(self):
        for optimized in (False, True):
            for worker in (False, True):
                for mismatch in (False, True):
                    with self.subTest(optimized=optimized, worker=worker, mismatch=mismatch):
                        code = r'''
import json, runpy, sys, tempfile, types
from pathlib import Path
from unittest.mock import patch
script, worker, mismatch = sys.argv[1], sys.argv[2] == 'True', sys.argv[3] == 'True'
g = runpy.run_path(script)['main'].__globals__
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for name in ('season.jsonl', 'propositions.jsonl'):
        (root / name).write_text('[]')
    if worker:
        overlap = types.ModuleType('dragowing.overlap')
        overlap.default_conditions = lambda *args: []
        answers = iter([{'regions': []}, {'regions': [1] if mismatch else []}])
        overlap.load_overlap = lambda *args, **kwargs: next(answers)
        records = types.ModuleType('dragowing.records')
        records.read_jsonl = lambda *args: []
        with patch.dict(sys.modules, {'dragowing.overlap': overlap, 'dragowing.records': records}):
            g['worker'](types.SimpleNamespace(results=root, worker='stdlib', warm_repeats=1))
    else:
        g['platform'].platform()
        def report(backend, digest):
            return types.SimpleNamespace(stdout=json.dumps(dict(
                backend=backend, canonical_sha256=digest,
                cold_seconds=1, warm_median_seconds=1, python_peak_bytes=1, process_peak_rss_bytes=1)))
        with patch.object(g['subprocess'], 'run', side_effect=[report('native', 'same'), report('stdlib', 'other' if mismatch else 'same')]), patch.object(sys, 'argv', [script, '--results', tmp, '--repeats', '1']):
            g['main']()
'''
                        result = subprocess.run(
                            [sys.executable, '-S', *(['-O'] if optimized else []), '-c', code,
                             str(SCRIPT), str(worker), str(mismatch)],
                            capture_output=True, text=True, timeout=30,
                        )
                        if mismatch:
                            self.assertEqual(result.returncode, 1, result.stderr)
                            self.assertEqual(result.stdout, '')
                            self.assertIn('result mismatch' if worker else 'backend JSON differs', result.stderr)
                        else:
                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertTrue(result.stdout.startswith('{'))

if __name__ == '__main__':
    unittest.main()
