"""Regular-season forecasts; no network access and no results after the cutoff."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import random


@dataclass(frozen=True)
class Game:
    id: str
    date: str
    home: str
    away: str
    result: str | None = None  # H, A, D; None means not yet played


@dataclass(frozen=True)
class Rules:
    members: tuple[str, ...]
    previous_order: tuple[str, ...]
    wins_before_h2h: bool
    cs_slots: int
    label: str
    source: str
    league_pct_tiebreak: bool = True

    def __post_init__(self):
        if (len(self.members) < 2 or len(set(self.members)) != len(self.members)
                or set(self.members) != set(self.previous_order)
                or len(self.previous_order) != len(self.members)):
            raise ValueError('members and previous_order must be unique permutations')
        if not isinstance(self.wins_before_h2h, bool) or not isinstance(self.league_pct_tiebreak, bool):
            raise ValueError('tiebreak switches must be booleans')
        if type(self.cs_slots) is not int or not 0 <= self.cs_slots <= len(self.members):
            raise ValueError('invalid CS slot count (zero means not held)')
        if not self.label or not self.source:
            raise ValueError('rule label and source are required')


def npb_rules(year, league, members, previous_order):
    """Only versions actually checked against the official source are preset."""
    if (year, league) not in {(2022, 'CL'), (2022, 'PL'), (2025, 'CL')}:
        raise ValueError('unverified year/league: supply explicit Rules with its source')
    if len(members) != 6:
        raise ValueError('NPB presets require six league members')
    return Rules(tuple(members), tuple(previous_order), league == 'CL', 3,
                 f'NPB-{year}-{league}', f'https://npb.jp/games/{year}/info_cs{league.lower()}.html')


@dataclass
class Snapshot:
    teams: tuple[str, ...]
    wins: list[list[int]]  # wins[i][j] against j, including interleague
    draws: list[list[int]]
    remaining: tuple[Game, ...]
    as_of: str
    schedule_basis: str

    def validate(self):
        n = len(self.teams)
        if n < 2 or len(set(self.teams)) != n or not all(isinstance(t, str) and t for t in self.teams) or not self.schedule_basis:
            raise ValueError('unique teams and schedule provenance required')
        if date.fromisoformat(self.as_of).isoformat() != self.as_of:
            raise ValueError('as_of must be ISO YYYY-MM-DD')
        for matrix in (self.wins, self.draws):
            if len(matrix) != n or any(len(row) != n for row in matrix):
                raise ValueError('invalid matrix size')
            if any(type(x) is not int or x < 0 for row in matrix for x in row):
                raise ValueError('counts must be nonnegative integers')
            if any(matrix[i][i] for i in range(n)):
                raise ValueError('self games are invalid')
        if any(self.draws[i][j] != self.draws[j][i] for i in range(n) for j in range(n)):
            raise ValueError('draw counts must be symmetric')
        seen = set()
        for g in self.remaining:
            _validate_game(g, self.teams)
            if g.id in seen or g.date <= self.as_of or g.result is not None:
                raise ValueError('remaining games must be unique, future, and result-free')
            seen.add(g.id)
        if max(self.played(t) + sum(t in (g.home, g.away) for g in self.remaining)
               for t in self.teams) > 1000:
            raise ValueError('at most 1000 games per team supported')
        return self

    def played(self, team):
        i = self.teams.index(team)
        return sum(self.wins[i]) + sum(row[i] for row in self.wins) + sum(self.draws[i])

    def fingerprint(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True,
                                          separators=(',', ':')).encode()).hexdigest()


def _validate_game(g, teams):
    if not isinstance(g.id, str) or not g.id or g.home not in teams or g.away not in teams or g.home == g.away:
        raise ValueError('invalid game identity or teams')
    if date.fromisoformat(g.date).isoformat() != g.date:
        raise ValueError('dates must be ISO YYYY-MM-DD')
    if g.result not in (None, 'H', 'A', 'D'):
        raise ValueError('result must be H, A, D, or null')


def calendar_games(rows, year):
    """Adapt Aoi's regular-season calendar observations; retain no raw text."""
    result = []
    for row in rows:
        if date.fromisoformat(row['date']).year != year:
            continue
        h, a = row['hs'], row['as']
        if type(h) is not int or type(a) is not int or min(h, a) < 0:
            raise ValueError('calendar scores must be nonnegative integers')
        result.append(Game(str(row['key']), row['date'], row['home'], row['away'],
                           'H' if h > a else 'A' if h < a else 'D'))
    if not result:
        raise ValueError('no calendar observations for the selected year')
    return result


