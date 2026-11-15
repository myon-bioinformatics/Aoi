"""🧭 近い候補の保持（core/neighbors.py）と、そのベンチマーク（scripts/benchmark_neighbor_retention.py）の -O ガード。

旧 test_benchmark_optimization_guard.py もここにまとめた。標準ライブラリだけ（docs/neighbor-retention.md）:

    python -S -m unittest discover -s tests -p test_neighbor_retention.py -v
"""
import subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'core'))  # neighbors.py は core/（python -S -m unittest でも読める）
import neighbors  # noqa: E402


class NeighborRetentionTests(unittest.TestCase):
    def test_ties_exclusions_and_empty(self):
        rows=[{'team':t,'season':2024,'league':'L','upper_half':upper,
               'rf_adv':value,'ra_adv':0,'vs_lower_wpct':0}
              for t,upper,value in [('z',True,0),('b',False,1),('a',False,-1)]]
        result=neighbors.discover(rows)
        self.assertEqual([p['units'] for p in result['pairs']], [['a-2024','z-2024'],['b-2024','z-2024']])
        self.assertEqual(neighbors.discover(rows,excluded=[2024])['pairs'],[])
        self.assertEqual(neighbors.discover([])['pairs'],[])
        self.assertEqual(neighbors.discover(rows,limit=1)['pairs'],result['pairs'][:1])
        self.assertEqual(rows[0]['team'],'z')


# ==== -O ガード（旧 test_benchmark_optimization_guard.py）: assert を外す -O でも不一致の検査が効く

class BenchmarkGuardTests(unittest.TestCase):
    def test_mismatch_exits_under_optimization_without_reporting_success(self):
        code = "import runpy, types; ns = runpy.run_path('scripts/benchmark_neighbor_retention.py'); ns = ns['main'].__globals__; ns['subprocess'].check_output = lambda *args, **kwargs: b'def discover(rows): return {\"reference\": True}'; ns['neighbors'].discover = lambda rows: {}; ns['main']()"
        result = subprocess.run([sys.executable, '-O', '-S', '-c', code],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('report mismatch', result.stderr)
        self.assertEqual(result.stdout, '')


if __name__=='__main__': unittest.main()
