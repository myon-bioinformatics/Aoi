"""Synthetic fixtures only. Exhaustion is independent of the constraint model."""
from dataclasses import replace
from itertools import product
from importlib.util import find_spec
import json
from pathlib import Path
import random
import subprocess
import sys

import pytest

# Only tests that actually invoke the solver require the optional dependency.
requires_solver = pytest.mark.skipif(find_spec('ortools') is None,
    reason='install season-requirements.txt for exact simulator tests')

from season_simulator import (Game, Rules, Snapshot, baseline_probabilities,
    calendar_games, crossing_events, forecast, magic_events, npb_rules, ranking, snapshot, wilson)
from season_exact import qualification, solve, title_magic


def rule(members=('A', 'B', 'C'), central=True, slots=2, previous=None):
    return Rules(tuple(members), tuple(previous or members), central, slots, 'synthetic-v1', 'synthetic')


def brute(s, rules, target):
    completions = []
    for outcomes in product('HAD', repeat=len(s.remaining)):
        w = [r[:] for r in s.wins]
        won, all_won = 0, True
        for g, o in zip(s.remaining, outcomes):
            h, a = s.teams.index(g.home), s.teams.index(g.away)
            winner = g.home if o == 'H' else g.away if o == 'A' else None
            if o != 'D':
                w[h if o == 'H' else a][a if o == 'H' else h] += 1
            if target in (g.home, g.away):
                won += winner == target
                all_won &= winner == target
        completions.append((ranking(s.teams, w, rules).index(target) + 1, won, all_won))
    return completions


@requires_solver
@pytest.mark.parametrize('central', [True, False])
@pytest.mark.parametrize('case', range(10))
def test_exact_matches_exhaustive_completions(central, case):
    rng = random.Random(case)
    teams = ('A', 'B', 'C', 'X')
    games = []
    for k in range(12):
        h, a = rng.sample(teams, 2)
        games.append(Game(str(k), '2022-01-01', h, a, rng.choice('HAD')))
    for k in range(3):
        h, a = rng.sample(teams, 2)
        games.append(Game(f'r{k}', '2022-01-02', h, a))
    s = snapshot(games, teams, '2022-01-01', schedule_basis='synthetic known schedule')
    r = rule(central=central, previous=('C', 'A', 'B'))
    for t in r.members:
        possibilities = brute(s, r, t)
        for k in (1, 2):
            for inside in (True, False):
                expected = any((rank <= k) == inside for rank, _, _ in possibilities)
                actual = solve(s, r, t, top_k=k, inside=inside)
                assert actual['feasible'] is expected
        bad = [(rank, w) for rank, w, _ in possibilities if rank > 1]
        actual = solve(s, r, t, inside=False, maximize_wins=True)
        assert actual['max_new_wins'] == (max(w for _, w in bad) if bad else None)
        actual = solve(s, r, t, inside=False, force_wins=t)
        assert actual['feasible'] is any(rank > 1 and all_won for rank, _, all_won in possibilities)
        expected = ('clinched' if all(rank <= 2 for rank, _, _ in possibilities) else
                    'eliminated' if all(rank > 2 for rank, _, _ in possibilities) else 'open')
        assert qualification(s, r, t)['status'] == expected


def test_tiebreak_priority_and_multiway_group():
    teams = ('A', 'B', 'X')
    w = [[0, 0, 2], [1, 0, 0], [1, 1, 0]]
    assert ranking(teams, w, rule(('A', 'B'), True, 1, ('B', 'A'))) == ['A', 'B']
    assert ranking(teams, w, rule(('A', 'B'), False, 1)) == ['B', 'A']
    teams = ('A', 'B', 'C', 'X')
    w = [[0, 2, 0, 0], [0, 0, 2, 0], [1, 0, 0, 1], [1, 0, 0, 0]]
    # All are 2-2; A 2/3, B 2/4, C 1/3 inside the three-team tie.
    assert ranking(teams, w, rule(previous=('C', 'B', 'A'))) == ['A', 'B', 'C']
    # All-draw ties fall through to the supplied previous order.
    assert ranking(teams, [[0]*4 for _ in teams], rule(previous=('C', 'B', 'A'))) == ['C', 'B', 'A']


def test_league_tiebreak_before_previous_rank():
    teams = ('A', 'B', 'C', 'X')
    # A/B both 3-3, H2H 1-1. A has a 3-2 league record, B has 1-2.
    w = [[0, 1, 2, 0], [1, 0, 0, 2], [1, 1, 0, 0], [1, 1, 0, 0]]
    r = rule(previous=('B', 'A', 'C'))
    assert ranking(teams, w, r).index('A') < ranking(teams, w, r).index('B')
    without = ranking(teams, w, replace(r, league_pct_tiebreak=False))
    assert without.index('B') < without.index('A')