def snapshot(games, teams, as_of, *, schedule_basis):
    """Future results are discarded, never used to estimate team strength."""
    teams = tuple(teams)
    index = {t: i for i, t in enumerate(teams)}
    wins = [[0] * len(teams) for _ in teams]
    draws = [[0] * len(teams) for _ in teams]
    remaining, seen = [], set()
    for g in sorted(games, key=lambda g: (g.date, g.id)):
        _validate_game(g, teams)
        if g.id in seen:
            raise ValueError('duplicate game id')
        seen.add(g.id)
        if g.date > as_of:
            remaining.append(Game(g.id, g.date, g.home, g.away))
            continue
        if g.result is None:
            raise ValueError('past scheduled game lacks a result: update postponed schedule first')
        h, a = index[g.home], index[g.away]
        if g.result == 'H':
            wins[h][a] += 1
        elif g.result == 'A':
            wins[a][h] += 1
        else:
            draws[h][a] += 1
            draws[a][h] += 1
    return Snapshot(teams, wins, draws, tuple(remaining), as_of, schedule_basis).validate()


def _pct(w, l):
    # Explicit engine convention for no decisive games, including all-draw groups.
    return Fraction(w, max(1, w + l))


def ranking(teams, wins, rules):
    """Exact rational comparisons; H2H uses the whole initially tied group."""
    ids = [teams.index(t) for t in rules.members]
    total_w = {i: sum(wins[i]) for i in ids}
    total_l = {i: sum(row[i] for row in wins) for i in ids}
    primary = {i: (_pct(total_w[i], total_l[i]), total_w[i] if rules.wins_before_h2h else 0)
               for i in ids}
    keys = {}
    for i in ids:
        tied = [j for j in ids if j != i and primary[j] == primary[i]]
        head = _pct(sum(wins[i][j] for j in tied), sum(wins[j][i] for j in tied))
        league = (_pct(sum(wins[i][j] for j in ids), sum(wins[j][i] for j in ids))
                  if rules.league_pct_tiebreak else Fraction(0))
        keys[i] = (*primary[i], head, league, -rules.previous_order.index(teams[i]))
    return [teams[i] for i in sorted(ids, key=keys.__getitem__, reverse=True)]


def baseline_probabilities(s, prior_games=20.0, draw_prior=0.05):
    """Smoothed current W/L strength, Log5 matchup, pooled smoothed draw rate."""
    if not math.isfinite(prior_games) or prior_games <= 0 or not 0 < draw_prior < 1:
        raise ValueError('positive finite prior_games and draw_prior in (0,1) required')
    w = [sum(row) for row in s.wins]
    l = [sum(row[i] for row in s.wins) for i in range(len(s.teams))]
    strength = [(a + prior_games / 2) / (a + b + prior_games) for a, b in zip(w, l)]
    draws = sum(map(sum, s.draws)) / 2
    games = sum(w) + draws
    d = (draws + prior_games * draw_prior) / (games + prior_games)
    index = {t: i for i, t in enumerate(s.teams)}
    result = {}
    for g in s.remaining:
        a, b = strength[index[g.home]], strength[index[g.away]]
        h = a * (1 - b) / (a * (1 - b) + b * (1 - a))
        result[g.id] = ((1 - d) * h, (1 - d) * (1 - h), d)
    return result


def wilson(k, n, z=1.959963984540054):
    p, z2 = k / n, z * z
    center = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return [max(0.0, center - half), min(1.0, center + half)]


