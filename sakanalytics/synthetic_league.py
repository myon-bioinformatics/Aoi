"""Annual-first, constructive synthetic leagues, then exact game-level witnesses.

Pure Python 3.11+. Synthetic units are model checks, never extra NPB observations.
Declared family: each pair has >=1 win in each direction; nonnegative integer
scores; round-robin pair counts. Infeasible means within this family only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction
import hashlib
import json
import math
import platform
from pathlib import Path
import random
import statistics


class InfeasibleScenario(ValueError):
    pass


def _apportion(values, total):
    floors=[math.floor(v) for v in values]
    left=total-sum(floors)
    if not 0 <= left <= len(values):
        raise ValueError('expected values must sum to the integer total')
    order=sorted(range(len(values)),key=lambda i:(-(values[i]-floors[i]),i))
    for i in order[:left]:floors[i]+=1
    return floors


def _flow(team_targets, pair_capacities):
    """Integer max flow: allocate pair-level decisive games to annual win quotas."""
    graph=defaultdict(dict)
    def edge(a,b,c):
        graph[a][b]=c
        graph[b].setdefault(a,0)
    for team,n in team_targets.items():
        if type(n) is not int or n<0:raise InfeasibleScenario('negative/noninteger residual win quota')
        edge(('team',team),'sink',n)
    for i,(a,b,n) in enumerate(pair_capacities):
        node=('pair',i)
        edge('source',node,n)
        edge(node,('team',a),n)
        edge(node,('team',b),n)
    wanted=sum(n for _,_,n in pair_capacities)
    if sum(team_targets.values())!=wanted:raise InfeasibleScenario('win quotas do not conserve decisive games')
    sent=0
    while True:
        prev={'source':None}
        q=deque(['source'])
        while q and 'sink' not in prev:
            u=q.popleft()
            for v,c in graph[u].items():
                if c>0 and v not in prev:prev[v]=u;q.append(v)
        if 'sink' not in prev:break
        step=wanted
        v='sink'
        while prev[v] is not None:
            step=min(step,graph[prev[v]][v]);v=prev[v]
        v='sink'
        while prev[v] is not None:
            u=prev[v];graph[u][v]-=step;graph[v][u]+=step;v=u
        sent+=step
    if sent!=wanted:raise InfeasibleScenario('no pair allocation satisfies the declared annual win quotas')
    return [(graph[('team',a)][('pair',i)],graph[('team',b)][('pair',i)]) for i,(a,b,_) in enumerate(pair_capacities)]


def _pythag(rf,ra,exponent=1.83):
    d=rf**exponent+ra**exponent
    return rf**exponent/d if d else None


def _rank(rows):
    for lg in sorted({r['league'] for r in rows}):
        group=sorted([r for r in rows if r['league']==lg],key=lambda r:(-Fraction(r['W'],max(1,r['W']+r['L'])),-r['W'],r['team']))
        # Synthetic total order is explicit; shared winning pct remains visibly tied.
        counts=Counter(Fraction(r['W'],max(1,r['W']+r['L'])) for r in group)
        for i,r in enumerate(group,1):
            r.update(rank=i,rank_tie=counts[Fraction(r['W'],max(1,r['W']+r['L']))]>1,upper_half=i<=len(group)//2)
    return rows


def plan(*, seed=0, profile='aligned', conversion=1., mean_runs=4., leagues=2,
         within=25, inter=3, win_quotas=None):
    if profile not in ('aligned','same_totals','reversed') or leagues not in (1,2):raise ValueError('invalid profile/league count')
    if type(seed) is not int or not math.isfinite(conversion) or not math.isfinite(mean_runs) or mean_runs<1:
        raise ValueError('finite conversion and mean_runs>=1 required')
    if type(within) is not int or type(inter) is not int or within<3 or inter<3:
        raise ValueError('at least three games per pair required by the declared family')
    rng=random.Random(seed)
    teams=[f'{lg}{i+1}' for lg in ('C','P')[:leagues] for i in range(6)]
    strengths={}
    for lg in ('C','P')[:leagues]:
        values=[-.6,-.36,-.12,.12,.36,.6]
        rng.shuffle(values)
        strengths.update({f'{lg}{i+1}':v for i,v in enumerate(values)})
    pairs=[]
    for i,a in enumerate(teams):
        for j,b in enumerate(teams[i+1:],i+1):
            n=within if a[0]==b[0] else inter
            draws=int((i+j+seed)%7==0)
            common=round((mean_runs-1)*n)
            # Score budgets are annual pair aggregates, not fabricated per-game rows.
            bias=0 if profile=='same_totals' else (1 if profile=='aligned' else -1)
            ma=n+round(n*max(0,bias*strengths[a]))
            mb=n+round(n*max(0,bias*strengths[b]))
            pairs.append(dict(a=a,b=b,G=n,T=draws,common_runs=common,margin_a=ma,margin_b=mb,
                              RF_a=common+ma,RF_b=common+mb))
    annual={t:dict(synthetic=True,team=t,league=t[0],G=0,W=0,L=0,T=0,RF=0,RA=0) for t in teams}
    for pair in pairs:
        a,b=pair['a'],pair['b']
        for t,rf,ra in [(a,pair['RF_a'],pair['RF_b']),(b,pair['RF_b'],pair['RF_a'])]:
            annual[t]['G']+=pair['G'];annual[t]['T']+=pair['T'];annual[t]['RF']+=rf;annual[t]['RA']+=ra
    expected={t:0. for t in teams}
    base=Counter()
    residual=[]
    for p in pairs:
        a,b=p['a'],p['b']
        # Start from annual Pythagorean odds. Conversion is an explicit scenario
        # assumption: align, reverse, or vary allocation while score totals tie.
        pa=_pythag(annual[a]['RF'],annual[a]['RA'])
        pb=_pythag(annual[b]['RF'],annual[b]['RA'])
        base_odds=math.log(pa/(1-pa))-math.log(pb/(1-pb))
        odds=conversion*((strengths[a]-strengths[b]) if profile=='same_totals' else
                         base_odds if profile=='aligned' else -base_odds)
        probability=1/(1+math.exp(-odds)) if odds>=0 else math.exp(odds)/(1+math.exp(odds))
        n=p['G']-p['T']-2
        expected[a]+=1+n*probability;expected[b]+=1+n*(1-probability)
        base[a]+=1;base[b]+=1
        residual.append((a,b,n))
    total=sum(p['G']-p['T'] for p in pairs)
    quotas=dict(zip(teams,_apportion([expected[t] for t in teams],total))) if win_quotas is None else dict(win_quotas)
    if set(quotas)!=set(teams) or any(type(v) is not int for v in quotas.values()):
        raise InfeasibleScenario('win quotas must name every synthetic team with integer values')
    allocation=_flow({t:quotas[t]-base[t] for t in teams},residual)
    for p,(wa,wb) in zip(pairs,allocation):
        p.update(W_a=wa+1,W_b=wb+1)
    for t,row in annual.items():
        row.update(W=quotas[t],L=row['G']-row['T']-quotas[t],expected_schedule_wins=expected[t])
        row['pythag_fixed']=_pythag(row['RF'],row['RA'])
        row['pythag_expected_wins']=(row['W']+row['L'])*row['pythag_fixed']
    result={'schema':'aoi-synthetic-plan/1','synthetic':True,'seed':seed,'profile':profile,
            'conversion':conversion,'mean_runs':mean_runs,'leagues':leagues,'within':within,'inter':inter,
            'family':'each pair >=1 win each direction; integer nonnegative scores; optional draws',
            'expectation_model':'Log5 from annual Pythagorean odds, then explicit profile/conversion; one fixed win each direction per pair is conditioned on',
            'ranking_policy':'winning fraction, wins, synthetic team ID; not official NPB CS rules',
            'annual':_rank(list(annual.values())),'pairs':pairs}
    validate_plan(result)
    return result


def validate_plan(p):
    if p.get('synthetic') is not True:raise ValueError('synthetic identity required')
    rows=p['annual'];teams=[r['team'] for r in rows]
    if len(set(teams))!=len(teams):raise ValueError('duplicate annual teams')
    derived={t:Counter() for t in teams}
    seen_pairs=set()
    for pair in p['pairs']:
        a,b=pair['a'],pair['b']
        if a==b or a not in derived or b not in derived:raise ValueError('invalid pair')
        key=tuple(sorted((a,b)))
        if key in seen_pairs:raise ValueError('duplicate pair')
        seen_pairs.add(key)
        for c in ['G','T','W_a','W_b','common_runs','margin_a','margin_b','RF_a','RF_b']:
            if type(pair[c]) is not int or pair[c]<0:raise ValueError('integer nonnegative pair quantities required')
        if pair['W_a']+pair['W_b']+pair['T']!=pair['G']:raise ValueError('pair outcomes do not sum to games')
        if min(pair['W_a'],pair['W_b'])<1 or pair['margin_a']<pair['W_a'] or pair['margin_b']<pair['W_b']:
            raise ValueError('pair margin budget cannot realize the declared outcomes')
        if pair['RF_a']!=pair['common_runs']+pair['margin_a'] or pair['RF_b']!=pair['common_runs']+pair['margin_b']:
            raise ValueError('pair score budgets do not match margins')
        for t,w,l,rf,ra in [(a,pair['W_a'],pair['W_b'],pair['RF_a'],pair['RF_b']),
                            (b,pair['W_b'],pair['W_a'],pair['RF_b'],pair['RF_a'])]:
            derived[t].update(G=pair['G'],W=w,L=l,T=pair['T'],RF=rf,RA=ra)
    for r in rows:
        for key in ('G','W','L','T','RF','RA'):
            if type(r[key]) is not int or r[key]!=derived[r['team']][key]:raise ValueError('annual/pair mismatch: '+key)
        probability=_pythag(r['RF'],r['RA'])
        if r.get('pythag_fixed')!=probability or r.get('pythag_expected_wins')!=(r['W']+r['L'])*probability:
            raise ValueError('annual Pythagorean expectation mismatch')
    ranked=_rank([dict(r) for r in rows])
    for actual,expected in zip(rows,ranked):
        if any(actual.get(k)!=expected[k] for k in ('rank','rank_tie','upper_half')):
            raise ValueError('annual ranking mismatch')
    if sum(r['RF'] for r in rows)!=sum(r['RA'] for r in rows) or sum(r['W'] for r in rows)!=sum(r['L'] for r in rows):
        raise ValueError('global conservation failure')
    return True


def _partition(total,count,rng,minimum=0):
    if total<minimum*count:raise InfeasibleScenario('partition lower bound')
    values=[minimum]*count
    for _ in range(total-minimum*count):values[rng.randrange(count)]+=1
    return values


def expand(p):
    """Only after annual validation, construct integer game scores as a witness."""
    validate_plan(p)
    rng=random.Random(p['seed']+104729)
    games=[]
    for pair_index,pair in enumerate(p['pairs']):
        outcomes=['A']*pair['W_a']+['B']*pair['W_b']+['D']*pair['T']
        rng.shuffle(outcomes)
        ma=iter(_partition(pair['margin_a'],pair['W_a'],rng,1))
        mb=iter(_partition(pair['margin_b'],pair['W_b'],rng,1))
        common=_partition(pair['common_runs'],pair['G'],rng)
        for i,(outcome,c) in enumerate(zip(outcomes,common)):
            a=c+(next(ma) if outcome=='A' else 0)
            b=c+(next(mb) if outcome=='B' else 0)
            home,away=pair['a'],pair['b']
            if i%2:home,away=away,home;a,b=b,a
            games.append(dict(key=f'synthetic-{p["seed"]}-{p["profile"]}-{pair_index}-{i}',synthetic=True,
                              home=home,away=away,hs=a,**{'as':b}))
    validate_games(p,games)
    return games


def aggregate(games):
    out=defaultdict(Counter)
    seen=set()
    for g in games:
        if g.get('synthetic') is not True or g['key'] in seen or g['home']==g['away']:raise ValueError('invalid/duplicate synthetic game')
        seen.add(g['key'])
        if type(g['hs']) is not int or type(g['as']) is not int or min(g['hs'],g['as'])<0:raise ValueError('integer score required')
        for t,rf,ra in [(g['home'],g['hs'],g['as']),(g['away'],g['as'],g['hs'])]:
            out[t].update(G=1,W=int(rf>ra),L=int(rf<ra),T=int(rf==ra),RF=rf,RA=ra)
    return out


def validate_games(p,games):
    validate_plan(p)
    actual=aggregate(games)
    if set(actual)!={r['team'] for r in p['annual']}:raise ValueError('game/annual member mismatch')
    for r in p['annual']:
        for key in ('G','W','L','T','RF','RA'):
            if actual[r['team']][key]!=r[key]:raise ValueError('game/annual mismatch: '+key)
    pair_counts=Counter(tuple(sorted((g['home'],g['away']))) for g in games)
    if pair_counts!=Counter({tuple(sorted((p['a'],p['b']))):p['G'] for p in p['pairs']}):raise ValueError('schedule pair-count mismatch')
    return True


def experiment(seeds=range(20),mean_runs=4.,leagues=2,conversion=1.):
    seeds=list(seeds)
    cases=[]
    for profile in ('aligned','same_totals','reversed'):
        for seed in seeds:
            p=plan(seed=seed,profile=profile,mean_runs=mean_runs,leagues=leagues,conversion=conversion)
            games=expand(p)
            # Cross-check only against frozen annual values; do not derive the plan from generated games.
            counts=Counter()
            for r in p['annual']:
                high=r['pythag_fixed']>=.5
                counts['tp' if high and r['upper_half'] else 'fp' if high else 'fn' if r['upper_half'] else 'tn']+=1
            body=json.dumps(games,sort_keys=True,separators=(',',':')).encode()
            cases.append(dict(seed=seed,profile=profile,annual=p['annual'],year_check=True,game_check=True,
                              games=len(games),games_sha256=hashlib.sha256(body).hexdigest(),conditional_counts=dict(counts)))
    groups=[]
    for profile in ('aligned','same_totals','reversed'):
        subset=[c for c in cases if c['profile']==profile]
        count=Counter()
        for c in subset:count.update(c['conditional_counts'])
        high=count['tp']+count['fp']
        groups.append(dict(profile=profile,cases=len(subset),year_passed=sum(c['year_check'] for c in subset),
                           game_passed=sum(c['game_check'] for c in subset),counts=dict(count),
                           p_upper_given_pythag_at_least_half=count['tp']/high if high else None))
    controls=[]
    for seed in seeds:
        p=plan(seed=seed,mean_runs=mean_runs,leagues=leagues)
        quotas={r['team']:r['W'] for r in p['annual']}
        quotas['C1']+=1
        try:plan(seed=seed,mean_runs=mean_runs,leagues=leagues,win_quotas=quotas)
        except InfeasibleScenario:controls.append(dict(seed=seed,kind='nonconserving_annual_wins',rejected=True))
        else:raise AssertionError('nonconserving annual wins were accepted')
        six=plan(seed=seed,mean_runs=mean_runs,leagues=1)
        remaining=sum(r['W'] for r in six['annual'])-330
        low,extra=divmod(remaining,3)
        quotas={f'C{i}':110 if i<=3 else low+int(i-4<extra) for i in range(1,7)}
        try:plan(seed=seed,mean_runs=mean_runs,leagues=1,win_quotas=quotas)
        except InfeasibleScenario:controls.append(dict(seed=seed,kind='balanced_but_pairwise_infeasible',rejected=True))
        else:raise AssertionError('pairwise infeasible annual wins were accepted')
        games=expand(p)
        games[0]['hs']+=1
        try:validate_games(p,games)
        except ValueError:controls.append(dict(seed=seed,kind='tampered_game_score',rejected=True))
        else:raise AssertionError('tampered game was accepted')
    return dict(schema='aoi-synthetic-experiment/1',synthetic=True,
                interpretation='Model-conditional checks, not independent observations or causal evidence about Chunichi. Counts stay separate from actual NPB sample sizes.',
                games_digest_format='JSON array, sorted keys, compact separators, UTF-8',
                mean_runs=mean_runs,leagues=leagues,conversion=conversion,groups=groups,cases=cases,negative_controls=controls)


def write_witnesses(result,directory):
    directory.mkdir(parents=True,exist_ok=True)
    files=[]
    for case in result['cases']:
        p=plan(seed=case['seed'],profile=case['profile'],mean_runs=result['mean_runs'],leagues=result['leagues'],conversion=result['conversion'])
        games=expand(p)
        canonical=json.dumps(games,sort_keys=True,separators=(',',':')).encode()
        if hashlib.sha256(canonical).hexdigest()!=case['games_sha256']:
            raise ValueError('witness differs from the checked experiment')
        prefix=f"{case['profile']}-{case['seed']:04d}"
        for name,body in [(prefix+'.annual.json',json.dumps(p,ensure_ascii=False,indent=2)+'\n'),
                          (prefix+'.games.jsonl',''.join(json.dumps(g,ensure_ascii=False)+'\n' for g in games))]:
            path=directory/name
            path.write_text(body,encoding='utf-8')
            files.append(dict(file=name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size))
    (directory/'manifest.json').write_text(json.dumps(dict(synthetic=True,files=files),indent=2)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--seeds',type=int,default=20)
    p.add_argument('--mean-runs',type=float,default=4.)
    p.add_argument('--conversion',type=float,default=1.)
    p.add_argument('--leagues',type=int,choices=[1,2],default=2)
    p.add_argument('--calibrate-annual',type=Path)
    p.add_argument('--calibration-years',default='2013-2026')
    p.add_argument('--witness-dir',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.seeds<1:p.error('seeds must be positive')
    calibration=None
    if a.calibrate_annual:
        start,end=map(int,a.calibration_years.split('-'))
        rows=[json.loads(s) for s in a.calibrate_annual.read_text(encoding='utf-8').splitlines() if s.strip()]
        units=[r for r in rows if start<=r['season']<=end and r.get('G',0)>0 and 'RF' in r]
        if not units:p.error('no calibration units in the declared years')
        a.mean_runs=statistics.median(r['RF']/r['G'] for r in units)
        calibration=dict(path=str(a.calibrate_annual),sha256=hashlib.sha256(a.calibrate_annual.read_bytes()).hexdigest(),
                         years=[start,end],units=len(units),statistic='median RF/G; only common-run volume calibrated, no causal or joint-distribution fit')
    result=experiment(range(a.seeds),a.mean_runs,a.leagues,a.conversion)
    result['calibration']=calibration
    result['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['python_version']=platform.python_version()
    if a.witness_dir:write_witnesses(result,a.witness_dir)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    for g in result['groups']:print(g['profile'],f"annual={g['year_passed']}/{g['cases']}",f"games={g['game_passed']}/{g['cases']}",g['p_upper_given_pythag_at_least_half'])


if __name__=='__main__':main()
