"""Mismatch checks must remain active when Python removes assert statements."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkGuardTests(unittest.TestCase):
    def test_mismatch_exits_under_optimization_without_reporting_success(self):
        code = "import runpy, types; ns = runpy.run_path('scripts/benchmark_accessible_walk.py'); ns = ns['main'].__globals__; ns['names']._walk = lambda root: iter(()); ns['main']()"
        result = subprocess.run([sys.executable, '-O', '-S', '-c', code],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('traversal mismatch', result.stderr)
        self.assertEqual(result.stdout, '')
