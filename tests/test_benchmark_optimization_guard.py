"""Parity guards must execute without requiring git history, even under -O."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OptimizedBenchmarkTests(unittest.TestCase):
    def test_mismatch_stops_without_success_json(self):
        code = "import runpy; ns = runpy.run_path('scripts/benchmark_record_selection.py'); ns = ns['main'].__globals__; ns['subprocess'].check_output = lambda *a, **kw: b'def select_items(*a, **kw): return [1]'; ns['records'].select_items = lambda *a, **kw: []; ns['main']()"
        result = subprocess.run([sys.executable, '-O', '-S', '-c', code],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('selection mismatch', result.stderr)
        self.assertEqual(result.stdout, '')
