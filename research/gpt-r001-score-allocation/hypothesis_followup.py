"""Counterexample-led fixed-condition exploration; stdlib, retrospective."""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

EXPECTED_BLOB = 'fd76d410b7d8d9438237abc751820dcbf95c05e4'


def classify(rows, predicate):
    cells = {k: [] for k in ['tp', 'fp', 'fn', 'tn']}
    for r in rows:
        a, b = predicate(r), not r['upper_half']
        cells['tp' if a and b else 'fp' if a else 'fn' if b else 'tn'].append([r['season'], r['team']])
    tp, fp, fn, tn = (len(cells[k]) for k in ['tp', 'fp', 'fn', 'tn'])
    denominator = math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
    return dict(n=len(rows), counts=dict(tp=tp, fp=fp, fn=fn, tn=tn),
                precision=tp/(tp+fp) if tp+fp else None, recall=tp/(tp+fn) if tp+fn else None,
                mcc=(tp*tn-fp*fn)/denominator if denominator else None,
                cases=cells)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--season', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    raw = args.season.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob != EXPECTED_BLOB:
        raise ValueError('season Git blob mismatch')
    source = [json.loads(line) for line in raw.decode().splitlines()]
    bykey = {(r['season'],r['team']):r for r in source}
    assert len(bykey)==len(source)==168
    ranked = {}
    for r in source:
        if r['inn_R'] is None or r['inn_S'] is None:
            continue
        assert r['inn_R']==r['RF'] and r['inn_S']>0
        peers = [p for p in source if p['season']==r['season'] and p['league']==r['league']]
        assert len(peers)==6 and all(p['inn_S'] for p in peers)
        rps = Fraction(r['inn_R'], r['inn_S'])
        ranked[r['season'],r['team']] = 1+sum(Fraction(p['inn_R'],p['inn_S'])>rps for p in peers)
    paired, dropped = [], []
    for r in source:
        year, team = r['season'], r['team']
        if year<2013 or year==2020:
            continue
        if year-1==2020:
            dropped.append(dict(year=year,team=team,reason='previous year excluded'))
            continue
        if (year-1,team) not in ranked:
            dropped.append(dict(year=year,team=team,reason='previous RPS missing'))
            continue
        paired.append(dict(r,rps_rank=ranked[year,team],previous_rps_rank=ranked[year-1,team]))
    low = lambda r:r['rps_rank']>=5
    persistent = lambda r:low(r) and r['previous_rps_rank']>=5
    scopes = {'all':paired,'without_chunichi':[r for r in paired if r['team']!='d']}
    persistence = {scope:dict(single=classify(rows,low),persistent=classify(rows,persistent)) for scope,rows in scopes.items()}
    persistence['teams']={team:dict(n=len(rows),persistent_n=sum(persistent(r) for r in rows),
        persistent_b=sum(persistent(r) and not r['upper_half'] for r in rows))
        for team in sorted({r['team'] for r in paired})
        for rows in [[r for r in paired if r['team']==team]]}
    persistence['dropped']=dropped
    persistence['paired_rows']=[dict(year=r['season'],team=r['team'],rank=r['rps_rank'],previous_rank=r['previous_rps_rank'],
        persistent=persistent(r),upper_half=r['upper_half']) for r in paired]
    population=[r for r in source if r['season']>=2013 and r['season']!=2020]
    assert len(population)==144 and len(paired)==120
    baseline=lambda r:r['sim_p_upper']<0.4 or r['alloc_z_strat']< -1
    comparisons={}
    for limit in ['0.10','0.25','0.50']:
        threshold=Fraction(limit)
        close=lambda r:abs(Fraction(r['RF']-r['RA'],r['G']))<=threshold and r['one_run_net']<0
        standalone=classify(population,close)
        combined=classify(population,lambda r:baseline(r) or close(r))
        comparisons[limit]=dict(standalone=standalone,combined=combined,
            new_a_counterexamples=[[r['season'],r['team']] for r in population if r['upper_half'] and close(r) and not baseline(r)],
            new_b_covered=[[r['season'],r['team']] for r in population if not r['upper_half'] and close(r) and not baseline(r)])
    exceptions=[]
    for r in source:
        if r['season']!=2020:
            continue
        prior=ranked.get((2019,r['team']))
        exceptions.append(dict(year=2020,team=r['team'],upper_half=r['upper_half'],rps_rank=ranked[2020,r['team']],
            previous_rank=prior,persistent=ranked[2020,r['team']]>=5 and prior>=5,
            close=abs(Fraction(r['RF']-r['RA'],r['G']))<=Fraction('0.25') and r['one_run_net']<0))
    result=dict(plan_commit='cd8ccdee09ee827e6c3c8e3ae1a45780022e9d5a',source_git_blob=blob,
        source_sha256=hashlib.sha256(raw).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        population='2013-2025 excluding2020; consecutive pairs omit missing2012 and pairs touching2020',
        persistence=persistence,baseline=classify(population,baseline),close=comparisons,excluded2020=exceptions,
        chunichi=[dict(year=r['season'],rank=r['rank'],rps_rank=ranked.get((r['season'],r['team'])),
            previous_rps_rank=ranked.get((r['season']-1,r['team'])),rd_per_game=(r['RF']-r['RA'])/r['G'],one_run_net=r['one_run_net'])
            for r in source if r['team']=='d'],
        interpretation='Fixed definitions after hypothesis-generation data were observed; no causal attribution or independent validation.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(persistence={k:v for k,v in persistence.items() if k in scopes},close=comparisons),ensure_ascii=False))


if __name__=='__main__':main()
