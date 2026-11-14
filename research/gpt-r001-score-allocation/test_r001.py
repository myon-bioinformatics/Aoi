"""R001 の集計・取得の検査（旧 test_*.py の 6 本をまとめた）。

    python -m unittest research/gpt-r001-score-allocation/test_r001.py

CI の pytest の対象（tests/）には入れていない（旧ファイルと同じ）。
"""

import argparse
import csv
import gzip
import itertools
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

import analyses as a  # noqa: E402
from analyses import features, inning_features_aggregate as aggregate, INNING_FEATURES_FIELDS as FIELDS, metrics, read_input, split, zero_probability  # noqa: E402
from fetch import cell, inning_pilot_parse as test_inning_pilot_parse, observe_parse as test_observe_parse  # noqa: E402


# ==== test_analyze（旧 test_analyze.py）

class ScorePairingTests(unittest.TestCase):
    def test_ties_are_half_a_win_with_fixed_denominator(self):
        games = [(2, 1, "home", "g"), (0, 8, "away", "g"), (2, 2, "home", "g")]
        r = a.analyze_describe(games)
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


def test_analyze(argv=None):
    """Check interpretation-changing edge cases, independently of NPB access.
    """
    unittest.test_analyze_main()


# ==== test_inning_features（旧 test_inning_features.py）

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


def test_inning_features(argv=None):
    unittest.test_inning_features_main()


# ==== test_inning_pilot（旧 test_inning_pilot.py）

class InningPilotTests(unittest.TestCase):
    def test_x_is_not_a_zero_run_inning(self):
        self.assertEqual(cell('X','home',True),{'runs':None,'played':False,'completed':False})
        self.assertEqual(cell('0','home',True),{'runs':0,'played':True,'completed':True})

    def test_walkoff_runs_are_retained_but_incomplete(self):
        self.assertEqual(cell('２ｘ','home',True),{'runs':2,'played':True,'completed':False})

    def test_unknown_or_misplaced_cells_fail(self):
        for value,side,last in [('?', 'home',True),('X','away',True),('1X','home',False),('', 'home',True)]:
            with self.assertRaises(ValueError):cell(value,side,last)

    def test_wrong_score_is_rejected(self):
        def row(name,values):
            return '<tr><td class="gmscoreteam">'+name+'</td>'+''.join('<td class="gmscore">'+v+'</td>' for v in values)+'</tr>'
        html='<div id="gmdivresult"><table>'+row('中日',['0']*9+['-','1','0','0'])+row('東京ヤクルト',['0']*8+['X','-','0','0','0'])+'</table></div>'
        with self.assertRaisesRegex(ValueError,'total'):
            test_inning_pilot_parse(html,{'away':'d','home':'s','as':1,'hs':0})

    def test_scoreboard_rows_match_modest_parser(self):
        # Values locked to selectolax 0.4.13 Modest HTMLParser on the same fragments.
        def cells(vals):
            parts=[]
            for i,v in enumerate(vals):
                parts.append('<td class="gmscore">'+v+'</td>')
                if i in (2,5):
                    parts.append('<td class="gmscspan"><br /></td>')
            return ''.join(parts)
        real=('<div id="gmdivresult"><table>'
              '<tr><td class="gmscorettl" colspan="13"><br /></td><td class="gmscorettl">Ｒ</td></tr>'
              '<tr><td class="gmscoreteam">阪　神</td>'+cells(['0']*9)+'<td align="center" class="gmscore">-</td><td align="center" class="gmscore">0</td><td class="gmscore">4</td><td class="gmscore">0</td></tr>'
              '<tr><td class="gmscoreteam">読　売</td>'+cells(['0','0','0','0','3','0','0','1','X'])+'<td align="center" class="gmscore">-</td><td align="center" class="gmscore">4</td><td class="gmscore">10</td><td class="gmscore">1</td></tr>'
              '</table></div>')
        rows=test_inning_pilot_parse(real,{'away':'t','home':'g','as':0,'hs':4})
        self.assertEqual([(r['team'],r['side']) for r in rows],[('t','away'),('g','home')])
        self.assertEqual([c['runs'] for c in rows[0]['cells']],[0]*9)
        self.assertEqual([c['runs'] for c in rows[1]['cells']],[0,0,0,0,3,0,0,1,None])
        self.assertEqual(rows[1]['cells'][-1],{'runs':None,'played':False,'completed':False})
        marked=('<div id="gmdivresult"><table>'
                '<tr><td class="gmscoreteam">中　日</td>'+cells([' 0 ','\n1\n','２','0','0','0','0','0','<span>0</span>'])+'<td class="gmscore">-</td><td class="gmscore">3</td><td class="gmscore">8</td><td class="gmscore">1</td></tr>'
                '<tr><td class="gmscoreteam"> 東京ヤクルト </td>'+cells(['0']*8+['２ｘ'])+'<td class="gmscore">-</td><td class="gmscore">2</td><td class="gmscore">9</td><td class="gmscore">0</td></tr>'
                '</table></div>')
        rows=test_inning_pilot_parse(marked,{'away':'d','home':'s','as':3,'hs':2})
        self.assertEqual([(r['team'],r['side']) for r in rows],[('d','away'),('s','home')])
        self.assertEqual([c['runs'] for c in rows[0]['cells']],[0,1,2,0,0,0,0,0,0])
        self.assertTrue(all(c['played'] and c['completed'] for c in rows[0]['cells']))
        self.assertEqual([c['runs'] for c in rows[1]['cells']],[0,0,0,0,0,0,0,0,2])
        self.assertEqual(rows[1]['cells'][-1],{'runs':2,'played':True,'completed':False})


