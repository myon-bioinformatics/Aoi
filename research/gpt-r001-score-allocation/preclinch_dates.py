"""Schedule-consistent A/B clinch bounds without assuming yearly tie-break rules."""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SakAnalytics'/'baseball'))
from season_simulator import Game, Snapshot
from inning_features import read_input, require
from clinch_interval import date
from game_state import build

CL=tuple(sorted(['d','g','t','c','db','s']))


def possible(snapshot, members, target, inside, favorable, seconds=10):
    """Existential top-3 (inside) or bottom (outside), with ties assigned to target."""
    from ortools.sat.python import cp_model
    snapshot.validate();teams=snapshot.teams;n=len(teams);ti=teams.index(target)
    wins=[sum(r) for r in snapshot.wins];losses=[sum(r[i] for r in snapshot.wins) for i in range(n)]
    pairs=Counter(tuple(sorted((teams.index(g.home),teams.index(g.away)))) for g in snapshot.remaining)
    # In top-k feasibility, replacing a target draw/loss with win cannot worsen rank.
    # In outside feasibility, replacing a target draw/win with loss cannot improve rank.
    forced=[]
    for (i,j),count in list(pairs.items()):
        if ti not in (i,j):continue
        other=j if i==ti else i;winner=ti if inside else other;loser=other if inside else ti
        wins[winner]+=count;losses[loser]+=count
        forced.append(dict(teams=[teams[i],teams[j]],wins=[count if winner==i else 0,count if winner==j else 0],draws=0))
        del pairs[i,j]
    tw,td=wins[ti],max(1,wins[ti]+losses[ti]);m=cp_model.CpModel();fw={};fl={};variables={}
    for (i,j),count in pairs.items():
        a=m.new_int_var(0,count,'');b=m.new_int_var(0,count,'');m.add(a+b<=count)
        variables[i,j]=(a,b,count)
        fw.setdefault(i,[]).append(a);fl.setdefault(j,[]).append(a)
        fw.setdefault(j,[]).append(b);fl.setdefault(i,[]).append(b)
    ahead=[]
    for t in members:
        if t==target:continue
        i=teams.index(t);w=wins[i]+sum(fw.get(i,[]));l=losses[i]+sum(fl.get(i,[]))
        denom=m.new_int_var(1,1000,'');m.add_max_equality(denom,[w+l,1])
        delta=w*td-tw*denom;v=m.new_bool_var('')
        if favorable:m.add(delta>0).only_enforce_if(v);m.add(delta<=0).only_enforce_if(~v)
        else:m.add(delta>=0).only_enforce_if(v);m.add(delta<0).only_enforce_if(~v)
        ahead.append(v)
    m.add(sum(ahead)<=2 if inside else sum(ahead)>=3)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=0
    status=solver.solve(m)
    if status==cp_model.MODEL_INVALID:raise RuntimeError(solver.solution_info())
    feasible=True if status in (cp_model.FEASIBLE,cp_model.OPTIMAL) else False if status==cp_model.INFEASIBLE else None
    witness=None
    if feasible:
        witness=list(forced)
        for (i,j),(a,b,count) in variables.items():
            va,vb=solver.value(a),solver.value(b);wins[i]+=va;losses[j]+=va;wins[j]+=vb;losses[i]+=vb
            witness.append(dict(teams=[teams[i],teams[j]],wins=[va,vb],draws=count-va-vb))
        target_pct=Fraction(wins[ti],max(1,wins[ti]+losses[ti]))
        count=0
        for t in members:
            if t==target:continue
            i=teams.index(t);pct=Fraction(wins[i],max(1,wins[i]+losses[i]))
            count+=pct>target_pct if favorable else pct>=target_pct
        require((count<=2)==inside,'rational witness failed')
    return dict(feasible=feasible,status=solver.status_name(status),target_ties='favorable' if favorable else 'unfavorable',witness=witness)


def snapshot(games,day):
    teams=tuple(sorted({g['home'] for g in games}|{g['away'] for g in games}));n=len(teams);w=[[0]*n for _ in teams];d=[[0]*n for _ in teams];remaining=[]
    for g in games:
        when=date(g['url']);i=teams.index(g['home']);j=teams.index(g['away'])
        if when>day:remaining.append(Game(g['url'],when,g['home'],g['away']))
        else:
            delta=sum(g['home_runs'])-sum(g['away_runs'])
            if delta>0:w[i][j]+=1
            elif delta<0:w[j][i]+=1
            else:d[i][j]+=1;d[j][i]+=1
    return Snapshot(teams,w,d,tuple(remaining),day,'retrospective realized complete regular-season schedule; future results hidden')


