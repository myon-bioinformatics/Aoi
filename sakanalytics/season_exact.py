"""Draw-aware schedule feasibility using integer constraints (optional OR-Tools)."""
from __future__ import annotations

from collections import Counter
import math

try:
    from .season_simulator import ranking
except ImportError:
    from season_simulator import ranking


def solve(s, rules, target, *, top_k=1, inside=True, force_wins=None,
          maximize_wins=False, seconds=10):
    """Existence of a joint completion, or max target wins in such a completion.

    FEASIBLE proves existence, but only OPTIMAL certifies an optimized maximum.
    A time limit never turns into proof of infeasibility.
    """
    from ortools.sat.python import cp_model
    import ortools

    s.validate()
    if target not in rules.members or not set(rules.members) <= set(s.teams):
        raise ValueError('invalid target or rule members')
    if type(top_k) is not int or not 1 <= top_k <= len(rules.members):
        raise ValueError('invalid top_k')
    if force_wins is not None and force_wins not in s.teams:
        raise ValueError('invalid force_wins team')
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError('seconds must be finite and nonnegative')
    m = cp_model.CpModel()
    n = len(s.teams)
    ids = [s.teams.index(t) for t in rules.members]
    target_i = s.teams.index(target)
    pairs = Counter(tuple(sorted((s.teams.index(g.home), s.teams.index(g.away)))) for g in s.remaining)
    limit = max(s.played(t) + sum(t in (g.home, g.away) for g in s.remaining) for t in s.teams)
    limit = max(1, limit)

    def integer(expr, bound=limit):
        v = m.new_int_var(0, bound, '')
        m.add(v == expr)
        return v

    def comparison(a, b, op):
        v = m.new_bool_var('')
        if op == 'eq':
            m.add(a == b).only_enforce_if(v)
            m.add(a != b).only_enforce_if(~v)
        else:
            m.add(a > b).only_enforce_if(v)
            m.add(a <= b).only_enforce_if(~v)
        return v

    def conjunction(items):
        v = m.new_bool_var('')
        m.add_bool_and(items).only_enforce_if(v)
        m.add_bool_or([~x for x in items]).only_enforce_if(~v)
        return v

    def product(a, b):
        v = m.new_int_var(0, limit * limit, '')
        m.add_multiplication_equality(v, [a, b])
        return v

    def denominator(w, l):
        v = m.new_int_var(1, limit, '')
        m.add_max_equality(v, [w + l, 1])
        return v

    def ratio_compare(w1, d1, w2, d2):
        a, b = product(w1, d2), product(w2, d1)
        return comparison(a, b, 'gt'), comparison(a, b, 'eq')

    future = {}
    for (i, j), count in pairs.items():
        a, b = m.new_int_var(0, count, ''), m.new_int_var(0, count, '')
        m.add(a + b <= count)  # remainder draws; same outcome for both teams
        if force_wins in (s.teams[i], s.teams[j]):
            m.add((a if force_wins == s.teams[i] else b) == count)
        future[i, j], future[j, i] = a, b
    wins = [[integer(s.wins[i][j] + future.get((i, j), 0)) for j in range(n)] for i in range(n)]
    total_w = {i: integer(sum(wins[i])) for i in ids}
    total_l = {i: integer(sum(wins[j][i] for j in range(n))) for i in ids}
    total_d = {i: denominator(total_w[i], total_l[i]) for i in ids}
    pct, same = {}, {}
    for i in ids:
        for j in ids:
            if i == j:
                continue
            pct[i, j] = ratio_compare(total_w[i], total_d[i], total_w[j], total_d[j])
            conditions = [pct[i, j][1]]
            if rules.wins_before_h2h:
                conditions.append(comparison(total_w[i], total_w[j], 'eq'))
            same[i, j] = conjunction(conditions)
    head_w, head_d, league_w, league_d = {}, {}, {}, {}
    for i in ids:
        hw, hl = [], []
        for j in ids:
            if i == j:
                continue
            for source, dest in ((wins[i][j], hw), (wins[j][i], hl)):
                v = m.new_int_var(0, limit, '')
                m.add(v == source).only_enforce_if(same[i, j])
                m.add(v == 0).only_enforce_if(~same[i, j])
                dest.append(v)
        head_w[i] = integer(sum(hw))
        head_d[i] = denominator(head_w[i], integer(sum(hl)))
        league_w[i] = integer(sum(wins[i][j] for j in ids))
        league_d[i] = denominator(league_w[i], integer(sum(wins[j][i] for j in ids)))
    ahead = []
    for i in ids:
        if i == target_i:
            continue
        j = target_i
        criteria = [pct[i, j]]
        if rules.wins_before_h2h:
            criteria.append((comparison(total_w[i], total_w[j], 'gt'), comparison(total_w[i], total_w[j], 'eq')))
        criteria.append(ratio_compare(head_w[i], head_d[i], head_w[j], head_d[j]))
        if rules.league_pct_tiebreak:
            criteria.append(ratio_compare(league_w[i], league_d[i], league_w[j], league_d[j]))
        terms, prefix = [], []
        for greater, equal in criteria:
            terms.append(conjunction([*prefix, greater]))
            prefix.append(equal)
        if rules.previous_order.index(s.teams[i]) < rules.previous_order.index(target):
            terms.append(conjunction(prefix))
        v = m.new_bool_var('')
        m.add_max_equality(v, terms)
        ahead.append(v)
    m.add(sum(ahead) < top_k if inside else sum(ahead) >= top_k)
    new_wins = sum(future.get((target_i, j), 0) for j in range(n))
    if maximize_wins:
        m.maximize(new_wins)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    status = solver.solve(m)
    if status == cp_model.MODEL_INVALID:
        raise RuntimeError('invalid exact model: ' + solver.solution_info())
    feasible = True if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else False if status == cp_model.INFEASIBLE else None
    result = {'feasible': feasible, 'solver_status': solver.status_name(status),
              'solver': 'ortools-' + ortools.__version__, 'time_limit_seconds': seconds,
              'max_new_wins': None, 'witness': None}
    if feasible:
        witness_wins = [[solver.value(v) for v in row] for row in wins]
        order = ranking(s.teams, witness_wins, rules)
        if (order.index(target) < top_k) != inside:
            raise RuntimeError('exact witness disagrees with independent rational ranking')
        result['witness'] = [{'teams': [s.teams[i], s.teams[j]],
                              'wins': [solver.value(future[i, j]), solver.value(future[j, i])],
                              'draws': count - solver.value(future[i, j]) - solver.value(future[j, i])}
                             for (i, j), count in sorted(pairs.items())]
        if maximize_wins and status == cp_model.OPTIMAL:
            result['max_new_wins'] = solver.value(new_wins)
    return result


