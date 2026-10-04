"""Scoring-inning placement diagnostics; no baserunner-event inference."""
import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from inning_features import read_input


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def describe(values):
    counts=Counter(values);s=sum(v>0 for v in values);runs=sum(values)
    result=dict(innings=len(values),runs=runs,scoring=s,zero=counts[0],one=counts[1],two=counts[2],three=counts[3],
                four_plus=sum(n for k,n in counts.items() if k>=4))
    if s:
        result.update(rps=runs/s,one_share=counts[1]/s,big_share=sum(v>=3 for v in values)/s,
            two_extra=counts[2]/s,three_extra=2*counts[3]/s,
            four_plus_extra=sum(v-1 for v in values if v>=4)/s,
            big_runs_share=sum(v for v in values if v>=3)/runs)
        assert math.isclose(result['rps'],1+result['two_extra']+result['three_extra']+result['four_plus_extra'],abs_tol=1e-12)
    else:
        result.update({k:None for k in ['rps','one_share','big_share','two_extra','three_extra','four_plus_extra','big_runs_share']})
    return result


def summary(games):
    result={}
    for label,home_filter,inning_filter in [('all',None,lambda i:True),('home',True,lambda i:True),
        ('away',False,lambda i:True),('first6',None,lambda i:i<=6),('after6',None,lambda i:i>=7)]:
        vals=[r for g in games if home_filter is None or g['home']==home_filter for i,r in enumerate(g['innings'],1) if inning_filter(i)]
        result[label]=describe(vals)
    concentration=[]
    for g in games:
        total=sum(g['innings'])
        if total>=3:
            concentration.append(dict(total=total,hhi=sum((v/total)**2 for v in g['innings']),maximum_share=max(g['innings'])/total))
    result['three_plus_games']=dict(n=len(concentration),mean_hhi=mean(p['hhi'] for p in concentration),
                                  mean_maximum_share=mean(p['maximum_share'] for p in concentration)) if concentration else dict(n=0)
    score_groups={}
    for total in [3,4,5]:
        q=[p for p in concentration if p['total']==total]
        score_groups[str(total)]=dict(n=len(q),hhi=mean(p['hhi'] for p in q) if q else None,
                                    maximum_share=mean(p['maximum_share'] for p in q) if q else None)
    result['same_score']=score_groups
    result['equal_weight_3_4_5_hhi']=mean(p['hhi'] for p in score_groups.values()) if all(p['n'] for p in score_groups.values()) else None
    result['equal_weight_3_4_5_maximum_share']=mean(p['maximum_share'] for p in score_groups.values()) if all(p['n'] for p in score_groups.values()) else None
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--innings',type=Path,required=True)
    ap.add_argument('--season',type=Path,required=True)
    ap.add_argument('--prediction',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if sha(args.innings)!='0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb':raise ValueError('inning input hash mismatch')
    raw=args.season.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!='fd76d410b7d8d9438237abc751820dcbf95c05e4':raise ValueError('season input blob mismatch')
    source=[json.loads(line) for line in raw.decode().splitlines()]
    sm={(s['season'],s['team']):s for s in source}
    if sha(args.prediction)!='0b76e0f0cc5e0a11dd4c949fedfacbc66009546d4064d9f614397a5f53fb8b04':raise ValueError('prediction input hash mismatch')
    pred=json.loads(args.prediction.read_text())
    assert pred['season_blob']=='fd76d410b7d8d9438237abc751820dcbf95c05e4'
    pm={(p['year'],p['team']):p for p in pred['results']['without2020']['year']['predictions']}
    assert len(pm)==144
    records,row_count=read_input(args.innings)
    team_games=defaultdict(list)
    for g in records:
        if g['year']>2025:continue
        for home in [True,False]:
            ours=g['home_runs'] if home else g['away_runs'];theirs=g['away_runs'] if home else g['home_runs']
            team=g['home'] if home else g['away']
            team_games[g['year'],team].append(dict(home=home,innings=ours,ra=sum(theirs)))
    rows=[]
    for key,games in sorted(team_games.items()):
        year,team=key;s=sm[key]
        w=sum(sum(g['innings'])>g['ra'] for g in games);l=sum(sum(g['innings'])<g['ra'] for g in games);t=len(games)-w-l
        checks=[len(games)==s['G'],w==s['W'],l==s['L'],t==s['T'],sum(sum(g['innings']) for g in games)==s['RF'],sum(g['ra'] for g in games)==s['RA']]
        assert all(checks),(year,team)
        r=dict(year=year,team=team,name=s['team_name'],league=s['league'],games=len(games),**summary(games))
        assert r['all']['runs']==s['inn_R'] and r['all']['scoring']==s['inn_S']
        if year!=2020:
            p=pm[key];r['rps_log_actual']=p['actual'];r['rps_log_predicted']=p['predictions']['both']
            r['residual']=p['actual']-p['predictions']['both']
        rows.append(r)
    assert len(rows)==156
    population=[r for r in rows if r['year']!=2020]
    cells={k:[] for k in ['tp','fp','fn','tn']}
    for r in population:
        peers=[p for p in population if p['year']==r['year'] and p['league']==r['league'] and p['team']!=r['team']]
        assert len(peers)==5
        r['peer_one_share']=sum(p['all']['one'] for p in peers)/sum(p['all']['scoring'] for p in peers)
        a=r['all']['one_share']>r['peer_one_share'];b=r['residual']<0
        cells['tp' if a and b else 'fp' if a else 'fn' if b else 'tn'].append([r['year'],r['team']])
    result=dict(plan_commit='ead424f40492ef5b2dd30da11734d03705247109',sha256=dict(innings=sha(args.innings),season=sha(args.season),prediction=sha(args.prediction),script=sha(Path(__file__)),inning_features_helper=sha(Path(__file__).with_name('inning_features.py'))),
        checked_team_years=len(rows),checked_annual_fields=len(rows)*6,input_rows=row_count,input_games=len(records),
        diagnostic=dict(n=len(population),condition='one_share > other-five pooled one_share',conclusion='observed - estimated RPS log < 0',
                        counts={k:len(v) for k,v in cells.items()},cases=cells),
        team_years=rows,interpretation='Score-only accounting and placement diagnostics. No hits/walks/LOB/steal events observed; not an independent predictor test or causal attribution.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps(dict(diagnostic=result['diagnostic'],focus=[r for r in rows if r['year']==2022 and r['league']=='C']),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
