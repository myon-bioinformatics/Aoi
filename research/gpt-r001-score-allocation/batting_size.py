"""Descriptive batting/RPS association; no causal or significance verdict (stdlib)."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

METRICS = ['iso', 'hr_pa', 'xbh_h', 'obp', 'bb_pa', 'avg']


def corr(x, y):
    a, b = mean(x), mean(y)
    xx, yy = sum((v-a)**2 for v in x), sum((v-b)**2 for v in y)
    return sum((u-a)*(v-b) for u, v in zip(x, y))/math.sqrt(xx*yy) if xx*yy else None


def partial(x, y, z):
    xy, xz, yz = corr(x, y), corr(x, z), corr(y, z)
    return (xy-xz*yz)/math.sqrt((1-xz*xz)*(1-yz*yz))


def center(rows, field):
    groups = {}
    for r in rows:
        groups.setdefault(r['team'], []).append(r[field])
    return [r[field]-mean(groups[r['team']]) for r in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--season', type=Path, required=True)
    ap.add_argument('--part5', type=Path, required=True, help='team_season_relative.csv')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--season-blob', help='expected Git blob SHA of the season input')
    args = ap.parse_args()
    season = [json.loads(s) for s in args.season.read_text().splitlines()]
    raw = args.season.read_bytes()
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if args.season_blob:assert blob == args.season_blob, 'season Git blob mismatch'
    with args.part5.open(encoding='utf-8-sig', newline='') as f:
        part5 = list(csv.DictReader(f))
    sm = {(r['season'], r['team']):r for r in season}
    assert len(sm) == len(season) == 168
    rows = []
    for p in part5:
        s = sm[int(p['year']), p['team']]
        for a, b in [('G','G'), ('W','W'), ('L','L'), ('T','T'), ('RF','R'), ('RA','RA')]:
            assert s[a] == int(p[b]), (p['year'],p['team'],a)
        assert math.isclose(s['bat_iso'], s['bat_slg']-s['bat_avg'], abs_tol=1e-12)
        assert s['inn_R'] == s['RF'] and math.isclose(s['inn_R']/s['inn_S'],float(p['off_runs_per_scoring_inn']),abs_tol=1e-12)
        r=dict(year=s['season'],team=s['team'],name=s['team_name'],league=s['league'],
               rps_log=float(p['off_lRPS']),rps=s['inn_R']/s['inn_S'],runs_rank=int(float(p['R/G_CL/PL順位'])))
        for k in METRICS:r[k]=s['bat_d_'+k]
        rows.append(r)
    assert len(rows)==156
    # Independently verify the existing other-five-team relative batting values.
    for r in rows:
        peers=[s for s in season if s['season']==r['year'] and s['league']==r['league'] and s['team']!=r['team']]
        assert len(peers)==5
        for k in METRICS:assert math.isclose(r[k],sm[r['year'],r['team']]['bat_'+k]-mean(s['bat_'+k] for s in peers),abs_tol=1e-12)
    results=[]
    for scope,selected in [('all',rows),('without2020',[r for r in rows if r['year']!=2020]),
                           ('without_chunichi',[r for r in rows if r['team']!='d']),
                           ('C',[r for r in rows if r['league']=='C']),('P',[r for r in rows if r['league']=='P']),
                           ('chunichi',[r for r in rows if r['team']=='d'])]:
        for k in METRICS:
            results.append(dict(scope=scope,metric=k,n=len(selected),pearson=corr([r[k] for r in selected],[r['rps_log'] for r in selected]),
                within_team=corr(center(selected,k),center(selected,'rps_log')),
                partial_obp=partial([r[k] for r in selected],[r['rps_log'] for r in selected],[r['obp'] for r in selected]) if k!='obp' else None))
    bykey={(r['year'],r['team']):r for r in rows}
    changes=[]
    for omit in [False,True]:
        pairs=[(r,bykey[r['year']+1,r['team']]) for r in rows if (r['year']+1,r['team']) in bykey and (not omit or r['year'] not in [2019,2020])]
        for k in METRICS:changes.append(dict(omit_pairs_touching2020=omit,metric=k,n=len(pairs),
            first_difference_r=corr([b[k]-a[k] for a,b in pairs],[b['rps_log']-a['rps_log'] for a,b in pairs])))
    tables=[]
    for omit in [False,True]:
        q=[r for r in rows if not omit or r['year']!=2020]
        for k in METRICS:
            low=[r for r in q if r[k]<0]
            tables.append(dict(omit2020=omit,metric=k,n=len(q),low_n=len(low),low_and_low_rps=sum(r['rps_log']<0 for r in low),
                               low_rps_base_rate=mean(r['rps_log']<0 for r in q)))
    failures=[dict(r,direction='low_iso_nonlow_rps' if r['iso']<0 else 'nonlow_iso_low_rps') for r in rows if (r['iso']<0)!=(r['rps_log']<0)]
    d=[r for r in rows if r['team']=='d']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(source_sha256=dict(season=sha(args.season),part5=sha(args.part5)),season_git_blob=blob,
        validated_team_years=len(rows),checked_annual_fields=6*len(rows),correlations=results,changes=changes,tables=tables,
        chunichi=d,counterexamples=failures,script_sha256=sha(Path(__file__)),
        scope='Descriptive fixed-metric exploration from existing derived inputs; not raw batting-page verification or a causal effect.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(correlations=results[:6],changes=changes[:6],tables=tables[:6],
        chunichi_iso_below=sum(r['iso']<0 for r in d),chunichi_obp_below=sum(r['obp']<0 for r in d),counterexamples=len(failures)),indent=2))


if __name__=='__main__':main()
