"""Copy the reusable single files (no bundling) into an empty directory, run them together with no source checkout or site packages, and check the min APIs on domain-neutral examples (docs/distributions.md)."""
from copy import deepcopy
import importlib.util
import math
from pathlib import Path
import random
import shutil
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_reusable_files_are_isolated_and_interoperate(tmp_path):
    # 📄 束ねずに元のファイルをそのまま写す（docs/distributions.md の表と同じ一覧）
    for rel in ('blueprobe/blueprobe.py', 'dragowing/dragowing.py', 'queryu/core/cache_core.py',
                'pythdragoras/core/registration_audit.py', *(f'distributions/entries/{n}.py' for n in (
                    'period_comparison', 'neighbor_comparison', 'score_math', 'sakanalytics_api', 'pythdragoras_api'))):
        shutil.copyfile(ROOT / rel, tmp_path / Path(rel).name)
    code = r'''
import sys
sys.path.insert(0, '.')
import blueprobe as blue
import cache_core as query
import sakanalytics_api as saka
import dragowing as draw
import pythdragoras_api as pyth
from pathlib import Path
assert blue.normalize('Ａ\0 B') == 'A� B'
c = query.Cache(Path('cache'))
e = c.put('one', 'https://example.invalid/one', 'group', 200, b'<p>raw</p>', {})
assert e['code_version'] is None
snap = c.snapshot(e)
assert snap['html'] == '<p>raw</p>' and snap['response_sha256'] == e['sha256']
class Parser:
    def parse(self, html, url):
        return blue.new_report()
assert blue.inspect_queryu_cache(Parser(), c)
p = c.root / e['file']
p.write_bytes(b'corrupt')
try:
    c.snapshot(e)
except query.CacheIntegrityError:
    pass
else:
    raise AssertionError('corrupt cache accepted')
rows = [dict(sensor='north', year=2024, energy=10),
        dict(sensor='north', year=2025, energy=12)]
comparison = saka.compare_periods(rows, entity='sensor', period='year', metrics=['energy'], before=2024, after=2025)
assert comparison['comparisons'][0]['metrics']['energy']['delta'] == 2
assert saka.discover([{'id':'a', 'latency':10}, {'id':'b', 'latency':12}], identifier='id', features=['latency'])['pairs'][0]['units'] == ['a', 'b']
curve = pyth.threshold_curve([.1, .4, .9], [False, True, True], [.2, .4, 1.])
assert curve[1]['mcc'] == 1. and curve[2]['mcc'] is None
assert pyth.shape(curve)['covered_span'] == .4-.2
assert not any(hasattr(saka, n) for n in ['FEATURES', 'audit_annual'])
assert not any(hasattr(pyth, n) for n in ['ScoreState', 'team_games', 'analyze'])
assert pyth.classify({'posthoc': False}).status == 'unknown'
assert pyth.classify({'posthoc': True}).status == 'posthoc'
report = draw.render_report({'title': '<unsafe>', 'frames': {'x': {}}, 'default': 'x'})
assert '&lt;unsafe&gt;' in report
assert draw.series_figure([1, 2], [3, None])['data'][0]['connectgaps'] is False
assert draw.matrix_figure(['p'], ['q'], [[4]])['data'][0]['z'] == [[4]]
assert not any(name in sys.modules for name in ['snapshot_source', 'annual_audit', 'figures', 'score_sensitivity'])
assert not any(name in sys.modules for name in ['numpy', 'polars', 'httpx', 'selectolax'])
'''
    out = subprocess.run([sys.executable, '-I', '-S', '-c', code], cwd=tmp_path,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


# ---- Domain-neutral examples and independent numerical references for min APIs.（旧 tests/test_distribution_kernels.py）

@pytest.fixture
def api(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'distributions/entries'))
    import period_comparison, neighbor_comparison, score_math
    import dragowing.dragowing as plot_specs  # series_figure・matrix_figure は dragowing.py（旧 plot_specs）
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
    spec = importlib.util.spec_from_file_location('_original_season_math', ROOT / 'pythdragoras/npb/season_sensitivity.py')
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
