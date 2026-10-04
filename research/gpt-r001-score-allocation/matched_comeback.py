"""Descriptive late-comeback comparison on common year/deficit/venue strata."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from inning_features import read_input, require
from late_reaction import INPUT_SHA, SEASON_BLOB

CATEGORIES = ('no_runs', 'never_level', 'level_never_led', 'led')
METRICS = ('level_or_better', 'led', 'W')
FIELDS = ('G', 'level_or_better', 'led', 'W', 'L', 'T', 'no_runs', 'never_level',
          'level_never_led', 'late_RF', 'late_RA', 'off_innings')


def trajectory(home_runs, away_runs, home, cutoff):
    """Requires play beyond cutoff; detects parity-or-better, not exact tie visits."""
    if min(len(home_runs), len(away_runs)) < cutoff or len(away_runs) <= cutoff:
        return None
    own, opp = (home_runs, away_runs) if home else (away_runs, home_runs)
    deficit = sum(opp[:cutoff]) - sum(own[:cutoff])
    if deficit <= 0:
        return None
    differences = [sum(own[:i+1]) - sum(opp[:i+1 if home else i])
                   for i in range(cutoff, len(own))]
    level = any(d >= 0 for d in differences)
    lead = any(d > 0 for d in differences)
    rf, ra = sum(own[cutoff:]), sum(opp[cutoff:])
    final = sum(own)-sum(opp)
    category = 'led' if lead else 'level_never_led' if level else 'never_level' if rf else 'no_runs'
    result = {k: 0 for k in FIELDS}
    result.update(G=1, level_or_better=int(level), led=int(lead), W=int(final>0),
                  L=int(final<0), T=int(final==0), late_RF=rf, late_RA=ra,
                  off_innings=len(own)-cutoff)
    result[category] = 1
    return deficit, result


def build(innings, season):
    require(hashlib.sha256(innings.read_bytes()).hexdigest() == INPUT_SHA, 'inning hash mismatch')
    raw = season.read_bytes()
    require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == SEASON_BLOB, 'season blob mismatch')
    seasons = {(s['season'],s['team']):s for s in map(json.loads,raw.decode().splitlines())}
    games, input_rows = read_input(innings)
    annual = defaultdict(Counter)
    cells = defaultdict(Counter)
    eligibility = defaultdict(Counter)
    for g in games:
        if g['year'] > 2025:
            continue
        for home in (False, True):
            team = g['home'] if home else g['away']
            own, opp = (g['home_runs'],g['away_runs']) if home else (g['away_runs'],g['home_runs'])
            final = sum(own)-sum(opp)
            annual[g['year'],team].update(G=1,RF=sum(own),RA=sum(opp),W=int(final>0),L=int(final<0),T=int(final==0))
            for cutoff in (6,7):
                e = eligibility[g['year'],team,cutoff]
                e['all_games'] += 1
                if min(len(own),len(opp)) < cutoff:
                    e['cutoff_not_both_present'] += 1
                    continue
                if len(g['away_runs']) <= cutoff:
                    e['no_next_top'] += 1
                    continue
                e['continued'] += 1
                t = trajectory(g['home_runs'],g['away_runs'],home,cutoff)
                if t is not None:
                    deficit, values = t
                    e['behind'] += 1
                    cells[g['year'],team,seasons[g['year'],team]['league'],cutoff,home,deficit].update(values)
    require(len(annual)==156, 'team-year coverage')
    for k, a in annual.items():
        require(dict(a)=={f:seasons[k][f] for f in a}, 'annual count mismatch')
    rows=[]
    for (year,team,league,cutoff,home,deficit), c in sorted(cells.items()):
        require(sum(c[k] for k in CATEGORIES)==c['G'], 'category partition')
        require(c['W']+c['L']+c['T']==c['G'], 'outcome partition')
        require(c['W']<=c['led']<=c['level_or_better']<=c['G'], 'arrival ordering')
        rows.append(dict(year=year,team=team,league=league,cutoff=cutoff,home=home,deficit=deficit,**{f:c[f] for f in FIELDS}))
    eligible=[dict(year=y,team=t,cutoff=c,**v) for (y,t,c),v in sorted(eligibility.items())]
    return rows, eligible, input_rows


def compare(rows, team, league, years, cutoff, venue='all', margin='exact'):
    selected=[r for r in rows if r['year'] in years and r['league']==league and r['cutoff']==cutoff
              and (venue=='all' or r['home']==(venue=='home'))]
    ours, peers=defaultdict(Counter),defaultdict(Counter)
    for r in selected:
        key=(r['year'],r['home'],r['deficit'] if margin=='exact' else min(r['deficit'],3))
        target=ours if r['team']==team else peers
        target[key].update({f:r[f] for f in FIELDS})
    common=[k for k in ours if peers[k]['G']]
    own_all=sum(c['G'] for c in ours.values()); peer_all=sum(c['G'] for c in peers.values())
    n=sum(ours[k]['G'] for k in common)
    results={}
    for metric in METRICS:
        own=sum(ours[k][metric] for k in common)
        expected=sum((Fraction(ours[k]['G']*peers[k][metric],peers[k]['G']) for k in common),Fraction())
        delta=Fraction(own,n)-expected/n if n else None
        results[metric]=dict(own_count=own,own_rate=own/n if n else None,
            peer_expected_count=float(expected),peer_standardized_rate=float(expected/n) if n else None,
            difference=float(delta) if delta is not None else None,
            difference_fraction=[delta.numerator,delta.denominator] if delta is not None else None,
            direction='lower' if delta is not None and delta<0 else 'not_lower' if delta is not None else 'unavailable',
            own_unadjusted_count=sum(c[metric] for c in ours.values()),
            own_unadjusted_rate=sum(c[metric] for c in ours.values())/own_all if own_all else None,
            peer_unadjusted_count=sum(c[metric] for c in peers.values()),
            peer_unadjusted_rate=sum(c[metric] for c in peers.values())/peer_all if peer_all else None)
    return dict(team=team,league=league,years=sorted(years),cutoff=cutoff,venue=venue,margin=margin,
                own_G=own_all,peer_G=peer_all,common_own_G=n,
                own_coverage=n/own_all if own_all else None,common_strata=len(common),
                unmatched_own_G=own_all-n,
                unmatched_strata=[dict(year=k[0],home=k[1],deficit=k[2],G=ours[k]['G']) for k in sorted(ours) if k not in common],
                common_own_categories={f:sum(ours[k][f] for k in common) for f in CATEGORIES},metrics=results)


def analyze(rows):
    teams=sorted({(r['team'],r['league']) for r in rows})
    yearly=[]
    for team,league in teams:
        for year in range(2013,2026):
            for cutoff in (6,7):
                yearly.append(dict(period=str(year),**compare(rows,team,league,{year},cutoff)))
    pooled=[]
    for period,years in [('no2020',set(range(2013,2026))-{2020}),('with2020',set(range(2013,2026)))]:
        for team,league in teams:
            for cutoff in (6,7):
                for venue in ('all','home','away'):
                    for margin in ('exact','1_2_3plus'):
                        pooled.append(dict(period=period,**compare(rows,team,league,years,cutoff,venue,margin)))
    cases=[dict(year=r['years'][0],team=r['team'],league=r['league'],G=r['common_own_G'],
                difference=r['metrics']['level_or_better']['difference'],direction=r['metrics']['level_or_better']['direction'])
           for r in yearly if r['cutoff']==7 and r['years']!=[2020]]
    return yearly,pooled,cases


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('innings','season','out','csv'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--plan-commit',required=True)
    a=p.parse_args()
    rows,eligible,n=build(a.innings,a.season)
    yearly,pooled,cases=analyze(rows)
    result=dict(schema='aoi-matched-comeback/1',plan_commit=a.plan_commit,
                input_sha256=INPUT_SHA,season_blob=SEASON_BLOB,input_rows=n,annual_checks=936,
                helper_sha256=hashlib.sha256(Path(__file__).with_name('inning_features.py').read_bytes()).hexdigest(),
                eligibility=eligible,cells=rows,yearly=yearly,pooled=pooled,primary_team_year_cases=cases,
                interpretation='descriptive target-weighted comparison; no opponent-strength or causal adjustment')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n')
    with a.csv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps([r for r in pooled if r['team']=='d' and r['cutoff']==7 and r['venue']=='all' and r['margin']=='exact'],ensure_ascii=False))


if __name__=='__main__':main()