def forecast(s, rules, *, trials=10000, seed=0, probabilities=None, prior_games=20.0, draw_prior=0.05):
    s.validate()
    if type(trials) is not int or trials < 1:
        raise ValueError('trials must be a positive integer')
    if not set(rules.members) <= set(s.teams):
        raise ValueError('rule members absent from snapshot')
    supplied = probabilities is not None
    probs = probabilities if supplied else baseline_probabilities(s, prior_games, draw_prior)
    if set(probs) != {g.id for g in s.remaining}:
        raise ValueError('probabilities must cover exactly the remaining schedule')
    prepared = []
    for g in s.remaining:
        p = probs[g.id]
        if (len(p) != 3 or any(not math.isfinite(x) or not 0 <= x <= 1 for x in p)
                or not math.isclose(sum(p), 1.0, abs_tol=1e-12, rel_tol=0)):
            raise ValueError('H/A/D probabilities must be finite, nonnegative and sum to one')
        prepared.append((s.teams.index(g.home), s.teams.index(g.away), p[0], p[0] + p[1]))
    counts = {t: [0] * len(rules.members) for t in rules.members}
    rng = random.Random(seed)
    for _ in range(trials):
        wins = [row[:] for row in s.wins]
        for h, a, ph, pha in prepared:
            u = rng.random()
            if u < ph:
                wins[h][a] += 1
            elif u < pha:
                wins[a][h] += 1
        for r, t in enumerate(ranking(s.teams, wins, rules)):
            counts[t][r] += 1
    output = {}
    for t, c in counts.items():
        k = sum(c[:rules.cs_slots])
        output[t] = {'rank_counts': c, 'title': c[0] / trials,
                     'title_mc95': wilson(c[0], trials),
                     'cs': k / trials if rules.cs_slots else None,
                     'cs_mc95': wilson(k, trials) if rules.cs_slots else None}
    return {'as_of': s.as_of, 'snapshot_sha256': s.fingerprint(), 'rules': asdict(rules),
            'trials': trials, 'seed': seed, 'python': platform.python_version(),
            'model': 'supplied-HAD' if supplied else 'smoothed-WL-log5-pooled-draw-v1',
            'model_parameters': None if supplied else {'prior_games': prior_games, 'draw_prior': draw_prior},
            'probabilities_sha256': hashlib.sha256(json.dumps(probs, sort_keys=True).encode()).hexdigest(),
            'schedule_basis': s.schedule_basis, 'teams': output,
            'uncertainty': 'mc95 covers Monte Carlo error only; 0 hits is not elimination'}


def crossing_events(rows, thresholds=(0.05, 0.01, 0.001)):
    """Keep recrossings as well as first passages; team-days are not independent."""
    events, previous, last_date = [], {}, None
    for row in rows:
        if last_date is not None and row['as_of'] <= last_date:
            raise ValueError('rows must have strictly increasing dates')
        last_date = row['as_of']
        for t, values in row['teams'].items():
            if values['cs'] is None:
                continue
            for threshold in thresholds:
                if not 0 < threshold < 1:
                    raise ValueError('thresholds must be in (0,1)')
                below = values['cs'] < threshold
                key = (t, threshold)
                before = previous.get(key)
                if before is None and below or before is not None and before != below:
                    events.append({'date': row['as_of'], 'team': t, 'threshold': threshold,
                                   'event': ('initial_below' if before is None else
                                             'below' if below else 'recovered'),
                                   'probability': values['cs'], 'mc95': values['cs_mc95']})
                previous[key] = below
    return events


def magic_events(rows):
    events, previous = [], {}
    for row in rows:
        for t, value in row['magic'].items():
            status = value['status']
            if previous.get(t) != status:
                events.append({'date': row['as_of'], 'team': t, 'from': previous.get(t), 'to': status})
            previous[t] = status
    return events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--calendar-jsonl', type=Path, help='Aoi regular-season observations (local only)')
    parser.add_argument('--season', type=int, help='calendar year; required with --calendar-jsonl')
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--through', help='replay daily through this inclusive date')
    parser.add_argument('--trials', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--exact', action='store_true', help='also calculate qualification and title magic')
    parser.add_argument('--solver-seconds', type=float, default=10)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    if args.calendar_jsonl:
        if args.season is None or 'games' in data:
            parser.error('calendar mode requires --season and a config without games')
        games = calendar_games((json.loads(line) for line in args.calendar_jsonl.read_text().splitlines() if line.strip()), args.season)
    else:
        if args.season is not None:
            parser.error('--season requires --calendar-jsonl')
        games = [Game(**g) for g in data['games']]
    rule_data = data['rules']
    rules = Rules(**{**rule_data, 'members': tuple(rule_data['members']),
                     'previous_order': tuple(rule_data['previous_order'])})
    current, end = date.fromisoformat(args.as_of), date.fromisoformat(args.through or args.as_of)
    if end < current:
        parser.error('--through precedes --as-of')
    rows = []
    while current <= end:
        s = snapshot(games, data['teams'], current.isoformat(), schedule_basis=data['schedule_basis'])
        row = forecast(s, rules, trials=args.trials, seed=args.seed)
        if args.exact:
            try:
                from .season_exact import qualification, title_magic
            except ImportError:
                from season_exact import qualification, title_magic
            row['qualification'] = {t: qualification(s, rules, t, seconds=args.solver_seconds)
                                    for t in rules.members}
            row['magic'] = title_magic(s, rules, seconds=args.solver_seconds)
        rows.append(row)
        current += timedelta(days=1)
    result = {'schema_version': 1,
              'engine_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'exact_engine_sha256': hashlib.sha256(Path(__file__).with_name('season_exact.py').read_bytes()).hexdigest() if args.exact else None,
              'daily': rows, 'threshold_events': crossing_events(rows),
              'magic_events': magic_events(rows) if args.exact else []}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
