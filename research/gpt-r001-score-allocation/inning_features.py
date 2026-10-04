"""Validate an external inning CSV and derive descriptive features, offline."""
import argparse
import csv
import gzip
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pvariance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CL = set('gtcds') | {'db'}
TEAMS = CL | set('hlmfbe')
FIELDS = ['year', 'team', 'league', 'batting_home', 'side', 'inning', 'runs', 'url']


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ratio(a, b):
    return a / b if b else None


def write_csv(path, rows):
    with Path(path).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def read_input(path):
    games = defaultdict(dict)
    rows = 0
    with gzip.open(path, 'rt', newline='') as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == FIELDS, 'unexpected CSV schema')
        for r in reader:
            rows += 1
            y, inning, runs = (int(r[k]) for k in ['year', 'inning', 'runs'])
            t, side, home = r['team'], r['side'], r['batting_home']
            require(2013 <= y <= 2026 and t in TEAMS, 'unknown year/team')
            require(r['league'] == ('CL' if t in CL else 'PL'), 'league mismatch')
            require(side in {'off', 'def'} and home in {'True', 'False'}, 'unknown side/home')
            require(inning >= 1 and runs >= 0, 'invalid inning/runs')
            u = r['url']
            require(u.startswith(f'https://npb.jp/bis/{y}/games/') or
                    u.startswith(f'https://npb.jp/scores/{y}/'), 'URL/year mismatch')
            key = (t, side, inning)
            require(key not in games[u], f'duplicate row {u} {key}')
            games[u][key] = (y, home == 'True', runs)
    records = []
    for url, cells in sorted(games.items()):
        teams = {k[0] for k in cells}
        require(len(teams) == 2, f'not two teams {url}')
        require(len({v[0] for v in cells.values()}) == 1, 'inconsistent years')
        off = {}
        for t in sorted(teams):
            opp, = teams - {t}
            a = {i: v for (tt, s, i), v in cells.items() if tt == t and s == 'off'}
            mirror = {i: v for (tt, s, i), v in cells.items() if tt == opp and s == 'def'}
            require(a == mirror, f'off/def mirror mismatch {url}')
            require(a and sorted(a) == list(range(1, max(a) + 1)), f'noncontiguous innings {url}')
            require(len({v[1] for v in a.values()}) == 1, 'mixed home flags')
            off[t] = (a[1][1], [a[i][2] for i in sorted(a)])
        require(sorted(v[0] for v in off.values()) == [False, True], 'home sides mismatch')
        h = next(t for t in off if off[t][0])
        a = next(t for t in off if not off[t][0])
        require(len(off[a][1]) - len(off[h][1]) in (0, 1), f'top/bottom length mismatch {url}')
        records.append(dict(url=url, year=next(iter(cells.values()))[0], home=h, away=a,
                            home_runs=off[h][1], away_runs=off[a][1]))
    return records, rows


def verify(records, base_path, official_path):
    base = [json.loads(s) for s in Path(base_path).read_text().splitlines()]
    bm = {g['href']: g for g in base}
    require(len(bm) == len(base) == 11028, 'invalid baseline cardinality')
    old = [g for g in records if g['year'] <= 2025]
    require({g['url'] for g in old} == set(bm), 'baseline URL set mismatch')
    totals = defaultdict(Counter)
    for g in old:
        b = bm[g['url']]
        require((g['year'], g['home'], g['away'], sum(g['home_runs']), sum(g['away_runs'])) ==
                (int(b['date'][:4]), b['home'], b['away'], b['hs'], b['as']),
                f'baseline game mismatch {g["url"]}')
        for side, other in [('home', 'away'), ('away', 'home')]:
            r, ra = sum(g[side + '_runs']), sum(g[other + '_runs'])
            totals[g['year'], g[side]].update(dict(G=1, W=int(r > ra), L=int(r < ra),
                                                  T=int(r == ra), R=r, RA=ra))
    official = list(csv.DictReader(Path(official_path).open()))
    require(len(official) == 156, 'official row count')
    seen = set()
    for r in official:
        k = int(r['year']), r['team']
        require(k not in seen and k in totals, 'official duplicate/unknown')
        seen.add(k)
        for v in ['G', 'W', 'L', 'T', 'R', 'RA']:
            require(totals[k][v] == int(r['o' + v]) == int(r[v]), f'official mismatch {k} {v}')
    require(seen == set(totals), 'official coverage mismatch')
    return dict(baseline_games=len(old), baseline_mismatches=0,
                official_team_seasons=len(seen), official_field_comparisons=len(seen)*6,
                official_mismatches=0)


def longest(flags):
    best = current = 0
    for v in flags:
        current = current + 1 if v else 0
        best = max(best, current)
    return best


