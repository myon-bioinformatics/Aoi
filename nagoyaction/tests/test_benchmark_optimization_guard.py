"""Parity guards must execute without requiring git history, even under -O."""
import subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptimizedBenchmarkTests(unittest.TestCase):
    def test_mismatch_stops_without_success_json(self):
        code = "import runpy; ns = runpy.run_path('scripts/benchmark_link_case_index.py'); ns = ns['main'].__globals__; ns['subprocess'].check_output = lambda *a, **kw: b'def check_local(*a, **kw): return [1]'; ns['linkcheck'].check_local = lambda *a, **kw: []; ns['main']()"
        result = subprocess.run([sys.executable, '-O', '-S', '-c', code],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('link report mismatch', result.stderr)
        self.assertEqual(result.stdout, '')
