"""Domain-neutral examples and independent numerical references for min APIs."""
from copy import deepcopy
import importlib.util
import math
from pathlib import Path
import random

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def api(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'distributions/entries'))
    import period_comparison, neighbor_comparison, score_math, plot_specs
    return period_comparison, neighbor_comparison, score_math, plot_specs


def test_periods_preserve_exact_counts_and_report_missing_baselines(api):
    periods, _, _, _ = api
    rows = [{'instrument': 'a', 'year': 2024, 'photons': 2**60},
            {'instrument': 'a', 'year': 2025, 'photons': 2**60+1},
            {'instrument': 'b', 'year': 2024, 'photons': 0},
            {'instrument': 'b', 'year': 2025, 'photons': 3},
            {'instrument': 'c', 'year': 2025, 'photons': 5},
            {'instrument': 'd', 'year': 2024, 'photons': None},
            {'instrument': 'd', 'year': 2025, 'photons': True}]
    original = deepcopy(rows)
    result = periods.compare_periods(rows, entity='instrument', period='year', metrics=['photons'], before=2024, after=2025)
    a, b, c, d = [r['metrics']['photons'] for r in result['comparisons']]
    assert a['before'] == 2**60 and a['delta'] == 1
    assert b['delta'] == 3 and b['relative_delta'] is None
    assert b['reasons'] == ['relative_delta:zero_baseline']
    assert c['delta'] is None and c['reasons'] == ['before:missing_period']
    assert d['delta'] is None and len(d['reasons']) == 2
    assert rows == original
    with pytest.raises(ValueError, match='duplicate'):
        periods.compare_periods(rows + rows[:1], entity='instrument', period='year', metrics=['photons'], before=2024, after=2025)


def test_neighbors_have_explicit_features_groups_gaps_and_stable_ties(api):
    _, neighbors, _, _ = api
    rows = [{'id': 'a', 'lab': 'x', 'latency': 0, 'constant': 7},
            {'id': 'b', 'lab': 'x', 'latency': 1, 'constant': 7},
            {'id': 'c', 'lab': 'x', 'latency': 2, 'constant': 7},
            {'id': 'd', 'lab': 'y', 'latency': 1, 'constant': 7},
            {'id': 'e', 'lab': 'x', 'latency': None, 'constant': 7},
            {'id': 'f', 'lab': 'x', 'latency': 100, 'constant': 7}]
    original = deepcopy(rows)
    kwargs = dict(identifier='id', features=['latency', 'constant'], group='lab', excluded=['f'])
    got = neighbors.discover(rows, **kwargs)
    assert got == neighbors.discover(list(reversed(rows)), **kwargs)
    assert got['features'] == ['latency']
    assert [p['units'] for p in got['pairs']] == [['a', 'b'], ['b', 'c']]
    assert got['scales']['latency'] == math.sqrt(.5)
    assert got['pairs'][0]['distance'] == pytest.approx(math.sqrt(2))
    assert got['skipped'] == [{'id': 'e', 'reason': 'missing_or_nonfinite_feature'}, {'id': 'f', 'reason': 'excluded'}]
    assert neighbors.discover([{'id':'a', 'v':1}, {'id':'b', 'v':1}], identifier='id', features=['v'])['pairs'] == []
    assert rows == original
    with pytest.raises(ValueError, match='distinct'):
        neighbors.discover(rows + rows[:1], **kwargs)


def test_threshold_sweep_matches_independent_recounts_and_existing_math(api):
    _, _, score, _ = api
    spec = importlib.util.spec_from_file_location('_original_season_math', ROOT / 'pythdragoras/season_sensitivity.py')
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    rng = random.Random(871)
    thresholds = [-5, -2, 0, 1, 2, 4, 6]
    for size in range(25):
        scores = [rng.randrange(-4, 5) for _ in range(size)]
        outcomes = [bool(rng.randrange(2)) for _ in range(size)]
        frozen = (list(scores), list(outcomes), list(thresholds))
        got = score.threshold_curve(scores, outcomes, thresholds)
        assert got == original.threshold_curve(scores, outcomes, thresholds)
        assert score.shape(got) == original.shape(got)
        previous_crossings = 0
        for threshold, point in zip(thresholds, got):
            counts = {key: 0 for key in ('tp', 'fp', 'fn', 'tn')}
            for value, actual in zip(scores, outcomes):
                predicted = value >= threshold
                key = 'tp' if predicted and actual else 'fp' if predicted else 'fn' if actual else 'tn'
                counts[key] += 1
            assert {k: point[k] for k in counts} == counts
            crossings = sum(v < threshold for v in scores)
            assert point['crossed_units'] == crossings - previous_crossings
            previous_crossings = crossings
        # Regardless of the number of thresholds, each observation crosses once.
        assert sum(p['crossed_units'] for p in got) == size
        assert (scores, outcomes, thresholds) == frozen


@pytest.mark.parametrize('scores,outcomes,thresholds', [([1], [1], [0]), ([float('nan')], [True], [0]), ([1], [], [0]), ([1], [True], [0, 0]), ([1], [True], []), ([True], [True], [0])])
def test_invalid_threshold_inputs_are_rejected(api, scores, outcomes, thresholds):
    with pytest.raises(ValueError):
        api[2].threshold_curve(scores, outcomes, thresholds)


def test_shapes_do_not_bridge_missing_values_or_accept_duplicate_abscissae(api):
    score = api[2]
    got = score.shape([{'threshold':0, 'mcc':1}, {'threshold':1, 'mcc':None}, {'threshold':2, 'mcc':3}])
    assert got['covered_span'] == 0 and got['trapezoid_area'] is None
    assert all(s['slope'] is None for s in got['finite_slopes'])
    with pytest.raises(ValueError):
        score.shape([{'threshold':0, 'mcc':1}, {'threshold':0, 'mcc':2}])
    assert score.counts_metrics(0, 0, 0, 0)['mcc'] is None
    with pytest.raises(ValueError):
        score.counts_metrics(-1, 0, 0, 0)


def test_plot_specs_retain_order_gaps_and_caller_data(api):
    draw = api[3]
    data = [[1, None], [3, 4]]
    figure = draw.matrix_figure(['beta', 'alpha'], ['sensor-2', 'sensor-1'], data)
    assert figure['data'][0]['z'] == data
    assert figure['layout']['yaxis']['categoryarray'] == ['sensor-2', 'sensor-1']
    data[0][0] = 100
    assert figure['data'][0]['z'][0][0] == 1
    assert draw.series_figure(['t1', 't2'], [0, None])['data'][0]['connectgaps'] is False
    with pytest.raises(ValueError):
        draw.matrix_figure([1], [2], [[3, 4]])
    with pytest.raises(ValueError):
        draw.series_figure([1], [float('nan')])
