"""Describe runs reached by innings six/seven, before interpreting outcomes."""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from inning_features import read_input

INPUT_SHA='0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb'
SEASON_BLOB='fd76d410b7d8d9438237abc751820dcbf95c05e4'


def counts(games,cutoff):
    hist=Counter(sum(g['ours'][:cutoff]) for g in games)
    n=len(games);rf=sum(k*v for k,v in hist.items())
    si=sum(v>0 for g in games for v in g['ours'][:cutoff])
    result=dict(G=n,RF=rf,scoring_innings=si,innings=n*cutoff,
        histogram={str(k):v for k,v in sorted(hist.items())},
        buckets={str(k):hist[k] for k in range(5)}|{'5+':sum(v for k,v in hist.items() if k>=5)},
        zero=hist[0],three_plus=sum(v for k,v in hist.items() if k>=3),
        mean_runs=rf/n if n else None,zero_rate=hist[0]/n if n else None,
        three_plus_rate=sum(v for k,v in hist.items() if k>=3)/n if n else None,
        scoring_rate=si/(n*cutoff) if n else None,rps=rf/si if si else None)
    assert sum(result['buckets'].values())==n
    if si:assert abs(result['mean_runs']-cutoff*result['scoring_rate']*result['rps'])<1e-12
    return result


def window(games,cutoff):
    gs=[g for g in games if min(len(g['ours']),len(g['theirs']))>=cutoff]
    by={v:counts([g for g in gs if v=='all' or g['home']==(v=='home')],cutoff) for v in ['all','home','away']}
    for k in ['G','RF','scoring_innings','innings','zero','three_plus']:
        assert by['all'][k]==by['home'][k]+by['away'][k]
    return dict(excluded=len(games)-len(gs),by_venue=by)


def paired_seventh(games):
    gs=[g for g in games if min(len(g['ours']),len(g['theirs']))>=7]
    n=len(gs);six=sum(sum(g['ours'][:6]) for g in gs);seven=sum(g['ours'][6] for g in gs)
    rf7=sum(sum(g['ours'][:7]) for g in gs);assert six+seven==rf7
    return dict(G=n,first6_RF=six,seventh_RF=seven,first7_RF=rf7,
        first6_mean=six/n if n else None,seventh_mean=seven/n if n else None,first7_mean=rf7/n if n else None,
        seventh_scoring_games=sum(g['ours'][6]>0 for g in gs),
        newly_reached_three=sum(sum(g['ours'][:6])<3<=sum(g['ours'][:7]) for g in gs))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['innings','season','out']:p.add_argument('--'+k,type=Path,required=True)
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
            ours,theirs=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            groups[g['year'],g['home'] if home else g['away']].append(dict(home=home,ours=ours,theirs=theirs))
    rows=[]
    for (year,team),games in sorted(groups.items()):
        s=sm[year,team]
        check=dict(G=len(games),RF=sum(sum(g['ours']) for g in games),RA=sum(sum(g['theirs']) for g in games),
            W=sum(sum(g['ours'])>sum(g['theirs']) for g in games),L=sum(sum(g['ours'])<sum(g['theirs']) for g in games),T=sum(sum(g['ours'])==sum(g['theirs']) for g in games))
        if check!={k:s[k] for k in check}:raise ValueError(('annual mismatch',year,team))
        rows.append(dict(year=year,team=team,league=s['league'],annual=check,windows={str(c):window(games,c) for c in [6,7]},paired7=paired_seventh(games)))
    assert len(rows)==156
    for row in rows:
        peers=[r for r in rows if r['year']==row['year'] and r['league']==row['league'] and r['team']!=row['team']]
        assert len(peers)==5
        row['comparison']={}
        for c in ['6','7']:
            ours=row['windows'][c]['by_venue']['all'];ps=[r['windows'][c]['by_venue']['all'] for r in peers]
            g=sum(r['G'] for r in ps)
            peer=dict(G=g,RF=sum(r['RF'] for r in ps),zero=sum(r['zero'] for r in ps),three_plus=sum(r['three_plus'] for r in ps))
            peer.update(mean_runs=peer['RF']/g,zero_rate=peer['zero']/g,three_plus_rate=peer['three_plus']/g)
            gaps={k:ours[k]-peer[k] for k in ['mean_runs','zero_rate','three_plus_rate']}
            row['comparison'][c]=dict(other5_pooled=peer,gaps=gaps,
                mean_runs_rank=1+sum(r['RF']*ours['G']>ours['RF']*r['G'] for r in ps),
                lower_mean=ours['RF']*g<peer['RF']*ours['G'],
                higher_zero=ours['zero']*g>peer['zero']*ours['G'],
                lower_three_plus=ours['three_plus']*g<peer['three_plus']*ours['G'])
    d=[r for r in rows if r['team']=='d' and r['year']!=2020]
    main={}
    for c in ['6','7']:
        main[c]={}
        for condition in ['lower_mean','higher_zero','lower_three_plus']:
            main[c][condition]=dict(yes_years=[r['year'] for r in d if r['comparison'][c][condition]],
                no_years=[r['year'] for r in d if not r['comparison'][c][condition]])
        main[c]['mean_annual_gaps']={k:sum(r['comparison'][c]['gaps'][k] for r in d)/len(d) for k in ['mean_runs','zero_rate','three_plus_rate']}
    result=dict(plan_commit='96f8205b0647c4fcf811d18ed7afa0417b7f9943',input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,
        helper_sha256=hashlib.sha256(Path(__file__).with_name('inning_features.py').read_bytes()).hexdigest(),
        input_rows=nrows,annual_checks=936,main_team_years=144,rows=rows,chunichi_without2020=main)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    if a.csv:
        a.csv.parent.mkdir(parents=True,exist_ok=True)
        with a.csv.open('w',newline='') as f:
            fields=['year','team','league','cutoff','excluded','G','RF','mean_runs','zero','zero_rate','three_plus','three_plus_rate','n0','n1','n2','n3','n4','n5_plus','mean_runs_rank','other5_mean_runs','other5_zero_rate','other5_three_plus_rate']
            writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
            for row in rows:
                for c in ['6','7']:
                    v=row['windows'][c]['by_venue']['all'];comp=row['comparison'][c]
                    out={k:v[k] for k in ['G','RF','mean_runs','zero','zero_rate','three_plus','three_plus_rate']}
                    out.update(year=row['year'],team=row['team'],league=row['league'],cutoff=c,excluded=row['windows'][c]['excluded'],mean_runs_rank=comp['mean_runs_rank'])
                    out.update({'n'+k.replace('+','_plus'):val for k,val in v['buckets'].items()})
                    out.update({'other5_'+k:comp['other5_pooled'][k] for k in ['mean_runs','zero_rate','three_plus_rate']})
                    writer.writerow(out)
    print('156 team-years / 936 annual checks; fixed-window and seventh-inning identities verified')
    print(json.dumps(main,ensure_ascii=False))
    for r in rows:
        if r['year']==2022 and r['league']=='C':
            print(r['team'],json.dumps({k:r[k] for k in ['windows','comparison','paired7']},ensure_ascii=False))

if __name__=='__main__':main()
