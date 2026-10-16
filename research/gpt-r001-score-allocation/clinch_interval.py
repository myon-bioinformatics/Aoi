"""Descriptive 2022 clinch cutoff and Wilson-z sensitivity from fixed inputs."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
from inning_features import read_input, digest

INPUT_SHA='0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb'
OBJECT_BLOB='e22e9253126a21128af55863e4fb3654470cbc61'
CUT='2022-09-27'
CL=['d','c','db','g','s','t']


def wilson(k,n,z):
    if n==0:return [0.,1.]
    p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d
    h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]


def stat(k,n):
    if not 0<=k<=n:raise ValueError('invalid n,k')
    intervals=[]
    for z in [1,1.959963984540054,2,3]:
        lo,hi=wilson(k,n,z)
        intervals.append(dict(z=z,coverage_normal=math.erf(z/math.sqrt(2)),lo=lo,hi=hi,
                              relation='no_data' if n==0 else 'above' if lo>=.5 else 'below' if hi<.5 else 'includes'))
    return dict(n=n,k=k,rate=k/n if n else None,intervals=intervals,
                binomial_upper_p=sum(math.comb(n,i) for i in range(k,n+1))/2**n if n else None)


def intervals(text):
    b=text.encode();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if blob!=OBJECT_BLOB:raise ValueError('objections input blob mismatch')
    out=[]
    for block in re.split(r'(?=^## P\d+:)',text,flags=re.M):
        m=re.match(r'## (P\d+):',block)
        if not m or not re.search(r'強さ:.*?基準 0\.50',block):continue
        pid=m[1]
        for line in block.splitlines():
            row=re.match(r'\| (元の命題|対偶|逆|裏) \| (\d+) \| (\d+) \|',line)
            if row:
                cells=[v.strip() for v in line.strip('|').split('|')]
                out.append(dict(proposition=pid,form=row[1],undetermined=int(cells[7]),reported_verdict=cells[8],**stat(int(row[3]),int(row[2]))))
            if line.startswith('**きっかけ以外での判定**'):
                held=re.search(r'n=(\d+) 成立=(\d+)',line)
                if not held:raise ValueError('unknown held-out schema')
                out.append(dict(proposition=pid,form='きっかけ以外',undetermined=None,reported_verdict=None,**stat(int(held[2]),int(held[1]))))
    if not out:raise ValueError('no interval rows')
    p78=[r for r in out if r['proposition']=='P78' and r['form']=='きっかけ以外']
    if len(p78)!=1 or (p78[0]['n'],p78[0]['k'])!=(7,6):raise ValueError('P78 mismatch')
    return out


def date(url):
    match=re.search(r'/s(\d{4})(\d{2})(\d{2})\d+\.html$',url)
    if match:return '-'.join(match.groups())
    match=re.search(r'/scores/(\d{4})/(\d{2})(\d{2})/',url)
    if match:return '-'.join(match.groups())
    raise ValueError('unknown date URL')


def scoring(path):
    if digest(path)!=INPUT_SHA:raise ValueError('inning input hash mismatch')
    games,input_rows=read_input(path)
    totals=defaultdict(Counter);windows=defaultdict(Counter)
    for g in games:
        if g['year']!=2022:continue
        phase='before' if date(g['url'])<=CUT else 'after'
        for side,opp in [('home','away'),('away','home')]:
            team=g[side]
            if team not in CL:continue
            runs=g[side+'_runs'];allowed=g[opp+'_runs'];rf=sum(runs);ra=sum(allowed)
            outcome='W' if rf>ra else 'L' if rf<ra else 'T'
            c=totals[phase,team];c.update(G=1,RF=rf,RA=ra);c[outcome]+=1
            for cut in [6,7]:
                w=windows[phase,team,cut]
                if min(len(runs),len(allowed))<cut:w['excluded']+=1;continue
                early=sum(runs[:cut]);late=sum(runs[cut:9]);extra=sum(runs[9:])
                w.update(G=1,early_RF=early,zero=int(early==0),three_plus=int(early>=3))
                w.update({f'{outcome}_G':1,f'{outcome}_reg_RF':late,f'{outcome}_reg_innings':max(0,min(9,len(runs))-cut),f'{outcome}_extra_RF':extra})
    # Check entry cut against independently reported games remaining.
    if totals['before','d']['G']!=139 or totals['after','d']['G']!=4:raise ValueError('reported 139/4 split mismatch')
    rows=[]
    for phase in ['before','after','full']:
        for name,teams in [('中日',['d']),('他セ5球団',CL[1:])]:
            phases=['before','after'] if phase=='full' else [phase]
            ann=Counter();ws={c:Counter() for c in [6,7]}
            for ph in phases:
                for t in teams:
                    ann.update(totals[ph,t])
                    for c in [6,7]:ws[c].update(windows[ph,t,c])
            for c in [6,7]:
                w=ws[c]
                rows.append(dict(phase=phase,group=name,cut=c,annual=dict(ann),counts=dict(w),early_mean=w['early_RF']/w['G'] if w['G'] else None,
                                 zero_rate=w['zero']/w['G'] if w['G'] else None,three_plus_rate=w['three_plus']/w['G'] if w['G'] else None))
    return rows,input_rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inning',type=Path,required=True);p.add_argument('--objections',type=Path,required=True)
    p.add_argument('--plan-commit',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();rows,raw=scoring(a.inning)
    out=dict(plan_commit=a.plan_commit,cutoff_date=CUT,input_sha256=INPUT_SHA,objections_blob=OBJECT_BLOB,
             input_rows=raw,scoring_rows=rows,interval_rows=intervals(a.objections.read_text(encoding='utf-8')))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'scoring_rows':len(rows),'interval_rows':len(out['interval_rows'])}))


if __name__=='__main__':main()
