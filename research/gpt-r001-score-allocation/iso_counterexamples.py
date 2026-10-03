"""Fixed-threshold descriptive follow-up of low-ISO counterexamples (stdlib)."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows):
    low = [r for r in rows if r['iso'] < 0]
    groups = {}
    for name, group in [('nonlow_rps', [r for r in low if r['rps_log'] >= 0]),
                        ('low_rps', [r for r in low if r['rps_log'] < 0])]:
        groups[name] = dict(n=len(group), stats={k: dict(mean=mean(r[k] for r in group), median=median(r[k] for r in group)) if group else None
                          for k in ['iso', 'obp', 'sr_log', 'rps_log', 'rg_log']})
    tables = {}
    for k in ['obp', 'sr_log']:
        tp = sum(r[k] >= 0 and r['rps_log'] >= 0 for r in low)
        fp = sum(r[k] >= 0 and r['rps_log'] < 0 for r in low)
        fn = sum(r[k] < 0 and r['rps_log'] >= 0 for r in low)
        tn = sum(r[k] < 0 and r['rps_log'] < 0 for r in low)
        tables[k] = dict(tp=tp, fp=fp, fn=fn, tn=tn,
                         precision=tp/(tp+fp) if tp+fp else None,
                         recall=tp/(tp+fn) if tp+fn else None)
    contrasts = []
    for year, league in sorted({(r['year'], r['league']) for r in low}):
        q = [r for r in low if (r['year'], r['league']) == (year, league)]
        a = [r for r in q if r['rps_log'] >= 0]
        b = [r for r in q if r['rps_log'] < 0]
        if a and b:
            contrasts.append(dict(year=year, league=league, nonlow_n=len(a), low_n=len(b),
                **{k: mean(r[k] for r in a)-mean(r[k] for r in b) for k in ['iso','obp','sr_log']}))
    obp_low = [r for r in low if r['obp'] < 0]
    return dict(n=len(rows),low_iso_n=len(low), groups=groups, tables=tables,
                same_year_league_contrasts=contrasts,
                contrast_summary={k:dict(n=len(contrasts),mean=mean(c[k] for c in contrasts),
                    positive=sum(c[k]>0 for c in contrasts)) if contrasts else None for k in ['iso','obp','sr_log']},
                low_iso_low_obp=dict(n=len(obp_low),low_rps=sum(r['rps_log']<0 for r in obp_low),
                                    counterexamples=sum(r['rps_log']>=0 for r in obp_low)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--season', type=Path, required=True)
    ap.add_argument('--batting-result', type=Path, required=True)
    ap.add_argument('--part5', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    previous = json.loads(args.batting_result.read_text())
    assert sha(args.part5) == previous['source_sha256']['part5'], 'Part5 input hash mismatch'
    with args.part5.open(encoding='utf-8-sig',newline='') as f:
        source = list(csv.DictReader(f))
    failures = {(r['year'],r['team']):r for r in previous['counterexamples']}
    rows=[]
    for p in source:
        r=dict(year=int(p['year']),team=p['team'],name=p['name'],league=p['league'],
               sr_log=float(p['off_lSR']),rps_log=float(p['off_lRPS']),
               ig_log=float(p['off_lIG']),rg_log=float(p['off_lRG']))
        assert math.isclose(r['sr_log']+r['rps_log']+r['ig_log'],r['rg_log'],abs_tol=1e-12)
        rows.append(r)
    assert len(rows)==156 and len({(r['year'],r['team']) for r in rows})==156
    return args,previous,rows,failures


def run():
    args,previous,rows,failures=main()
    season_path=args.season
    assert sha(season_path)==previous['source_sha256']['season'], 'season input hash mismatch'
    season=[json.loads(s) for s in season_path.read_text().splitlines()]
    sm={(s['season'],s['team']):s for s in season}
    for r in rows:
        s=sm[r['year'],r['team']]
        r.update(league=s['league'],iso=s['bat_d_iso'],obp=s['bat_d_obp'])
        if (r['iso']<0)!=(r['rps_log']<0):
            old=failures[r['year'],r['team']]
            assert r['iso']==old['iso'] and r['obp']==old['obp'] and r['rps_log']==old['rps_log']
    assert sum(r['iso']<0 and r['rps_log']>=0 for r in rows)==32
    scopes={'all':rows,'without2020':[r for r in rows if r['year']!=2020],
            'without_chunichi':[r for r in rows if r['team']!='d'],
            'C':[r for r in rows if r['league']=='C'],'P':[r for r in rows if r['league']=='P'],
            '2013_2019':[r for r in rows if r['year']<=2019],
            '2021_2025':[r for r in rows if r['year']>=2021]}
    result=dict(source_sha256=dict(season=sha(season_path),part5=sha(args.part5),batting_result=sha(args.batting_result)),
                script_sha256=sha(Path(__file__)),thresholds=dict(iso=0,obp=0,sr_log=0,rps_log=0),
                scopes={k:summarize(q) for k,q in scopes.items()},
                low_iso_rows=[r for r in rows if r['iso']<0],
                interpretation='Descriptive post-hoc exploration; no blind holdout, causal attribution, or calibrated inference.')
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'iso_counterexamples.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (args.out/'iso_counterexamples.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(result['low_iso_rows'])
    print(json.dumps(result['scopes'],ensure_ascii=False,indent=2))


if __name__=='__main__':run()
