"""Model assumptions, conserved game witnesses, frozen evaluation and units."""
from copy import deepcopy
import json
from pathlib import Path
import tomllib

import pytest

import league_laboratory as lab
import synthetic_league as sl

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / 'cycles/c001-chunichi'
OUT = CYCLE / 'outputs/exploratory/league-laboratory'


@pytest.fixture
def cfg():
    return tomllib.loads((CYCLE / 'league-laboratory.toml').read_text())


@pytest.fixture
def props(cfg):
    registry = {p['id']: p for p in tomllib.loads((CYCLE / 'propositions.toml').read_text())['proposition']}
    return [registry[key] for key in cfg['reference_propositions']]


def test_masked_completions_preserve_fixed_values_and_all_attempts(cfg):
    template = sl.plan(seed=2013, leagues=1, within=9)
    before = deepcopy(template)
    feasible, attempts = lab.completions(template, ['C1', 'C2'], attempts=40, seed=17)
    assert template == before
    assert len(attempts) == 40 and feasible
    assert len(feasible) == sum(r['status'] == 'feasible' for r in attempts)
    original = {r['team']: r for r in template['annual']}
    assert any(any(r['W'] != original[r['team']]['W'] for r in p['annual']) for _, p in feasible)
    for _, p in feasible:
        sl.validate_games(p, sl.expand(p))
        for row in p['annual']:
            assert all(row[k] == original[row['team']][k] for k in ('G', 'T', 'RF', 'RA', 'pythag_fixed'))
            if row['team'] in ('C1', 'C2'):
                assert row['W'] == original[row['team']]['W']
    assert lab.completions(template, ['C1', 'C2'], attempts=40, seed=17) == (feasible, attempts)


def test_conserving_but_pairwise_impossible_wins_are_rejected():
    p = sl.plan(seed=2013, leagues=1)
    teams = sorted(r['team'] for r in p['annual'])
    annual = {r['team']: r for r in p['annual']}
    low = 5
    quota = {t: low for t in teams}
    for t in teams[:2]:
        quota[t] = annual[t]['G'] - annual[t]['T'] - low
    left = sum(r['W'] for r in p['annual']) - sum(quota.values())
    for t in teams[2:]:
        extra = min(left, annual[t]['G'] - annual[t]['T'] - low - quota[t])
        quota[t] += extra
        left -= extra
    assert left == 0 and sum(quota.values()) == sum(r['W'] for r in p['annual'])
    with pytest.raises(sl.InfeasibleScenario):
        lab.assign_wins(p, quota)


def test_skill_budget_effects_have_distinct_units_and_loss_keeps_score_budgets(cfg):
    points = lab.allocations(cfg['skill_budget'])
    assert len(points) == 28 and all(sum(a) == 6 and min(a) >= 0 for a in points)
    plans = [lab.skill_plan(cfg, allocation=a, seed=2013) for a in [(6, 0, 0), (0, 6, 0), (0, 0, 6), (2, 2, 2)]]
    for p in plans:
        assert all(sum(a) == 6 for a in p['skills'].values())
        sl.validate_games(p, sl.expand(p))
    get = lambda p: next(r for r in p['annual'] if r['team'] == 'C1')
    assert get(plans[0])['RF'] > get(plans[1])['RF']
    assert get(plans[1])['RA'] < get(plans[0])['RA']
    depleted = lab.skill_plan(cfg, allocation=(0, 0, 6), seed=2013, loss=1.)
    assert [(r['RF'], r['RA']) for r in depleted['annual']] == [(r['RF'], r['RA']) for r in plans[2]['annual']]
    assert get(depleted)['expected_schedule_wins'] < get(plans[2])['expected_schedule_wins']
    for allocation, loss in [((1, 2, 2), 0), ((-1, 1, 6), 0), ((2, 2, 2), -1), ((2, 2, 2), float('nan'))]:
        with pytest.raises(ValueError):
            lab.skill_plan(cfg, allocation=allocation, seed=2013, loss=loss)


