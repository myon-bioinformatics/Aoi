"""Offline research regressions; run explicitly (outside repository pytest testpaths)."""
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import stage_transitions as st


def counts(b,a,l,w=0,draw=0):
    return Counter(B=b,A=a,L=l,W=w,loss=b-w-draw,draw=draw)


def key(team,year=2013,venue='home',deficit=1,scope='preclinch'):
    return scope,year,team,venue,deficit


def reference(home,away,is_home):
    if min(len(home),len(away))<7 or len(away)<=7:return None
    h=sum(home[:7]);a=sum(away[:7]);start=h-a if is_home else a-h
    if start>=0:return None
    level=lead=False
    for i in range(7,len(away)):
        a+=away[i]
        if not is_home:
            level |= a>=h;lead |= a>h
        if i<len(home):
            h+=home[i]
            if is_home:
                level |= h>=a;lead |= h>a
    final=(h-a)*(1 if is_home else -1)
    return -start,dict(B=1,A=int(level),L=int(lead),W=int(final>0),loss=int(final<0),draw=int(final==0))


class TrajectoryTests(unittest.TestCase):
    def test_direct_lead_is_simultaneous_arrival(self):
        h=[1,0,0,0,0,0,0,0,0];a=[0]*7+[2,0]
        self.assertEqual(st.arrivals(h,a,False),(1,dict(B=1,A=1,L=1,W=1,loss=0,draw=0)))

    def test_tie_only_final_draw_stays_in_denominator(self):
        h=[1,0,0,0,0,0,0,0,0];a=[0]*7+[1,0]
        self.assertEqual(st.arrivals(h,a,False)[1],dict(B=1,A=1,L=0,W=0,loss=0,draw=1))

    def test_tie_then_lose_without_leading(self):
        h=[1,0,0,0,0,0,0,1,0];a=[0]*7+[1,0]
        self.assertEqual(st.arrivals(h,a,False)[1],dict(B=1,A=1,L=0,W=0,loss=1,draw=0))

    def test_lead_then_lose(self):
        h=[1,0,0,0,0,0,0,2,0];a=[0]*7+[2,0]
        self.assertEqual(st.arrivals(h,a,False)[1]['W'],0)
        self.assertEqual(st.arrivals(h,a,False)[1]['L'],1)

    def test_repeated_comeback_counted_once(self):
        h=[1,0,0,0,0,0,0,2,0];a=[0]*7+[2,2]
        self.assertEqual(st.arrivals(h,a,False)[1],dict(B=1,A=1,L=1,W=1,loss=0,draw=0))

    def test_extras_included(self):
        h=[1,0,0,0,0,0,0,0,0,0];a=[0]*7+[0,0,2]
        self.assertEqual(st.arrivals(h,a,False)[1]['W'],1)

    def test_unplayed_bottom_not_padded(self):
        h=[0]*7+[2];a=[1,0,0,0,0,0,0,0,0]
        self.assertEqual(st.arrivals(h,a,True)[1]['W'],1)

    def test_cutoff_and_next_top_required(self):
        self.assertIsNone(st.arrivals([0]*7,[1]+[0]*6,True))
        self.assertIsNone(st.arrivals([0]*6,[1]+[0]*7,True))

    def test_not_trailing_excluded(self):
        self.assertIsNone(st.arrivals([0]*9,[0]*9,True))
        self.assertIsNone(st.arrivals([2]+[0]*8,[0]*9,True))

    def test_324_small_trajectories(self):
        n=0
        for deficit,is_home,late in product((1,2),(False,True),product(range(3),repeat=4)):
            own=[0]*7+[late[0],late[2]];opp=[deficit]+[0]*6+[late[1],late[3]]
            h,a=(own,opp) if is_home else (opp,own)
            self.assertEqual(st.arrivals(h,a,is_home),reference(h,a,is_home));n+=1
        # 2 deficits * 2 venues * 3^4 future scores = 324, both definitions checked.
        self.assertEqual(n,324)


