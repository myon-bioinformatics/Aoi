"""Independent off-row chronological replay and direct-weight comparison check."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import gzip
import json
from pathlib import Path


def verify(innings, output):
    result=json.loads(output.read_text())
    games=defaultdict(dict)
    with gzip.open(innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or int(r['year'])>2025:continue
            t=games[int(r['year']),r['url']].setdefault(r['team'],dict(home=r['batting_home']=='True',runs={}))
            t['runs'][int(r['inning'])]=int(r['runs'])
    counts=defaultdict(Counter)
    for (year,_),teams in games.items():
        h=next(t for t,v in teams.items() if v['home']);a=next(t for t in teams if t!=h)
        hr,ar=teams[h]['runs'],teams[a]['runs']
        score={h:0,a:0};states={h:{},a:{}};cuts={}
        for i in range(1,max(ar)+1):
            score[a]+=ar[i];states[a][i]=score[a]-score[h]
            if i in hr:score[h]+=hr[i];states[h][i]=score[h]-score[a]
            if i in (6,7) and i in hr and i+1 in ar:cuts[i]=dict(score)
        for team,other in ((h,a),(a,h)):
            own=teams[team]['runs'];opp=teams[other]['runs']
            for cut,early in cuts.items():
                if early[team]>=early[other]:continue
                ds=[v for i,v in states[team].items() if i>cut]
                rf=sum(v for i,v in own.items() if i>cut)
                highest=max(ds,default=-999)
                category='led' if highest>0 else 'level_never_led' if highest==0 else 'never_level' if rf>0 else 'no_runs'
                final=score[team]-score[other]
                c=counts[year,team,cut,team==h,early[other]-early[team]]
                c.update(G=1,level_or_better=int(highest>=0),W=int(final>0),L=int(final<0),T=int(final==0),
                         late_RF=rf,late_RA=sum(v for i,v in opp.items() if i>cut),off_innings=sum(i>cut for i in own))
                c[category]+=1
    fields=['G','level_or_better','led','W','L','T','no_runs','never_level','level_never_led','late_RF','late_RA','off_innings']
    assert len(counts)==len(result['cells'])
    for r in result['cells']:
        key=tuple(r[k] for k in ['year','team','cutoff','home','deficit'])
        assert all(r[f]==counts[key][f] for f in fields),key
    checks=0
    for comparison in result['yearly']+result['pooled']:
        own=defaultdict(Counter);peer=defaultdict(Counter)
        for r in result['cells']:
            if r['year'] not in comparison['years'] or r['league']!=comparison['league'] or r['cutoff']!=comparison['cutoff']:continue
            if comparison['venue']!='all' and r['home']!=(comparison['venue']=='home'):continue
            m=r['deficit'] if comparison['margin']=='exact' else min(3,r['deficit'])
            target=own if r['team']==comparison['team'] else peer
            target[r['year'],r['home'],m].update({f:r[f] for f in fields})
        shared=set(own)&set(peer);n=sum(own[k]['G'] for k in shared)
        assert n==comparison['common_own_G']
        for metric in ('level_or_better','led','W'):
            numerator=sum(own[k][metric] for k in shared)
            expected=Fraction(0)
            for k in shared:expected+=Fraction(peer[k][metric],peer[k]['G'])*own[k]['G']
            observed=comparison['metrics'][metric]
            assert numerator==observed['own_count']
            if n:
                delta=(numerator-expected)/n
                assert [delta.numerator,delta.denominator]==observed['difference_fraction']
            else:assert observed['difference'] is None
            checks+=1
    return dict(status='passed',source_games=len(games),cell_rows=len(counts),integer_values=len(counts)*len(fields),weighted_metric_comparisons=checks,
                scope='separate CSV off-row replay and rational weighting; same source, not independent HTML acquisition')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('innings','result','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();report=verify(a.innings,a.result)
    a.out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
