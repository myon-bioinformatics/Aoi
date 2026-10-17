"""Optional integration check using authorized local calendar observations only."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from season_simulator import calendar_games, forecast, npb_rules, ranking, snapshot
from season_exact import qualification, solve, title_magic


def verify(path):
    games = calendar_games((json.loads(line) for line in path.read_text().splitlines() if line.strip()), 2022)
    teams = tuple(sorted({g.home for g in games} | {g.away for g in games}))
    if len(games) != 858 or len(teams) != 12:
        raise ValueError('expected a complete 2022 regular season (858 games, 12 teams)')
    previous = {'CL': ('s', 't', 'g', 'c', 'd', 'db'), 'PL': ('b', 'm', 'e', 'h', 'f', 'l')}
    rules = {lg: npb_rules(2022, lg, order, order) for lg, order in previous.items()}
    basis = 'retrospective actual played schedule; not an archived as-of schedule'
    result = {'calendar_input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'canonical_games_sha256': hashlib.sha256(json.dumps([asdict(g) for g in sorted(games, key=lambda g: (g.date, g.id))], sort_keys=True).encode()).hexdigest(),
              'games': len(games), 'schedule_basis': basis,
              'rules': {lg: asdict(r) for lg, r in rules.items()}, 'checks': []}
    for d in ('2022-09-24', '2022-09-25', '2022-09-26', '2022-09-27', '2022-10-03'):
        s = snapshot(games, teams, d, schedule_basis=basis)
        q = qualification(s, rules['CL'], 'd', seconds=20)
        title = solve(s, rules['CL'], 's', inside=False, seconds=20)
        expected_cs = 'open' if d < '2022-09-27' else 'eliminated'
        if q['status'] != expected_cs or title['feasible'] is not (d < '2022-09-25'):
            raise AssertionError((d, q, title))
        f = forecast(s, rules['CL'], trials=10000, seed=20221004)
        row = {'date': d, 'snapshot_sha256': s.fingerprint(), 'chunichi_cs_status': q['status'],
               'chunichi_remaining': sum('d' in (g.home, g.away) for g in s.remaining),
               'yakult_title_clinched': not title['feasible'],
               'chunichi_cs_baseline_probability': f['teams']['d']['cs'],
               'chunichi_cs_mc95': f['teams']['d']['cs_mc95'],
               'forecast_model': f['model'], 'trials': f['trials'], 'seed': f['seed'],
               'model_parameters': f['model_parameters'], 'python': f['python'], 'solver': title['solver']}
        if d in ('2022-09-24', '2022-09-25'):
            magic = title_magic(s, rules['CL'], seconds=20)['s']
            expected = 2 if d == '2022-09-24' else 0
            if magic['magic'] != expected:
                raise AssertionError(magic)
            row['yakult_guarantee_magic'] = magic['magic']
        if d == '2022-10-03':
            orders = {lg: ranking(s.teams, s.wins, r) for lg, r in rules.items()}
            if orders != {'CL': ['s', 'db', 't', 'g', 'c', 'd'], 'PL': ['b', 'h', 'l', 'e', 'm', 'f']}:
                raise AssertionError(orders)
            if not solve(s, rules['PL'], 'b')['feasible'] or solve(s, rules['PL'], 'h')['feasible']:
                raise AssertionError('PL tied-title feasibility mismatch')
            row['final_orders_match_official'] = True
            if any(s.played(t) != 143 for t in teams):
                raise AssertionError('incomplete team schedules')
        result['checks'].append(row)
    result['passed'] = True
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('calendar_jsonl', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.write_text(json.dumps(verify(args.calendar_jsonl), ensure_ascii=False, indent=2) + '\n')
