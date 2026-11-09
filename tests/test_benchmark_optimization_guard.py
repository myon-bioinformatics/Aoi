"""Mismatch checks must remain active when Python removes assert statements."""
import subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkGuardTests(unittest.TestCase):
    def test_mismatch_exits_under_optimization_without_reporting_success(self):
        code = "import runpy, types; ns = runpy.run_path('scripts/benchmark_neighbor_retention.py'); ns = ns['main'].__globals__; ns['subprocess'].check_output = lambda *args, **kwargs: b'def discover(rows): return {\"reference\": True}'; ns['neighbors'].discover = lambda rows: {}; ns['main']()"
        result = subprocess.run([sys.executable, '-O', '-S', '-c', code],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('report mismatch', result.stderr)
        self.assertEqual(result.stdout, '')