class MatchingTests(unittest.TestCase):
    def comp(self,cells,den='B',num='A',years=None,venue='all'):
        return st.compare(cells,'preclinch',years or {2013},venue,den,num)

    def test_target_weighted_not_peer_pooled(self):
        c={key('d'):counts(10,2,0),key('g'):counts(100,90,0),
           key('d',deficit=2):counts(90,18,0),key('g',deficit=2):counts(10,1,0)}
        r=self.comp(c)
        self.assertEqual(r['own_n'],100);self.assertEqual(r['peer_rate'],.18)
        self.assertEqual(r['difference_fraction'],'1/50')
        self.assertEqual(r['peer_common_n'],110)

    def test_stage_zero_peer_is_not_zero_percent(self):
        c={key('d'):counts(1,1,1,1),key('g'):counts(10,0,0)}
        self.assertEqual(self.comp(c)['own_n'],1)
        r=self.comp(c,'A','L')
        self.assertIsNone(r['peer_rate']);self.assertEqual(r['own_unmatched_n'],1)
        self.assertEqual(r['own_unmatched_x'],1)
        self.assertEqual(r['direction'],'unavailable')

    def test_zero_own_stage_not_an_observation(self):
        r=self.comp({key('d'):counts(4,0,0),key('g'):counts(4,2,1)},'A','L')
        self.assertEqual(r['own_all_n'],0);self.assertIsNone(r['own_coverage'])

    def test_exact_year_deficit_and_venue_not_coarsened(self):
        for peer in (key('g',year=2014),key('g',venue='away'),key('g',deficit=2)):
            r=self.comp({key('d'):counts(1,1,1),peer:counts(9,9,9)},years={2013,2014})
            self.assertEqual(r['own_n'],0);self.assertEqual(r['own_unmatched_n'],1)

    def test_peers_pooled_within_stratum(self):
        r=self.comp({key('d'):counts(10,5,2),key('g'):counts(1,1,1),key('t'):counts(9,0,0)})
        self.assertEqual(r['peer_rate'],.1)

    def test_stage_weights_change(self):
        c={key('d'):counts(10,1,1),key('g'):counts(10,5,5),
           key('d',deficit=2):counts(10,9,0),key('g',deficit=2):counts(10,5,0)}
        self.assertEqual(self.comp(c,'A','L')['peer_rate'],.1)
        self.assertEqual(self.comp(c,'B','L')['peer_rate'],.25)

    def test_equal_direction_uses_exact_fraction(self):
        r=self.comp({key('d'):counts(3,1,0),key('g'):counts(9,3,0)})
        self.assertEqual(r['difference_fraction'],'0/1');self.assertEqual(r['direction'],'equal')

    def test_peer_common_counts_not_all_peer_counts(self):
        c={key('d'):counts(2,1,0),key('g'):counts(4,2,0),key('g',deficit=8):counts(7,0,0)}
        r=self.comp(c);self.assertEqual(r['peer_all_n'],11);self.assertEqual(r['peer_common_n'],4)

    def test_venue_sensitivity(self):
        c={key('d'):counts(1,1,1),key('g'):counts(2,0,0),
           key('d',venue='away'):counts(2,0,0),key('g',venue='away'):counts(2,2,0)}
        self.assertEqual(self.comp(c,venue='home')['own_n'],1)
        self.assertEqual(self.comp(c,venue='away')['own_n'],2)


class ValidationTests(unittest.TestCase):
    def test_annual_scope_frozen(self):
        self.assertEqual(set(st.DATES),set(range(2013,2026))-{2020})

    def test_date_inclusive_and_exclusions(self):
        g=dict(url='https://npb.jp/bis/2013/games/s2013092500001.html',year=2013,home='d',away='g',
               home_runs=[0]*9,away_runs=[1]+[0]*8)
        c,e=st.aggregate([g])
        self.assertIn(key('d',scope='preclinch'),c)
        g=dict(g,url='https://npb.jp/bis/2013/games/s2013092600001.html')
        c,e=st.aggregate([g]);self.assertFalse(any(k[0]=='preclinch' for k in c))
        self.assertTrue(any(k[0]=='full_season' for k in c))

    def test_eligibility_reasons_preserved(self):
        gs=[dict(url=f'https://npb.jp/bis/2013/games/s201309250000{i}.html',year=2013,home='d',away='g',
                 home_runs=[0]*n,away_runs=[1]+[0]*(n-1)) for i,n in enumerate((6,7,9))]
        _,e=st.aggregate(gs);r=e['preclinch',2013,'d','home']
        self.assertEqual([r[f] for f in st.ELIGIBLE],[3,1,1,1,1])

    def test_counter_corruption_rejected(self):
        with self.assertRaisesRegex(ValueError,'reference count'):
            st.verify_cells({key('d'):counts(2,1,0)}, {key('d'):counts(2,0,0)},st.COUNTS)

    def test_invalid_order_and_partition_rejected(self):
        for c in (counts(1,2,0),Counter(B=1,A=1,L=1,W=1,loss=1,draw=0)):
            with self.assertRaises(ValueError):st.check_counts(c)

    def test_wrong_input_stops_before_creating_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);bad=root/'bad';bad.write_bytes(b'invalid');out=root/'output'
            r=subprocess.run([sys.executable,str(Path(st.__file__)),'--innings',str(bad),
                              '--official',str(bad),'--out',str(out)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0);self.assertFalse(out.exists())
            self.assertIn('inning hash mismatch',r.stderr)

    def test_compare_audit_rejects_mutation(self):
        cells={key('d'):counts(3,1,0),key('g'):counts(9,3,0)}
        r=dict(scope='preclinch',period='2013',venue='all',denominator='B',numerator='A',
               **st.compare(cells,'preclinch',{2013},'all','B','A'))
        r['own_x']+=1
        with self.assertRaisesRegex(ValueError,'comparison counts'):
            st.verify_comparisons(cells,[r])


if __name__=='__main__':unittest.main()
