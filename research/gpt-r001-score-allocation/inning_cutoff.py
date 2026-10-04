"""End-of-inning conditional outcomes; scoreline walkoff opportunity diagnostics."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pvariance
from inning_features import read_input

INPUT_SHA = '0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb'
SEASON_BLOB = 'fd76d410b7d8d9438237abc751820dcbf95c05e4'


def describe(games, cutoff):
    n = len(games)
    w = sum(g['outcome'] == 'W' for g in games)
    l = sum(g['outcome'] == 'L' for g in games)
    t = n-w-l
    rf = sum(sum(g['ours'][cutoff:]) for g in games)
    ra = sum(sum(g['theirs'][cutoff:]) for g in games)
    oi = sum(len(g['ours'][cutoff:]) for g in games)
    ai = sum(len(g['theirs'][cutoff:]) for g in games)
    net = [sum(g['ours'][cutoff:])-sum(g['theirs'][cutoff:]) for g in games]
    return dict(G=n,W=w,L=l,T=t,win_rate=w/(w+l) if w+l else None,
                draw_rate=t/n if n else None,win_equivalent=(w+0.5*t)/n if n else None,
                late_RF=rf,late_RA=ra,late_off_innings=oi,late_def_innings=ai,
                late_RF_per_inning=rf/oi if oi else None,late_RA_per_inning=ra/ai if ai else None,
                late_net_mean=mean(net) if n else None,late_net_variance=pvariance(net) if n else None,
                late_net_sum=sum(net),late_net_sum_squares=sum(v*v for v in net),
                late_net_positive=sum(v>0 for v in net),late_net_zero=sum(v==0 for v in net),
                late_net_negative=sum(v<0 for v in net))


def cutoff_cells(games, cutoff):
    eligible = [g for g in games if min(len(g['ours']),len(g['theirs']))>=cutoff]
    out = {'excluded_short_games':len(games)-len(eligible),'by_venue':{}}
    for venue in ['all','home','away']:
        subset=[g for g in eligible if venue=='all' or g['home']==(venue=='home')]
        def run_bin(g):
            r=sum(g['ours'][:cutoff])
            return '0' if r==0 else '1-2' if r<=2 else '3+'
        def state(g):
            d=sum(g['ours'][:cutoff])-sum(g['theirs'][:cutoff])
            return 'lead' if d>0 else 'tie' if d==0 else 'trail'
        cells={'all':describe(subset,cutoff), 'runs':{},'state':{},'cross':{}}
        for r in ['0','1-2','3+']:
            cells['runs'][r]=describe([g for g in subset if run_bin(g)==r],cutoff)
            for s in ['lead','tie','trail']:
                cells['cross'][r+'|'+s]=describe([g for g in subset if run_bin(g)==r and state(g)==s],cutoff)
        for s in ['lead','tie','trail']:
            cells['state'][s]=describe([g for g in subset if state(g)==s],cutoff)
        for dimension in ['runs','state','cross']:
            for field in ['G','W','L','T','late_RF','late_RA','late_off_innings','late_def_innings']:
                assert sum(c[field] for c in cells[dimension].values())==cells['all'][field]
        out['by_venue'][venue]=cells
    for field in ['G','W','L','T','late_RF','late_RA','late_off_innings','late_def_innings']:
        assert sum(out['by_venue'][v]['all'][field] for v in ['home','away'])==out['by_venue']['all']['all'][field]
    return out


def walkoffs(games):
    result={}
    for venue in ['home','away']:
        subset=[g for g in games if g['home']==(venue=='home')]
        count=sum(g['walkoff'] for g in subset)
        opportunities=sum(g['opportunity_innings']>0 for g in subset)
        innings=sum(g['opportunity_innings'] for g in subset)
        assert count<=opportunities
        result[venue]=dict(G=len(subset),walkoff_condition_games=count,
            opportunity_games=opportunities,opportunity_innings=innings,
            per_all_games=count/len(subset) if subset else None,
            per_opportunity_game=count/opportunities if opportunities else None,
            per_opportunity_inning=count/innings if innings else None)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['innings','season','out']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if hashlib.sha256(a.innings.read_bytes()).hexdigest()!=INPUT_SHA:raise ValueError('inning hash mismatch')
    raw=a.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=SEASON_BLOB:raise ValueError('season blob mismatch')
    seasons={(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    records,row_count=read_input(a.innings)
    groups=defaultdict(list)
    total_walkoffs=0
    for g in records:
        if not 2013<=g['year']<=2025:continue
        hr,ar=g['home_runs'],g['away_runs']
        walkoff=len(hr)==len(ar) and len(hr)>=9 and sum(hr)>sum(ar) and sum(hr[:-1])<=sum(ar)
        opportunity=sum(i>=8 and sum(hr[:i])<=sum(ar[:i+1]) for i in range(len(hr)))
        assert not walkoff or opportunity>0
        total_walkoffs+=walkoff
        for home in [True,False]:
            ours,theirs=(hr,ar) if home else (ar,hr)
            d=sum(ours)-sum(theirs)
            groups[g['year'],g['home'] if home else g['away']].append(dict(home=home,ours=ours,theirs=theirs,
                outcome='W' if d>0 else 'L' if d<0 else 'T',walkoff=walkoff,opportunity_innings=opportunity))
    rows=[]
    for (year,team),games in sorted(groups.items()):
        s=seasons[year,team]
        actual=dict(G=len(games),W=sum(g['outcome']=='W' for g in games),L=sum(g['outcome']=='L' for g in games),
            T=sum(g['outcome']=='T' for g in games),RF=sum(sum(g['ours']) for g in games),RA=sum(sum(g['theirs']) for g in games))
        if actual!={k:s[k] for k in actual}:raise ValueError(('annual mismatch',year,team))
        rows.append(dict(year=year,team=team,league=s['league'],annual=actual,
            cutoffs={str(c):cutoff_cells(games,c) for c in [6,7]},walkoff=walkoffs(games)))
    assert len(rows)==156
    assert sum(r['walkoff']['home']['walkoff_condition_games'] for r in rows)==total_walkoffs
    assert sum(r['walkoff']['away']['walkoff_condition_games'] for r in rows)==total_walkoffs
    main_games=[g for (y,t),gs in groups.items() if y!=2020 for g in gs]
    result=dict(input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,helper_sha256=hashlib.sha256(Path(__file__).with_name('inning_features.py').read_bytes()).hexdigest(),
        plan_commit='9035ab67e7c70efb71c0a21a03ac8088f5bf18a5',input_rows=row_count,annual_checks=936,
        main_team_years=144,excluded_year=2020,rows=rows,
        main_pooled=dict(cutoffs={str(c):cutoff_cells(main_games,c) for c in [6,7]},walkoff=walkoffs(main_games)))
    # Publish sufficient aggregated counts, not duplicated derived rates or game rows.
    columns = ['G','W','L','T','late_RF','late_RA','late_off_innings','late_def_innings',
               'late_net_sum','late_net_sum_squares','late_net_positive','late_net_zero','late_net_negative']
    result['cell_columns'] = columns
    for row in result['rows']:
        for cut in row['cutoffs'].values():
            for cells in cut['by_venue'].values():
                for dim in ['all','runs','state','cross']:
                    if dim == 'all':
                        cells[dim] = [cells[dim][k] for k in columns]
                    else:
                        cells[dim] = {label:[cell[k] for k in columns] for label,cell in cells[dim].items()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    print('156 annual rows / 936 annual checks; partitions and walkoff mirror verified')

if __name__=='__main__':main()
