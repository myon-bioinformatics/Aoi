"""Independent score accumulation, cell partitions and prior denominator checks."""
import argparse
from collections import Counter,defaultdict
import csv,gzip,json
from pathlib import Path


def verify(innings,csv_path,result_path,previous):
    pages=defaultdict(dict)
    with gzip.open(innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or int(r['year'])>2025:continue
            g=pages[int(r['year']),r['url']].setdefault(r['team'],{'home':r['batting_home']=='True','runs':{}})
            g['runs'][int(r['inning'])]=int(r['runs'])
    counts=defaultdict(Counter)
    for (year,_),teams in pages.items():
        h=next(t for t in teams if teams[t]['home']);a=next(t for t in teams if t!=h)
        scores={h:0,a:0};cuts={}
        for i in sorted(teams[a]['runs']):
            scores[a]+=teams[a]['runs'][i]
            if i in teams[h]['runs']:scores[h]+=teams[h]['runs'][i]
            if i in (6,7) and i in teams[h]['runs'] and i+1 in teams[a]['runs']:cuts[i]=dict(scores)
        for cut,early in cuts.items():
            for t,o in ((h,a),(a,h)):
                c=counts[year,t,cut,t==h,early[t]-early[o]];final=scores[t]-scores[o]
                c.update(G=1,W=int(final>0),L=int(final<0),T=int(final==0),
                         late_RF=scores[t]-early[t],late_RA=scores[o]-early[o],
                         off_innings=sum(i>cut for i in teams[t]['runs']),def_innings=sum(i>cut for i in teams[o]['runs']))
    fields=('G','W','L','T','late_RF','late_RA','off_innings','def_innings')
    with csv_path.open() as f: rows=list(csv.DictReader(f))
    assert len(counts)==len(rows)
    for r in rows:
        for k in ('year','cutoff','margin',*fields):r[k]=int(r[k])
        r['home']=r['home']=='True'
        key=tuple(r[k] for k in ('year','team','cutoff','home','margin'))
        assert all(r[f]==counts[key][f] for f in fields),key
    x=json.loads(result_path.read_text());checked=0
    for c in x['comparisons']:
        years={int(c['period'])} if c['period'].isdigit() else set(range(2013,2026)) - ({2020} if c['period']=='no2020' else set())
        selected=[r for r in rows if r['year'] in years and r['cutoff']==c['cutoff'] and (c['venue']=='all' or r['home']==(c['venue']=='home'))]
        for side in ('own','peer'):
            subset=[r for r in selected if (r['team']==c['team'] if side=='own' else r['league']==c['league'] and r['team']!=c['team'])]
            bins=defaultdict(Counter);states=defaultdict(Counter);all_=Counter()
            for r in subset:
                m=r['margin'];b='-3+' if m<=-3 else '3+' if m>=3 else str(m);s='lead' if m>0 else 'trail' if m<0 else 'tie'
                values={f:r[f] for f in fields};bins[b].update(values);states[s].update(values);all_.update(values)
            checks=[(c[side]['all'],all_)]+[(v,bins[k]) for k,v in c[side]['bins'].items()]+[(v,states[k]) for k,v in c[side]['states'].items()]
            for actual,expected in checks:
                assert all(actual[f]==expected[f] for f in fields)
                assert actual['share']==(expected['G']/all_['G'] if all_['G'] else None)
                assert actual['win_fraction']==(expected['W']/expected['G'] if expected['G'] else None)
                checked+=1
        for key,state,rate,sign in [('S1','trail','share',1),('S2','lead','share',-1),('S3','lead','win_fraction',-1)]:
            p=c['propositions'][key];oa,ob=p['own'];pa,pb=p['peer']
            expected=(oa/ob-pa/pb) if ob and pb else None
            assert p['difference']==expected
            assert p['verdict']==('unavailable' if expected is None else 'supports_direction' if (oa*pb-pa*ob)*sign>0 else 'counterexample')
    old=json.loads(previous.read_text());prior_checks=0
    for r in old['cells']:
        c=counts[r['year'],r['team'],r['cutoff'],r['home'],-r['deficit']]
        assert all(c[f]==r[f] for f in ('G','W','L','T','late_RF','late_RA','off_innings'));prior_checks+=1
    return dict(status='passed',source_games=len(pages),cell_rows=len(rows),integer_values=len(rows)*len(fields),summary_groups=checked,previous_trailing_cells=prior_checks,
                scope='independent accumulation of same shared CSV; no separate raw HTML retrieval')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('innings','csv','result','previous','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=verify(a.innings,a.csv,a.result,a.previous);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(r)


if __name__=='__main__':main()