def features(xs):
    require(bool(xs), 'empty innings')
    n, r = len(xs), sum(xs)
    z = [x > 0 for x in xs]
    s = sum(z)
    positive = [i + 1 for i, x in enumerate(xs) if x]
    return dict(innings=n, runs=r, scoring_innings=s,
                max_zero_run=longest([not b for b in z]), max_scoring_run=longest(z),
                leading_zeros=positive[0]-1 if positive else n,
                trailing_zeros=n-positive[-1] if positive else n,
                scoring_clusters=sum(b and (i == 0 or not z[i-1]) for i, b in enumerate(z)),
                first_scoring_inning=positive[0] if positive else None,
                last_scoring_inning=positive[-1] if positive else None,
                max_inning_runs=max(xs), max_inning_share=ratio(max(xs), r),
                inning_run_hhi=ratio(sum(x*x for x in xs), r*r),
                transitions=Counter((int(a), int(b)) for a, b in zip(z, z[1:])))


def zero_probability(total, scoring, slots):
    """P(no scoring labels in slots) under fixed-count uniform placement."""
    require(0 <= scoring <= total and 0 <= slots <= total, 'invalid hypergeometric sizes')
    if slots > total-scoring:
        return 0.0
    return math.prod((total-scoring-j)/(total-j) for j in range(slots))


