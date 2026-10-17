"""Descriptive decomposition; see HOME_AWAY_PROTOCOL.md. No network calls."""
import csv
import json
import math
import statistics as st
from pathlib import Path
from analyze import CL, units, sha

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def components(games):
    h = [g for g in games if g[2] == 'home']
    a = [g for g in games if g[2] == 'away']
    if not h or not a:
        raise ValueError('both sides required')
    hr, ar = st.mean(g[0] for g in h), st.mean(g[0] for g in a)
    hra, ara = st.mean(g[1] for g in h), st.mean(g[1] for g in a)
    result = dict(home_r=hr, away_r=ar, home_ra=hra, away_ra=ara,
                  scoring=hr-ar, prevention=ara-hra, gap=(hr-hra)-(ar-ara))
    if not math.isclose(result['gap'], result['scoring']+result['prevention'], abs_tol=1e-12):
        raise ValueError('decomposition mismatch')
    return result


def main():
    data = ROOT / 'data/observations/r001/games.jsonl'
    check = json.loads((HERE / 'outputs/official_verification.json').read_text())
    if sha(data) != check['games_sha256'] or len(check['checks']) != 156 or not all(c['match'] for c in check['checks']):
        raise ValueError('official verification does not cover input')
    grouped = units([json.loads(s) for s in data.read_text().splitlines()])
    rows, pairs = [], []
    for (year, team), games in sorted(grouped.items()):
        if team not in CL:
            continue
        cl = [g for g in games if g[3] in CL]
        pair = []
        for opp in sorted(CL - {team}):
            selected = [g for g in cl if g[3] == opp]
            row = dict(year=year, team=team, opponent=opp,
                       home_n=sum(g[2]=='home' for g in selected),
                       away_n=sum(g[2]=='away' for g in selected), **components(selected))
            pairs.append(row)
            pair.append(row)
        balanced = {k: st.mean(r[k] for r in pair) for k in components(cl)}
        for mode, values in [('all_raw', components(games)), ('cl_raw', components(cl)), ('cl_balanced', balanced)]:
            rows.append(dict(mode=mode, year=year, team=team, **values))
    for row in rows:
        others = [r for r in rows if r['year']==row['year'] and r['mode']==row['mode'] and r['team']!=row['team']]
        for key in ['home_r','away_r','home_ra','away_ra','scoring','prevention','gap']:
            row[key+'_minus_others'] = row[key] - st.mean(r[key] for r in others)
    out = HERE / 'outputs'
    for name, records in [('home_away_team_years.csv', rows), ('home_away_opponent_cells.csv', pairs)]:
        with (out/name).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
            writer.writeheader(); writer.writerows(records)
    summary = {}
    for mode in ['all_raw','cl_raw','cl_balanced']:
        for omit in [False, True]:
            selected = [r for r in rows if r['mode']==mode and r['team']=='d' and (not omit or r['year']!=2020)]
            keys = [k for k in selected[0] if k not in ['mode','year','team']]
            summary[mode+('/without2020' if omit else '/all')] = {
                'n':len(selected), 'means':{k:st.mean(r[k] for r in selected) for k in keys},
                'positive_gap_minus_others_years':[r['year'] for r in selected if r['gap_minus_others']>0]}
    result = dict(data_sha256=sha(data), script_sha256=sha(__file__),
                  protocol_sha256=sha(HERE/'HOME_AWAY_PROTOCOL.md'), summaries=summary,
                  note='Descriptive opponent weighting, not park-adjusted or causal.')
    (out/'home_away_summary.json').write_text(json.dumps(result, indent=2)+'\n')
    for k,v in summary.items():
        print(k, json.dumps({m:round(v['means'][m],4) for m in ['scoring','prevention','gap','scoring_minus_others','prevention_minus_others','gap_minus_others']}), 'positive years:', len(v['positive_gap_minus_others_years']))
    for opp in sorted(CL-{'d'}):
        sel=[r for r in pairs if r['team']=='d' and r['opponent']==opp]
        print('opponent',opp,{k:round(st.mean(r[k] for r in sel),4) for k in ['scoring','prevention','gap']})


if __name__=='__main__':
    main()
