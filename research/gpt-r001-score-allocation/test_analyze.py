"""Check interpretation-changing edge cases, independently of NPB access."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("score_allocation", Path(__file__).with_name("analyze.py"))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class ScorePairingTests(unittest.TestCase):
    def test_ties_are_half_a_win_with_fixed_denominator(self):
        games = [(2, 1, "home", "g"), (0, 8, "away", "g"), (2, 2, "home", "g")]
        r = a.describe(games)
        self.assertEqual((r["w"], r["l"], r["d"], r["actual_we"]), (1, 1, 1, 1.5))
        self.assertEqual(r["actual_we_rate"], .5)
        self.assertEqual(r["r"] - r["ra"], -7)

    def test_reference_agrees_with_two_exact_permutations(self):
        # Two equiprobable pairings yield WE=1 and WE=0; exact mean is 0.5.
        games = [(2, 1, "home", "g"), (0, 3, "home", "g")]
        r = a.shuffle_reference(games, "side", 4000, 10)
        self.assertAlmostEqual(r["shuffle_mean_we"], .5, delta=.03)
        self.assertEqual((r["shuffle_low_we"], r["shuffle_high_we"]), (0, 1))
        self.assertEqual(r["excess_we"], 1 - r["shuffle_mean_we"])

    def test_home_and_opponent_strata_are_not_crossed(self):
        by_side = [(2, 1, "home", "g"), (0, 3, "away", "g")]
        by_opponent = [(2, 1, "home", "g"), (0, 3, "home", "t")]
        for games, mode in [(by_side, "side"), (by_opponent, "side_opponent")]:
            r = a.shuffle_reference(games, mode, 100, 10)
            self.assertEqual(r["excess_we"], 0)
            self.assertEqual(r["shuffle_mean_mcse"], 0)

    def test_shuffling_can_change_ties_but_not_totals(self):
        # Original (1,1),(2,2) and swapped (1,2),(2,1) both have WE=1.
        r = a.shuffle_reference([(1, 1, "home", "g"), (2, 2, "home", "g")], "side", 100, 20)
        self.assertEqual(r["shuffle_mean_we"], 1)
        self.assertEqual(r["excess_we"], 0)

    def test_2020_removal_never_bridges_2019_to_2021(self):
        rows = [{"year": y, "team": "d", "excess_rate": v}
                for y, v in [(2018, .1), (2019, .2), (2020, .5), (2021, -.2), (2022, .1)]]
        self.assertEqual(a.lag_summary(rows)["n"], 4)
        self.assertEqual(a.lag_summary(rows, True)["n"], 2)

    def test_duplicate_and_incomplete_data_rejected(self):
        g = {"key": "20130401", "date": "2013-04-01", "home": "d", "away": "g", "hs": 2, "as": 1}
        with self.assertRaisesRegex(ValueError, "duplicate"):
            a.units([g, g])
        with self.assertRaisesRegex(ValueError, "incomplete"):
            a.units([g])


if __name__ == "__main__":
    unittest.main()
