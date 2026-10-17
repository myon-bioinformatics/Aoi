"""Independent CSV-off-row replay of cutoff counts (does not import main/helper)."""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--innings',type=Path,required=True)
    ap.add_argument('--result',type=Path,required=True)
    a=ap.parse_args()
    raw=defaultdict(dict)
    with gzip.open(a.innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or not 2013<=int(r['year'])<=2025:continue
            key=(int(r['year']),r['url'])
            team=r['team']
            raw[key].setdefault(team,{'home':r['batting_home'],'runs':{}})['runs'][int(r['inning'])]=int(r['runs'])
    groups=defaultdict(list)
    for (year,url),teams in raw.items():
        assert len(teams)==2
        vals=list(teams.items())
        for team,v in vals:
            other=next(o for t,o in vals if t!=team)
            # Input uses 1/0 (accept boolean spellings explicitly, no truthy strings).
            assert v['home'] in ['1','0','True','False','true','false']
            home=v['home'] in ['1','True','true']
            ours=[v['runs'][i] for i in range(1,max(v['runs'])+1)]
            theirs=[other['runs'][i] for i in range(1,max(other['runs'])+1)]
            hr,ar=(ours,theirs) if home else (theirs,ours)
            home_sofar=0;away_sofar=0;opp=0;last_before=None
            for i,awayrun in enumerate(ar,1):
                away_sofar+=awayrun
                if i<=len(hr):
                    if i>=9 and home_sofar<=away_sofar:opp+=1
                    last_before=home_sofar
                    home_sofar+=hr[i-1]
            walkoff=int(len(hr)==len(ar) and len(hr)>=9 and home_sofar>away_sofar and last_before<=away_sofar)
            groups[year,team].append((home,ours,theirs,opp,walkoff))
    x=json.loads(a.result.read_text());assert len(groups)==156
    checked=0
    for row in x['rows']:
        games=groups[row['year'],row['team']]
        for venue in ['home','away']:
            gs=[g for g in games if g[0]==(venue=='home')]
            w=row['walkoff'][venue]
            assert [len(gs),sum(g[3]>0 for g in gs),sum(g[3] for g in gs),sum(g[4] for g in gs)]==[w['G'],w['opportunity_games'],w['opportunity_innings'],w['walkoff_condition_games']]
        for c in [6,7]:
            cut=row['cutoffs'][str(c)]
            gs=[g for g in games if len(g[1])>=c and len(g[2])>=c]
            assert len(games)-len(gs)==cut['excluded_short_games']
            for venue in ['all','home','away']:
                bins=defaultdict(lambda:[0]*13)
                for home,o,t,_,_ in gs:
                    if venue!='all' and home!=(venue=='home'):continue
                    total_o,total_t=sum(o),sum(t)
                    front_o,front_t=sum(o[:c]),sum(t[:c])
                    r='0' if front_o==0 else '1-2' if front_o<=2 else '3+'
                    state='lead' if front_o>front_t else 'tie' if front_o==front_t else 'trail'
                    net=sum(o[c:])-sum(t[c:])
                    counts=[1,int(total_o>total_t),int(total_o<total_t),int(total_o==total_t),sum(o[c:]),sum(t[c:]),len(o[c:]),len(t[c:]),net,net*net,int(net>0),int(net==0),int(net<0)]
                    for label in ['all','runs:'+r,'state:'+state,'cross:'+r+'|'+state]:
                        bins[label]=[v+n for v,n in zip(bins[label],counts)]
                actual=cut['by_venue'][venue]
                assert actual['all']==bins['all'];checked+=1
                for dim in ['runs','state','cross']:
                    for label,values in actual[dim].items():
                        assert values==bins[dim+':'+label],(row['year'],row['team'],c,venue,dim,label)
                        checked+=1
    print(f'Independent replay: {checked} cells / {checked*13} integer values and 312 walkoff venue aggregates match')

if __name__=='__main__':main()
