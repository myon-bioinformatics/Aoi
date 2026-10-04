"""Finite-season scoring variance and exact-score frequencies; no causal attribution."""
import json
import math
import statistics as st
from pathlib import Path
from analyze import sha

HERE=Path(__file__).resolve().parent

def main():
    source=HERE/'outputs/scoring_distribution.json'
    payload=json.loads(source.read_text())
    rows=[]
    for r in payload['rows']:
        counts=r['counts'];n=sum(counts)
        if n!=r['n'] or sum(k*c for k,c in enumerate(counts))!=r['r']:
            raise ValueError('invalid scoring frequency totals')
        mean=r['r']/n
        var=sum(c*(k-mean)**2 for k,c in enumerate(counts))/n
        rows.append(dict(year=r['year'],team=r['team'],side=r['side'],mean=mean,variance=var,sd=math.sqrt(var),
                         zero=counts[0]/n,one=counts[1]/n,two=counts[2]/n,up_to_one=sum(counts[:2])/n))
    summary={}
    for team in sorted({r['team'] for r in rows}):
        for side in ['home','away']:
            for omit in [False,True]:
                selected=[r for r in rows if r['team']==team and r['side']==side and (not omit or r['year']!=2020)]
                summary[f'{team}/{side}/'+('without2020' if omit else 'all')]={k:st.mean(r[k] for r in selected) for k in ['mean','variance','sd','zero','one','two','up_to_one']}
    result=dict(source_sha256=sha(source),games_sha256=payload['data_sha256'],script_sha256=sha(__file__),
                protocol_sha256=sha(HERE/'SCORING_SPREAD_PROTOCOL.md'),summaries=summary,rows=rows,
                note='Means of annual population variances and annual SDs are separate quantities; not pooled.',exit_code=0)
    (HERE/'outputs/scoring_spread.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k.endswith('/all')},indent=2))

if __name__=='__main__':
    main()
