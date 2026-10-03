"""Descriptive outcomes conditional on final runs; see SAME_SCORE_PROTOCOL.md."""
import csv
import json
import sys
from pathlib import Path
from analyze import CL,TEAMS,YEARS,sha,units

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def metrics(games):
    n=len(games);w=sum(a>b for a,b,*_ in games);l=sum(a<b for a,b,*_ in games);d=n-w-l
    return dict(g=n,w=w,l=l,d=d,win_rate=w/(w+l) if w+l else None,we_rate=(w+.5*d)/n if n else None)

def main():
    data=ROOT/'data/observations/r001/games.jsonl'
    meta=json.loads(data.with_suffix('.manifest.json').read_text())
    verify=json.loads((HERE/'outputs/official_verification.json').read_text())
    digest=sha(data)
    if (meta['sha256']!=digest or meta['unknown']!=0 or verify['games_sha256']!=digest or len(verify['checks'])!=156
        or {(c['year'],c['team']) for c in verify['checks'] if c['match']}!={(y,t) for y in YEARS for t in TEAMS}):
        raise ValueError('source or verification mismatch')
    raw=[json.loads(s) for s in data.read_text().splitlines()]
    grouped=units(raw)
    maximum=max(max(g['hs'],g['as']) for g in raw)
    rows=[];totals={}
    for (year,team),gg in sorted(grouped.items()):
        if team not in CL:continue
        for side in ['home','away']:
            selected=[g for g in gg if g[2]==side]
            cells=[]
            for score in range(maximum+1):
                r=dict(year=year,team=team,side=side,score=score,**metrics([g for g in selected if g[0]==score]))
                cells.append(r);rows.append(r)
            target=metrics(selected)
            if any(sum(r[k] for r in cells)!=target[k] for k in ['g','w','l','d']):
                raise AssertionError('score cells do not reconstruct outcomes')
            totals[year,team,side]=target['g']
    pooled=[]
    for omit in [False,True]:
        for label,teams in [('chunichi',{'d'}),('other_cl',CL-{'d'})]:
            for side in ['home','away']:
                selected=[g for (y,t),gg in grouped.items() if t in teams and (not omit or y!=2020) for g in gg if g[2]==side]
                for score in range(8):
                    gg=[g for g in selected if (g[0]==score if score<7 else g[0]>=7)]
                    pooled.append(dict(scope='without2020' if omit else 'all',group=label,side=side,score=str(score) if score<7 else '7+',
                                       frequency=len(gg)/len(selected),**metrics(gg)))
    matched=[]
    for side in ['home','away']:
        for score in range(7):
            comparisons=[];missing=[]
            for y in YEARS:
                a=next(r for r in rows if r['year']==y and r['team']=='d' and r['side']==side and r['score']==score)
                other=[r for r in rows if r['year']==y and r['team']!='d' and r['side']==side and r['score']==score]
                ow=sum(r['w'] for r in other);ol=sum(r['l'] for r in other)
                if a['win_rate'] is None or ow+ol==0:missing.append(y)
                else:comparisons.append(dict(year=y,chunichi=a['win_rate'],other_cl=ow/(ow+ol),difference=a['win_rate']-ow/(ow+ol)))
            matched.append(dict(side=side,score=score,years=comparisons,missing_years=missing))
    with (HERE/'outputs/same_score_cells.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    result=dict(input_sha256=digest,script_sha256=sha(__file__),protocol_sha256=sha(HERE/'SAME_SCORE_PROTOCOL.md'),
                aggregation='pooled games; annual cells and same-year comparisons retained',pooled=pooled,matched_years=matched,exit_code=0)
    (HERE/'outputs/same_score_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for side in ['home','away']:
        print(side)
        for score in [str(k) for k in range(7)]+['7+']:
            a,b=[next(r for r in pooled if r['scope']=='all' and r['side']==side and r['score']==score and r['group']==group) for group in ['chunichi','other_cl']]
            print(score,f"d={a['w']}-{a['l']}-{a['d']} {a['win_rate']:.3f} other={b['win_rate']:.3f}")
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except FileNotFoundError as e:print(str(e),file=sys.stderr);sys.exit(66)
    except (ValueError,KeyError,TypeError) as e:print(str(e),file=sys.stderr);sys.exit(65)
    except Exception as e:print(str(e),file=sys.stderr);sys.exit(70)
