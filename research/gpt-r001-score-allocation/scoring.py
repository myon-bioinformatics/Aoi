"""Observe scoring distributions, without attributing causes. See SCORING_PROTOCOL.md."""
import json
import statistics as st
import sys
from collections import Counter
from pathlib import Path
from analyze import CL, TEAMS, YEARS, sha, units

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    data=ROOT/'data/observations/r001/games.jsonl'
    manifest=json.loads(data.with_suffix('.manifest.json').read_text())
    verify=json.loads((HERE/'outputs/official_verification.json').read_text())
    digest=sha(data)
    if (digest!=manifest['sha256'] or manifest['unknown']!=0 or digest!=verify['games_sha256']
        or len(verify['checks'])!=156
        or {(r['year'],r['team']) for r in verify['checks'] if r['match']}!={(y,t) for y in YEARS for t in TEAMS}):
        raise ValueError('input provenance or official checks mismatch')
    games=[json.loads(s) for s in data.read_text().splitlines()]
    grouped=units(games)
    maximum=max(max(g['hs'],g['as']) for g in games)
    rows=[]
    for (year,team),gg in sorted(grouped.items()):
        if team not in CL:
            continue
        for side in ['home','away']:
            scores=[g[0] for g in gg if g[2]==side]
            n=len(scores)
            counts=Counter(scores)
            vector=[counts[k] for k in range(maximum+1)]
            if sum(vector)!=n or sum(k*c for k,c in enumerate(vector))!=sum(scores):
                raise AssertionError('score frequency reconstruction failed')
            rows.append(dict(year=year,team=team,side=side,n=n,r=sum(scores),mean=st.mean(scores),
                             zero=counts[0]/n,up_to_two=sum(x<=2 for x in scores)/n,
                             five_plus=sum(x>=5 for x in scores)/n,counts=vector,
                             cumulative=[sum(vector[:k+1])/n for k in range(maximum+1)]))
    summaries={}
    for label,teams in [('chunichi',{'d'}),('other_cl',CL-{'d'})]:
        for side in ['home','away']:
            for omit in [False,True]:
                selected=[r for r in rows if r['team'] in teams and r['side']==side and (not omit or r['year']!=2020)]
                summaries[f'{label}/{side}/'+('without2020' if omit else 'all')]={k:st.mean(r[k] for r in selected) for k in ['mean','zero','up_to_two','five_plus']}
    annual=[]
    for y in YEARS:
        d={r['side']:r for r in rows if r['team']=='d' and r['year']==y}
        other={side:st.mean(r['mean'] for r in rows if r['team']!='d' and r['year']==y and r['side']==side) for side in ['home','away']}
        annual.append(dict(year=y,home_mean=d['home']['mean'],away_mean=d['away']['mean'],
                           away_minus_home=d['away']['mean']-d['home']['mean'],
                           home_minus_others=d['home']['mean']-other['home'],away_minus_others=d['away']['mean']-other['away']))
    output=dict(data_sha256=digest,script_sha256=sha(__file__),protocol_sha256=sha(HERE/'SCORING_PROTOCOL.md'),
                maximum_runs=maximum,summaries=summaries,annual_chunichi=annual,rows=rows,exit_code=0)
    (HERE/'outputs/scoring_distribution.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(summaries=summaries,annual_chunichi=annual,exit_code=0),ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':
    try:
        code=main()
    except FileNotFoundError as e:
        code=66; print(str(e),file=sys.stderr)
    except (ValueError,KeyError,TypeError) as e:
        code=65; print(str(e),file=sys.stderr)
    except Exception as e:
        code=70; print(f'{type(e).__name__}: {e}',file=sys.stderr)
    sys.exit(code)
