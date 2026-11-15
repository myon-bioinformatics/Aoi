"""🧭 近い候補の保持（core/neighbors.py）。ベンチマークの -O ガードは tests/test_fleet.py（親の fleet_check.run_main）。

標準ライブラリだけ（docs/neighbor-retention.md）:

    python -S -m unittest discover -s tests -p test_neighbor_retention.py -v
"""
import sys, unittest
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


if __name__=='__main__': unittest.main()
