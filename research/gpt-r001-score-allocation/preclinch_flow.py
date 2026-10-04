"""Pool game-state transitions through each Chunichi clinch date, inclusive."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from inning_features import read_input, require
from game_state import build
from clinch_interval import date
from matched_comeback import trajectory, INPUT_SHA, SEASON_BLOB

CL={'d','g','t','c','db','s'}
STATES=('lead','tie','trail','unavailable')
CATEGORIES=('no_runs','never_level','level_never_led','led')


def aggregate(games, dates):
    cells=defaultdict(Counter)
    for g in games:
        y=g['year']
        if y not in dates or date(g['url'])>dates[y]:continue
        for home in (True,False):
            team=g['home'] if home else g['away']
            if team not in CL:continue
            own,opp=(g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            final=sum(own)-sum(opp);outcome='W' if final>0 else 'L' if final<0 else 'T'
            for cut in (6,7):
                state='unavailable';category='not_trailing'
                if min(len(own),len(opp))>=cut and len(g['away_runs'])>cut:
                    margin=sum(own[:cut])-sum(opp[:cut])
                    state='lead' if margin>0 else 'trail' if margin<0 else 'tie'
                    if state=='trail':
                        t=trajectory(g['home_runs'],g['away_runs'],home,cut)
                        category=next(k for k in CATEGORIES if t[1][k])
                cells[y,team,cut,state,category].update(G=1,**{outcome:1})
    return [dict(year=y,team=t,cutoff=c,state=s,category=k,**{f:v[f] for f in ('G','W','L','T')})
            for (y,t,c,s,k),v in sorted(cells.items())]


def summarize(rows):
    def total(rs):return {f:sum(r[f] for r in rs) for f in ('G','W','L','T')}
    result=dict(total=total(rows),states={s:total([r for r in rows if r['state']==s]) for s in STATES},
                trailing={c:total([r for r in rows if r['category']==c]) for c in CATEGORIES})
    for f in ('G','W','L','T'):
        require(sum(r[f] for r in result['states'].values())==result['total'][f],'state partition')
        require(sum(r[f] for r in result['trailing'].values())==result['states']['trail'][f],'trajectory partition')
    require(result['total']['G']==sum(result['total'][f] for f in ('W','L','T')),'outcome partition')
    return result


def analyze(rows):
    periods=[('no2020',set(range(2013,2026))-{2020}),('with2020',set(range(2013,2026)))]+[(str(y),{y}) for y in range(2013,2026)]
    return [dict(period=p,cutoff=c,own=summarize([r for r in rows if r['year'] in ys and r['cutoff']==c and r['team']=='d']),
                 peer=summarize([r for r in rows if r['year'] in ys and r['cutoff']==c and r['team']!='d']))
            for p,ys in periods for c in (6,7)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('innings','season','dates','out','csv'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();build(a.innings,a.season)
    ds=json.loads(a.dates.read_text());require(all(y['exact'] for y in ds['years']),'unresolved dates')
    dates={y['year']:y['date'] for y in ds['years']}
    games,n=read_input(a.innings);rows=aggregate(games,dates)
    result=dict(schema='aoi-preclinch-flow/1',plan_commit=ds['plan_commit'],input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,
                annual_checks=936,input_rows=n,dates=dates,year2026=ds['year2026'],comparisons=analyze(rows))
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    with a.csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps(result['comparisons'][1],ensure_ascii=False))


if __name__=='__main__':main()
