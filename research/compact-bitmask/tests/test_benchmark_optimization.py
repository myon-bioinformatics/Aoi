"""Fault injection must stop measurement, including when assertions are stripped."""
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BenchmarkOptimizationTests(unittest.TestCase):
    def test_all_parity_guards_survive_optimization(self):
        for target, diagnostic in (
            ('CompactRule.evaluate_dense', 'dense evaluation mismatch'),
            ('FeatureLayout.decode', 'packed roundtrip mismatch'),
            ('CompactRule.evaluate_source', 'timed evaluation mismatch'),
        ):
            code = f'''
import runpy
ns = runpy.run_path('benchmark.py')['run'].__globals__
owner, method = {target!r}.split('.')
setattr(ns[owner], method, lambda *a, **kw: object())
ns['run']()
'''
            with self.subTest(target=target):
                result = subprocess.run([sys.executable, '-O', '-S', '-c', code],
                                        cwd=ROOT, capture_output=True, text=True, timeout=30)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(diagnostic, result.stderr)
                self.assertEqual(result.stdout, '')