def boundary(games,year,inside,favorable):
    days=sorted({date(g['url']) for g in games});cache={}
    def query(i):
        if i not in cache:
            cache[i]=possible(snapshot(games,days[i]),CL,'d',inside,favorable)
            require(cache[i]['feasible'] is not None,'solver timeout')
        return cache[i]
    lo=-1;hi=len(days)-1
    require(query(hi)['feasible'] is False,'end of season not clinched')
    while hi-lo>1:
        mid=(hi+lo)//2
        if query(mid)['feasible']:lo=mid
        else:hi=mid
    require(lo>=0,'unexpected first-date clinch')
    return dict(date=days[hi],previous_date=days[lo],at=query(hi),before=query(lo),queries=len(cache),year=year)


def small_check():
    # Exhaust all outcomes for a small four-team round-robin, with draws.
    teams=('d','a','b','c');games=[Game(str(i),'2025-09-02',a,b) for i,(a,b) in enumerate([('d','a'),('d','b'),('a','c'),('b','c')])]
    matrices=[[[0,1,0,1],[1,0,1,0],[1,0,0,1],[0,1,1,0]],
              [[0,9,9,9],[0,0,1,0],[0,0,0,1],[0,1,0,0]],
              [[0,0,0,0],[9,0,1,0],[9,0,0,1],[9,1,0,0]],
              [[0]*4 for _ in teams]]
    checks=0;seen=set()
    for w in matrices:
        s=Snapshot(teams,w,[[0]*4 for _ in teams],tuple(games),'2025-09-01','synthetic')
        for inside,fav in product((True,False),repeat=2):
            exists=False
            for outcomes in product((0,1,2),repeat=len(games)):
                totals=[sum(r) for r in w];ls=[sum(r[i] for r in w) for i in range(4)]
                for g,o in zip(games,outcomes):
                    i,j=teams.index(g.home),teams.index(g.away)
                    if o==0:totals[i]+=1;ls[j]+=1
                    elif o==1:totals[j]+=1;ls[i]+=1
                ps=[Fraction(t,max(1,t+l)) for t,l in zip(totals,ls)]
                ahead=sum(p>ps[0] if fav else p>=ps[0] for p in ps[1:])
                exists|=(ahead<3)==inside
            require(possible(s,teams,'d',inside,fav)['feasible']==exists,'enumeration mismatch');checks+=1;seen.add(exists)
    require(seen=={True,False},'enumeration must cover feasible and infeasible')
    return checks


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('innings','season','out'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--plan-commit',required=True);a=p.parse_args()
    build(a.innings,a.season) # pinned hashes and 936 annual checks before date calculation
    test_count=small_check();games,_=read_input(a.innings);results=[]
    for year in range(2013,2026):
        gs=[g for g in games if g['year']==year];inside=year!=2020
        bounds=[boundary(gs,year,inside,fav) for fav in (True,False)]
        ds=sorted(b['date'] for b in bounds)
        r=dict(year=year,kind='B_class' if inside else 'top3_no_CS',earliest=ds[0],latest=ds[1],exact=ds[0]==ds[1],bounds=bounds)
        if not r['exact'] and year==2016:
            from season_simulator import Rules
            from season_exact import solve
            rules=Rules(CL,('s','g','t','c','d','db'),True,3,'NPB-2016-CL',
                        'https://npb.jp/games/2016/info_cscl.html',False)
            previous=max(date(g['url']) for g in gs if date(g['url'])<ds[0])
            checks={day:solve(snapshot(gs,day),rules,'d',top_k=3,seconds=10) for day in (previous,ds[0])}
            require(checks[previous]['feasible'] is True and checks[ds[0]]['feasible'] is False,'2016 boundary not resolved')
            r.update(exact=True,date=ds[0],official_resolution=dict(source=rules.source,
                previous_order_source='https://npb.jp/bis/2015/stats/std_c.html',league_pct_tiebreak=False,checks=checks))
        elif r['exact']:r['date']=ds[0]
        results.append(r);print(year,r['kind'],r.get('date',ds),flush=True)
    g26=[g for g in games if g['year']==2026]
    import ortools
    result=dict(plan_commit=a.plan_commit,solver='ortools-'+ortools.__version__,small_enumeration_checks=test_count,annual_checks=936,years=results,
                year2026=dict(status='not_evaluable_incomplete_schedule',games=len(g26),last_observed_date=max((date(g['url']) for g in g26),default=None)),
                scope='end-of-day first clinch conditional on complete realized schedule; ties bounded, not assumed')
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