def test_equal_raw_margins_can_have_distinct_geometries():
    gap = lambda rf, ra, v: lab.point_values(rf, ra, v)[0] - lab.point_values(rf, ra, v)[1]
    assert gap(3, 4, 'raw') == gap(6, 7, 'raw') == -1
    assert gap(3, 4, 'linear_097') == pytest.approx(-.97)
    assert abs(gap(3, 4, 'log1p')) > abs(gap(6, 7, 'log1p'))
    assert gap(3, 4, 'relative') == pytest.approx(-1 / 8)
    assert gap(6, 7, 'relative') == pytest.approx(-1 / 14)
    assert lab.point_values(0, 0, 'log1p') == (0., 0.)
    for rf, ra, view in [(-1, 0, 'raw'), (float('nan'), 1, 'raw'), (1, 1, 'other')]:
        with pytest.raises(ValueError):
            lab.point_values(rf, ra, view)


def test_transform_precedes_aggregation_and_input_scores_remain_integer():
    make = lambda values: [dict(key=str(i), home='A', away='B', hs=x, **{'as': 1}) for i, x in enumerate(values)]
    clustered, spread = make([0, 0, 6]), make([2, 2, 2])
    first = lab.score_views(clustered, ['A', 'B'])['A']
    second = lab.score_views(spread, ['A', 'B'])['A']
    assert first['raw'] == second['raw']
    assert first['log1p']['attack'] < second['log1p']['attack']
    assert all(type(g['hs']) is int for g in clustered + spread)
    assert lab.score_views(clustered, ['A', 'B']) == lab.score_views(list(reversed(clustered)), ['A', 'B'])
    assert first['linear_097'] == {k: .97 * value for k, value in first['raw'].items()}


def test_alternative_witness_preserves_all_official_scores_totals_and_outcomes():
    p = sl.plan(seed=2013, leagues=1)
    before = deepcopy(p)
    first, shifted = lab.witness_games(p), lab.witness_games(p, 'concentrated-common')
    assert p == before
    assert sl.aggregate(first) == sl.aggregate(shifted)
    assert [(g['hs'] > g['as'], g['hs'] == g['as']) for g in first] == [(g['hs'] > g['as'], g['hs'] == g['as']) for g in shifted]
    assert lab.score_views(first, ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])['C1']['raw'] == lab.score_views(shifted, ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])['C1']['raw']
    assert lab.digest(first) != lab.digest(shifted)


def test_evaluation_does_not_fit_and_new_errors_are_not_hidden(cfg, props):
    small = {**cfg, 'within': 3, 'skill_budget': 3, 'completion_attempts': 2}
    first = lab.experiment(small, props)
    second = lab.experiment({**small, 'evaluation_seed': 19, 'evaluation_loss': 1.}, props)
    assert first['models'] == second['models']
    assert {r['season'] for r in first['observations']} == set(range(2013, 2027))
    for track, fitted in first['models'].items():
        for model in fitted.values():
            ids = sum(model['training']['sets'].values(), [])
            assert all('/discovery/' in unit for unit in ids)
        for group in first['groups']:
            assert group['metrics']['linear_097']['same_predictions_as_raw']
    with pytest.raises(ValueError, match='discovery'):
        lab.fit_threshold([r for r in first['observations'] if r['phase'] == 'year-holdout'], 'raw')


def test_references_keep_registered_targets_and_rank_ties(cfg, props):
    p = sl.plan(seed=2013, leagues=1, profile='same_totals')
    rows = lab.annual_features(p)
    assert all(r['rank_pythag'] == 1 for r in rows)
    for row in rows:
        row['unit_id'] = row['team']
    metrics = lab.reference_metrics(rows, props)
    assert metrics['P2']['antecedent'] == 6
    assert metrics['P2']['tp'] == metrics['P2']['fp'] == 3
    assert metrics['P5']['tp'] == metrics['P5']['fp'] == 0
    assert lab.antecedent({'x': 2}, {'if_any': [[dict(col='x', op='<', value=0)], [dict(col='x', op='>', value=1)]]})


