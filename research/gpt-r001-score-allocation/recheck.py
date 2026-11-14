"""R001 の結果の独立した検算（集計とは別の書き方で数え直し、保存された結果と合うかを確かめる）。

    python research/gpt-r001-score-allocation/recheck.py <処理> [その処理の引数]

処理: clinch_interval, cutoff_independent, early_scoring, game_state, late_reaction, matched_comeback, part5, part6, part7_v2, part7_v2_1, preclinch_flow, prediction_independent, supplement

1 つの処理が 1 つのサブコマンド（旧 verify_clinch_interval.py, verify_cutoff_independent.py, verify_early_scoring.py … の 1 本が 1 つ）。引数と説明は各関数の説明（旧ファイルの冒頭）にある。
集計（analyses.py）の補助（read_input・digest・require など）を使う。
prediction_independent だけは、わざと別の道具（numpy・pandas）で数え直す。
同じ中身の補助は 1 つにし、処理ごとに中身が違う名前には処理の名前を付けた。旧ファイルの HERE・ROOT・sys.path の行は、この冒頭の 1 か所にまとめた。
"""

import argparse
import csv
import gzip
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from statistics import mean, NormalDist

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

from analyses import digest, HERE, INNING_FEATURES_CL as CL, INNING_FEATURES_TEAMS as TEAMS, inning_features_write_csv as write_csv, read_input, require as part5_require, require as supplement_require, ROOT  # noqa: E402


# ==== clinch_interval（旧 verify_clinch_interval.py）

CLINCH_INTERVAL_DOC = """Cross-check the new split against previously verified full-season aggregates."""


def clinch_interval_main(argv=None):
    p=argparse.ArgumentParser(description=CLINCH_INTERVAL_DOC)
    p.add_argument('--result',type=Path,required=True);p.add_argument('--prior-dir',type=Path,required=True)
    a=p.parse_args(argv);d=json.loads(a.result.read_text());early=json.loads((a.prior_dir/'early_scoring.json').read_text());late=json.loads((a.prior_dir/'late_reaction.json').read_text())
    er={(v['year'],v['team']):v for v in early['rows']};lr={(v['year'],v['team']):v for v in late['rows']};checks=0
    rows={(v['phase'],v['group'],v['cut']):v for v in d['scoring_rows']}
    for group,teams in [('中日',['d']),('他セ5球団',['c','db','g','s','t'])]:
        for cut in [6,7]:
            full=rows['full',group,cut]
            for name in ['annual','counts']:
                summed=Counter(rows['before',group,cut][name]);summed.update(rows['after',group,cut][name])
                assert summed==Counter(full[name]);checks+=1
            prior=Counter()
            for t in teams:prior.update(er[2022,t]['annual'])
            assert prior==Counter(full['annual']);checks+=1
            ps=[er[2022,t]['windows'][str(cut)]['by_venue']['all'] for t in teams]
            for target,key in [('G','G'),('early_RF','RF'),('zero','zero'),('three_plus','three_plus')]:
                assert full['counts'][target]==sum(v[key] for v in ps);checks+=1
            for outcome in ['W','L','T']:
                for target,key in [('G','G'),('reg_RF','reg_RF'),('reg_innings','reg_off_innings'),('extra_RF','extra_RF')]:
                    i=late['columns'].index(key)
                    assert full['counts'].get(outcome+'_'+target,0)==sum(lr[2022,t]['cutoffs'][str(cut)]['by_venue']['all']['by_outcome'][outcome][i] for t in teams);checks+=1
    # Wilson endpoints invert the score-z test: check using independent residual form.
    for r in d['interval_rows']:
        n,k=r['n'],r['k']
        if not n:continue
        for ci in r['intervals']:
            z=ci['z']
            for bound in [ci['lo'],ci['hi']]:
                if 0<bound<1:
                    residual=(k/n-bound)**2-z*z*bound*(1-bound)/n
                    assert abs(residual)<1e-12;checks+=1
            assert abs(ci['coverage_normal']-(2*NormalDist().cdf(z)-1))<1e-14;checks+=1
    print(json.dumps({'checks':checks,'all_match':True}))


def clinch_interval(argv=None):
    """verify_clinch_interval.py の入口（説明は CLINCH_INTERVAL_DOC）。
    """
    clinch_interval_main(argv)


# ==== cutoff_independent（旧 verify_cutoff_independent.py）

CUTOFF_INDEPENDENT_DOC = """Independent CSV-off-row replay of cutoff counts (does not import main/helper)."""


