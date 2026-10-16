"""Late runs, outcome-conditioned gradients, and whether a losing comeback reached parity."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from inning_features import read_input

INPUT_SHA='0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb'
SEASON_BLOB='fd76d410b7d8d9438237abc751820dcbf95c05e4'
COLUMNS=['G','W','L','T','early_RF','early_RA','reg_RF','reg_RA','extra_RF','extra_RA',
         'reg_off_innings','reg_def_innings','extra_off_innings','extra_def_innings',
         'reg_zero','reg_one','reg_two','reg_three_plus','all_late_positive']
CLASSES=['no_late_runs','scored_never_tied','tied_never_led','led_then_lost']


def annotate(g,c):
    o,t=g['ours'],g['theirs'];early_o,early_t=sum(o[:c]),sum(t[:c]);delta=early_o-early_t
    state='lead' if delta>0 else 'tie' if delta==0 else 'trail'
    reg_o,reg_t=sum(o[c:9]),sum(t[c:9]);extra_o,extra_t=sum(o[9:]),sum(t[9:])
    rf_late=reg_o+extra_o;ra_late=reg_t+extra_t
    assert early_o+rf_late==sum(o) and early_t+ra_late==sum(t)
    category=None
    if state=='trail' and g['outcome']=='L':
        if rf_late==0:category='no_late_runs'
        else:
            # At the end of our top half the opponent's same-inning bottom is unplayed.
            differences=[sum(o[:i+1])-sum(t[:i+1 if g['home'] else i]) for i in range(c,len(o))]
            category='led_then_lost' if any(d>0 for d in differences) else 'tied_never_led' if any(d==0 for d in differences) else 'scored_never_tied'
    return dict(**g,state=state,early_RF=early_o,early_RA=early_t,reg_RF=reg_o,reg_RA=reg_t,
        extra_RF=extra_o,extra_RA=extra_t,reg_off_innings=len(o[c:9]),reg_def_innings=len(t[c:9]),
        extra_off_innings=len(o[9:]),extra_def_innings=len(t[9:]),category=category)


def summary(gs):
    n=len(gs)
    result=dict(G=n,W=sum(g['outcome']=='W' for g in gs),L=sum(g['outcome']=='L' for g in gs),T=sum(g['outcome']=='T' for g in gs))
    for k in COLUMNS[4:14]:result[k]=sum(g[k] for g in gs)
    for k,predicate in [('reg_zero',lambda n:n==0),('reg_one',lambda n:n==1),('reg_two',lambda n:n==2),('reg_three_plus',lambda n:n>=3)]:
        result[k]=sum(predicate(g['reg_RF']) for g in gs)
    result['all_late_positive']=sum(g['reg_RF']+g['extra_RF']>0 for g in gs)
    assert sum(result[k] for k in ['reg_zero','reg_one','reg_two','reg_three_plus'])==n
    return [result[k] for k in COLUMNS]


def categories(gs):
    out={}
    for margin in ['all','1','2','3+']:
        subset=[g for g in gs if g['category'] is not None and (margin=='all' or str(min(g['early_RA']-g['early_RF'],3))+('+' if g['early_RA']-g['early_RF']>=3 else '')==margin)]
        out[margin]={}
        for label in CLASSES:
            selected=[g for g in subset if g['category']==label]
            out[margin][label]=[len(selected),sum(g['early_RA']-g['early_RF'] for g in selected),
                sum(g['reg_RF']+g['extra_RF'] for g in selected),sum(g['reg_RA']+g['extra_RA'] for g in selected)]
        assert sum(v[0] for v in out[margin].values())==len(subset)
    for label in CLASSES:
        assert out['all'][label]==[sum(out[m][label][i] for m in ['1','2','3+']) for i in range(4)]
    return out


def window(gs,c):
    selected=[annotate(g,c) for g in gs if min(len(g['ours']),len(g['theirs']))>=c]
    result={'excluded':len(gs)-len(selected),'by_venue':{}}
    for venue in ['all','home','away']:
        vs=[g for g in selected if venue=='all' or g['home']==(venue=='home')]
        v=dict(all=summary(vs),by_outcome={o:summary([g for g in vs if g['outcome']==o]) for o in ['W','L','T']},
            by_state={s:summary([g for g in vs if g['state']==s]) for s in ['lead','tie','trail']},
            cross={s+'|'+o:summary([g for g in vs if g['state']==s and g['outcome']==o]) for s in ['lead','tie','trail'] for o in ['W','L','T']},
            losing_comeback=categories(vs),joint_by_outcome={})
        for outcome in ['W','L','T']:
            cells={}
            for early in ['0','1-2','3+']:
                for late in ['0','1','2','3+']:
                    cells[early+'|'+late]=sum(('0' if g['early_RF']==0 else '1-2' if g['early_RF']<=2 else '3+')==early and ('3+' if g['reg_RF']>=3 else str(g['reg_RF']))==late for g in vs if g['outcome']==outcome)
            assert sum(cells.values())==v['by_outcome'][outcome][0]
            v['joint_by_outcome'][outcome]=cells
        for dim in ['by_outcome','by_state','cross']:
            assert [sum(a[i] for a in v[dim].values()) for i in range(len(COLUMNS))]==v['all']
        assert sum(a[0] for a in v['losing_comeback']['all'].values())==v['cross']['trail|L'][0]
        result['by_venue'][venue]=v
    for i in range(len(COLUMNS)):
        assert result['by_venue']['all']['all'][i]==sum(result['by_venue'][v]['all'][i] for v in ['home','away'])
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['innings','season','out']:p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--plan-commit',required=True)
    p.add_argument('--csv',type=Path)
    a=p.parse_args()
    if hashlib.sha256(a.innings.read_bytes()).hexdigest()!=INPUT_SHA:raise ValueError('inning hash mismatch')
    raw=a.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SEASON_BLOB:raise ValueError('season blob mismatch')
    sm={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    records,nrows=read_input(a.innings);groups=defaultdict(list)
    for g in records:
        if not 2013<=g['year']<=2025:continue
        for home in [True,False]:
            o,t=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            d=sum(o)-sum(t)
            groups[g['year'],g['home'] if home else g['away']].append(dict(home=home,ours=o,theirs=t,outcome='W' if d>0 else 'L' if d<0 else 'T'))
    rows=[]
    for (year,team),gs in sorted(groups.items()):
        s=sm[year,team]
        annual=dict(G=len(gs),RF=sum(sum(g['ours']) for g in gs),RA=sum(sum(g['theirs']) for g in gs),
            W=sum(g['outcome']=='W' for g in gs),L=sum(g['outcome']=='L' for g in gs),T=sum(g['outcome']=='T' for g in gs))
        if annual!={k:s[k] for k in annual}:raise ValueError(('annual mismatch',year,team))
        rows.append(dict(year=year,team=team,league=s['league'],annual=annual,cutoffs={str(c):window(gs,c) for c in [6,7]}))
    assert len(rows)==156
    dcomparisons=[]
    for r in rows:
        if r['team']!='d':continue
        result=dict(year=r['year'],cutoffs={})
        for c in ['6','7']:
            own=r['cutoffs'][c]['by_venue']['all'];peers=[p['cutoffs'][c]['by_venue']['all'] for p in rows if p['year']==r['year'] and p['league']=='C' and p['team']!='d']
            n=own['cross']['trail|L'][0];yes=own['losing_comeback']['all']['scored_never_tied'][0]
            pn=sum(v['cross']['trail|L'][0] for v in peers);py=sum(v['losing_comeback']['all']['scored_never_tied'][0] for v in peers)
            result['cutoffs'][c]=dict(behind_then_lost_G=n,scored_never_tied_G=yes,rate=yes/n if n else None,
                other5_G=pn,other5_scored_never_tied_G=py,other5_rate=py/pn if pn else None,
                higher_than_other5=yes*pn>py*n if n and pn else None)
        dcomparisons.append(result)
    result=dict(plan_commit=a.plan_commit,input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,
        helper_sha256=hashlib.sha256(Path(__file__).with_name('inning_features.py').read_bytes()).hexdigest(),
        input_rows=nrows,annual_checks=936,main_team_years=144,columns=COLUMNS,
        category_columns=['G','early_deficit_sum','all_late_RF','all_late_RA'],rows=rows,chunichi_comparisons=dcomparisons)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    if a.csv:
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        with a.csv.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['year','team','league','cutoff','outcome']+COLUMNS,lineterminator='\n');writer.writeheader()
            for row in rows:
                for c in ['6','7']:
                    for outcome,values in row['cutoffs'][c]['by_venue']['all']['by_outcome'].items():
                        writer.writerow(dict(year=row['year'],team=row['team'],league=row['league'],cutoff=c,outcome=outcome,**dict(zip(COLUMNS,values))))
    print('156 team-years / 936 annual checks; outcome, state, venue and comeback partitions verified')
    for r in rows:
        if r['year']==2022 and r['team'] in ['d','c']:
            for c in ['6','7']:
                v=r['cutoffs'][c]['by_venue']['all']
                print(r['team'],c,'outcomes',v['by_outcome'],'comeback',v['losing_comeback'])

if __name__=='__main__':main()
