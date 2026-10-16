"""Three exploratory experiments: masked leagues, skill budgets, score geometry.

Pure stdlib. Integer scores and registered propositions remain unchanged. All
coefficients are declared assumptions, not inferred true team abilities.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import gzip
import io
import json
import math
from pathlib import Path
import random
import tomllib

import synthetic_league as sl

VIEWS = ("raw", "linear_097", "log1p", "sqrt", "capped4", "relative")
SCHEMA = "aoi-league-laboratory/1"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_settings(cfg):
    if cfg.get('schema') != SCHEMA or cfg['years'] != list(sl.PRIMARY_YEARS):
        raise ValueError('the primary experiment requires every year 2013-2026 exactly once')
    for key in ('within', 'completion_attempts', 'skill_budget', 'discovery_seed', 'evaluation_seed', 'train_through'):
        if type(cfg[key]) is not int:
            raise ValueError('integer setting required: ' + key)
    if (cfg['within'] < 3 or cfg['completion_attempts'] < 1 or cfg['skill_budget'] < 3
            or cfg['skill_budget'] % 3 or min(cfg['discovery_seed'], cfg['evaluation_seed']) < 0
            or cfg['discovery_seed'] == cfg['evaluation_seed']
            or not min(cfg['years']) <= cfg['train_through'] < max(cfg['years'])):
        raise ValueError('invalid schedule, budget, seeds, attempts, or training boundary')
    for key in ('mean_runs', 'attack_weight', 'defense_weight', 'conversion_weight', 'evaluation_loss'):
        if isinstance(cfg[key], bool) or not isinstance(cfg[key], (int, float)) or not math.isfinite(cfg[key]):
            raise ValueError('finite numeric setting required: ' + key)
    if (min(cfg['attack_weight'], cfg['defense_weight'], cfg['conversion_weight']) < 0
            or cfg['mean_runs'] < math.exp(cfg['defense_weight']) or not 0 <= cfg['evaluation_loss'] <= 1):
        raise ValueError('invalid rate/weight/loss or insufficient score budget for this family')
    if (cfg['views'] != list(VIEWS) or cfg['threshold_ops'] != ['<', '>='] or cfg['measurement_decimals'] != 12
            or not cfg['fixed_teams'] or len(set(cfg['fixed_teams'])) != len(cfg['fixed_teams'])
            or not set(cfg['fixed_teams']) < {f'C{i}' for i in range(1, 7)}):
        raise ValueError('fixed views and a nonempty proper subset of known teams required')


def annual_features(p):
    rows = deepcopy(p['annual'])
    for row in rows:
        same = [r for r in rows if r['league'] == row['league']]
        row.update(rd=row['RF'] - row['RA'], wins_vs_pythag=row['W'] - row['pythag_expected_wins'],
                   rank_pythag=1 + sum(r['pythag_fixed'] > row['pythag_fixed'] for r in same),
                   rank_rf=1 + sum(r['RF'] > row['RF'] for r in same),
                   rank_ra=1 + sum(r['RA'] < row['RA'] for r in same))
    return rows


def assign_wins(template, quotas):
    """Complete masked annual wins, preserving all pair score budgets exactly."""
    p = deepcopy(template)
    teams = [r['team'] for r in p['annual']]
    if set(quotas) != set(teams) or any(type(v) is not int for v in quotas.values()):
        raise sl.InfeasibleScenario('integer win quotas for every team required')
    capacities = [(q['a'], q['b'], q['G'] - q['T'] - 2) for q in p['pairs']]
    base = Counter(t for q in p['pairs'] for t in (q['a'], q['b']))
    allocated = sl._flow({t: quotas[t] - base[t] for t in teams}, capacities)
    for pair, (wa, wb) in zip(p['pairs'], allocated):
        pair.update(W_a=wa + 1, W_b=wb + 1)
    for row in p['annual']:
        row.update(W=quotas[row['team']], L=row['G'] - row['T'] - quotas[row['team']])
        row['pythag_expected_wins'] = (row['W'] + row['L']) * row['pythag_fixed']
    p['annual'] = sl._rank(p['annual'])
    sl.validate_plan(p)
    return p


def completions(template, fixed_teams, *, attempts, seed):
    """Bounded random proposals plus integer max-flow, not uniform enumeration."""
    sl.validate_plan(template)
    if type(attempts) is not int or attempts < 1:
        raise ValueError('positive attempt budget required')
    teams = sorted(r['team'] for r in template['annual'])
    if not fixed_teams or len(set(fixed_teams)) != len(fixed_teams) or not set(fixed_teams) < set(teams):
        raise ValueError('known teams must be a unique nonempty proper subset')
    annual = {r['team']: r for r in template['annual']}
    base = Counter(t for p in template['pairs'] for t in (p['a'], p['b']))
    limits = {t: (base[t], annual[t]['G'] - annual[t]['T'] - base[t]) for t in teams}
    fixed = {t: annual[t]['W'] for t in fixed_teams}
    total = sum(r['W'] for r in template['annual'])
    rng = random.Random(seed)
    seen, records, feasible = set(), [], []
    for attempt in range(attempts):
        unknown = [t for t in teams if t not in fixed]
        rng.shuffle(unknown)
        quota = dict(fixed)
        left = total - sum(fixed.values())
        for i, team in enumerate(unknown):
            rest = unknown[i + 1:]
            lo = max(limits[team][0], left - sum(limits[t][1] for t in rest))
            hi = min(limits[team][1], left - sum(limits[t][0] for t in rest))
            if lo > hi:
                raise ValueError('template has contradictory bounds')
            quota[team] = rng.randint(lo, hi)
            left -= quota[team]
        key = tuple(quota[t] for t in teams)
        record = dict(attempt=attempt, fixed_wins=fixed, proposed_wins=quota)
        if key in seen:
            record['status'] = 'duplicate-proposal'
        else:
            seen.add(key)
            try:
                candidate = assign_wins(template, quota)
            except sl.InfeasibleScenario as exc:
                record.update(status='infeasible-in-declared-family', reason=str(exc))
            else:
                record['status'] = 'feasible'
                feasible.append((attempt, candidate))
        records.append(record)
    return feasible, records


def allocations(budget):
    if type(budget) is not int or budget < 0:
        raise ValueError('integer nonnegative skill budget required')
    return [(a, d, budget - a - d) for a in range(budget + 1) for d in range(budget - a + 1)]


def skill_plan(cfg, *, allocation, seed, loss=0.0):
    """Same point cost for attack/defense/conversion; rates have separate units."""
    budget = cfg['skill_budget']
    if (len(allocation) != 3 or any(type(x) is not int or x < 0 for x in allocation)
            or sum(allocation) != budget or not math.isfinite(loss) or not 0 <= loss <= 1):
        raise ValueError('allocation must spend exactly the declared budget; loss in [0,1]')
    opponents = [(budget, 0, 0), (0, budget, 0), (0, 0, budget), (budget // 3,) * 3,
                 (budget // 2, budget - budget // 2, 0)]
    random.Random(seed).shuffle(opponents)
    skills = dict(zip([f'C{i}' for i in range(1, 7)], [tuple(allocation), *opponents]))
    p = sl.plan(seed=seed, leagues=1, within=cfg['within'], mean_runs=cfg['mean_runs'])
    expected, base = Counter(), Counter()
    for pair in p['pairs']:
        a, b, n = pair['a'], pair['b'], pair['G']
        rate_a = cfg['mean_runs'] * math.exp((cfg['attack_weight'] * skills[a][0] - cfg['defense_weight'] * skills[b][1]) / budget)
        rate_b = cfg['mean_runs'] * math.exp((cfg['attack_weight'] * skills[b][0] - cfg['defense_weight'] * skills[a][1]) / budget)
        rf_a, rf_b = round(n * rate_a), round(n * rate_b)
        common = min(rf_a, rf_b) - n
        pair.update(RF_a=rf_a, RF_b=rf_b, common_runs=common,
                    margin_a=rf_a - common, margin_b=rf_b - common)
        odds = 1.83 * math.log(rf_a / rf_b) + cfg['conversion_weight'] * (1 - loss) * (skills[a][2] - skills[b][2]) / budget
        probability = 1 / (1 + math.exp(-odds))
        decisive = n - pair['T'] - 2
        expected[a] += 1 + decisive * probability
        expected[b] += 1 + decisive * (1 - probability)
        base[a] += 1
        base[b] += 1
    teams = sorted(skills)
    # Recompute annual score budgets before using the existing conservation checks.
    for row in p['annual']:
        row['RF'] = sum(q['RF_a'] if q['a'] == row['team'] else q['RF_b'] for q in p['pairs'] if row['team'] in (q['a'], q['b']))
        row['RA'] = sum(q['RF_b'] if q['a'] == row['team'] else q['RF_a'] for q in p['pairs'] if row['team'] in (q['a'], q['b']))
        row['pythag_fixed'] = sl._pythag(row['RF'], row['RA'])
        row['expected_schedule_wins'] = expected[row['team']]
    total = sum(q['G'] - q['T'] for q in p['pairs'])
    quotas = dict(zip(teams, sl._apportion([expected[t] for t in teams], total)))
    p = assign_wins(p, quotas)
    p.update(profile='skill-budget', skills={t: list(s) for t, s in skills.items()}, conversion_loss=loss,
             skill_budget=budget, expected_model='pair-score odds + retained conversion advantage; conditional one win each way')
    return p


def point_values(rf, ra, view):
    """Alternative analysis units. Official integer scores are never overwritten."""
    if min(rf, ra) < 0 or not all(math.isfinite(x) for x in (rf, ra)):
        raise ValueError('finite nonnegative scores required')
    if view == 'relative':
        return rf / (rf + ra + 1), ra / (rf + ra + 1)
    functions = dict(raw=lambda x: x, linear_097=lambda x: .97 * x,
                     log1p=math.log1p, sqrt=math.sqrt, capped4=lambda x: min(x, 4))
    if view not in functions:
        raise ValueError('unknown score view')
    return functions[view](rf), functions[view](ra)


def score_views(games, teams):
    sums = {t: {v: [[], []] for v in VIEWS if v != 'linear_097'} for t in teams}
    count = Counter()
    for game in games:
        for t, rf, ra in ((game['home'], game['hs'], game['as']), (game['away'], game['as'], game['hs'])):
            if t not in sums:
                raise ValueError('unknown team in witness')
            count[t] += 1
            for view in sums[t]:
                a, d = point_values(rf, ra, view)
                sums[t][view][0].append(a)
                sums[t][view][1].append(d)
    result = {}
    for t in teams:
        if not count[t]:
            raise ValueError('a team has no games')
        result[t] = {v: dict(attack=round(math.fsum(a) / count[t], 12), allowed=round(math.fsum(d) / count[t], 12),
                              margin=round((math.fsum(a) - math.fsum(d)) / count[t], 12))
                     for v, (a, d) in sums[t].items()}
        # Exact scale control: do not introduce a summation-roundoff experiment.
        result[t]['linear_097'] = {k: .97 * value for k, value in result[t]['raw'].items()}
    return result


def rank_views(rows):
    """Rank candidate measurements within a league-year-case, keeping ties."""
    for row in rows:
        peers = [r for r in rows if (r.get('case_id'), r['season'], r['league']) ==
                 (row.get('case_id'), row['season'], row['league'])]
        for view in VIEWS:
            values = row['views'][view]
            for name, higher in (('attack', True), ('allowed', False), ('margin', True)):
                values['rank_' + name] = 1 + sum(
                    (peer['views'][view][name] > values[name] if higher else peer['views'][view][name] < values[name])
                    for peer in peers)
    return rows


def confusion(rows, predictions, *, truth=None):
    if len(rows) != len(predictions) or (truth is not None and len(rows) != len(truth)):
        raise ValueError('prediction/truth length mismatch')
    if truth is None and any(type(r.get('upper_half')) is not bool for r in rows):
        raise ValueError('determined official or synthetic upper-half labels required')
    truth = [not r['upper_half'] for r in rows] if truth is None else truth
    sets = {key: [] for key in ('tp', 'fp', 'fn', 'tn')}
    for row, hit, target in zip(rows, predictions, truth):
        if type(hit) is not bool or type(target) is not bool:
            raise ValueError('determined boolean labels required')
        sets['tp' if hit and target else 'fp' if hit else 'fn' if target else 'tn'].append(row['unit_id'])
    if len({r['unit_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate evaluation units')
    counts = {key: len(ids) for key, ids in sets.items()}
    tp, fp, fn, tn = (counts[key] for key in ('tp', 'fp', 'fn', 'tn'))
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return dict(n=len(rows), **counts, holds=tp, antecedent=tp + fp,
                mcc=(tp * tn - fp * fn) / den if den else 0., mcc_defined=bool(den),
                precision=tp / (tp + fp) if tp + fp else None,
                recall=tp / (tp + fn) if tp + fn else None,
                sets={key: sorted(ids) for key, ids in sets.items()})


def _condition(row, conditions):
    ops = {'<': lambda a, b: a < b, '<=': lambda a, b: a <= b, '>': lambda a, b: a > b,
           '>=': lambda a, b: a >= b, '==': lambda a, b: a == b, '!=': lambda a, b: a != b}
    return all(ops[c['op']](row[c['col']], c['value']) for c in conditions)


def reference_metrics(rows, props):
    return {prop['id']: confusion(rows, [antecedent(r, prop) for r in rows],
                                 truth=[_condition(r, prop['then']) for r in rows]) for prop in props}


def antecedent(row, prop):
    if prop.get('scope'):
        raise ValueError('scoped reference propositions require an explicit cohort adapter')
    return _condition(row, prop.get('if', [])) and (
        'if_any' not in prop or any(_condition(row, group) for group in prop['if_any']))


def fit_threshold(rows, view):
    """One-dimensional candidate rule, selected exclusively on discovery rows."""
    if not rows or any(r['phase'] != 'discovery' for r in rows):
        raise ValueError('fit requires discovery rows only')
    values = sorted({r['views'][view]['margin'] for r in rows})
    thresholds = [values[0], *(a + (b - a) / 2 for a, b in zip(values, values[1:])), math.nextafter(values[-1], math.inf)]
    best = None
    for threshold in thresholds:
        for op in ('<', '>='):
            metric = confusion(rows, [compare(r['views'][view]['margin'], threshold, op) for r in rows])
            key = (-round(metric['mcc'], 12), metric['fp'] + metric['fn'], op, threshold)
            if best is None or key < best[0]:
                best = (key, threshold, op, metric)
    return dict(id=f'LAB-G{VIEWS.index(view) + 1:02d}', view=view, threshold=best[1], op=best[2], target='synthetic lower half',
                training=best[3], thresholds_tested=2 * len(thresholds), source='exploratory', posthoc=True)


def compare(value, threshold, op):
    if op not in ('<', '>='):
        raise ValueError('unknown frozen threshold operator')
    return value < threshold if op == '<' else value >= threshold


def evaluate_views(rows, models):
    out = {}
    baseline = None
    for view in VIEWS:
        model = models[view]
        metric = confusion(rows, [compare(r['views'][view]['margin'], model['threshold'], model['op']) for r in rows])
        if view == 'raw':
            baseline = metric['sets']
        metric.update(same_predictions_as_raw=metric['sets'] == baseline,
                      corrected_fp=sorted(set(baseline['fp']) & set(metric['sets']['tn'])),
                      corrected_fn=sorted(set(baseline['fn']) & set(metric['sets']['tp'])),
                      introduced_fp=sorted(set(baseline['tn']) & set(metric['sets']['fp'])),
                      introduced_fn=sorted(set(baseline['tp']) & set(metric['sets']['fn'])))
        out[view] = metric
    return out


def witness_games(p, kind='original'):
    games = sl.expand(p)
    if kind == 'concentrated-common':
        grouped = defaultdict(list)
        for game in games:
            grouped[tuple(sorted((game['home'], game['away'])))].append(game)
        for group in grouped.values():
            common = sum(min(g['hs'], g['as']) for g in group)
            for i, game in enumerate(group):
                offset = min(game['hs'], game['as'])
                game['hs'] = game['hs'] - offset + (common if i == 0 else 0)
                game['as'] = game['as'] - offset + (common if i == 0 else 0)
    elif kind != 'original':
        raise ValueError('unknown witness family')
    sl.validate_games(p, games)
    return games


def observe(p, *, year, phase, track, case_id, witness='original'):
    games = witness_games(p, witness)
    views = score_views(games, [r['team'] for r in p['annual']])
    rows = []
    for row in annual_features(p):
        row.update(season=year, phase=phase, track=track, case_id=case_id,
                   unit_id=case_id + '/' + row['team'], views=views[row['team']])
        rows.append(row)
    return rank_views(rows), dict(case_id=case_id, season=year, phase=phase, track=track, plan=p, witness=witness,
                     games_sha256=digest(games), games=len(games), structural_check=True)


def phases(cfg):
    for year in cfg['years']:
        yield year, 'discovery' if year <= cfg['train_through'] else 'year-holdout', cfg['discovery_seed'], 0.
        if year > cfg['train_through']:
            yield year, 'seed-holdout', cfg['evaluation_seed'], 0.
            yield year, 'loss-shift', cfg['evaluation_seed'], cfg['evaluation_loss']


def experiment(cfg, props):
    validate_settings(cfg)
    observations, cases, attempts, scan = [], [], [], []
    budget = cfg['skill_budget']
    representatives = {(budget, 0, 0), (0, budget, 0), (0, 0, budget), (budget // 3,) * 3}
    for year, phase, batch, loss in phases(cfg):
        seed = batch * 10000 + year
        if phase != 'loss-shift':
            template = sl.plan(seed=seed, profile='aligned', mean_runs=cfg['mean_runs'], leagues=1, within=cfg['within'])
            feasible, records = completions(template, cfg['fixed_teams'], attempts=cfg['completion_attempts'], seed=seed)
            for record in records:
                record.update(season=year, phase=phase, seed=seed, track='masked-wins')
                attempts.append(record)
            for attempt, p in feasible:
                case_id = f'masked/{phase}/{year}/a{attempt}'
                rows, case = observe(p, year=year, phase=phase, track='masked-wins', case_id=case_id)
                case.update(fixed_teams=cfg['fixed_teams'], masked_columns=['W'], template_sha256=digest(template))
                observations.extend(rows)
                cases.append(case)
        for allocation in allocations(budget):
            case_id = f'skills/{phase}/{year}/' + '-'.join(map(str, allocation))
            try:
                p = skill_plan(cfg, allocation=allocation, seed=seed, loss=loss)
            except sl.InfeasibleScenario as exc:
                scan.append(dict(case_id=case_id, season=year, phase=phase, allocation=list(allocation),
                                 loss=loss, status='infeasible-in-declared-family', reason=str(exc)))
                continue
            focal = next(r for r in annual_features(p) if r['team'] == 'C1')
            focal.update(case_id=case_id, season=year, phase=phase, allocation=list(allocation), loss=loss,
                         spent=sum(allocation), unit_id=case_id + '/C1', status='feasible')
            scan.append(focal)
            # Annual-first screening avoids expanding all point allocations.
            if allocation in representatives:
                rows, case = observe(p, year=year, phase=phase, track='skill-budget', case_id=case_id)
                observations.extend(rows)
                cases.append(case)
    for case in list(cases):
        if case['phase'] == 'seed-holdout':
            case_id = case['case_id'].replace('/seed-holdout/', '/witness-shift/')
            rows, shifted = observe(case['plan'], year=case['season'], phase='witness-shift', track=case['track'],
                                    case_id=case_id, witness='concentrated-common')
            observations.extend(rows)
            cases.append(shifted)
    models = {}
    for track in sorted({r['track'] for r in observations}):
        training = [r for r in observations if r['phase'] == 'discovery' and r['track'] == track]
        fitted = {view: fit_threshold(training, view) for view in VIEWS if view != 'linear_097'}
        fitted['linear_097'] = {**deepcopy(fitted['raw']), 'id': 'LAB-G02', 'view': 'linear_097',
                                'threshold': .97 * fitted['raw']['threshold'], 'source': 'unit-conversion-control'}
        models[track] = fitted
    for row in [*observations, *(r for r in scan if r['status'] == 'feasible')]:
        row['reference_hits'] = {p['id']: dict(antecedent=antecedent(row, p), target=_condition(row, p['then'])) for p in props}
    groups = []
    for track, phase in sorted({(r['track'], r['phase']) for r in observations}):
        part = [r for r in observations if (r['track'], r['phase']) == (track, phase)]
        changes = {view: {key: [r['unit_id'] for r in part if r['views'][view]['rank_' + key] != r['views']['raw']['rank_' + key]]
                          for key in ('attack', 'allowed', 'margin')} for view in VIEWS}
        groups.append(dict(track=track, phase=phase, n=len(part), metrics=evaluate_views(part, models[track]), rank_changes=changes,
                           reference_propositions=reference_metrics(part, props)))
    if any(not g['metrics']['linear_097']['same_predictions_as_raw'] for g in groups):
        raise ValueError('unit-conversion negative control changed classifications')
    transfers = []
    for group in groups:
        if group['phase'] == 'discovery':
            continue
        part = [r for r in observations if (r['track'], r['phase']) == (group['track'], group['phase'])]
        for source_track in models:
            if source_track != group['track']:
                transfers.append(dict(training_track=source_track, evaluation_track=group['track'], phase=group['phase'],
                                      metrics=evaluate_views(part, models[source_track])))
    return dict(schema=SCHEMA, synthetic=True, real_sample_increment=0, independent_confirmation=False,
                settings=cfg, models=models, groups=groups, observations=observations, cases=cases,
                attempts=attempts, skill_scan=scan, transfer_groups=transfers,
                reference_definitions=props, reference_definitions_sha256=digest(props),
                score_examples={f'{rf}-{ra}': {v: point_values(rf, ra, v)[0] - point_values(rf, ra, v)[1]
                                              for v in VIEWS} for rf, ra in [(3, 4), (6, 7)]})


def read_real(games_path, seasons_path, cfg):
    """Optional bridge: reject incomplete raw scores instead of inferring them."""
    annual = [json.loads(line) for line in Path(seasons_path).read_text().splitlines() if line.strip()]
    annual = [r for r in annual if r['season'] in cfg['years']]
    if any(r.get('synthetic') is True or type(r.get('upper_half')) is not bool
           or any(type(r.get(k)) is not int or r[k] < 0 for k in ('G', 'W', 'L', 'T', 'RF', 'RA')) for r in annual):
        raise ValueError('real annual labels required')
    indexed = {(r['season'], r['team']): r for r in annual}
    if len(indexed) != len(annual) or not indexed:
        raise ValueError('unique nonempty official annual rows required')
    by_year, seen = defaultdict(list), set()
    for line in Path(games_path).read_text().splitlines():
        if not line.strip():
            continue
        game = json.loads(line)
        year = game.get('season', int(game['date'][:4]) if 'date' in game else None)
        if year not in cfg['years']:
            continue
        if (game.get('synthetic') is True or game['key'] in seen or game['home'] == game['away']
                or any(type(game[k]) is not int or game[k] < 0 for k in ('hs', 'as'))):
            raise ValueError('unique real integer-score games required')
        seen.add(game['key'])
        by_year[year].append(game)
    if set(by_year) != {r['season'] for r in annual}:
        raise ValueError('raw game years do not cover the supplied annual cohort')
    rows = []
    for year, games in sorted(by_year.items()):
        teams = sorted(t for y, t in indexed if y == year)
        # Reuse the strict aggregate checker on a synthetic-marked COPY only.
        aggregate = sl.aggregate([{**g, 'synthetic': True} for g in games])
        if set(aggregate) != set(teams):
            raise ValueError('raw/official team coverage differs')
        views = score_views(games, teams)
        for team in teams:
            original = indexed[year, team]
            if any(aggregate[team][k] != original[k] for k in ('G', 'W', 'L', 'T', 'RF', 'RA')):
                raise ValueError('incomplete or inconsistent real game totals')
            rows.append({**original, 'synthetic': False, 'unit_id': f'real/{year}/{team}',
                         'views': views[team], 'phase': 'real-retrospective', 'track': 'real'})
    return rank_views(rows)


def render(report):
    counts = report['attempt_counts']
    lines = ['# 3方向のリーグ実験', '', '記録: 2026-10-15', '',
             '合成データによる探索の記録。実測件数に加えず、命題・合格条件を変更しない。',
             '係数は仮定であり、潜在的な「真の攻撃力・守備力」が同定されたという意味ではない。', '',
             '## ① 勝敗を隠した条件付き補完', '',
             f"- 提案 {report['attempt_count']} 件: {dict(sorted(counts.items()))}",
             '- 各リーグ6球団。得失点・対戦数・引分数と指定球団の勝利数を固定し、他球団の勝利数を補完する。',
             '- 総勝利数で残りを絞ってから整数最大流で判定する。有限回の偏りを持つ乱数提案であり、全解列挙や一様抽出ではない。',
             '- 通過/不通過/重複を全件残す。生成不能は宣言した生成族内の判定であり、野球全体の不可能性ではない。', '',
             '## ② 能力予算と変換の損失', '',
             f"- 全配分の年次スキャン {report['skill_scan_count']} 件。実現可能 {report['skill_scan_feasible']} 件。",
             f"- 各球団の攻撃/守備/変換への配分合計は {report['settings']['skill_budget']} ポイント。費用と得点の単位を混ぜない。",
             '- 得点率は対戦相手の守備を含む指数モデル。変換能力の残存率(1−loss)を勝敗オッズへ適用する。',
             '- lossは計算するたびに失われる量ではなく、宣言した能力効果の減衰率。W−ピタゴラス期待勝利数も別欄に残す。',
             '- 全配分を年成績で先に検査し、攻撃偏重・守備偏重・変換偏重・均衡型だけ試合へ展開して費用を抑える。',
             '- 同じ配分を14年間続けた架空C1の順位列・上位回数・最長下位連続年数もskill_pathsに残す。', '',
             '## ③ 得点の物差し', '',
             '| スコア | raw差 | log1p差 | sqrt差 | relative差 |', '|---|---:|---:|---:|---:|']
    for example, values in report['score_examples'].items():
        lines.append(f"| {example} | {values['raw']:.6f} | {values['log1p']:.6f} | {values['sqrt']:.6f} | {values['relative']:.6f} |")
    lines += ['', '公式の整数スコアを保存したまま、試合ごとに変換してから年平均を作る。',
              'raw/0.97倍/ln(1+x)/sqrt(x)/min(x,4)/(相手との合計+1)で規格化、の6尺度。',
              '集計はmath.fsumで試合順への依存を避け、小数12桁へ丸める。丸め誤差だけの順位・閾値分割を避けるためである。',
              'allowedは変換後の失点で、小さいほどよい。relativeは相手依存の指標で、独立した能力量ではない。',
              'ピタゴラス式や既存命題の値は補正で置換しない。別ID LAB-G01〜06の探索候補として比較する。', '',
              '## 固定した閾値の評価', '',
              '生成系列ごとに、発見seed・2013〜2022年・loss=0だけで「変換後平均差と閾値の比較 ⇒ 下位半分」を選ぶ。',
              '比較方向(<または>=)も探索対象で、逆向きに選ばれる場合もそのまま残す。異なる生成系列への転用結果も保存する。',
              'その後、後年・別seed・変換損失変更へ固定して適用する。尺度の採否を評価結果から自動で選び直さない。', '',
              '| 系列 | 評価 | 尺度 | n | MCC | TP | FP | FN | TN |', '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for group in report['groups']:
        for view in VIEWS:
            m = group['metrics'][view]
            value = f"{m['mcc']:.6f}" if m['mcc_defined'] else '未定義'
            lines.append(f"| {group['track']} | {group['phase']} | {view} | {m['n']} | {value} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} |")
    lines += ['', '成立=TP。0.97倍は閾値も同じ単位へ換算する対照で、全群でrawと判定集合が一致することを必須にした。',
              '各候補の修正/新規FP・FNのID集合、登録済みP2/P3/P4/P5の補助評価をresults.jsonへ保存する。',
              '全判定集合はclassifications.jsonl.gz、生成条件と試合ハッシュはcases.jsonl.gz、変換前後の値はobservations.jsonl.gzにある。', '',
              '## 発見側で固定した候補', '',
              '| 発見系列 | 候補 | 尺度 | 比較 | 閾値 | 発見MCC |', '|---|---|---|---|---:|---:|']
    for track in sorted(report['models']):
        for view in VIEWS:
            model = report['models'][track][view]
            lines.append(f"| {track} | {model['id']} | {view} | {model['op']} | {model['threshold']:.9f} | {model['training']['mcc']:.6f} |")
    lines += ['', '## 尺度で変わった順位（別seed評価）', '',
              '| 系列 | 尺度 | 攻撃順位が変化 | 失点抑制順位が変化 | 差分順位が変化 |', '|---|---|---:|---:|---:|']
    for group in report['groups']:
        if group['phase'] == 'seed-holdout':
            for view in VIEWS:
                changes = group['rank_changes'][view]
                lines.append(f"| {group['track']} | {view} | {changes['attack']['n']} | {changes['allowed']['n']} | {changes['margin']['n']} |")
    lines += ['',
              '## 適用範囲と次の問い', '',
              '- 2013〜2026年をすべて生成する。各年は独立した架空モデルで、14年連続の組織特性をまだモデル化していない。',
              '- 同リーグ25試合×5相手を既定とする。交流戦・公式日程・公式の同率順位/CS開催規則は再現しない。2020年も架空モデルに含む。',
              '- 真の順位ラベルは元スコアから固定する。補正に合わせて正解ラベルや既存閾値を変更しない。',
              '- witness-shiftはW/L/RF/RAを保ったまま共通得点を集中させる極端な対照。勝敗から組み立てた試合の配分に識別力が依存していないか調べる。',
              '- 最初の試行後に系列別学習・比較方向の探索を追加した事後的設計で、設計中に評価年も閲覧している。未閲覧年での事前登録検証ではない。',
              '- 攻撃/守備の尺度間の順位が入れ替わる球団と、既存条件の通過/不通過を次の命題の材料にする。',
              '- 平均値だけでは非線形変換後の平均を復元できない。実測への適用には試合スコアが必要。',
              f"- 実測への適用状態: {report['real_evaluation']['status']}。",
              '- 合成データのholdoutは生成仮定内の比較であり、現実の独立確認・因果説明を意味しない。', '']
    return '\n'.join(lines)


def write_jsonl_gz(path, rows):
    stream = io.BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as zipped:
        zipped.write(''.join(canonical(row) + '\n' for row in rows).encode())
    path.write_bytes(stream.getvalue())


def read_jsonl(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as source:
        return [json.loads(line) for line in source if line.strip()]


def scan_summary(rows):
    groups = defaultdict(list)
    for row in rows:
        if row['status'] == 'feasible':
            groups[row['phase'], tuple(row['allocation'])].append(row)
    return [dict(phase=phase, allocation=list(allocation), n=len(part),
                 upper_count=sum(r['upper_half'] for r in part),
                 mean_wins=sum(r['W'] for r in part) / len(part),
                 mean_runs_for_per_game=sum(r['RF'] / r['G'] for r in part) / len(part),
                 mean_runs_allowed_per_game=sum(r['RA'] / r['G'] for r in part) / len(part),
                 mean_wins_vs_pythag=sum(r['wins_vs_pythag'] for r in part) / len(part),
                 reference_hits={key: sum(r['reference_hits'][key]['antecedent'] for r in part)
                                 for key in part[0]['reference_hits']})
            for (phase, allocation), part in sorted(groups.items())]


def skill_paths(rows):
    """A fixed skill allocation across the 14 year labels, not a fitted dynasty."""
    groups = defaultdict(list)
    for row in rows:
        if row['status'] == 'feasible' and row['phase'] in ('discovery', 'year-holdout'):
            groups[tuple(row['allocation'])].append(row)
    result = []
    for allocation, part in sorted(groups.items()):
        part.sort(key=lambda r: r['season'])
        if [r['season'] for r in part] != list(sl.PRIMARY_YEARS):
            result.append(dict(allocation=list(allocation), complete=False))
            continue
        run = longest = 0
        for row in part:
            run = 0 if row['upper_half'] else run + 1
            longest = max(longest, run)
        result.append(dict(allocation=list(allocation), complete=True,
                           years=[dict(season=r['season'], rank=r['rank'], upper_half=r['upper_half']) for r in part],
                           upper_count=sum(r['upper_half'] for r in part), longest_lower_run=longest))
    return result


def compact_metric(metric):
    return {key: value for key, value in metric.items() if key != 'sets'}


def write_outputs(result, out, *, config_path, props_path, real_games=None, real_seasons=None):
    out.mkdir(parents=True, exist_ok=True)
    fields = ('observations', 'cases', 'attempts', 'skill_scan', 'classifications', 'transfers')
    artifacts = {field: result['groups'] if field == 'classifications' else result['transfer_groups'] if field == 'transfers' else result[field] for field in fields}
    for field, rows in artifacts.items():
        write_jsonl_gz(out / (field + '.jsonl.gz'), rows)
    report = {key: value for key, value in result.items() if key not in ('observations', 'cases', 'attempts', 'skill_scan', 'groups', 'models', 'transfer_groups')}
    report['models'] = {track: {view: {**model, 'training': compact_metric(model['training'])}
                                for view, model in fitted.items()} for track, fitted in result['models'].items()}
    report['groups'] = [{**group, 'metrics': {v: compact_metric(m) for v, m in group['metrics'].items()},
                         'rank_changes': {v: {key: dict(n=len(ids), examples=ids[:3]) for key, ids in changes.items()}
                                          for v, changes in group['rank_changes'].items()},
                         'reference_propositions': {key: compact_metric(m) for key, m in group['reference_propositions'].items()}}
                        for group in result['groups']]
    report['transfer_groups'] = [{**group, 'metrics': {v: compact_metric(m) for v, m in group['metrics'].items()}}
                                  for group in result['transfer_groups']]
    report.update(attempt_counts=dict(Counter(r['status'] for r in result['attempts'])), attempt_count=len(result['attempts']),
                  skill_scan_count=len(result['skill_scan']), skill_scan_feasible=sum(r['status'] == 'feasible' for r in result['skill_scan']),
                  skill_summary=scan_summary(result['skill_scan']), skill_paths=skill_paths(result['skill_scan']))
    report['artifacts'] = {field: dict(path=field + '.jsonl.gz', rows=len(rows), sha256=file_sha(out / (field + '.jsonl.gz')))
                           for field, rows in artifacts.items()}
    report['inputs'] = dict(settings_sha256=file_sha(config_path), propositions_sha256=file_sha(props_path),
                           analysis_sha256=file_sha(__file__), generator_sha256=file_sha(Path(sl.__file__)))
    if real_games is None:
        report['real_evaluation'] = dict(status='not-run: raw game scores not supplied',
                                         reason='Annual totals do not identify per-game nonlinear score views.')
    else:
        rows = read_real(real_games, real_seasons, result['settings'])
        report['real_evaluation'] = dict(status='completed-retrospective', n=len(rows), years=sorted({r['season'] for r in rows}),
                                         games_sha256=file_sha(real_games), annual_sha256=file_sha(real_seasons),
                                         metrics={track: evaluate_views(rows, fitted) for track, fitted in result['models'].items()})
    (out / 'results.json').write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (out / 'report.md').write_text(render(report), encoding='utf-8')
    return report


def main(argv=None):
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=root / 'cycles/c001-chunichi/league-laboratory.toml')
    parser.add_argument('--propositions', type=Path, default=root / 'cycles/c001-chunichi/propositions.toml')
    parser.add_argument('--out', type=Path, default=root / 'cycles/c001-chunichi/outputs/exploratory/league-laboratory')
    parser.add_argument('--real-games', type=Path)
    parser.add_argument('--real-seasons', type=Path, default=root / 'cycles/c001-chunichi/outputs/season.jsonl')
    args = parser.parse_args(argv)
    cfg = tomllib.loads(args.config.read_text(encoding='utf-8'))
    registered = {p['id']: p for p in tomllib.loads(args.propositions.read_text(encoding='utf-8'))['proposition']}
    props = [registered[key] for key in cfg['reference_propositions']]
    result = experiment(cfg, props)
    report = write_outputs(result, args.out, config_path=args.config, props_path=args.propositions,
                           real_games=args.real_games, real_seasons=args.real_seasons)
    print(canonical(dict(cases=len(result['cases']), attempts=len(result['attempts']),
                         skill_scan=len(result['skill_scan']), observations=len(result['observations']),
                         real_evaluation=report['real_evaluation']['status'], out=str(args.out))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
