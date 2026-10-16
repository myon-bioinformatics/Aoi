"""Recalculate Part5's main comparisons using the previously reconciled inputs."""
import argparse
import csv
import gzip
import json
import math
import sys
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path
from statistics import mean
from inning_features import HERE,ROOT,CL,digest,require,write_csv


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--share',type=Path,required=True)
    p=ap.parse_args().share
    with gzip.open(HERE/'outputs/inning_features/team_year_metrics.csv.gz','rt') as f:
        metrics=list(csv.DictReader(f))
    innings={(int(r['year']),r['team'],r['role']):r for r in metrics if r['venue']=='all' and r['window']=='all'}
    totals=defaultdict(Counter)
    base=ROOT/'data/observations/r001/games.jsonl'
    receipt=json.loads((HERE/'outputs/inning_features/validation.json').read_text())
    require(digest(base)==receipt['baseline_sha256'],'baseline changed')
    require(digest(HERE/'outputs/inning_features/team_year_metrics.csv.gz')==
            receipt['output_sha256']['team_year_metrics.csv.gz'],'inning metrics changed')
    for line in base.read_text().splitlines():
        g=json.loads(line);y=int(g['date'][:4])
        for t,r,ra in [(g['home'],g['hs'],g['as']),(g['away'],g['as'],g['hs'])]:
            totals[y,t].update(G=1,W=int(r>ra),L=int(r<ra),T=int(r==ra),R=r,RA=ra,
                               oneW=int(r-ra==1),oneL=int(ra-r==1))
    supplied=list(csv.DictReader((p/'team_season_relative.csv').open(encoding='utf-8-sig')))
    sm={(int(r['year']),r['team']):r for r in supplied}
    require(len(sm)==len(supplied)==156 and set(sm)==set(totals),'coverage')
    rows=[];max_log_error=0.0
    for (y,t),v in sorted(totals.items()):
        peers=[(tt,w) for (yy,tt),w in totals.items() if yy==y and (tt in CL)==(t in CL)]
        rank=1+sum(Fraction(w['W'],w['W']+w['L'])>Fraction(v['W'],v['W']+v['L']) for tt,w in peers)
        rr=1+sum(Fraction(w['R'],w['G'])>Fraction(v['R'],v['G']) for tt,w in peers)
        rar=1+sum(Fraction(w['RA'],w['G'])<Fraction(v['RA'],v['G']) for tt,w in peers)
        residual=v['W']-v['R']**1.83/(v['R']**1.83+v['RA']**1.83)*(v['W']+v['L'])
        r=dict(year=y,team=t,rank=rank,runs_rank=rr,allowed_rank=rar,A=rank<=3,low_runs=rr>=5,
               pyth_residual=residual,one_run_win_rate=v['oneW']/(v['oneW']+v['oneL']))
        sr=sm[y,t]
        for k in ['G','W','L','T','R','RA']:require(v[k]==int(sr[k]),f'annual mismatch {y,t,k}')
        require(rank==int(sr['rank']) and rr==int(float(sr['R/G_CL/PL順位'])) and
                rar==int(float(sr['RA/G_CL/PL順位'])),'rank mismatch')
        require(math.isclose(residual,float(sr['pythW_diff']),abs_tol=1e-10) and
                math.isclose(r['one_run_win_rate'],float(sr['1点差勝率']),abs_tol=1e-12),'residual/close game mismatch')
        for role in ['off','def']:
            I,S,R=[int(innings[y,t,role][k]) for k in ['innings','scoring_innings','runs']]
            li,ls,lr=[sum(int(innings[y,tt,role][k]) for tt,w in peers) for k in ['innings','scoring_innings','runs']]
            lg=sum(w['G'] for tt,w in peers)
            terms=dict(lIG=math.log((I/v['G'])/(li/lg)),lSR=math.log((S/I)/(ls/li)),
                       lRPS=math.log((R/S)/(lr/ls)),lRG=math.log((R/v['G'])/(lr/lg)))
            require(math.isclose(terms['lRG'],sum(terms[k] for k in ['lIG','lSR','lRPS']),abs_tol=1e-12),'identity')
            for k,x in terms.items():
                key=role+'_'+k;r[key]=x
                err=abs(x-float(sr[key]));max_log_error=max(max_log_error,err)
                require(err<1e-12,'log mismatch')
        r['net']=r['off_lRG']-r['def_lRG'];require(abs(r['net']-float(sr['net']))<1e-12,'net mismatch')
        rows.append(r)
    tables=[]
    for omit in [False,True]:
        a=[r for r in rows if not omit or r['year']!=2020]
        tables.append(dict(scope='without2020' if omit else 'all',n=len(a),
                           low_B=sum(r['low_runs'] and not r['A'] for r in a),
                           low_A=sum(r['low_runs'] and r['A'] for r in a),
                           other_B=sum(not r['low_runs'] and not r['A'] for r in a),
                           other_A=sum(not r['low_runs'] and r['A'] for r in a)))
    ce=[r for r in rows if r['low_runs'] and r['A']]
    ce7=[r for r in ce if r['year']!=2020];d=[r for r in rows if r['team']=='d']
    require({(r['year'],sm[r['year'],r['team']]['name']) for r in ce}=={(int(r['year']),r['name']) for r in
            csv.DictReader((p/'counterexamples_lowruns_Aclass.csv').open(encoding='utf-8-sig'))},'counterexample set')
    differences={k:mean(r[k] for r in d)-mean(r[k] for r in ce7) for k in
                 ['off_lRG','off_lIG','off_lSR','off_lRPS']}
    # Directly check the report's proposed necessary disjunction; keep its counterexamples.
    failures=[r for r in ce if not ((r['allowed_rank']<=2 and r['net']>=0) or r['pyth_residual']>=6)]
    out=HERE/'outputs'
    write_csv(out/'part5_recalculated.csv',rows)
    result=dict(source_sha256={f.name:digest(f) for f in sorted(p.iterdir()) if f.is_file()},
                checked_team_seasons=len(rows),log_cells_checked=8*len(rows),max_log_absolute_error=max_log_error,
                tables=tables,ce7_count=len(ce7),chunichi_minus_ce7=differences,
                decomposition_shares={k:v/differences['off_lRG'] for k,v in differences.items() if k!='off_lRG'},
                necessary_disjunction_counterexamples=failures,
                script_sha256=digest(__file__),exit_code=0,
                scope='Recomputation from reconciled calendar totals and shared inning-derived metrics; not a new raw-HTML observation.')
    (out/'part5_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','necessary_disjunction_counterexamples']},indent=2))
    print('Necessary-disjunction counterexamples:',[(r['year'],r['team'],r['net'],r['pyth_residual']) for r in failures])


if __name__=='__main__':
    try:main()
    except FileNotFoundError as e:print(e,file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError) as e:print(e,file=sys.stderr);sys.exit(65)