def test_inning_pilot(argv=None):
    unittest.test_inning_pilot_main()


# ==== test_loss_tail（旧 test_loss_tail.py）

class LossTailTests(unittest.TestCase):
    def test_cap_definition_includes_body_of_large_scores(self):
        self.assertEqual(split([0,2],[2,10],6),(5,3,2))

    def test_invalid_stage_exit_64(self):
        p=subprocess.run([sys.executable,str(HERE/"analyses.py"),"loss_tail","invalid-stage"],capture_output=True,text=True)
        self.assertEqual(p.returncode,64)

    def test_missing_input_exit_66(self):
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,str(HERE/'analyses.py'),'loss_tail','analyze','--games',str(Path(d)/'absent.jsonl')],capture_output=True,text=True)
            self.assertEqual(p.returncode,66)
            self.assertEqual(json.loads(p.stderr)['exit_code'],66)

    def test_bad_manifest_exit_65(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'games.jsonl'
            path.write_text('')
            path.with_suffix('.manifest.json').write_text('{}')
            verify=Path(d)/'verification.json';verify.write_text('{}')
            p=subprocess.run([sys.executable,str(HERE/'analyses.py'),'loss_tail','analyze','--games',str(path),'--verification',str(verify)],capture_output=True,text=True)
            self.assertEqual(p.returncode,65)

    def test_existing_engine_returns_objection_not_success(self):
        sys.path[:0]=[str(HERE.parents[1]/'PythDRagoras'),str(HERE.parents[1]/'PythDRagoras'/'logic')]
        import polars as pl
        import propositions as pr
        prop=pr.load(HERE/'tail_propositions.toml')[0][0]
        rows=[dict(season=2000+i,team='d',team_name='d',away_more=True,tail_dominates=False,gap=5,body_gap=3,tail_gap=2) for i in range(12)]
        result=pr.evaluate(prop,pl.DataFrame(rows))
        self.assertEqual(result['judgement']['code'],3)
        forms={x['form']:x for x in result['forms']}
        self.assertEqual(len(forms['original']['counterexamples']),12)
        self.assertEqual(len(forms['contrapositive']['counterexamples']),12)


def test_loss_tail(argv=None):
    """Verify exit contracts with real child processes, including intentional failures.
    """
    unittest.test_loss_tail_main()


# ==== test_observe（旧 test_observe.py）

class CompetitionTests(unittest.TestCase):
    def test_same_day_regular_and_postseason_are_separated_by_labels(self):
        html = '''<div class="stvsteam"><div class="tescheaten">CS ファーストS</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>
        <div class="stvsteam"><div><a href="/bis/2013/games/s2013101200002.html">楽 3 - 2 オ</a></div></div>'''
        report, excluded = test_observe_parse(html, "https://npb.jp/example")
        self.assertEqual(len(report["records"]), 1)
        self.assertEqual(report["records"][0]["home"], "e")
        self.assertEqual(excluded[0]["label"], "CS ファーストS")

    def test_allstar_abbreviations_are_excluded_with_evidence(self):
        html = '''<div class="stvsteam"><div class="tescheaten">オールスター</div>
        <div><a href="/bis/2013/games/s2013071900001.html">パ 2 - 2 セ</a></div></div>'''
        report, excluded = test_observe_parse(html, "https://npb.jp/example")
        self.assertEqual(report["unknown"], [])
        self.assertEqual(len(excluded), 1)

    def test_unknown_label_is_not_silently_discarded(self):
        html = '''<div class="stvsteam"><div class="tescheaten">未知大会</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>'''
        with self.assertRaisesRegex(ValueError, "unclassified"):
            test_observe_parse(html, "https://npb.jp/example")

    def test_2020_single_stage_cs_label(self):
        html = '''<div class="stvsteam"><div class="tescheaten">クライマックスS</div>
        <div><a href="/bis/2020/games/s2020111400001.html">ソ 2 - 1 ロ</a></div></div>'''
        report, excluded = test_observe_parse(html, "https://npb.jp/example")
        self.assertEqual(len(report["records"]), 0)
        self.assertEqual(excluded[0]["label"], "クライマックスS")


def test_observe(argv=None):
    """Real-world failure shape, with synthetic scores (not republished source rows).
    """
    unittest.test_observe_main()


# ==== test_same_score（旧 test_same_score.py）

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


def test_same_score(argv=None):
    unittest.test_same_score_main()


if __name__ == "__main__":
    unittest.main()