def qualification(s, rules, target, *, seconds=10):
    if not rules.cs_slots:
        return {'status': 'not_held'}
    good = solve(s, rules, target, top_k=rules.cs_slots, seconds=seconds)
    bad = solve(s, rules, target, top_k=rules.cs_slots, inside=False, seconds=seconds)
    status = ('eliminated' if good['feasible'] is False else 'clinched' if bad['feasible'] is False
              else 'open' if good['feasible'] and bad['feasible'] else 'unknown')
    return {'status': status, 'can_qualify': good, 'can_miss': bad}


def title_magic(s, rules, *, seconds=10):
    """Aoi guarantee magic, explicitly distinct from unverified media conventions."""
    control = {}
    for t in rules.members:
        counterexample = solve(s, rules, t, force_wins=t, inside=False, seconds=seconds)
        control[t] = (None if counterexample['feasible'] is None else not counterexample['feasible'])
    result = {}
    for t in rules.members:
        bad = solve(s, rules, t, inside=False, maximize_wins=True, seconds=seconds)
        others = [control[u] for u in rules.members if u != t]
        guarantee = (0 if bad['feasible'] is False else
                     bad['max_new_wins'] + 1 if bad['max_new_wins'] is not None else None)
        remaining = sum(t in (g.home, g.away) for g in s.remaining)
        if guarantee is not None and guarantee > remaining:
            guarantee = None  # no attainable all-outcomes guarantee
        status = ('clinched' if bad['feasible'] is False else
                  'off' if control[t] is False or any(x is True for x in others) else
                  'unknown' if control[t] is None or any(x is None for x in others) else 'lit')
        result[t] = {'status': status, 'self_control': control[t],
                     'guaranteed_wins_needed': guarantee,
                     'magic': guarantee if status in ('lit', 'clinched') else None,
                     'definition': 'unique self-control; all-completions win guarantee',
                     'failure_with_most_wins': bad}
    return result