def cutoff_independent_main(argv=None):
    ap=argparse.ArgumentParser(description=CUTOFF_INDEPENDENT_DOC)
    ap.add_argument('--innings',type=Path,required=True)
    ap.add_argument('--result',type=Path,required=True)
    a=ap.parse_args(argv)
    raw=defaultdict(dict)
    with gzip.open(a.innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or not 2013<=int(r['year'])<=2025:continue
            key=(int(r['year']),r['url'])
            team=r['team']
            raw[key].setdefault(team,{'home':r['batting_home'],'runs':{}})['runs'][int(r['inning'])]=int(r['runs'])
    groups=defaultdict(list)
    for (year,url),teams in raw.items():
        assert len(teams)==2
        vals=list(teams.items())
        for team,v in vals:
            other=next(o for t,o in vals if t!=team)
            # Input uses 1/0 (accept boolean spellings explicitly, no truthy strings).
            assert v['home'] in ['1','0','True','False','true','false']
            home=v['home'] in ['1','True','true']
            ours=[v['runs'][i] for i in range(1,max(v['runs'])+1)]
            theirs=[other['runs'][i] for i in range(1,max(other['runs'])+1)]
            hr,ar=(ours,theirs) if home else (theirs,ours)
            home_sofar=0;away_sofar=0;opp=0;last_before=None
            for i,awayrun in enumerate(ar,1):
                away_sofar+=awayrun
                if i<=len(hr):
                    if i>=9 and home_sofar<=away_sofar:opp+=1
                    last_before=home_sofar
                    home_sofar+=hr[i-1]
            walkoff=int(len(hr)==len(ar) and len(hr)>=9 and home_sofar>away_sofar and last_before<=away_sofar)
            groups[year,team].append((home,ours,theirs,opp,walkoff))
    x=json.loads(a.result.read_text());assert len(groups)==156
    checked=0
    for row in x['rows']:
        games=groups[row['year'],row['team']]
        for venue in ['home','away']:
            gs=[g for g in games if g[0]==(venue=='home')]
            w=row['walkoff'][venue]
            assert [len(gs),sum(g[3]>0 for g in gs),sum(g[3] for g in gs),sum(g[4] for g in gs)]==[w['G'],w['opportunity_games'],w['opportunity_innings'],w['walkoff_condition_games']]
        for c in [6,7]:
            cut=row['cutoffs'][str(c)]
            gs=[g for g in games if len(g[1])>=c and len(g[2])>=c]
            assert len(games)-len(gs)==cut['excluded_short_games']
            for venue in ['all','home','away']:
                bins=defaultdict(lambda:[0]*13)
                for home,o,t,_,_ in gs:
                    if venue!='all' and home!=(venue=='home'):continue
                    total_o,total_t=sum(o),sum(t)
                    front_o,front_t=sum(o[:c]),sum(t[:c])
                    r='0' if front_o==0 else '1-2' if front_o<=2 else '3+'
                    state='lead' if front_o>front_t else 'tie' if front_o==front_t else 'trail'
                    net=sum(o[c:])-sum(t[c:])
                    counts=[1,int(total_o>total_t),int(total_o<total_t),int(total_o==total_t),sum(o[c:]),sum(t[c:]),len(o[c:]),len(t[c:]),net,net*net,int(net>0),int(net==0),int(net<0)]
                    for label in ['all','runs:'+r,'state:'+state,'cross:'+r+'|'+state]:
                        bins[label]=[v+n for v,n in zip(bins[label],counts)]
                actual=cut['by_venue'][venue]
                assert actual['all']==bins['all'];checked+=1
                for dim in ['runs','state','cross']:
                    for label,values in actual[dim].items():
                        assert values==bins[dim+':'+label],(row['year'],row['team'],c,venue,dim,label)
                        checked+=1
    print(f'Independent replay: {checked} cells / {checked*13} integer values and 312 walkoff venue aggregates match')


def cutoff_independent(argv=None):
    """verify_cutoff_independent.py の入口（説明は CUTOFF_INDEPENDENT_DOC）。
    """
    cutoff_independent_main(argv)


# ==== early_scoring（旧 verify_early_scoring.py）

EARLY_SCORING_DOC = """Independent offense-only CSV histogram replay and preceding cutoff cross-check."""


def early_scoring_main(argv=None):
    p=argparse.ArgumentParser(description=EARLY_SCORING_DOC)
    for k in ['innings','result','cutoff']:p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args(argv)
    pages=defaultdict(dict)
    with gzip.open(a.innings,'rt') as f:
        for r in csv.DictReader(f):
            y=int(r['year'])
            if r['side']!='off' or not 2013<=y<=2025:continue
            team=pages[y,r['url']].setdefault(r['team'],{'home':r['batting_home'] in ['1','True','true'],'scores':{}})
            team['scores'][int(r['inning'])]=int(r['runs'])
    groups=defaultdict(list)
    for (y,url),teams in pages.items():
        assert len(teams)==2
        for t,r in teams.items():
            other=next(v for k,v in teams.items() if k!=t)
            groups[y,t].append((r['home'],r['scores'],other['scores']))
    x=json.loads(a.result.read_text());old=json.loads(a.cutoff.read_text())
    oldrows={(r['year'],r['team']):r for r in old['rows']}
    n=0
    for row in x['rows']:
        gs=groups[row['year'],row['team']]
        for c in [6,7]:
            eligible=[g for g in gs if max(g[1])>=c and max(g[2])>=c]
            assert row['windows'][str(c)]['excluded']==len(gs)-len(eligible)
            for venue in ['all','home','away']:
                subset=[g for g in eligible if venue=='all' or g[0]==(venue=='home')]
                hist=Counter(sum(g[1][i] for i in range(1,c+1)) for g in subset)
                si=sum(g[1][i]>0 for g in subset for i in range(1,c+1))
                v=row['windows'][str(c)]['by_venue'][venue]
                assert v['histogram']=={str(k):val for k,val in hist.items()}
                assert v['G']==len(subset) and v['RF']==sum(k*val for k,val in hist.items()) and v['scoring_innings']==si
                prior=oldrows[row['year'],row['team']]['cutoffs'][str(c)]['by_venue'][venue]
                assert [hist[0],hist[1]+hist[2],sum(val for k,val in hist.items() if k>=3)]==[prior['runs'][label][0] for label in ['0','1-2','3+']]
                col=old['cell_columns'];priorall=dict(zip(col,prior['all']))
                assert v['RF']==sum(sum(g[1].values()) for g in subset)-priorall['late_RF']
                n+=1
        paired=[g for g in gs if max(g[1])>=7 and max(g[2])>=7]
        v=row['paired7']
        expected=dict(G=len(paired),first6_RF=sum(sum(g[1][i] for i in range(1,7)) for g in paired),seventh_RF=sum(g[1][7] for g in paired),first7_RF=sum(sum(g[1][i] for i in range(1,8)) for g in paired),seventh_scoring_games=sum(g[1][7]>0 for g in paired),newly_reached_three=sum(sum(g[1][i] for i in range(1,7))<3<=sum(g[1][i] for i in range(1,8)) for g in paired))
        assert all(v[k]==val for k,val in expected.items())
        for c in ['6','7']:
            peers=[r for r in x['rows'] if r['year']==row['year'] and r['league']==row['league'] and r['team']!=row['team']]
            pv=[p['windows'][c]['by_venue']['all'] for p in peers]
            ours=row['windows'][c]['by_venue']['all'];actual=row['comparison'][c]
            den=sum(p['G'] for p in pv)
            for k,numerator in [('mean_runs','RF'),('zero_rate','zero'),('three_plus_rate','three_plus')]:
                expected_rate=sum(p[numerator] for p in pv)/den
                assert abs(actual['other5_pooled'][k]-expected_rate)<1e-12
                assert abs(actual['gaps'][k]-(ours[k]-expected_rate))<1e-12
            assert actual['mean_runs_rank']==1+sum(p['RF']/p['G']>ours['RF']/ours['G'] for p in pv)
    print(f'Independent direct CSV replay: {n} histograms, preceding cutoff buckets/early totals, 156 paired-seventh groups, 312 peer comparisons match')


def early_scoring(argv=None):
    """verify_early_scoring.py の入口（説明は EARLY_SCORING_DOC）。
    """
    early_scoring_main(argv)


# ==== game_state（旧 verify_game_state.py）

GAME_STATE_DOC = """Independent score accumulation, cell partitions and prior denominator checks."""


def game_state_verify(innings,csv_path,result_path,previous):
    pages=defaultdict(dict)
    with gzip.open(innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or int(r['year'])>2025:continue
            g=pages[int(r['year']),r['url']].setdefault(r['team'],{'home':r['batting_home']=='True','runs':{}})
            g['runs'][int(r['inning'])]=int(r['runs'])
    counts=defaultdict(Counter)
    for (year,_),teams in pages.items():
        h=next(t for t in teams if teams[t]['home']);a=next(t for t in teams if t!=h)
        scores={h:0,a:0};cuts={}
        for i in sorted(teams[a]['runs']):
            scores[a]+=teams[a]['runs'][i]
            if i in teams[h]['runs']:scores[h]+=teams[h]['runs'][i]
            if i in (6,7) and i in teams[h]['runs'] and i+1 in teams[a]['runs']:cuts[i]=dict(scores)
        for cut,early in cuts.items():
            for t,o in ((h,a),(a,h)):
                c=counts[year,t,cut,t==h,early[t]-early[o]];final=scores[t]-scores[o]
                c.update(G=1,W=int(final>0),L=int(final<0),T=int(final==0),
                         late_RF=scores[t]-early[t],late_RA=scores[o]-early[o],
                         off_innings=sum(i>cut for i in teams[t]['runs']),def_innings=sum(i>cut for i in teams[o]['runs']))
    fields=('G','W','L','T','late_RF','late_RA','off_innings','def_innings')
    with csv_path.open() as f: rows=list(csv.DictReader(f))
    assert len(counts)==len(rows)
    for r in rows:
        for k in ('year','cutoff','margin',*fields):r[k]=int(r[k])
        r['home']=r['home']=='True'
        key=tuple(r[k] for k in ('year','team','cutoff','home','margin'))
        assert all(r[f]==counts[key][f] for f in fields),key
    x=json.loads(result_path.read_text());checked=0
    for c in x['comparisons']:
        years={int(c['period'])} if c['period'].isdigit() else set(range(2013,2026)) - ({2020} if c['period']=='no2020' else set())
        selected=[r for r in rows if r['year'] in years and r['cutoff']==c['cutoff'] and (c['venue']=='all' or r['home']==(c['venue']=='home'))]
        for side in ('own','peer'):
            subset=[r for r in selected if (r['team']==c['team'] if side=='own' else r['league']==c['league'] and r['team']!=c['team'])]
            bins=defaultdict(Counter);states=defaultdict(Counter);all_=Counter()
            for r in subset:
                m=r['margin'];b='-3+' if m<=-3 else '3+' if m>=3 else str(m);s='lead' if m>0 else 'trail' if m<0 else 'tie'
                values={f:r[f] for f in fields};bins[b].update(values);states[s].update(values);all_.update(values)
            checks=[(c[side]['all'],all_)]+[(v,bins[k]) for k,v in c[side]['bins'].items()]+[(v,states[k]) for k,v in c[side]['states'].items()]
            for actual,expected in checks:
                assert all(actual[f]==expected[f] for f in fields)
                assert actual['share']==(expected['G']/all_['G'] if all_['G'] else None)
                assert actual['win_fraction']==(expected['W']/expected['G'] if expected['G'] else None)
                checked+=1
        for key,state,rate,sign in [('S1','trail','share',1),('S2','lead','share',-1),('S3','lead','win_fraction',-1)]:
            p=c['propositions'][key];oa,ob=p['own'];pa,pb=p['peer']
            expected=(oa/ob-pa/pb) if ob and pb else None
            assert p['difference']==expected
            assert p['verdict']==('unavailable' if expected is None else 'supports_direction' if (oa*pb-pa*ob)*sign>0 else 'counterexample')
    old=json.loads(previous.read_text());prior_checks=0
    for r in old['cells']:
        c=counts[r['year'],r['team'],r['cutoff'],r['home'],-r['deficit']]
        assert all(c[f]==r[f] for f in ('G','W','L','T','late_RF','late_RA','off_innings'));prior_checks+=1
    return dict(status='passed',source_games=len(pages),cell_rows=len(rows),integer_values=len(rows)*len(fields),summary_groups=checked,previous_trailing_cells=prior_checks,
                scope='independent accumulation of same shared CSV; no separate raw HTML retrieval')


def game_state_main(argv=None):
    p=argparse.ArgumentParser(description=GAME_STATE_DOC)
    for name in ('innings','csv','result','previous','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(argv);r=game_state_verify(a.innings,a.csv,a.result,a.previous);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(r)


def game_state(argv=None):
    """verify_game_state.py の入口（説明は GAME_STATE_DOC）。
    """
    game_state_main(argv)


# ==== late_reaction（旧 verify_late_reaction.py）

LATE_REACTION_DOC = """Cross-check all cutoff totals and independently replay comeback paths from CSV."""


def late_reaction_main(argv=None):
    ap=argparse.ArgumentParser(description=LATE_REACTION_DOC)
    for k in ['innings','result','cutoff']:ap.add_argument('--'+k,type=Path,required=True)
    a=ap.parse_args(argv);x=json.loads(a.result.read_text());old=json.loads(a.cutoff.read_text())
    om={(r['year'],r['team']):r for r in old['rows']};cells=0
    for r in x['rows']:
        for c in ['6','7']:
            v=r['cutoffs'][c];prior=om[r['year'],r['team']]['cutoffs'][c]
            assert v['excluded']==prior['excluded_short_games']
            for venue in ['all','home','away']:
                p=prior['by_venue'][venue];n=v['by_venue'][venue]
                pairs=[(n['all'],p['all'])]+[(n['by_state'][k],vals) for k,vals in p['state'].items()]
                for new,previous in pairs:
                    assert new[:4]==previous[:4]
                    assert [new[6]+new[8],new[7]+new[9],new[10]+new[12],new[11]+new[13]]==previous[4:8]
                    cells+=1
                for state in ['lead','tie','trail']:
                    for idx,outcome in [(1,'W'),(2,'L'),(3,'T')]:
                        assert n['cross'][state+'|'+outcome][0]==p['state'][state][idx]
                for idx,outcome in [(1,'W'),(2,'L'),(3,'T')]:
                    assert n['by_outcome'][outcome][0]==p['all'][idx]
                for runbin,previous in p['runs'].items():
                    for idx,outcome in [(1,'W'),(2,'L'),(3,'T')]:
                        assert sum(val for key,val in n['joint_by_outcome'][outcome].items() if key.split('|')[0]==runbin)==previous[idx]
    pages=defaultdict(dict)
    with gzip.open(a.innings,'rt') as f:
        for row in csv.DictReader(f):
            year=int(row['year']);team=row['team']
            if row['side']!='off' or not 2013<=year<=2025:continue
            r=pages[year,row['url']].setdefault(team,{'home':row['batting_home'] in ['1','True','true'],'runs':{}})
            r['runs'][int(row['inning'])]=int(row['runs'])
    # Independent chronology: update scoreboard top then bottom, recording own-half endpoints.
    direct=defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:[0,0,0,0])))
    direct_outcome=defaultdict(lambda:[0]*19)
    targeted=set((r['year'],r['team']) for r in x['rows'] if r['team']=='d' or (r['year']==2022 and r['league']=='C'))
    for (year,url),teams in pages.items():
        assert len(teams)==2
        home=next((t,v) for t,v in teams.items() if v['home']);away=next((t,v) for t,v in teams.items() if not v['home'])
        h,a0=home[1]['runs'],away[1]['runs'];score_h=score_a=0;states={home[0]:{},away[0]:{}}
        cutoff_scores={}
        for inning in range(1,max(h.keys()|a0.keys())+1):
            if inning in a0:
                score_a+=a0[inning];states[away[0]][inning]=score_a-score_h
            if inning in h:
                score_h+=h[inning];states[home[0]][inning]=score_h-score_a
            if inning in [6,7] and inning in h and inning in a0:cutoff_scores[inning]=(score_h,score_a)
        for team,ours,theirs,homeflag in [(home[0],h,a0,True),(away[0],a0,h,False)]:
            if (year,team) not in targeted:continue
            outcome='W' if sum(ours.values())>sum(theirs.values()) else 'L' if sum(ours.values())<sum(theirs.values()) else 'T'
            for c,(sh,sa) in cutoff_scores.items():
                eo,et=(sh,sa) if homeflag else (sa,sh)
                ro=sum(v for i,v in ours.items() if c<i<=9);rt=sum(v for i,v in theirs.items() if c<i<=9)
                xo=sum(v for i,v in ours.items() if i>9);xt=sum(v for i,v in theirs.items() if i>9)
                counts=[1,int(outcome=='W'),int(outcome=='L'),int(outcome=='T'),eo,et,ro,rt,xo,xt,
                    sum(c<i<=9 for i in ours),sum(c<i<=9 for i in theirs),sum(i>9 for i in ours),sum(i>9 for i in theirs),
                    int(ro==0),int(ro==1),int(ro==2),int(ro>=3),int(ro+xo>0)]
                for venue in ['all','home' if homeflag else 'away']:
                    key=(year,team,str(c),venue,outcome)
                    direct_outcome[key]=[v+n for v,n in zip(direct_outcome[key],counts)]
                if eo>=et or outcome!='L':continue
                rf=sum(v for i,v in ours.items() if i>c);ra=sum(v for i,v in theirs.items() if i>c)
                deltas=[d for i,d in states[team].items() if i>c]
                if not rf:label='no_late_runs'
                elif max(deltas)>0:label='led_then_lost'
                elif max(deltas)==0:label='tied_never_led'
                else:label='scored_never_tied'
                margin=str(et-eo) if et-eo<=2 else '3+'
                for venue in ['all','home' if homeflag else 'away']:
                    for m in ['all',margin]:
                        key=(year,team,str(c),venue,m)
                        v=direct[key][label]['value']
                        direct[key][label]['value']=[v[0]+1,v[1]+et-eo,v[2]+rf,v[3]+ra]
    checked=0;outcome_checked=0
    for r in x['rows']:
        if (r['year'],r['team']) not in targeted:continue
        for c in ['6','7']:
            for venue,v in r['cutoffs'][c]['by_venue'].items():
                for outcome,values in v['by_outcome'].items():
                    assert values==direct_outcome[r['year'],r['team'],c,venue,outcome]
                    outcome_checked+=1
                for margin,classes in v['losing_comeback'].items():
                    for label,values in classes.items():
                        assert values==direct[r['year'],r['team'],c,venue,margin][label]['value'],(r['year'],r['team'],c,venue,margin,label)
                        checked+=1
    print(f'Prior cutoff cross-check: {cells} cells match; independent top/bottom chronology: {len(targeted)} team-years / {checked} classification cells and {outcome_checked} outcome totals match')


