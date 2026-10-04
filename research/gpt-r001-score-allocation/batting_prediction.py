"""Fixed ISO/OBP models with grouped retrospective evaluation (stdlib)."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

MODELS = {'zero': [], 'mean': [], 'iso': ['iso'], 'obp': ['obp'], 'both': ['iso', 'obp']}


def normalize(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r['year'],r['league']), []).append(r)
    result = []
    for r in rows:
        peers = groups[r['year'],r['league']]
        assert len(peers)>=5
        others = [p for p in peers if p['team']!=r['team']]
        ref = sum(p['runs'] for p in peers)/sum(p['scoring'] for p in peers)
        result.append(dict(r,iso=r['raw_iso']-mean(p['raw_iso'] for p in others),
            obp=r['raw_obp']-mean(p['raw_obp'] for p in others),y=math.log(r['rps']/ref)))
    return result


def fit(rows, fields):
    ybar = mean(r['y'] for r in rows)
    if not fields:
        return [ybar]
    means = [mean(r[k] for r in rows) for k in fields]
    xy = [sum((r[k]-a)*(r['y']-ybar) for r in rows) for k,a in zip(fields,means)]
    xx = [[sum((r[k]-a)*(r[l]-b) for r in rows) for l,b in zip(fields,means)] for k,a in zip(fields,means)]
    if len(fields)==1:
        assert xx[0][0]>0
        betas=[xy[0]/xx[0][0]]
    else:
        determinant=xx[0][0]*xx[1][1]-xx[0][1]*xx[1][0]
        assert determinant>1e-16
        betas=[(xy[0]*xx[1][1]-xy[1]*xx[0][1])/determinant,
               (xy[1]*xx[0][0]-xy[0]*xx[1][0])/determinant]
    return [ybar-sum(a*b for a,b in zip(means,betas)),*betas]


def predict(row, fields, coefficients):
    return coefficients[0]+sum(row[k]*b for k,b in zip(fields,coefficients[1:]))


def evaluate(rows, mode):
    normalized = normalize(rows)
    cache, predictions = {}, []
    for r in normalized:
        key = (r['year'],) if mode=='year' else (r['team'],) if mode=='team' else (r['year'],r['team'])
        if key not in cache:
            train = [p for p in rows if (mode=='team' or p['year']!=r['year']) and (mode=='year' or p['team']!=r['team'])]
            normalized_train=normalize(train)
            cache[key]={name:([0.] if name=='zero' else fit(normalized_train,fields)) for name,fields in MODELS.items()}
        estimates={name:predict(r,fields,cache[key][name]) for name,fields in MODELS.items()}
        predictions.append(dict(year=r['year'],team=r['team'],actual=r['y'],low_iso=r['iso']<0,predictions=estimates))
    metrics={name:dict(rmse=math.sqrt(mean((r['predictions'][name]-r['actual'])**2 for r in predictions)),
                       mae=mean(abs(r['predictions'][name]-r['actual']) for r in predictions)) for name in MODELS}
    differences={}
    for grouping in ['year','team']:
        differences[grouping]=[]
        for value in sorted({r[grouping] for r in predictions}):
            group=[r for r in predictions if r[grouping]==value]
            differences[grouping].append(dict(group=value,n=len(group),
                mse_both_minus_obp=mean((r['predictions']['both']-r['actual'])**2-(r['predictions']['obp']-r['actual'])**2 for r in group)))
    subset=[r for r in predictions if r['low_iso'] and r['actual']>=0]
    coefficients={name:[dict(min=min(c[name][i] for c in cache.values()),mean=mean(c[name][i] for c in cache.values()),max=max(c[name][i] for c in cache.values()))
                         for i in range(len(next(iter(cache.values()))[name]))] for name in MODELS}
    return dict(n=len(rows),folds=len(cache),metrics=metrics,group_differences=differences,coefficient_ranges=coefficients,
        low_iso_nonlow_rps=dict(n=len(subset),metrics={name:dict(rmse=math.sqrt(mean((r['predictions'][name]-r['actual'])**2 for r in subset))) for name in MODELS}),
        predictions=predictions)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--season',type=Path,required=True)
    ap.add_argument('--part5',type=Path,required=True)
    ap.add_argument('--previous-batting',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    raw=args.season.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if blob!='fd76d410b7d8d9438237abc751820dcbf95c05e4':raise ValueError('season blob mismatch')
    previous=json.loads(args.previous_batting.read_text())
    if hashlib.sha256(args.part5.read_bytes()).hexdigest()!=previous['source_sha256']['part5']:raise ValueError('Part5 hash mismatch')
    source=[json.loads(line) for line in raw.decode().splitlines()]
    sm={(r['season'],r['team']):r for r in source}
    assert len(sm)==len(source)==168
    with args.part5.open(encoding='utf-8-sig',newline='') as f:part5=list(csv.DictReader(f))
    rows=[]
    for p in part5:
        s=sm[int(p['year']),p['team']]
        for a,b in [('G','G'),('W','W'),('L','L'),('T','T'),('RF','R'),('RA','RA')]:assert s[a]==int(p[b])
        assert s['inn_R']==s['RF'] and s['inn_S']>0
        assert math.isclose(s['bat_iso'],s['bat_slg']-s['bat_avg'],abs_tol=1e-12)
        rows.append(dict(year=s['season'],team=s['team'],league=s['league'],runs=s['inn_R'],scoring=s['inn_S'],
                         rps=s['inn_R']/s['inn_S'],raw_iso=s['bat_iso'],raw_obp=s['bat_obp']))
    assert len(rows)==156 and len({(r['year'],r['team']) for r in rows})==156
    pm={(int(p['year']),p['team']):p for p in part5}
    for r in normalize(rows):
        p=pm[r['year'],r['team']];s=sm[r['year'],r['team']]
        assert math.isclose(r['y'],float(p['off_lRPS']),abs_tol=1e-12)
        assert math.isclose(r['rps'],float(p['off_runs_per_scoring_inn']),abs_tol=1e-12)
        for k in ['iso','obp']:assert math.isclose(r[k],s['bat_d_'+k],abs_tol=1e-12)
    results={}
    for scope,q in [('without2020',[r for r in rows if r['year']!=2020]),('including2020',rows)]:
        results[scope]={mode:evaluate(q,mode) for mode in ['year','team','double']}
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    output=dict(plan_commit='1a83cc1a2a6b5a82c911aaff3c2aaffbaa443b04',season_blob=blob,
                sha256=dict(season=sha(args.season),part5=sha(args.part5),script=sha(Path(__file__))),
                results=results,interpretation='Retrospective grouped evaluation; hypothesis chosen after observing the period. Team-excluded training uses reduced reference populations. No causal or future-year claim.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(json.dumps({scope:{mode:r['metrics'] for mode,r in v.items()} for scope,v in results.items()},indent=2))


if __name__=='__main__':main()