def test_real_bridge_demands_complete_scores_and_preserves_official_labels(tmp_path, cfg):
    # Fictional fixture shaped like real inputs, never a claim about real NPB data.
    p = sl.plan(seed=2013, leagues=1, within=3)
    annual = [{**r, 'season': 2013, 'synthetic': False} for r in p['annual']]
    games = [{**g, 'synthetic': False, 'season': 2013} for g in sl.expand(p)]
    source = tmp_path / 'games.jsonl'
    seasons = tmp_path / 'annual.jsonl'
    write = lambda path, rows: path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
    write(source, games)
    write(seasons, annual)
    measured = lab.read_real(source, seasons, cfg)
    assert {r['team']: r['upper_half'] for r in measured} == {r['team']: r['upper_half'] for r in annual}
    assert all(not r['synthetic'] for r in measured)
    write(source, games[:-1])
    with pytest.raises(ValueError):
        lab.read_real(source, seasons, cfg)
    write(source, [{**games[0], 'synthetic': True}, *games[1:]])
    with pytest.raises(ValueError):
        lab.read_real(source, seasons, cfg)


@pytest.mark.parametrize('change', [dict(years=[2013, 2026]), dict(evaluation_seed=0), dict(evaluation_loss=2.),
                                  dict(fixed_teams=['C7']), dict(skill_budget=5), dict(views=['raw'])])
def test_invalid_settings_fail_closed(cfg, change):
    with pytest.raises(ValueError):
        lab.validate_settings({**cfg, **change})


def replay_observations(case, props):
    """Rebuild observations from the case, never from stored observation values."""
    rows, actual = lab.observe(
        case['plan'], year=case['season'], phase=case['phase'], track=case['track'],
        case_id=case['case_id'], witness=case['witness'])
    for row in rows:
        row['reference_hits'] = {
            p['id']: dict(antecedent=lab.antecedent(row, p),
                          target=lab._condition(row, p['then'])) for p in props}
    return rows, actual


def assert_observations_match(expected, saved):
    """Compare complete rows and multiplicity, including JSON scalar types."""
    expected_by_id = {r['unit_id']: r for r in expected}
    saved_by_id = {r['unit_id']: r for r in saved}
    assert len(expected_by_id) == len(expected), 'duplicate replay unit_id'
    assert len(saved_by_id) == len(saved), 'duplicate saved unit_id'
    assert expected_by_id.keys() == saved_by_id.keys(), 'missing or unexpected unit_id'
    for unit_id, row in expected_by_id.items():
        assert lab.canonical(row) == lab.canonical(saved_by_id[unit_id]), unit_id


@pytest.fixture
def replayed_case(props):
    case = lab.read_jsonl(OUT / 'cases.jsonl.gz')[0]
    rows, _ = replay_observations(case, props)
    saved = [r for r in lab.read_jsonl(OUT / 'observations.jsonl.gz')
             if r['case_id'] == case['case_id']]
    assert_observations_match(rows, saved)
    return rows, saved