def blink_fixture():
    games = []
    for t, wins, losses in [('A', 6, 4), ('B', 5, 5)]:
        for k in range(wins + losses):
            games.append(Game(f'{t}{k}', '2022-01-01', t, 'X', 'H' if k < wins else 'A'))
    games += [Game('a1', '2022-01-02', 'A', 'X', 'A'),
              Game('b1', '2022-01-02', 'B', 'X', 'H'),
              Game('b2', '2022-01-03', 'B', 'X', 'A'),
              Game('a2', '2022-01-04', 'A', 'X', 'H')]
    return games, rule(('A', 'B'), slots=1, previous=('B', 'A'))


@requires_solver
def test_magic_lights_disappears_relights_and_clinches():
    games, r = blink_fixture()
    rows = []
    for d in range(1, 5):
        s = snapshot(games, ('A', 'B', 'X'), f'2022-01-0{d}', schedule_basis='synthetic')
        value = title_magic(s, r)
        for t in r.members:
            p = brute(s, r, t)
            bad = [w for rank, w, _ in p if rank > 1]
            guarantee = max(bad) + 1 if bad else 0
            left = sum(t in (g.home, g.away) for g in s.remaining)
            assert value[t]['guaranteed_wins_needed'] == (guarantee if guarantee <= left else None)
        rows.append({'as_of': s.as_of, 'magic': value})
    assert [r['magic']['A']['status'] for r in rows] == ['lit', 'off', 'lit', 'clinched']
    assert [r['magic']['A']['magic'] for r in rows] == [2, None, 1, 0]
    assert len([e for e in magic_events(rows) if e['team'] == 'A']) == 4


@requires_solver
def test_zero_time_is_unknown_not_eliminated():
    games, r = blink_fixture()
    s = snapshot(games, ('A', 'B', 'X'), '2022-01-01', schedule_basis='synthetic')
    assert solve(s, r, 'A', seconds=0)['feasible'] is None
    assert qualification(s, r, 'A', seconds=0)['status'] == 'unknown'
    assert title_magic(s, r, seconds=0)['A']['status'] == 'unknown'


def test_future_outcomes_do_not_leak_and_mc_conserves_places():
    games, r = blink_fixture()
    s = snapshot(games, ('A', 'B', 'X'), '2022-01-01', schedule_basis='synthetic')
    altered = [replace(g, result='D') if g.date > s.as_of else g for g in games]
    future = snapshot(altered, s.teams, s.as_of, schedule_basis='synthetic')
    a = forecast(s, r, trials=2000, seed=42)
    assert a == forecast(future, r, trials=2000, seed=42)
    assert sum(v['title'] for v in a['teams'].values()) == pytest.approx(1)
    assert sum(v['cs'] for v in a['teams'].values()) == pytest.approx(r.cs_slots)
    assert all(sum(v['rank_counts']) == 2000 for v in a['teams'].values())
    deterministic = forecast(s, r, trials=1, probabilities={g.id: (1, 0, 0) for g in s.remaining})
    assert deterministic['teams']['A']['cs'] == 1
    assert wilson(0, 1000)[1] > 0
    assert wilson(1000, 1000)[0] < 1


def test_thresholds_retain_recovery_and_initial_condition():
    rows = [{'as_of': f'2022-01-0{i}', 'teams': {'A': {'cs': p, 'cs_mc95': [0, 1]}}}
            for i, p in enumerate([.009, .02, .005], 1)]
    assert [e['event'] for e in crossing_events(rows, (.01,))] == ['initial_below', 'recovered', 'below']


def test_validation_and_unverified_profiles():
    games, r = blink_fixture()
    s = snapshot(games, ('A', 'B', 'X'), '2022-01-01', schedule_basis='synthetic')
    with pytest.raises(ValueError):
        snapshot(games + games[:1], s.teams, s.as_of, schedule_basis='synthetic')
    with pytest.raises(ValueError):
        snapshot([Game('x', s.as_of, 'A', 'B')], s.teams, s.as_of, schedule_basis='synthetic')
    with pytest.raises(ValueError):
        forecast(s, r, probabilities={g.id: (float('nan'), 0, 1) for g in s.remaining})
    with pytest.raises(ValueError):
        npb_rules(2020, 'CL', r.members, r.previous_order)
    assert npb_rules(2022, 'PL', tuple('ABCDEF'), tuple('ABCDEF')).wins_before_h2h is False
    assert qualification(s, replace(r, cs_slots=0), 'A')['status'] == 'not_held'
    assert forecast(s, replace(r, cs_slots=0), trials=1)['teams']['A']['cs'] is None


