"""Optional synthetic-only P96 follow-up. Never writes real ledgers or acceptance.

Run from repo root with PYTHONPATH=sakanalytics:pythdragoras.
Features reconstruct the checked game witness, using existing measurement and
proposition predicates. Candidate selection only reads batch 0 / reversed;
freeze its JSON registry before evaluating independent seeds and profiles.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import statistics

import polars as pl
from propositions import _antecedent, load
from sakanalytics import allocation_table, rank_probability, to_team_games
from synthetic_league import _season_witness, plan, validate_period

FEATURES = ('rd', 'wins_vs_pythag', 'sim_p_upper', 'alloc_z_strat')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def features(experiment):
    validate_period(experiment)
    rows = []
    for index, case in enumerate(experiment['cases'], 1):
        p = plan(seed=case['seed'], profile=case['profile'], mean_runs=experiment['mean_runs'],
                 leagues=experiment['leagues'], conversion=experiment['conversion'])
        games = _season_witness(p, case['season'])
        canonical = json.dumps(games, sort_keys=True, separators=(',', ':')).encode()
        if hashlib.sha256(canonical).hexdigest() != case['games_sha256'] or p['annual'] != case['annual']:
            raise ValueError('witness or annual rows differ from the checked experiment')
        # A year-only grouping key, not an asserted schedule/date reconstruction.
        g = pl.DataFrame(games).with_columns(date=pl.lit(f"{case['season']}-01-01"))
        teams = {r['team']: dict(name=r['team'], league=r['league']) for r in p['annual']}
        tg = to_team_games(g, teams)
        st = pl.DataFrame(p['annual']).with_columns(pl.col('season').cast(pl.Int32))
        st = st.join(rank_probability(tg), on=['season','team']).join(
            allocation_table(tg).select('season','team','alloc_z_strat'), on=['season','team'])
        for r in st.to_dicts():
            r.update(rd=r['RF']-r['RA'], wins_vs_pythag=r['W']-r['pythag_expected_wins'],
                     batch_seed=case['batch_seed'], seed=case['seed'], profile=case['profile'],
                     conversion=experiment['conversion'], mean_runs=experiment['mean_runs'])
            r['unit_id'] = f"b{r['batch_seed']}/{r['profile']}/{r['season']}/{r['team']}"
            rows.append(r)
        if index % 14 == 0:
            print(f"measured {index}/{len(experiment['cases'])} annual witnesses", flush=True)
    return rows


def predictions(prop, rows):
    st = pl.DataFrame(rows)
    # Preserve unknowns: this follow-up refuses a silently partial comparison.
    values = st.select(_antecedent(prop, st.columns).alias('hit'))['hit'].to_list()
    if any(v is None for v in values):
        raise ValueError('undetermined predicate; do not count as negative')
    return values


def score(rows, hit):
    groups = dict(tp=[r['unit_id'] for r,h in zip(rows,hit) if h and not r['upper_half']],
                  fp=[r['unit_id'] for r,h in zip(rows,hit) if h and r['upper_half']],
                  fn=[r['unit_id'] for r,h in zip(rows,hit) if not h and not r['upper_half']],
                  tn=[r['unit_id'] for r,h in zip(rows,hit) if not h and r['upper_half']])
    if len(rows) != len(hit):
        raise ValueError("prediction length mismatch")
    tp,fp,fn,tn = (len(groups[k]) for k in ('tp','fp','fn','tn'))
    denom = math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))
    return dict(tp=tp,fp=fp,fn=fn,tn=tn, precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None, mcc=(tp*tn-fp*fn)/denom if denom else None,
                ids=groups)


def characterize(rows):
    out = {}
    for col in FEATURES:
        vals = sorted(r[col] for r in rows if r[col] is not None)
        out[col] = dict(n=len(vals), min=min(vals) if vals else None,
                        median=statistics.median(vals) if vals else None, max=max(vals) if vals else None)
    return dict(n=len(rows), features=out,
                rd_ge_50=sum(r['rd']>=50 for r in rows),
                sim_ge_half=sum(r['sim_p_upper']>=.5 for r in rows),
                wins_below_expectation=sum(r['wins_vs_pythag']<0 for r in rows),
                allocation_below_minus_one=sum(r['alloc_z_strat'] is not None and r['alloc_z_strat'] < -1 for r in rows))


def discover(rows, props):
    train = [r for r in rows if r['batch_seed']==0 and r['profile']=='reversed']
    if len(train)!=168 or len(rows)!=504 or {r['batch_seed'] for r in rows}!={0}:
        raise ValueError('discovery requires only batch 0, all three complete profiles')
    base = props['P96']
    original = predictions(base, train)
    atoms=[]
    for col, thresholds in dict(rd=[-50,0,50], wins_vs_pythag=[-10,-5,0,5,10],
                                sim_p_upper=[.2,.4,.5,.6,.8], alloc_z_strat=[-2,-1,0]).items():
        for value in thresholds:
            for op in ('<','>='):
                atoms.append(dict(col=col,op=op,value=value))
    trials=[]
    for n in (1,2):
        for group in combinations(atoms,n):
            if len({c['col'] for c in group})!=n:continue
            extra=predictions({'if':list(group)},train)
            hit=[a or b for a,b in zip(original,extra)]
            metric=score(train,hit)
            rescued=sum(not a and b and not r['upper_half'] for a,b,r in zip(original,extra,train))
            trials.append(dict(group=list(group), rescued=rescued, added_fp=metric['fp'],
                               mcc=metric['mcc'], precision=metric['precision'], recall=metric['recall']))
    eligible=[t for t in trials if t['added_fp']==0 and t['rescued']>0]
    best=sorted(eligible,key=lambda t:(-t['rescued'],len(t['group']),json.dumps(t['group'],sort_keys=True)))[0] if eligible else None
    definitions=[]
    for cid, title, groups in [
        ('SYN96-C01','P96とP52の和集合',base['if_any']+props['P52']['if_any']),
        ('SYN96-C02','配分が不利という条件から得失点差の上限を外す',base['if_any']+[[dict(col='alloc_z_strat',op='<',value=-1)]]),
        ('SYN96-C03','期待勝利数未満を単独で足す（事後説明）',base['if_any']+[[dict(col='wins_vs_pythag',op='<',value=0)]]),
        ('SYN96-C04','得失点差が非負かつ期待勝利数未満を足す',base['if_any']+[[dict(col='rd',op='>=',value=0),dict(col='wins_vs_pythag',op='<',value=0)]]),
        ('SYN96-C05','配分指標が負なら下位という分岐を足す',base['if_any']+[[dict(col='alloc_z_strat',op='<',value=0)]]),
    ]:
        definitions.append(dict(id=cid,statement=title,if_any=groups,then=base['then'],strength='usually'))
    if best:
        definitions.append(dict(id='SYN96-C06',statement='固定グリッドで誤陽性追加なし・救済最多の拡張',
                                if_any=base['if_any']+[best['group']],then=base['then'],strength='usually'))
    return dict(schema='aoi-synthetic-candidates/1', synthetic=True, discovery_batch=0,
                discovery_profile='reversed', holdout_batches=[1,2],
                selection='No added FP, maximize rescued FN, minimize terms, canonical lexical tie-break. No holdout selection.',
                search_atoms=atoms, searched_rules=len(trials), selected=best,
                ranked_search=sorted(trials,key=lambda t:(-(t['mcc'] or 0),len(t['group'])))[:20],
                candidates=definitions)


def evaluate(rows, props, registry):
    allprops=[props['P52'],props['P96'],*registry['candidates']]
    groups=[]
    keys=sorted({(r['batch_seed'],r['profile'],r['conversion'],r['mean_runs']) for r in rows})
    for batch,profile,conversion,mean in keys:
        part=[r for r in rows if (r['batch_seed'],r['profile'],r['conversion'],r['mean_runs'])==(batch,profile,conversion,mean)]
        metrics={p['id']:score(part,predictions(p,part)) for p in allprops}
        a,b=predictions(props['P52'],part),predictions(props['P96'],part)
        overlap={}
        for name,mask in [('both',[x and y for x,y in zip(a,b)]),('P52_only',[x and not y for x,y in zip(a,b)]),
                          ('P96_only',[y and not x for x,y in zip(a,b)]),('neither',[not x and not y for x,y in zip(a,b)])]:
            subset=[r for r,h in zip(part,mask) if h]
            overlap[name]=dict(n=len(subset),lower=sum(not r['upper_half'] for r in subset),
                               upper=sum(r['upper_half'] for r in subset),ids=[r['unit_id'] for r in subset])
        categories={}
        for name,mask in [('P96_fn',[not h and not r['upper_half'] for r,h in zip(part,b)]),
                          ('P96_tp',[h and not r['upper_half'] for r,h in zip(part,b)]),
                          ('upper',[r['upper_half'] for r in part])]:
            categories[name]=characterize([r for r,h in zip(part,mask) if h])
        groups.append(dict(batch_seed=batch,profile=profile,conversion=conversion,mean_runs=mean,
                           metrics=metrics,overlap=overlap,characterization=categories))
    return dict(schema='aoi-synthetic-rule-evaluation/1',synthetic=True,real_sample_increment=0,
                interpretation='Exploratory retrospective rules, model conditional; no real-world causal verdict or acceptance change.',groups=groups)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['features','discover','evaluate'])
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--registry',type=Path)
    p.add_argument('--propositions',type=Path,default=Path('cycles/c001-chunichi/propositions.toml'))
    a=p.parse_args()
    source=json.loads(a.input.read_text())
    if a.mode=='features':
        result=dict(synthetic=True,source_sha256=sha(a.input),generator_sha256=sha(Path(__file__).with_name('synthetic_league.py')),
                    measurement_sha256=sha(Path(__file__).with_name('sakanalytics.py')),rows=features(source))
    else:
        if source.get('synthetic') is not True or any(r.get('synthetic') is not True for r in source['rows']):
            raise ValueError('synthetic-only input required')
        props={p['id']:p for p in load(a.propositions)[0]}
        result=discover(source['rows'],props) if a.mode=='discover' else evaluate(
            source['rows'],props,json.loads(a.registry.read_text()))
        result.update(input_sha256=sha(a.input),propositions_sha256=sha(a.propositions))
        if a.registry:result['registry_sha256']=sha(a.registry)
    result['analysis_sha256']=sha(__file__)
    write(a.out,result)


if __name__=='__main__':main()