@pytest.mark.parametrize('field', [
    'G', 'W', 'L', 'T', 'RF', 'RA', 'rank', 'rank_tie', 'rank_pythag',
    'rank_rf', 'rank_ra', 'rd', 'pythag_fixed', 'pythag_expected_wins',
    'expected_schedule_wins', 'wins_vs_pythag', 'upper_half', 'synthetic',
    'season', 'league', 'team', 'phase', 'track', 'case_id', 'unit_id',
    'views', 'reference_antecedent', 'reference_target', 'label_type',
])
def test_observation_replay_rejects_corrupted_fields(replayed_case, field):
    rows, saved = replayed_case
    corrupted = deepcopy(saved)
    row = corrupted[0]
    if field.startswith('reference_'):
        key = field.removeprefix('reference_')
        row['reference_hits']['P2'][key] = not row['reference_hits']['P2'][key]
    elif field == 'views':
        row['views']['raw']['margin'] += 1
    elif field == 'label_type':
        row['upper_half'] = int(row['upper_half'])
    else:
        value = row[field]
        row[field] = (not value if type(value) is bool else
                      value + 1 if isinstance(value, (int, float)) else value + '/corrupted')
    with pytest.raises(AssertionError):
        assert_observations_match(rows, corrupted)


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'extra', 'missing-field', 'extra-field'])
def test_observation_replay_rejects_incomplete_or_extra_evidence(replayed_case, change):
    rows, saved = replayed_case
    corrupted = deepcopy(saved)
    if change == 'missing':
        corrupted.pop()
    elif change == 'duplicate':
        corrupted.append(deepcopy(corrupted[0]))
    elif change == 'extra':
        corrupted.append({**deepcopy(corrupted[0]), 'unit_id': 'unexpected/C7'})
    elif change == 'missing-field':
        del corrupted[0]['reference_hits']
    else:
        corrupted[0]['unexpected'] = True
    with pytest.raises(AssertionError):
        assert_observations_match(rows, corrupted)


def test_saved_evidence_replays_and_contains_passes_and_nonpasses(cfg, props):
    report = json.loads((OUT / 'results.json').read_text())
    assert report['settings'] == cfg
    assert report['reference_definitions'] == props
    assert report['reference_definitions_sha256'] == lab.digest(props)
    assert report['inputs']['propositions_sha256'] == lab.file_sha(CYCLE / 'propositions.toml')
    assert report['inputs']['settings_sha256'] == lab.file_sha(CYCLE / 'league-laboratory.toml')
    assert report['inputs']['analysis_sha256'] == lab.file_sha(ROOT / 'sakanalytics/league_laboratory.py')
    assert report['inputs']['generator_sha256'] == lab.file_sha(ROOT / 'sakanalytics/synthetic_league.py')
    for info in report['artifacts'].values():
        assert lab.file_sha(OUT / info['path']) == info['sha256']
        assert len(lab.read_jsonl(OUT / info['path'])) == info['rows']
    cases = lab.read_jsonl(OUT / report['artifacts']['cases']['path'])
    observations = lab.read_jsonl(OUT / report['artifacts']['observations']['path'])
    indexed = {r['unit_id']: r for r in observations}
    assert len(indexed) == len(observations)
    replayed = []
    for case in cases:
        rows, actual = replay_observations(case, props)
        assert all(actual[key] == case[key] for key in actual), case['case_id']
        replayed.extend(rows)
    assert_observations_match(replayed, observations)
    for group in lab.read_jsonl(OUT / report['artifacts']['classifications']['path']):
        rows = [r for r in observations if (r['track'], r['phase']) == (group['track'], group['phase'])]
        assert lab.evaluate_views(rows, report['models'][group['track']]) == group['metrics']
        assert lab.reference_metrics(rows, props) == group['reference_propositions']
        assert group['metrics']['linear_097']['same_predictions_as_raw']
    for group in lab.read_jsonl(OUT / report['artifacts']['transfers']['path']):
        rows = [r for r in observations if (r['track'], r['phase']) == (group['evaluation_track'], group['phase'])]
        assert lab.evaluate_views(rows, report['models'][group['training_track']]) == group['metrics']
    assert any(r['reference_hits']['P2']['antecedent'] for r in observations)
    assert any(not r['reference_hits']['P2']['antecedent'] for r in observations)
    assert report['real_sample_increment'] == 0 and not report['independent_confirmation']
    assert len(report['skill_paths']) == 28
    assert all(p['complete'] and len(p['years']) == 14 for p in report['skill_paths'])
    assert report['real_evaluation']['status'].startswith('not-run')
    assert (OUT / 'report.md').read_text() == lab.render(report)
