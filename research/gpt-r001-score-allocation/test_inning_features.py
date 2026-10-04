import csv
import gzip
import itertools
import tempfile
import unittest
from pathlib import Path
from inning_features import aggregate, features, zero_probability, read_input, FIELDS


class InningFeaturesTests(unittest.TestCase):
    def test_sequence_and_concentration(self):
        f=features([0,1,0,2,0,0])
        self.assertEqual((f['scoring_innings'],f['max_zero_run'],f['leading_zeros'],
                          f['trailing_zeros'],f['scoring_clusters']),(2,2,1,2,2))
        self.assertEqual((f['first_scoring_inning'],f['last_scoring_inning']),(2,4))
        self.assertAlmostEqual(f['inning_run_hhi'],5/9)
        self.assertGreater(features([0,0,3,0])['inning_run_hhi'],f['inning_run_hhi'])

    def test_no_score_is_not_missing_or_infinite(self):
        a=aggregate([[0]*8,[0]*9])
        self.assertEqual(a['zero_scoring_game_rate'],1)
        self.assertIsNone(a['runs_per_scoring_inning'])
        self.assertIsNone(a['mean_max_inning_share_given_scored'])
        self.assertIsNone(a['transition_11_rate'])
        self.assertEqual(a['transition_from_0_n'],15)
        self.assertEqual(a['innings'],17)  # no zero-filled ninth inning

    def test_transition_does_not_cross_games(self):
        a=aggregate([[0,1],[1,0]])
        self.assertEqual(a['transition_11_n'],0)
        self.assertEqual(a['transition_01_n'],1)
        self.assertEqual(a['transition_10_n'],1)
        self.assertEqual(a['first3_eligible_games'],0)
        self.assertIsNone(a['first3_scoreless_rate'])

    def test_hypergeometric_matches_enumeration(self):
        placements=list(itertools.combinations(range(6),2))
        actual=sum(not ({0,1,2}&set(s)) for s in placements)/len(placements)
        self.assertAlmostEqual(zero_probability(6,2,3),actual)
        self.assertEqual(zero_probability(6,6,3),0)
        self.assertEqual(zero_probability(6,0,3),1)

    def fixture(self, duplicate=False, bad_mirror=False, gap=False):
        url='https://npb.jp/bis/2024/games/s2024032901088.html'
        rows=[]
        for t,opp,home,seq in [('g','t',True,[0,1]),('t','g',False,[1,0])]:
            for i,r in enumerate(seq,1):
                for team,side in [(t,'off'),(opp,'def')]:
                    rows.append([2024,team,'CL',str(home),side,i+1 if gap else i,
                                 r+1 if bad_mirror and side=='def' else r,url])
        if duplicate:rows.append(rows[0])
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        p=Path(temp.name)/'input.csv.gz'
        with gzip.open(p,'wt',newline='') as f:
            w=csv.writer(f);w.writerow(FIELDS);w.writerows(rows)
        return p

    def test_duplicate_mirror_gap_fail_closed(self):
        for kw in [{'duplicate':True},{'bad_mirror':True},{'gap':True}]:
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                read_input(self.fixture(**kw))

    def test_mirrored_rows_are_counted_once(self):
        games,rows=read_input(self.fixture())
        self.assertEqual(rows,8)
        self.assertEqual(len(games),1)
        self.assertEqual(games[0]['home_runs'],[0,1])
        self.assertEqual(sum(games[0]['home_runs']),1)


if __name__=='__main__':unittest.main()