def late_reaction(argv=None):
    """verify_late_reaction.py の入口（説明は LATE_REACTION_DOC）。
    """
    late_reaction_main(argv)


# ==== matched_comeback（旧 verify_matched_comeback.py）

MATCHED_COMEBACK_DOC = """Independent off-row chronological replay and direct-weight comparison check."""


def matched_comeback_verify(innings, output):
    result=json.loads(output.read_text())
    games=defaultdict(dict)
    with gzip.open(innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or int(r['year'])>2025:continue
            t=games[int(r['year']),r['url']].setdefault(r['team'],dict(home=r['batting_home']=='True',runs={}))
            t['runs'][int(r['inning'])]=int(r['runs'])
    counts=defaultdict(Counter)
    for (year,_),teams in games.items():
        h=next(t for t,v in teams.items() if v['home']);a=next(t for t in teams if t!=h)
        hr,ar=teams[h]['runs'],teams[a]['runs']
        score={h:0,a:0};states={h:{},a:{}};cuts={}
        for i in range(1,max(ar)+1):
            score[a]+=ar[i];states[a][i]=score[a]-score[h]
            if i in hr:score[h]+=hr[i];states[h][i]=score[h]-score[a]
            if i in (6,7) and i in hr and i+1 in ar:cuts[i]=dict(score)
        for team,other in ((h,a),(a,h)):
            own=teams[team]['runs'];opp=teams[other]['runs']
            for cut,early in cuts.items():
                if early[team]>=early[other]:continue
                ds=[v for i,v in states[team].items() if i>cut]
                rf=sum(v for i,v in own.items() if i>cut)
                highest=max(ds,default=-999)
                category='led' if highest>0 else 'level_never_led' if highest==0 else 'never_level' if rf>0 else 'no_runs'
                final=score[team]-score[other]
                c=counts[year,team,cut,team==h,early[other]-early[team]]
                c.update(G=1,level_or_better=int(highest>=0),W=int(final>0),L=int(final<0),T=int(final==0),
                         late_RF=rf,late_RA=sum(v for i,v in opp.items() if i>cut),off_innings=sum(i>cut for i in own))
                c[category]+=1
    fields=['G','level_or_better','led','W','L','T','no_runs','never_level','level_never_led','late_RF','late_RA','off_innings']
    assert len(counts)==len(result['cells'])
    for r in result['cells']:
        key=tuple(r[k] for k in ['year','team','cutoff','home','deficit'])
        assert all(r[f]==counts[key][f] for f in fields),key
    checks=0
    for comparison in result['yearly']+result['pooled']:
        own=defaultdict(Counter);peer=defaultdict(Counter)
        for r in result['cells']:
            if r['year'] not in comparison['years'] or r['league']!=comparison['league'] or r['cutoff']!=comparison['cutoff']:continue
            if comparison['venue']!='all' and r['home']!=(comparison['venue']=='home'):continue
            m=r['deficit'] if comparison['margin']=='exact' else min(3,r['deficit'])
            target=own if r['team']==comparison['team'] else peer
            target[r['year'],r['home'],m].update({f:r[f] for f in fields})
        shared=set(own)&set(peer);n=sum(own[k]['G'] for k in shared)
        assert n==comparison['common_own_G']
        for metric in ('level_or_better','led','W'):
            numerator=sum(own[k][metric] for k in shared)
            expected=Fraction(0)
            for k in shared:expected+=Fraction(peer[k][metric],peer[k]['G'])*own[k]['G']
            observed=comparison['metrics'][metric]
            assert numerator==observed['own_count']
            if n:
                delta=(numerator-expected)/n
                assert [delta.numerator,delta.denominator]==observed['difference_fraction']
            else:assert observed['difference'] is None
            checks+=1
    return dict(status='passed',source_games=len(games),cell_rows=len(counts),integer_values=len(counts)*len(fields),weighted_metric_comparisons=checks,
                scope='separate CSV off-row replay and rational weighting; same source, not independent HTML acquisition')


def matched_comeback_main(argv=None):
    p=argparse.ArgumentParser(description=MATCHED_COMEBACK_DOC)
    for k in ('innings','result','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args(argv);report=matched_comeback_verify(a.innings,a.result)
    a.out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


def matched_comeback(argv=None):
    """verify_matched_comeback.py の入口（説明は MATCHED_COMEBACK_DOC）。
    """
    matched_comeback_main(argv)


# ==== part5（旧 verify_part5.py）

def part5_main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--share',type=Path,required=True)
    p=ap.parse_args(argv).share
    with gzip.open(HERE/'outputs/inning_features/team_year_metrics.csv.gz','rt') as f:
        metrics=list(csv.DictReader(f))
    innings={(int(r['year']),r['team'],r['role']):r for r in metrics if r['venue']=='all' and r['window']=='all'}
    totals=defaultdict(Counter)
    base=ROOT/'data/observations/r001/games.jsonl'
    receipt=json.loads((HERE/'outputs/inning_features/validation.json').read_text())
    part5_require(digest(base)==receipt['baseline_sha256'],'baseline changed')
    part5_require(digest(HERE/'outputs/inning_features/team_year_metrics.csv.gz')==
            receipt['output_sha256']['team_year_metrics.csv.gz'],'inning metrics changed')
    for line in base.read_text().splitlines():
        g=json.loads(line);y=int(g['date'][:4])
        for t,r,ra in [(g['home'],g['hs'],g['as']),(g['away'],g['as'],g['hs'])]:
            totals[y,t].update(G=1,W=int(r>ra),L=int(r<ra),T=int(r==ra),R=r,RA=ra,
                               oneW=int(r-ra==1),oneL=int(ra-r==1))
    supplied=list(csv.DictReader((p/'team_season_relative.csv').open(encoding='utf-8-sig')))
    sm={(int(r['year']),r['team']):r for r in supplied}
    part5_require(len(sm)==len(supplied)==156 and set(sm)==set(totals),'coverage')
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
        for k in ['G','W','L','T','R','RA']:part5_require(v[k]==int(sr[k]),f'annual mismatch {y,t,k}')
        part5_require(rank==int(sr['rank']) and rr==int(float(sr['R/G_CL/PL順位'])) and
                rar==int(float(sr['RA/G_CL/PL順位'])),'rank mismatch')
        part5_require(math.isclose(residual,float(sr['pythW_diff']),abs_tol=1e-10) and
                math.isclose(r['one_run_win_rate'],float(sr['1点差勝率']),abs_tol=1e-12),'residual/close game mismatch')
        for role in ['off','def']:
            I,S,R=[int(innings[y,t,role][k]) for k in ['innings','scoring_innings','runs']]
            li,ls,lr=[sum(int(innings[y,tt,role][k]) for tt,w in peers) for k in ['innings','scoring_innings','runs']]
            lg=sum(w['G'] for tt,w in peers)
            terms=dict(lIG=math.log((I/v['G'])/(li/lg)),lSR=math.log((S/I)/(ls/li)),
                       lRPS=math.log((R/S)/(lr/ls)),lRG=math.log((R/v['G'])/(lr/lg)))
            part5_require(math.isclose(terms['lRG'],sum(terms[k] for k in ['lIG','lSR','lRPS']),abs_tol=1e-12),'identity')
            for k,x in terms.items():
                key=role+'_'+k;r[key]=x
                err=abs(x-float(sr[key]));max_log_error=max(max_log_error,err)
                part5_require(err<1e-12,'log mismatch')
        r['net']=r['off_lRG']-r['def_lRG'];part5_require(abs(r['net']-float(sr['net']))<1e-12,'net mismatch')
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
    part5_require({(r['year'],sm[r['year'],r['team']]['name']) for r in ce}=={(int(r['year']),r['name']) for r in
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


def part5(argv=None):
    """Recalculate Part5's main comparisons using the previously reconciled inputs.
    """
    try:part5_main(argv)
    except FileNotFoundError as e:print(e,file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError) as e:print(e,file=sys.stderr);sys.exit(65)


# ==== part6（旧 verify_part6.py）

PART6_DOC = """Check Part6 replay CSVs and calculate descriptive sensitivity checks (stdlib)."""


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def part6_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def compare_csv(a, b):
    af, ar = read_csv(a)
    bf, br = read_csv(b)
    require(af == bf and len(ar) == len(br), f'CSV shape: {a.name}')
    for i, (x, y) in enumerate(zip(ar, br)):
        for k in af:
            if x[k] == y[k]:
                continue
            try:
                u, v = float(x[k]), float(y[k])
            except ValueError:
                raise ValueError(f'CSV mismatch: {a.name} row {i} {k}')
            require(math.isclose(u, v, rel_tol=1e-10, abs_tol=1e-12),
                    f'CSV numeric mismatch: {a.name} row {i} {k}')
    return len(ar)


def corr(x, y):
    a, b = mean(x), mean(y)
    return sum((u-a)*(v-b) for u, v in zip(x, y)) / math.sqrt(
        sum((u-a)**2 for u in x) * sum((v-b)**2 for v in y))


def inverse(matrix):
    n = len(matrix)
    a = [list(row) + [float(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = max(range(j, n), key=lambda i: abs(a[i][j]))
        a[j], a[pivot] = a[pivot], a[j]
        require(abs(a[j][j]) > 1e-14, 'singular design')
        scale = a[j][j]
        a[j] = [v / scale for v in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [u-scale*v for u, v in zip(a[i], a[j])]
    return [row[n:] for row in a]


def matvec(a, v):
    return [sum(x*y for x, y in zip(row, v)) for row in a]


def regression(rows):
    fields = ['off_lSR', 'off_lRPS', 'def_lSR', 'def_lRPS']
    x = [[1.0] + [float(r[k]) for k in fields] for r in rows]
    y = [float(r['win%']) for r in rows]
    n, p = len(x), 5
    bread = inverse([[sum(r[i]*r[j] for r in x) for j in range(p)] for i in range(p)])
    beta = matvec(bread, [sum(r[i]*v for r, v in zip(x, y)) for i in range(p)])
    error = [v-sum(a*b for a, b in zip(r, beta)) for r, v in zip(x, y)]
    # Contrast SR minus RPS; CR1 single-cluster sandwich, separately by team/year.
    c = [0.0, 1.0, -1.0, 0.0, 0.0]
    bc = matvec(bread, c)
    delta = beta[1]-beta[2]
    s2 = sum(v*v for v in error)/(n-p)
    se = math.sqrt(s2*sum(a*b for a, b in zip(c, bc)))
    out = dict(coefficient_order=['intercept']+fields, coefficients=beta,
               sr_minus_rps=delta, iid_se=se, iid_t=delta/se)
    for field in ['team', 'year']:
        groups = sorted({r[field] for r in rows})
        variance = 0.0
        for g in groups:
            score = [sum(xx[j]*ee for xx, ee, rr in zip(x, error, rows) if rr[field] == g)
                     for j in range(p)]
            variance += sum(a*b for a, b in zip(bc, score))**2
        se = math.sqrt(variance*len(groups)/(len(groups)-1)*(n-1)/(n-p))
        out[field+'_cluster'] = dict(clusters=len(groups), se=se, t=delta/se)
    return out


def part6_main(argv=None):
    ap = argparse.ArgumentParser(description=PART6_DOC)
    ap.add_argument('--part5', type=Path, required=True, help='extracted Part5 directory')
    ap.add_argument('--part6', type=Path, required=True, help='original extracted Part6 directory')
    ap.add_argument('--replay', type=Path, required=True, help='Part6 directory after replay of p6/p6b/p6c')
    ap.add_argument('--out', type=Path, default=Path(__file__).parent/'outputs/part6_verification.json')
    args = ap.parse_args(argv)
    matched = {p.name:compare_csv(p, args.replay/p.name) for p in sorted(args.part6.glob('*.csv'))}
    require(len(matched) == 10, 'expected 10 CSVs')
    _, rows = read_csv(args.part5/'team_season_relative.csv')
    by_key = {(int(r['year']), r['team']):r for r in rows}
    require(len(rows) == len(by_key) == 156, 'team-year coverage')
    pairs = [(r, by_key[y+1, t]) for (y, t), r in sorted(by_key.items()) if (y+1, t) in by_key]
    correlations = []
    for omit in [False, True]:
        selected = [(a, b) for a, b in pairs if not omit or int(a['year']) not in [2019, 2020]]
        for exclude in [False, True]:
            q = [(a, b) for a, b in selected if not exclude or a['team'] != 'd']
            correlations.append(dict(omit_pairs_touching2020=omit, exclude_chunichi=exclude,
                n=len(q), off_lRPS=corr([float(a['off_lRPS']) for a, b in q],
                                      [float(b['off_lRPS']) for a, b in q])))
    require([r['n'] for r in correlations] == [144, 132, 120, 110], 'pair coverage')
    result = dict(part6_source_sha256={p.name:part6_digest(p) for p in sorted(args.part6.iterdir()) if p.is_file()},
                  part5_team_season_sha256=part6_digest(args.part5/'team_season_relative.csv'),
                  replay_csv_rows=matched, csv_tolerance=dict(rel=1e-10, abs=1e-12),
                  correlations=correlations, regression_sensitivity=regression(rows),
                  script_sha256=part6_digest(__file__), exit_code=0,
                  scope='Replay comparison and descriptive sensitivity; no new raw HTML, causal effect, or calibrated hypothesis test.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(matched_csvs=len(matched), correlations=correlations,
                          regression_sensitivity=result['regression_sensitivity']), indent=2))


def part6(argv=None):
    """verify_part6.py の入口（説明は PART6_DOC）。
    """
    part6_main(argv)


# ==== part7_v2（旧 verify_part7_v2.py）

PART7_V2_DOC = """Independent aggregate checks for locally supplied Part7 v2 (stdlib; no raw output)."""


def part7_v2_read(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8-sig', newline='') as f:
        yield from csv.DictReader(f)


def number(value):
    return float(value) if value else None


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


def part7_v2_verify(source, previous=None):
    source = Path(source)
    halves = list(part7_v2_read(source/'v2/half_innings_v2_public.csv.gz'))
    official = list(part7_v2_read(source/'official_team_SB_CS_2013_2026.csv'))
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
    expected={(int(r['year']),r['team'],r['side']):r for r in part7_v2_read(source/'v2/team_season_v2.csv')}
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
    supplied=list(part7_v2_read(source/'v2/propositions_2x2_v2.csv')); checks=[]
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
    cases=list(part7_v2_read(source/'v2/counterexamples_2x2_v2.csv'))
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
        for r in part7_v2_read(Path(previous)/'half_innings_pbp_derived.csv.gz'):
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


def part7_v2_main(argv=None):
    p=argparse.ArgumentParser(description=PART7_V2_DOC)
    p.add_argument('source',type=Path,help='extracted part7 directory')
    p.add_argument('--previous',type=Path,help='v1 part7 directory, optional')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    result=part7_v2_verify(args.source,args.previous)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'diagnostics':result['diagnostics']},ensure_ascii=False))


def part7_v2(argv=None):
    """verify_part7_v2.py の入口（説明は PART7_V2_DOC）。
    """
    part7_v2_main(argv)


# ==== part7_v2_1（旧 verify_part7_v2_1.py）

PART7_V2_1_DOC = """Check supplied v2.1 audit tables against unchanged v2 inputs; emit aggregates only."""


def part7_v2_1_verify(source, previous):
    source, previous = Path(source), Path(previous)
    old = {str(p.relative_to(previous)): p for p in previous.rglob('*') if p.is_file()}
    new = {str(p.relative_to(source)): p for p in source.rglob('*') if p.is_file()}
    added = {'v2/errata_v2_1.md', 'v2/audit_cspo_min_vs_rowlevel_v2.csv',
             'v2/audit_cspo_rows_v2_public.csv'}
    require(set(new) - set(old) == added and not set(old) - set(new), 'unexpected file inventory')
    require(all(sha(p) == sha(new[n]) for n, p in old.items()), 'v2 input changed')
    key = lambda r: tuple(r[k] for k in ('year', 'slug', 'inning', 'half'))
    halves = list(part7_v2_read(source/'v2/half_innings_v2_public.csv.gz'))
    bykey = {key(r): r for r in halves}
    require(len(bykey) == len(halves), 'duplicate half key')
    rows = list(part7_v2_read(source/'v2/audit_cspo_rows_v2_public.csv'))
    grouped = defaultdict(list)
    for r in rows:
        require(key(r) in bykey, 'unknown event half')
        require(r['type'] in ('CS', 'PO') and r['runner_out'] in ('0', '1'), 'unknown event classification')
        require(r['complete'] == bykey[key(r)]['complete'], 'complete flag mismatch')
        grouped[key(r)].append(r)
    for h in halves:
        rs = grouped[key(h)]
        for kind in ('CS', 'PO'):
            for flag, suffix in ((None, ''), ('1', '_out'), ('0', '_noout')):
                n = sum(r['type'] == kind and (flag is None or r['runner_out'] == flag) for r in rs)
                require(n == float(h[kind + suffix]), 'event aggregate mismatch: '+kind+suffix)
        require(float(h['CSPO_undet']) == 0, 'undetermined events not represented')
        require(sum(int(r['runner_out']) for r in rs) == float(h['CSPO_out_rowlevel']), 'row-level mismatch')
    mismatch = {key(h): h for h in halves if h['complete'] == 'True'
                and float(h['CSPO_out']) != float(h['CSPO_out_rowlevel'])}
    supplied = list(part7_v2_read(source/'v2/audit_cspo_min_vs_rowlevel_v2.csv'))
    require(len({key(r) for r in supplied}) == len(supplied), 'duplicate mismatch half')
    require({key(r) for r in supplied} == set(mismatch), 'mismatch case set differs')
    kinds, years = Counter(), Counter()
    for r in supplied:
        h = mismatch[key(r)]
        for col, value in r.items():
            require(value == h[col] or (col not in ('year','slug','team','inning','half')
                    and float(value) == float(h[col])), 'mismatch table cell differs: '+col)
        rs = grouped[key(r)]
        require(len(rs) == 1 and rs[0]['runner_out'] == '0', 'unexpected mismatch event')
        require(float(h['batter_outs']) == 2 and float(h['RO']) == 1
                and float(h['CSPO_out']) == 1 and float(h['RO_other']) == 0, 'unexpected allocation')
        kinds[rs[0]['type']] += 1
        years[h['year']] += 1
    return dict(schema='aoi-part7-v2.1-reception/1', status='provided_audit_tables_consistent',
                unchanged_v2_files=len(old), added_files=sorted(added),
                input_sha256={n: sha(p) for n,p in sorted(new.items())},
                event_rows=len(rows), event_counts=dict(Counter(r['type'] for r in rows)),
                event_runner_out_counts=dict(Counter(r['runner_out'] for r in rows)),
                event_complete_counts=dict(Counter(r['complete'] for r in rows)),
                half_rows_checked=len(halves), mismatch_halves=len(supplied),
                mismatch_event_types=dict(kinds), mismatch_year_counts=dict(years),
                monte_carlo_zero_exceedance_one_sided_95_upper=1-0.05**(1/200000),
                limitations=['internal consistency of provided derived tables, not independent raw-event validation',
                             'event rows lack sequential before/after states and non-CS/PO events',
                             'min assignment remains inferred; 2026 remains provisional',
                             'original v2 report and finite z at p=1 unchanged; errata takes precedence'])


def part7_v2_1_main(argv=None):
    p = argparse.ArgumentParser(description=PART7_V2_1_DOC)
    p.add_argument('source', type=Path)
    p.add_argument('--previous', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args(argv)
    result = part7_v2_1_verify(a.source, a.previous)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('input_sha256','limitations')},ensure_ascii=False))


def part7_v2_1(argv=None):
    """verify_part7_v2_1.py の入口（説明は PART7_V2_1_DOC）。
    """
    part7_v2_1_main(argv)


# ==== preclinch_flow（旧 verify_preclinch_flow.py）

PRECLINCH_FLOW_DOC = """Independent off-row reconstruction of date-filtered aggregate transitions."""


def preclinch_flow_verify(innings, result, cells):
    x=json.loads(result.read_text())
    assert hashlib.sha256(innings.read_bytes()).hexdigest()==x['input_sha256']
    groups=defaultdict(dict)
    with gzip.open(innings,'rt') as f:
        for r in csv.DictReader(f):
            if r['side']!='off' or r['year'] not in x['dates']:continue
            m=re.search(r's(\d{4})(\d{2})(\d{2})\d*\.html',r['url']) or re.search(r'/scores/(\d{4})/(\d{2})(\d{2})/',r['url'])
            day='-'.join(m.groups())
            if day>x['dates'][r['year']]:continue
            key=(int(r['year']),r['url']);home=r['batting_home']=='True'
            team=groups[key].setdefault(home,dict(team=r['team'],league=r['league'],innings={}))
            team['innings'][int(r['inning'])]=int(r['runs'])
    expected=defaultdict(Counter)
    for (year,url),pair in groups.items():
        assert set(pair)=={True,False}
        for home,own in pair.items():
            if own['league']!='CL':continue
            for cut in (6,7):
                scores={True:0,False:0};margin=None;scored=0;level=False;led=False
                for inning in range(1,max(pair[False]['innings'])+1):
                    for side in (False,True):
                        if inning not in pair[side]['innings']:continue
                        runs=pair[side]['innings'][inning];scores[side]+=runs
                        if inning>cut and side==home:
                            scored+=runs
                            level|=scores[home]>=scores[not home]
                            led|=scores[home]>scores[not home]
                    if inning==cut and inning in pair[True]['innings']:margin=scores[home]-scores[not home]
                final=scores[home]-scores[not home];out='W' if final>0 else 'L' if final<0 else 'T'
                state='unavailable';category='not_trailing'
                if margin is not None and max(pair[False]['innings'])>cut:
                    state='lead' if margin>0 else 'trail' if margin<0 else 'tie'
                    if state=='trail':category='led' if led else 'level_never_led' if level else 'never_level' if scored else 'no_runs'
                expected[year,own['team'],cut,state,category].update(G=1,**{out:1})
    with cells.open() as f:rows=list(csv.DictReader(f))
    assert len(rows)==len(expected)
    for r in rows:
        key=(int(r['year']),r['team'],int(r['cutoff']),r['state'],r['category'])
        assert {k:int(r[k]) for k in ('G','W','L','T')}=={k:expected[key][k] for k in ('G','W','L','T')},key
    checks=0
    for c in x['comparisons']:
        p=c['period'];ys={int(p)} if p.isdigit() else set(range(2013,2026))-({2020} if p=='no2020' else set())
        for name in ('own','peer'):
            subset=[(k,v) for k,v in expected.items() if k[0] in ys and k[2]==c['cutoff'] and (k[1]=='d')==(name=='own')]
            for field in ('G','W','L','T'):
                assert c[name]['total'][field]==sum(v[field] for k,v in subset);checks+=1
                for section,pos in (('states',3),('trailing',4)):
                    for label,value in c[name][section].items():
                        assert value[field]==sum(v[field] for k,v in subset if k[pos]==label);checks+=1
    return dict(status='passed',method='independent chronological off-row score accumulation',cells=len(rows),integer_cells=len(rows)*4,summary_checks=checks,
                independence='same source CSV, independent aggregation; not independent raw acquisition')


def preclinch_flow_main(argv=None):
    p=argparse.ArgumentParser(description=PRECLINCH_FLOW_DOC)
    for k in ('innings','result','cells','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args(argv);v=preclinch_flow_verify(a.innings,a.result,a.cells);a.out.write_text(json.dumps(v,indent=2)+'\n');print(v)


def preclinch_flow(argv=None):
    """verify_preclinch_flow.py の入口（説明は PRECLINCH_FLOW_DOC）。
    """
    preclinch_flow_main(argv)


# ==== prediction_independent（旧 verify_prediction_independent.py）

def prediction_independent(argv=None):
    import argparse, json
    from pathlib import Path
    import numpy as np
    import pandas as pd
    ap=argparse.ArgumentParser(description='Independent grouped prediction verification; requires numpy and pandas')
    ap.add_argument('--season',type=Path,required=True)
    ap.add_argument('--result',type=Path,required=True)
    args=ap.parse_args(argv)
    z=json.loads(args.result.read_text())
    s=pd.read_json(args.season,lines=True)
    s=s[s.season>=2013].copy()
    s['rps']=s.inn_R/s.inn_S
    fields={'zero':[], 'mean':[], 'iso':['iso'], 'obp':['obp'], 'both':['iso','obp']}
    def independent_normalize(df):
     d=df.copy();g=d.groupby(['season','league']);n=g.team.transform('size')
     d['iso']=d.bat_iso-(g.bat_iso.transform('sum')-d.bat_iso)/(n-1)
     d['obp']=d.bat_obp-(g.bat_obp.transform('sum')-d.bat_obp)/(n-1)
     d['y']=np.log(d.rps/(g.inn_R.transform('sum')/g.inn_S.transform('sum')))
     return d
    maxdiff=0
    checks=0
    for scope,modes in z['results'].items():
     source=s[s.season!=2020] if scope=='without2020' else s
     tests=independent_normalize(source)
     for mode,result in modes.items():
      cache={}
      for pred in result['predictions']:
       year,team=pred['year'],pred['team']
       key=(year,) if mode=='year' else (team,) if mode=='team' else (year,team)
       if key not in cache:
        mask=np.ones(len(source),dtype=bool)
        if mode!='team':mask &= source.season.to_numpy()!=year
        if mode!='year':mask &= source.team.to_numpy()!=team
        train=independent_normalize(source.loc[mask])
        cache[key]={}
        for model,f in fields.items():
         x=np.column_stack([np.ones(len(train)),*[train[k].to_numpy() for k in f]])
         cache[key][model]=np.array([0.]) if model=='zero' else np.linalg.lstsq(x,train.y.to_numpy(),rcond=None)[0]
       row=tests[(tests.season==year)&(tests.team==team)].iloc[0]
       assert abs(row.y-pred['actual'])<1e-12
       for model,f in fields.items():
        estimate=np.array([1.,*[row[k] for k in f]])@cache[key][model]
        diff=abs(estimate-pred['predictions'][model]);maxdiff=max(maxdiff,diff);checks+=1
        assert diff<1e-12
    print('Independent pandas reference transforms + NumPy lstsq:',checks,'predictions agree; max abs diff',maxdiff)


# ==== supplement（旧 verify_supplement.py）

def supplement_read(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def supplement_main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--share',type=Path,required=True)
    args=ap.parse_args(argv);p=args.share
    manifest={}
    for line in (p/'MANIFEST.sha256').read_text().splitlines():
        m=re.fullmatch(r'([0-9a-f]{64})  (.+)  \((\d+) bytes\)',line)
        supplement_require(m is not None,'manifest format')
        h,name,size=m.groups();f=p/name
        supplement_require(f.resolve().is_relative_to(p.resolve()),'manifest path')
        supplement_require(name not in manifest and f.stat().st_size==int(size) and digest(f)==h,'manifest mismatch')
        manifest[name]=h
    supplement_require(set(manifest)=={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}-{'MANIFEST.sha256'},
            'manifest coverage')
    prior=json.loads((HERE/'outputs/inning_features/validation.json').read_text())
    supplement_require(digest(p/'data/part4/team_half_innings.csv.gz')==prior['input_sha256'],'inning CSV changed')
    records,nrows=read_input(p/'data/part4/team_half_innings.csv.gz')
    kept={g['url']:g for g in records}
    base={g['href']:g for g in map(json.loads,(ROOT/'data/observations/r001/games.jsonl').read_text().splitlines())}
    supplement_require(digest(ROOT/'data/observations/r001/games.jsonl')==prior['baseline_sha256'],'baseline changed')
    supplement_require(set(base)=={u for u,g in kept.items() if g['year']<=2025},'baseline URL mismatch')
    raw_rows=json.loads((p/'data/part2/games_raw.json').read_text())
    raw={g['url']:g for g in raw_rows};supplement_require(len(raw)==len(raw_rows),'raw duplicates')
    games=supplement_read(p/'data/game_list.csv');gm={g['url']:g for g in games}
    ex=supplement_read(p/'data/excluded_reasons.csv');em={g['url']:g for g in ex}
    supplement_require(len(gm)==len(games) and len(em)==len(ex),'duplicate source/exclusion')
    supplement_require(set(gm)==set(kept)|set(em) and not(set(kept)&set(em)),'not a partition')
    for u in em:supplement_require(gm[u]['usage']==em[u]['reason'],'reason mismatch')
    for u,g in kept.items():
        supplement_require(gm[u]['usage']=='used_regular_season','kept usage mismatch')
        rg=raw[u];supplement_require(rg['status']=='final','kept nonfinal')
        for side in ['home','away']:
            seq=rg[side+'_inn']
            supplement_require(all(type(x) is int or x in (None,'X') for x in seq),'unknown parsed inning')
            supplement_require([x for x in seq if type(x) is int]==g[side+'_runs'],'parsed/CSV inning mismatch')
            supplement_require(sum(g[side+'_runs'])==rg[side+'_R'],'parsed sum mismatch')
    # Independently reproduce each team's count cutoff from the supplied parsed games.
    candidates=defaultdict(list)
    for g in raw_rows:
        if g['status']!='final' or any(s in g['title'] for s in ['クライマックス','日本シリーズ','オールスター']):continue
        for side in ['home','away']:
            t='b' if g[side]=='bs' else g[side]
            supplement_require(t in TEAMS,'unknown candidate team')
            candidates[g['year'],t].append(g)
    selected=Counter();trimmed=Counter()
    for (y,t),gg in candidates.items():
        cap=120 if y==2020 else 144 if y in (2013,2014) else 143
        for i,g in enumerate(sorted(gg,key=lambda g:(g['date'],g['url']))):
            (selected if i<cap else trimmed)[g['url']]+=1
    supplement_require(set(selected)==set(kept) and set(selected.values())=={2},'count-cut selection mismatch')
    supplement_require(set(trimmed)=={u for u,g in em.items() if g['reason']=='postseason_trimmed'} and
            set(trimmed.values())=={2},'count-cut exclusion mismatch')
    detail=supplement_read(p/'data/part2/trim_check_detail.csv');dm={g['url']:g for g in detail}
    supplement_require(len(dm)==len(detail) and set(dm)==set(kept)|set(trimmed),'detail coverage')
    pairs=defaultdict(list)
    for u,b in base.items():
        y=int(b['date'][:4]);pair=tuple(sorted([b['home'],b['away']]))
        pairs[y,pair].append(u)
    for (y,pair),uu in pairs.items():
        inter=(pair[0] in CL)!=(pair[1] in CL)
        expected=(0 if y==2020 else 4 if y in (2013,2014) else 3) if inter else (24 if y in (2013,2014,2020) else 25)
        supplement_require(len(uu)==expected,'card count mismatch')
        for n,u in enumerate(sorted(uu,key=lambda u:(base[u]['date'],u)),1):
            supplement_require(dm[u]['kind']=='kept' and int(float(dm[u]['label']))==n and
                    int(float(gm[u]['h2h_label']))==n,'provided label mismatch')
    flags=supplement_read(p/'data/walkoff_innings.csv');seen=set();counts=Counter();yearcounts=Counter()
    annotations=[]
    for f in flags:
        u=f['url'];side=f['batting_side'];i=int(f['inning']);g=kept[u]
        t='b' if f['batting_team']=='bs' else f['batting_team'];key=(u,t,i)
        supplement_require(key not in seen,'duplicate x flag');seen.add(key)
        supplement_require(side in ['home','away'] and t==g[side] and int(f['year'])==g['year'],'flag identity')
        supplement_require(i==len(g[side+'_runs']) and g[side+'_runs'][i-1]==int(f['runs']),'flag not terminal / score mismatch')
        supplement_require(re.fullmatch(r'\d+[xX]',f['raw']) and int(f['raw'][:-1])==int(f['runs']),'raw flag syntax')
        is_walkoff=side=='home' and i>=9 and sum(g['home_runs'])>sum(g['away_runs'])
        kind='walkoff' if is_walkoff else 'incomplete_other'
        supplement_require(f['kind'].split('(')[0]==kind,'kind rule mismatch')
        counts[kind]+=1;yearcounts[g['year'],t,kind]+=1
        annotations.append(dict(url=u,year=g['year'],batting_team=t,batting_side=side,inning=i,
                                runs=int(f['runs']),kind=kind,source='supplement_walkoff_innings.csv'))
    fail={u for u,g in raw.items() if not g['check']}
    supplement_require(fail<=set(em),'unaccounted sumcheck failure')
    dates=sorted({gm[u]['date'] for u in trimmed}&{gm[u]['date'] for u in base})
    receipt=dict(manifest_files=len(manifest),manifest_sha256=digest(p/'MANIFEST.sha256'),
                 manifest_verified=True,input_csv_unchanged=True,input_rows=nrows,
                 source_urls=len(gm),kept_games=len(kept),excluded=len(em),
                 exclusions=dict(Counter(g['reason'] for g in ex)),
                 cutoff_kept_games=len(selected),cutoff_trimmed_games=len(trimmed),
                 cutoff_two_sided=True,parsed_csv_matched_games=len(kept),
                 pair_count=len(pairs),provided_labels_matched_games=len(base),
                 simultaneous_dates=dates,sumcheck_failures=len(fail),
                 sumcheck_failure_reasons=dict(Counter(em[u]['reason'] for u in fail)),
                 x_flags=len(flags),x_kinds=dict(counts),x_join_mismatches=0,
                 x_flags_2013_2025=sum(f['year']<=2025 for f in annotations),
                 script_sha256=digest(__file__),exit_code=0,
                 limits=['No raw HTML supplied; Nth-game labels and x markers are provided extractions.',
                         'incomplete_other is a classification rule, not an independently verified termination cause.'])
    out=HERE/'outputs';(out/'supplement_validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    write_csv(out/'partial_innings_by_year.csv',[dict(year=y,team=t,kind=k,count=n)
                                               for (y,t,k),n in sorted(yearcounts.items())])
    local=ROOT/'data/observations/r001_inning_features';local.mkdir(parents=True,exist_ok=True)
    write_csv(local/'partial_inning_annotations.csv',annotations)
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


def supplement(argv=None):
    """Offline reconciliation of the user-supplied supplemental evidence package.
    """
    try:supplement_main(argv)
    except FileNotFoundError as e:print(e,file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError) as e:print(e,file=sys.stderr);sys.exit(65)


# ==== 入口
COMMANDS = {
    "clinch_interval": clinch_interval,
    "cutoff_independent": cutoff_independent,
    "early_scoring": early_scoring,
    "game_state": game_state,
    "late_reaction": late_reaction,
    "matched_comeback": matched_comeback,
    "part5": part5,
    "part6": part6,
    "part7_v2": part7_v2,
    "part7_v2_1": part7_v2_1,
    "preclinch_flow": preclinch_flow,
    "prediction_independent": prediction_independent,
    "supplement": supplement,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="recheck.py", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=COMMANDS, help="どの処理を走らせるか（旧ファイルの名前は各関数の説明に書いた）")
    ap.add_argument("args", nargs=argparse.REMAINDER, help="その処理に渡す引数（旧ファイルと同じ）")
    a = ap.parse_args(argv)
    sys.argv[0] = f"recheck.py {a.command}"   # 各処理の argparse の使い方の行に、ファイルと処理の名前を出す
    return COMMANDS[a.command](a.args)


if __name__ == "__main__":
    raise SystemExit(main())
