"""Offline final-score distribution and existing PythDRAgoraS judgement."""
import argparse
import csv
import json
import math
import statistics as st
import sys
from collections import Counter
from pathlib import Path
from analyze import CL, TEAMS, YEARS, units, sha

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT/'PythDRagoras'), str(ROOT/'PythDRagoras/logic')]


def split(home, away, cap):
    if not home or not away:
        raise ValueError('home and away observations required')
    gap = st.mean(away)-st.mean(home)
    body = st.mean(min(x, cap) for x in away)-st.mean(min(x, cap) for x in home)
    tail = st.mean(max(x-cap, 0) for x in away)-st.mean(max(x-cap, 0) for x in home)
    if not math.isclose(gap, body+tail, abs_tol=1e-12):
        raise AssertionError('mean decomposition failed')
    return gap, body, tail


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def analyze(args):
    meta = json.loads(args.games.with_suffix('.manifest.json').read_text())
    verify = json.loads(args.verification.read_text())
    digest = sha(args.games)
    expected = {(y,t) for y in YEARS for t in TEAMS}
    if (meta['unknown'] != 0 or meta['sha256'] != digest or verify['games_sha256'] != digest
        or len(verify['checks']) != len(expected)
        or {(c['year'],c['team']) for c in verify['checks'] if c['match']} != expected):
        raise ValueError('input manifest/official verification mismatch')
    games = [json.loads(s) for s in args.games.read_text().splitlines()]
    grouped = units(games)
    maximum = max(max(g['hs'],g['as']) for g in games)
    frequencies, thresholds, seasons = [], [], []
    for (year, team), gg in sorted(grouped.items()):
        if team not in CL:
            continue
        sides = {side:[g[1] for g in gg if g[2]==side] for side in ['home','away']}
        for side, vals in sides.items():
            counts = Counter(vals)
            for x in range(maximum+1):
                frequencies.append(dict(season=year, team=team, side=side, runs=x, count=counts[x], n=len(vals), frequency=counts[x]/len(vals)))
        survival_gap = 0
        for k in range(maximum+1):
            gap, body, tail = split(sides['home'], sides['away'], k)
            hp = sum(x>=k for x in sides['home'])/len(sides['home'])
            ap = sum(x>=k for x in sides['away'])/len(sides['away'])
            if k:
                survival_gap += ap-hp
            thresholds.append(dict(season=year, team=team, cap=k, home_survival=hp, away_survival=ap,
                                   survival_gap=ap-hp, gap=gap, body_gap=body, tail_gap=tail))
            if k==6:
                seasons.append(dict(season=year, team=team, team_name=team, gap=gap, body_gap=body, tail_gap=tail,
                                    away_more=gap>0, tail_dominates=tail>body))
        if not math.isclose(survival_gap, gap, abs_tol=1e-12):
            raise AssertionError('survival sum does not reconstruct mean gap')
    args.out.mkdir(parents=True, exist_ok=True)
    for name, rows in [('loss_frequencies.csv',frequencies),('loss_thresholds.csv',thresholds),('loss_tail_seasons.csv',seasons)]:
        write_csv(args.out/name, rows)
    summaries = {}
    for label, teams in [('chunichi',{'d'}),('other_cl',CL-{'d'})]:
        for omit in [False,True]:
            selected=[r for r in seasons if r['team'] in teams and (not omit or r['season']!=2020)]
            summaries[label+('/without2020' if omit else '/all')] = {k:st.mean(r[k] for r in selected) for k in ['gap','body_gap','tail_gap']}
    result=dict(data_sha256=digest,script_sha256=sha(__file__),protocol_sha256=sha(HERE/'TAIL_PROTOCOL.md'),
                proposition_sha256=sha(args.propositions), table_sha256=sha(args.out/'loss_tail_seasons.csv'), maximum_runs=maximum, units=len(seasons), summaries=summaries,
                passed=['input provenance','156 official team-years','unique games and season completeness','body + tail identity','survival sum identity'],exit_code=0)
    (args.out/'loss_tail_receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    return 0


def judge(args):
    import polars as pl
    import propositions as pr
    props, digest=pr.load(args.propositions)
    receipt=json.loads((args.out/'loss_tail_receipt.json').read_text())
    if receipt['table_sha256']!=sha(args.out/'loss_tail_seasons.csv'):
        raise ValueError('analysis table hash mismatch')
    if receipt['proposition_sha256']!=digest:
        raise ValueError('proposition differs from analysis receipt')
    rows=[]
    for r in csv.DictReader((args.out/'loss_tail_seasons.csv').open()):
        rows.append({**r,'season':int(r['season']),**{k:float(r[k]) for k in ['gap','body_gap','tail_gap']},
                     **{k:r[k]=='True' for k in ['away_more','tail_dominates']}})
    results=[pr.evaluate(p,pl.DataFrame(rows),focus='d') for p in props]
    # Process all propositions sequentially; preserve every judgement. First nonzero is the process exit.
    code=next((r['judgement']['code'] for r in results if r['judgement']['code']),0)
    (args.out/'loss_tail_judgements.json').write_text(json.dumps(dict(results=results,exit_code=code,proposition_sha256=digest, engine_sha256=sha(ROOT/'PythDRagoras/logic/propositions.py'), table_sha256=receipt['table_sha256']),ensure_ascii=False,indent=2)+'\n')
    for r in results:
        print(json.dumps({'id':r['id'],'judgement':r['judgement']},ensure_ascii=False))
    return code


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(64, json.dumps(dict(exit_code=64,error=message))+"\n")


def main():
    ap=Parser(description=__doc__)
    ap.add_argument('stage',choices=['analyze','judge'])
    ap.add_argument('--games',type=Path,default=ROOT/'data/observations/r001/games.jsonl')
    ap.add_argument('--verification',type=Path,default=HERE/'outputs/official_verification.json')
    ap.add_argument('--propositions',type=Path,default=HERE/'tail_propositions.toml')
    ap.add_argument('--out',type=Path,default=HERE/'outputs')
    args=ap.parse_args()
    try:
        return analyze(args) if args.stage=='analyze' else judge(args)
    except FileNotFoundError as e:
        code=66; message=str(e)
    except (ValueError,KeyError,TypeError) as e:
        # Existing proposition exceptions subclass ValueError; retain their contract.
        code=64 if type(e).__name__=='PropositionError' else 65; message=str(e)
    except OSError as e:
        code=74; message=str(e)
    except Exception as e:
        code=70; message=f'{type(e).__name__}: {e}'
    print(json.dumps(dict(exit_code=code,error=message),ensure_ascii=False),file=sys.stderr)
    return code


if __name__=='__main__':
    sys.exit(main())
