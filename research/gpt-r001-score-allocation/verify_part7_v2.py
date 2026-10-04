"""Independent aggregate checks for locally supplied Part7 v2 (stdlib; no raw output)."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import gzip
import hashlib
from itertools import permutations
import json
import math
from pathlib import Path


def read(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8-sig', newline='') as f:
        yield from csv.DictReader(f)


def number(value):
    return float(value) if value else None


def require(ok, message):
    if not ok:
        raise ValueError(message)


def close(a, b):
    return math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-12)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def convolve(a, b):
    result = Counter()
    for i, x in a.items():
        for j, y in b.items():
            result[i+j] += x*y
    return result


def permutation_tail(rows, condition, outcome):
    total = Counter({0: 1})
    for league in ('CL', 'PL'):
        group = [r for r in rows if r['league'] == league]
        teams = sorted({r['team'] for r in group})
        years = sorted({r['year'] for r in group})
        require(len(teams) == 6 and len(group) == 6*len(years), 'incomplete league-year grid')
        cells = {(r['team'], r['year']): r for r in group}
        # Score matrix allows enumeration without assuming yearly independence.
        scores = [[sum(condition(cells[a,y]) and outcome(cells[b,y]) for y in years)
                   for b in teams] for a in teams]
        counts = Counter(sum(scores[p[j]][j] for j in range(6)) for p in permutations(range(6)))
        total = convolve(total, counts)
    obs = sum(condition(r) and outcome(r) for r in rows)
    return obs, sum(v for k,v in total.items() if k >= obs), sum(total.values())


def verify(source, previous=None):
    source = Path(source)
    halves = list(read(source/'v2/half_innings_v2_public.csv.gz'))
    official = list(read(source/'official_team_SB_CS_2013_2026.csv'))
    leagues = {(int(r['year']),r['team']):r['league'] for r in official}
    groups = defaultdict(Counter)
    games = defaultdict(set)
    reasons, diagnostics = Counter(), Counter()
    bounds = {k: [math.inf,-math.inf] for k in ('LOB','RO','RO_other')}
    key = lambda r:(r['year'],r['slug'],r['inning'],r['half'])
    require(len({key(r) for r in halves}) == len(halves), 'duplicate half keys')
    for raw in halves:
        r = {k:number(v) for k,v in raw.items() if k in ('R','PA','SB','CS','PO','batter_outs','LOB','RO','ROB','CSPO_out','CSPO_noout','RO_other','CSPO_out_rowlevel','CSPO_undet')}
        complete = raw['complete'] == 'True'
        require(raw['complete'] in ('True','False'), 'invalid complete flag')
        diagnostics['halves'] += 1
        diagnostics['complete' if complete else 'incomplete'] += 1
        if not complete:
            reasons[raw['excl_reason']] += 1
            require(bool(raw['excl_reason']), 'incomplete without reason')
        else:
            require(not raw['excl_reason'], 'complete with exclusion reason')
            require(close(r['LOB'],r['PA']-r['R']-3), 'LOB identity')
            require(close(r['RO'],3-r['batter_outs']), 'RO identity')
            require(close(r['CSPO_out'],min(r['CS']+r['PO'],r['RO'])), 'min allocation')
            require(close(r['CSPO_noout'],r['CS']+r['PO']-r['CSPO_out']), 'noout identity')
            require(close(r['RO_other'],r['RO']-r['CSPO_out']), 'other identity')
            require(close(r['ROB'],r['R']+r['LOB']+r['RO']), 'ROB identity')
            require(0 <= r['LOB'] <= 3 and 0 <= r['RO'] <= 3 and r['RO_other'] >= 0, 'negative or excessive count')
            for k in bounds:
                bounds[k][0] = min(bounds[k][0],r[k]); bounds[k][1] = max(bounds[k][1],r[k])
            diagnostics['clipped_halves'] += r['CSPO_noout'] > 0
            diagnostics['rowlevel_disagreement_halves'] += r['CSPO_out_rowlevel'] != r['CSPO_out']
            diagnostics['rowlevel_disagreement_outs'] += r['CSPO_out']-r['CSPO_out_rowlevel']
        for side, team in [('off',raw['team']),('def',raw['opp'])]:
            k=(int(raw['year']),team,side); s=groups[k]; games[k].add(raw['slug'])
            s['halves']+=1; s['sc']+=r['R']>0
            for m in ('R','PA','SB','CS','PO'): s[m]+=r[m]
            if complete:
                s['c_halves']+=1; s['c_R']+=r['R']
                for m in ('LOB','RO','RO_other','ROB','CSPO_out','CSPO_noout'): s[m]+=r[m]
                if r['R']>0:
                    s['s_n']+=1
                    for dest,m in [('s_R','R'),('s_ROB','ROB'),('s_LOB','LOB'),('s_CSPO','CSPO_out'),('s_ROoth','RO_other')]: s[dest]+=r[m]
    metrics=('cRPS','s_ROB_i','s_LOB_i','s_CSPO_i','s_ROoth_i','strand','CSPO_rate','ROoth_rate','SBatt_G')
    records=[]
    for (year,team,side),s in sorted(groups.items()):
        s['games']=len(games[year,team,side])
        for dest,a,b in [('SR','sc','halves'),('RPS_all','R','sc'),('cRPS','s_R','s_n'),('strand','LOB','ROB'),('CSPO_rate','CSPO_out','ROB'),('ROoth_rate','RO_other','ROB')]: s[dest]=s[a]/s[b]
        s['SBatt_G']=(s['SB']+s['CS'])/s['games']
        for m in ('ROB','LOB','CSPO','ROoth'): s['s_'+m+'_i']=s['s_'+m]/s['s_n']
        records.append(dict(s,year=year,team=team,side=side,league=leagues[year,team]))
    for year,league,side in sorted({(r['year'],r['league'],r['side']) for r in records}):
        block=[r for r in records if (r['year'],r['league'],r['side'])==(year,league,side)]
        require(len(block)==6, 'expected six teams')
        for m in metrics:
            avg=sum(r[m] for r in block)/6
            for rank,r in enumerate(sorted(block,key=lambda r:(r[m],r['team'])),1):
                r['rel_'+m]=r[m]-avg; r['rk_'+m]=rank
            diagnostics['tied_metric_groups'] += len({r[m] for r in block})<6
    expected={(int(r['year']),r['team'],r['side']):r for r in read(source/'v2/team_season_v2.csv')}
    require(len(expected)==len(records), 'season row count')
    cells=0
    for r in records:
        e=expected[r['year'],r['team'],r['side']]
        for k,v in e.items():
            if k in ('team','side','league'): require(r[k]==v,'season label')
            else:
                require(k in r and close(r[k],v),'season mismatch '+str((r['year'],r['team'],r['side'],k)))
                cells+=1
    diagnostics['season_rows']=len(records); diagnostics['season_numeric_cells']=cells
    supplied=list(read(source/'v2/propositions_2x2_v2.csv')); checks=[]
    conditions=[('rk_s_ROB_i',True),('rk_strand',False),('rk_ROoth_rate',False),('rk_CSPO_rate',False),('rk_SBatt_G',True),('rk_s_LOB_i',False)]
    counterexample_total=0
    expected_cases=set()
    for period in ('2016-2025','2016-2025(2020除く)'):
        for side in ('off','def'):
            rows=[r for r in records if 2016<=r['year']<=2025 and r['side']==side and not ('除く' in period and r['year']==2020)]
            subset=[p for p in supplied if p['期間']==period and p['side']==side]
            require(len(subset)==6,'proposition count')
            for (metric,low),p in zip(conditions,subset):
                cond=lambda r:r[metric]<=2 if low else r[metric]>=5
                bad=lambda r:r['rk_cRPS']<=2 if side=='off' else r['rk_cRPS']>=5
                obs,numer,denom=permutation_tail(rows,cond,bad)
                n=sum(cond(r) for r in rows); failures=n-obs
                require(int(p['n'])==len(rows) and int(p['反例(条件なのに非結果)'])==failures,'2x2 counts')
                bothnot=sum(not cond(r) and not bad(r) for r in rows)
                for field,a,b in [('命題 条件→結果',obs,n),('逆 結果→条件',obs,sum(bad(r) for r in rows)),('裏 非条件→非結果',bothnot,len(rows)-n),('対偶 非結果→非条件',bothnot,len(rows)-sum(bad(r) for r in rows))]:
                    require(p[field]==f'{a}/{b} = {a/b:.3f}','logical form counts')
                require(close(numer/denom,p['p_teamperm(球団軌跡入替,全列挙)']),'trajectory permutation')
                dist=Counter({0:1})
                for _ in range(len(rows)//6): dist=convolve(dist,Counter({0:6,1:8,2:1}))
                tail=Fraction(sum(v for k,v in dist.items() if k>=obs),15**(len(rows)//6))
                require(close(float(tail),p['p_exact(年×リーグ独立)']),'hypergeometric tail')
                counterexample_total+=failures
                label=p['命題'].split(' → ')[0]
                expected_cases.update((period,side,label,r['year'],r['team']) for r in rows if cond(r) and not bad(r))
                checks.append(dict(period=period,side=side,metric=metric,n=len(rows),condition=n,both=obs,counterexamples=failures,trajectory_tail_numerator=numer,trajectory_total=denom,p_trajectory=numer/denom,p_hypergeometric=float(tail)))
    cases=list(read(source/'v2/counterexamples_2x2_v2.csv'))
    require(len(cases)==counterexample_total,'counterexample listing size')
    require({(r['期間'],r['side'],r['命題'],int(r['year']),r['team']) for r in cases}==expected_cases,'counterexample identities')
    validation=[]
    bykey={(r['year'],r['team'],r['side']):r for r in records}
    for year in range(2016,2027):
        diffs=Counter()
        for o in official:
            if int(o['year'])!=year:continue
            r=bykey[year,o['team'],'off']
            for m,field in [('SB','SB'),('CS','CS'),('R','R'),('PA','PA'),('games','G')]: diffs[m]+=r[m]!=float(o[field])
        if year<=2025: require(not any(diffs.values()),'official annual mismatch')
        validation.append(dict(year=year,mismatch_team_counts=dict(diffs)))
    decomp=[]
    for name,keep in [('2016-2025',lambda r:2016<=r['year']<=2025),('2016-2025_no2020',lambda r:2016<=r['year']<=2025 and r['year']!=2020),('2022',lambda r:r['year']==2022)]:
        vals=[]
        for target in (True,False):
            rs=[r for r in records if r['side']=='off' and r['league']=='CL' and keep(r) and (r['team']=='d')==target]
            n=sum(r['s_n'] for r in rs)
            vals.append({m:sum(r[m] for r in rs)/n for m in ('s_R','s_ROB','s_LOB','s_CSPO','s_ROoth')})
        delta={m:vals[0][m]-vals[1][m] for m in vals[0]}
        decomp.append(dict(period=name,chunichi=vals[0],cl_other5=vals[1],difference=delta,identity_contributions={m:d if m=='s_ROB' else -d for m,d in delta.items() if m!='s_R'}))
    old_check=None
    if previous:
        new={key(r):r for r in halves}; changes=Counter(); old_negative=Counter()
        for r in read(Path(previous)/'half_innings_pbp_derived.csv.gz'):
            t=new[key(r)]
            changes['complete_changed']+=(r['complete']!=t['complete'])
            for m in ('R','PA','SB','CS','PO'):
                require(close(r[m],t[m]),'v1 count changed: '+m)
            for m in ('LOB','RO_other'):
                if r[m] and float(r[m])<0:
                    old_negative[m]+=1
                    require(t['complete']=='False' or float(t[m])>=0,'v1 negative persists')
        old_check=dict(changes=changes,old_negative=old_negative)
    files=['official_team_SB_CS_2013_2026.csv',*[str(p.relative_to(source)) for p in sorted((source/'v2').iterdir()) if p.is_file()]]
    return dict(schema='aoi-part7-v2-reception/1',status='aggregate_checks_passed',scope='provided half CSV; raw HTML parser not independently rerun',inputs={p:sha(source/p) for p in files},diagnostics=diagnostics,incomplete_reasons=reasons,ranges=bounds,previous=old_check,official_validation=validation,propositions=checks,counterexample_rows=counterexample_total,offense_decomposition=decomp,limitations=['min allocation is not event identification','trajectory permutation assumes within-league exchangeability','algebraic components are not causal contributions','2026 provisional; source event audit not included'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path,help='extracted part7 directory')
    p.add_argument('--previous',type=Path,help='v1 part7 directory, optional')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    result=verify(args.source,args.previous)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'diagnostics':result['diagnostics']},ensure_ascii=False))


if __name__=='__main__':
    main()
