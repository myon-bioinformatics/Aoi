"""Independent off-row reconstruction of date-filtered aggregate transitions."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re


def verify(innings, result, cells):
    x=json.loads(result.read_text())
    assert hashlib.sha256(innings.read_bytes()).hexdigest()==x['input_sha256']
    groups=defaultdict(dict)
    with gzip.open(innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or r['year'] not in x['dates']:continue
            m=re.search(r's(\d{4})(\d{2})(\d{2})\d*\.html',r['url']) or re.search(r'/scores/(\d{4})/(\d{2})(\d{2})/',r['url'])
            day='-'.join(m.groups())
            if day>x['dates'][r['year']]:continue
            key=(int(r['year']),r['url']);home=r['batting_home']=='True'
            team=groups[key].setdefault(home,dict(team=r['team'],league=r['league'],innings={}))
            team['innings'][int(r['inning'])]=int(r['runs'])
    expected=defaultdict(Counter)
    for (year,url),pair in groups.items():
        assert set(pair)=={True,False}
        for home,own in pair.items():
            if own['league']!='CL':continue
            for cut in (6,7):
                scores={True:0,False:0};margin=None;scored=0;level=False;led=False
                for inning in range(1,max(pair[False]['innings'])+1):
                    for side in (False,True):
                        if inning not in pair[side]['innings']:continue
                        runs=pair[side]['innings'][inning];scores[side]+=runs
                        if inning>cut and side==home:
                            scored+=runs
                            level|=scores[home]>=scores[not home]
                            led|=scores[home]>scores[not home]
                    if inning==cut and inning in pair[True]['innings']:margin=scores[home]-scores[not home]
                final=scores[home]-scores[not home];out='W' if final>0 else 'L' if final<0 else 'T'
                state='unavailable';category='not_trailing'
                if margin is not None and max(pair[False]['innings'])>cut:
                    state='lead' if margin>0 else 'trail' if margin<0 else 'tie'
                    if state=='trail':category='led' if led else 'level_never_led' if level else 'never_level' if scored else 'no_runs'
                expected[year,own['team'],cut,state,category].update(G=1,**{out:1})
    with cells.open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==len(expected)
    for r in rows:
        key=(int(r['year']),r['team'],int(r['cutoff']),r['state'],r['category'])
        assert {k:int(r[k]) for k in ('G','W','L','T')}=={k:expected[key][k] for k in ('G','W','L','T')},key
    checks=0
    for c in x['comparisons']:
        p=c['period'];ys={int(p)} if p.isdigit() else set(range(2013,2026))-({2020} if p=='no2020' else set())
        for name in ('own','peer'):
            subset=[(k,v) for k,v in expected.items() if k[0] in ys and k[2]==c['cutoff'] and (k[1]=='d')==(name=='own')]
            for field in ('G','W','L','T'):
                assert c[name]['total'][field]==sum(v[field] for k,v in subset);checks+=1
                for section,pos in (('states',3),('trailing',4)):
                    for label,value in c[name][section].items():
                        assert value[field]==sum(v[field] for k,v in subset if k[pos]==label);checks+=1
    return dict(status='passed',method='independent chronological off-row score accumulation',cells=len(rows),integer_cells=len(rows)*4,summary_checks=checks,
                independence='same source CSV, independent aggregation; not independent raw acquisition')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('innings','result','cells','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();v=verify(a.innings,a.result,a.cells);a.out.write_text(json.dumps(v,indent=2)+'\n');print(v)


if __name__=='__main__':main()
