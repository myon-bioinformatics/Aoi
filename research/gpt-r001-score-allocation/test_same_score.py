import unittest
from same_score import metrics

class SameScoreTests(unittest.TestCase):
    def test_no_decisive_games_are_not_zero_win_rate(self):
        self.assertIsNone(metrics([])['win_rate'])
        self.assertIsNone(metrics([])['we_rate'])
        r=metrics([(0,0,'home','g')])
        self.assertIsNone(r['win_rate'])
        self.assertEqual(r['we_rate'],.5)

    def test_ties_do_not_enter_win_rate_denominator(self):
        r=metrics([(2,1,'home','g'),(2,2,'home','g'),(2,4,'home','g')])
        self.assertEqual((r['g'],r['w'],r['l'],r['d']),(3,1,1,1))
        self.assertEqual(r['win_rate'],.5)

if __name__=='__main__':unittest.main()