@pytest.mark.parametrize('exact', [False, pytest.param(True, marks=requires_solver)])
def test_cli_daily_replay(tmp_path, exact):
    from dataclasses import asdict
    games, r = blink_fixture()
    data = {'teams': ['A', 'B', 'X'], 'games': [asdict(g) for g in games],
            'rules': asdict(r), 'schedule_basis': 'synthetic'}
    src, dest = tmp_path / 'input.json', tmp_path / 'output.json'
    src.write_text(json.dumps(data))
    script = Path(__file__).resolve().parents[1] / 'baseball' / 'season_simulator.py'
    # The stdlib CLI also runs with all site-packages disabled.
    subprocess.run([sys.executable, *([] if exact else ['-S']), str(script), str(src),
                    '--as-of', '2022-01-01', '--through', '2022-01-04', '--trials', '30',
                    *(['--exact'] if exact else []), '--output', str(dest)], check=True, cwd=tmp_path)
    out = json.loads(dest.read_text())
    assert len(out['daily']) == 4
    if exact:
        assert out['daily'][-1]['magic']['A']['status'] == 'clinched'
    else:
        assert 'magic' not in out['daily'][-1]


def test_calendar_adapter_filters_year_and_drops_raw_text():
    rows = [{'key': 'x', 'date': '2022-01-01', 'home': 'A', 'away': 'B',
             'hs': 1, 'as': 1, 'raw_text': 'must not be copied'},
            {'key': 'y', 'date': '2021-01-01', 'home': 'A', 'away': 'B', 'hs': 9, 'as': 0}]
    assert calendar_games(rows, 2022) == [Game('x', '2022-01-01', 'A', 'B', 'D')]
    with pytest.raises(ValueError):
        calendar_games(rows, 2019)


@requires_solver
def test_remaining_head_to_head_proves_more_than_independent_bounds():
    # A is fixed at 1/3. B and C can each reach 1/2, but cannot both do so.
    teams = ('A', 'B', 'C', 'X')
    w = [[0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [2, 1, 1, 0]]
    s = Snapshot(teams, w, [[0]*4 for _ in teams],
                 (Game('bc', '2022-01-02', 'B', 'C'),), '2022-01-01', 'synthetic')
    assert qualification(s, rule(), 'A')['status'] == 'clinched'
    # A can even finish first if the B-C game is drawn.
    assert solve(s, rule(), 'A', inside=True)['feasible'] is True


@pytest.mark.parametrize('solver_status,feasible', [('FEASIBLE', True), ('UNKNOWN', None)])
def test_magic_number_unresolved_is_unknown(monkeypatch, solver_status, feasible):
    import season_exact
    games, r = blink_fixture()
    s = snapshot(games, ('A', 'B', 'X'), '2022-01-01', schedule_basis='synthetic')

    def unresolved(s, rules, target, *, force_wins=None, **kwargs):
        if force_wins:
            return {'feasible': target != 'A'}  # only A has proven self-control
        return {'feasible': feasible, 'solver_status': solver_status, 'max_new_wins': None}

    monkeypatch.setattr(season_exact, 'solve', unresolved)
    value = title_magic(s, r)
    assert value['A']['self_control'] is True
    assert value['A']['status'] == 'unknown'
    assert value['A']['magic'] is None
    assert value['A']['guaranteed_wins_needed'] is None
    assert value['B']['status'] == 'off'
    rows = [{'as_of': '2022-01-01', 'magic': {'A': value['A']}},
            {'as_of': '2022-01-02', 'magic': {'A': {**value['A'], 'status': 'lit', 'magic': 2}}}]
    assert [e['to'] for e in magic_events(rows)] == ['unknown', 'lit']


@pytest.mark.parametrize('invalid_date', [None, 20220101, '20220101'])
def test_invalid_dates_raise_value_error_before_sorting(invalid_date):
    games, _ = blink_fixture()
    teams = ('A', 'B', 'X')
    with pytest.raises(ValueError):
        snapshot([*games, Game('bad', invalid_date, 'A', 'B', 'H')], teams,
                 '2022-01-01', schedule_basis='synthetic')
    with pytest.raises(ValueError):
        snapshot(games, teams, invalid_date, schedule_basis='synthetic')
    with pytest.raises(ValueError):
        calendar_games([{'date': invalid_date}], 2022)