def aggregate(sequences):
    fs = [features(x) for x in sequences]
    g = len(fs)
    I, R, S = (sum(f[k] for f in fs) for k in ['innings', 'runs', 'scoring_innings'])
    counts = Counter(x for xs in sequences for x in xs)
    scored = [f for f in fs if f['runs']]
    result = dict(games=g, innings=I, runs=R, scoring_innings=S,
                  innings_per_game=I/g, runs_per_game=R/g, runs_per_inning=R/I,
                  score_rate=S/I, zero_rate=counts[0]/I,
                  single_run_inning_rate=counts[1]/I, two_run_inning_rate=counts[2]/I,
                  big_inning_rate=sum(v for k,v in counts.items() if k>=3)/I,
                  runs_per_scoring_inning=ratio(R,S), single_share_scoring=ratio(counts[1],S),
                  extra_runs_per_game=(R-S)/g, scoring_innings_per_game=S/g,
                  scoring_innings_variance=pvariance(f['scoring_innings'] for f in fs),
                  zero_scoring_game_rate=sum(f['scoring_innings']==0 for f in fs)/g,
                  one_scoring_game_rate=sum(f['scoring_innings']==1 for f in fs)/g,
                  multi_scoring_game_rate=sum(f['scoring_innings']>=2 for f in fs)/g,
                  threeplus_scoring_game_rate=sum(f['scoring_innings']>=3 for f in fs)/g,
                  scored_games=len(scored),
                  one_scoring_given_scored=ratio(sum(f['scoring_innings']==1 for f in fs),len(scored)))
    for key in ['max_zero_run', 'max_scoring_run', 'leading_zeros', 'trailing_zeros',
                'scoring_clusters', 'max_inning_runs']:
        result['mean_'+key] = mean(f[key] for f in fs)
    result['zero_run_ge6_game_rate'] = sum(f['max_zero_run']>=6 for f in fs)/g
    result['consecutive_scoring_game_rate'] = sum(f['max_scoring_run']>=2 for f in fs)/g
    for key in ['first_scoring_inning', 'last_scoring_inning', 'max_inning_share', 'inning_run_hhi']:
        result['mean_'+key+'_given_scored'] = mean(f[key] for f in scored) if scored else None
    transitions = sum((f['transitions'] for f in fs), Counter())
    for a in [0,1]:
        den = transitions[a,0]+transitions[a,1]
        result[f'transition_from_{a}_n'] = den
        for b in [0,1]:
            result[f'transition_{a}{b}_n'] = transitions[a,b]
            result[f'transition_{a}{b}_rate'] = ratio(transitions[a,b],den)
    for end in [3,6]:
        eligible = [xs for xs in sequences if len(xs)>=end]
        result[f'first{end}_eligible_games'] = len(eligible)
        result[f'first{end}_scoreless_rate'] = ratio(sum(sum(xs[:end])==0 for xs in eligible),len(eligible))
    for name, lo, hi in [('early',1,3),('middle',4,6),('late',7,9),('extra',10,1000)]:
        slots = [x for xs in sequences for i,x in enumerate(xs,1) if lo<=i<=hi]
        result[name+'_innings'] = len(slots)
        result[name+'_score_rate'] = ratio(sum(x>0 for x in slots),len(slots))
        result[name+'_runs_per_inning'] = ratio(sum(slots),len(slots))
    expected = sum(zero_probability(I,S,len(xs)) for xs in sequences)
    result['zero_games_uniform_expected'] = expected
    result['zero_game_rate_uniform_expected'] = expected/g
    result['zero_game_rate_excess_uniform'] = result['zero_scoring_game_rate']-expected/g
    require(math.isclose(result['zero_rate']+result['score_rate'],1), 'rate partition')
    require(math.isclose(result['zero_scoring_game_rate']+result['one_scoring_game_rate']+
                         result['multi_scoring_game_rate'],1), 'game partition')
    if S:
        require(math.isclose(result['runs_per_game'],result['innings_per_game']*
                             result['score_rate']*result['runs_per_scoring_inning']), 'identity failed')
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--share', type=Path, required=True)
    p.add_argument('--out', type=Path, default=HERE/'outputs/inning_features')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    source = args.share/'team_half_innings.csv.gz'
    official = args.share/'official_check.csv'
    base = ROOT/'data/observations/r001/games.jsonl'
    records, nrows = read_input(source)
    receipt = verify(records, base, official)
    receipt.update(input_rows=nrows, input_games=len(records),
                   excluded_2026_games=sum(g['year']==2026 for g in records),
                   input_sha256=digest(source), baseline_sha256=digest(base),
                   shared_files_sha256={f.name:digest(f) for f in sorted(args.share.iterdir()) if f.is_file()},
                   script_sha256=digest(__file__), exit_code=0)
    groups = defaultdict(list)
    feature_rows = []
    for g in records:
        if g['year']==2026:
            continue
        for venue, opp in [('home','away'),('away','home')]:
            for role, bat in [('off',venue),('def',opp)]:
                xs = g[bat+'_runs']
                for side in ['all',venue]:
                    groups[g['year'],g[venue],side,role,'all'].append(xs)
                    if min(len(g['home_runs']),len(g['away_runs']))>=6:
                        groups[g['year'],g[venue],side,role,'first6'].append(xs[:6])
                f = features(xs)
                del f['transitions']
                feature_rows.append(dict(year=g['year'],team=g[venue],venue=venue,role=role,url=g['url'],**f))
    rows=[]
    for (y,t,v,role,window),xs in sorted(groups.items()):
        rows.append(dict(year=y,team=t,league='CL' if t in CL else 'PL',venue=v,role=role,window=window,
                         **aggregate(xs)))
    indexed={(r['year'],r['team'],r['venue'],r['role'],r['window']):r for r in rows}
    for r in rows:
        if r['venue']=='all':
            expected=sum(indexed[r['year'],r['team'],v,r['role'],r['window']]['zero_games_uniform_expected']
                         for v in ['home','away'])
            r['zero_games_uniform_expected']=expected
            r['zero_game_rate_uniform_expected']=expected/r['games']
            r['zero_game_rate_excess_uniform']=r['zero_scoring_game_rate']-expected/r['games']
    write_csv(args.out/'team_year_metrics.csv',rows)
    # Game-level features remain local, matching this research branch's data policy.
    local=ROOT/'data/observations/r001_inning_features'
    local.mkdir(parents=True,exist_ok=True)
    write_csv(local/'team_game_features.csv',feature_rows)
    summary=[]
    metrics=[k for k in rows[0] if k not in ['year','team','league','venue','role','window']]
    for omit in [False,True]:
        for label,teams in [('chunichi',{'d'}),('other_cl',CL-{'d'}),('cl',CL),('npb',TEAMS)]:
            for venue in ['all','home','away']:
                for role in ['off','def']:
                    for window in ['all','first6']:
                        selected=[r for r in rows if r['team'] in teams and r['venue']==venue and
                                  r['role']==role and r['window']==window and (not omit or r['year']!=2020)]
                        summary.append(dict(scope='without2020' if omit else 'all',group=label,
                                            venue=venue,role=role,window=window,team_years=len(selected),
                                            **{k:mean(r[k] for r in selected if r[k] is not None)
                                               if any(r[k] is not None for r in selected) else None for k in metrics}))
    write_csv(args.out/'group_summary.csv',summary)
    # All same-year peer differences, no selected-metric filtering.
    comparisons=[]
    for r in rows:
        if r['team']!='d':continue
        peers=[s for s in rows if s['year']==r['year'] and s['team'] in CL-{'d'} and
               all(s[k]==r[k] for k in ['venue','role','window'])]
        require(len(peers)==5,'peer count')
        for k in metrics:
            valid=[s[k] for s in peers if s[k] is not None]
            pmean=mean(valid) if valid else None
            comparisons.append(dict(year=r['year'],venue=r['venue'],role=r['role'],window=r['window'],
                                    metric=k,chunichi=r[k],other_cl_mean=pmean,peer_n=len(valid),
                                    difference=r[k]-pmean if r[k] is not None and pmean is not None else None))
    write_csv(args.out/'chunichi_peer_differences.csv',comparisons)
    for name in ['team_year_metrics.csv','chunichi_peer_differences.csv']:
        (args.out/(name+'.gz')).write_bytes(gzip.compress((args.out/name).read_bytes(),mtime=0))
    receipt.update(metric_columns=len(metrics), team_year_metric_rows=len(rows),
                   local_game_feature_rows=len(feature_rows), group_rows=len(summary),
                   output_sha256={f.name:digest(f) for f in sorted(args.out.iterdir())
                                  if f.suffix in {'.csv','.gz'}})
    (args.out/'validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':
    try:
        main()
    except FileNotFoundError as e:
        print(str(e),file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError) as e:
        print(str(e),file=sys.stderr);sys.exit(65)
