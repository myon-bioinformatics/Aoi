"""Independent offense-only CSV histogram replay and preceding cutoff cross-check."""
import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['innings','result','cutoff']:p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args()
    pages=defaultdict(dict)
    with gzip.open(a.innings,'rt') as f:
        for r in csv.DictReader(f):
            y=int(r['year'])
            if r['side']!='off' or not 2013<=y<=2025:continue
            team=pages[y,r['url']].setdefault(r['team'],{'home':r['batting_home'] in ['1','True','true'],'scores':{}})
            team['scores'][int(r['inning'])]=int(r['runs'])
    groups=defaultdict(list)
    for (y,url),teams in pages.items():
        assert len(teams)==2
        for t,r in teams.items():
            other=next(v for k,v in teams.items() if k!=t)
            groups[y,t].append((r['home'],r['scores'],other['scores']))
    x=json.loads(a.result.read_text());old=json.loads(a.cutoff.read_text())
    oldrows={(r['year'],r['team']):r for r in old['rows']}
    n=0
    for row in x['rows']:
        gs=groups[row['year'],row['team']]
        for c in [6,7]:
            eligible=[g for g in gs if max(g[1])>=c and max(g[2])>=c]
            assert row['windows'][str(c)]['excluded']==len(gs)-len(eligible)
            for venue in ['all','home','away']:
                subset=[g for g in eligible if venue=='all' or g[0]==(venue=='home')]
                hist=Counter(sum(g[1][i] for i in range(1,c+1)) for g in subset)
                si=sum(g[1][i]>0 for g in subset for i in range(1,c+1))
                v=row['windows'][str(c)]['by_venue'][venue]
                assert v['histogram']=={str(k):val for k,val in hist.items()}
                assert v['G']==len(subset) and v['RF']==sum(k*val for k,val in hist.items()) and v['scoring_innings']==si
                prior=oldrows[row['year'],row['team']]['cutoffs'][str(c)]['by_venue'][venue]
                assert [hist[0],hist[1]+hist[2],sum(val for k,val in hist.items() if k>=3)]==[prior['runs'][label][0] for label in ['0','1-2','3+']]
                col=old['cell_columns'];priorall=dict(zip(col,prior['all']))
                assert v['RF']==sum(sum(g[1].values()) for g in subset)-priorall['late_RF']
                n+=1
        paired=[g for g in gs if max(g[1])>=7 and max(g[2])>=7]
        v=row['paired7']
        expected=dict(G=len(paired),first6_RF=sum(sum(g[1][i] for i in range(1,7)) for g in paired),seventh_RF=sum(g[1][7] for g in paired),first7_RF=sum(sum(g[1][i] for i in range(1,8)) for g in paired),seventh_scoring_games=sum(g[1][7]>0 for g in paired),newly_reached_three=sum(sum(g[1][i] for i in range(1,7))<3<=sum(g[1][i] for i in range(1,8)) for g in paired))
        assert all(v[k]==val for k,val in expected.items())
        for c in ['6','7']:
            peers=[r for r in x['rows'] if r['year']==row['year'] and r['league']==row['league'] and r['team']!=row['team']]
            pv=[p['windows'][c]['by_venue']['all'] for p in peers]
            ours=row['windows'][c]['by_venue']['all'];actual=row['comparison'][c]
            den=sum(p['G'] for p in pv)
            for k,numerator in [('mean_runs','RF'),('zero_rate','zero'),('three_plus_rate','three_plus')]:
                expected_rate=sum(p[numerator] for p in pv)/den
                assert abs(actual['other5_pooled'][k]-expected_rate)<1e-12
                assert abs(actual['gaps'][k]-(ours[k]-expected_rate))<1e-12
            assert actual['mean_runs_rank']==1+sum(p['RF']/p['G']>ours['RF']/ours['G'] for p in pv)
    print(f'Independent direct CSV replay: {n} histograms, preceding cutoff buckets/early totals, 156 paired-seventh groups, 312 peer comparisons match')

if __name__=='__main__':main()
