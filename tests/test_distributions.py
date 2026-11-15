"""Run all five min artifacts together with no source checkout or site packages, and check the min APIs on domain-neutral examples."""
from copy import deepcopy
import importlib.util
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_min_distributions_are_isolated_and_interoperate(tmp_path):
    manifest = json.loads((ROOT / 'distributions.json').read_text())
    for item in manifest['projects'].values():
        p = ROOT / item['output']
        shutil.copyfile(p, tmp_path / p.name)
    code = r'''
import sys
sys.path.insert(0, '.')
import blueprobe_min as blue
import queryu_min as query
import sakanalytics_min as saka
import dragowing_min as draw
import pythdragoras_min as pyth
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
assert not any(hasattr(draw, n) for n in ['class_mark', 'trajectory_figure', 'heatmap_figure', 'select_items'])
assert not any(name in sys.modules for name in ['cache_core', 'snapshot_source', 'annual_audit', 'figures', 'score_sensitivity'])
assert not any(name in sys.modules for name in ['numpy', 'polars', 'httpx', 'selectolax'])
'''
    out = subprocess.run([sys.executable, '-I', '-S', '-c', code], cwd=tmp_path,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


def test_distribution_generator_rejects_tampered_tool_before_import(tmp_path):
    shutil.copyfile(ROOT / 'distributions.json', tmp_path / 'distributions.json')
    tool = tmp_path / 'untrusted.py'
    tool.write_text("raise RuntimeError('must not execute')\n")
    out = subprocess.run([sys.executable, '-I', '-S', str(ROOT / 'scripts/build_distributions.py'),
                          '--root', str(tmp_path), '--minpy', str(tool), '--check'],
                         capture_output=True, text=True)
    assert out.returncode == 1
    assert 'minpy tool SHA-256 mismatch' in out.stderr
    assert 'must not execute' not in out.stderr
    assert not (tmp_path / 'dist').exists()
    assert (ROOT / 'dist/LICENSE').read_bytes() == (ROOT / 'LICENSE').read_bytes()


@pytest.mark.parametrize('untracked', [False, True])
def test_generator_rejects_changed_transitive_sources(tmp_path, monkeypatch, untracked):
    # A helper in a search directory must be pinned even when it is not the entry.
    import runpy
    api = runpy.run_path(str(ROOT / 'scripts/build_distributions.py'))
    build = api['build']
    monkeypatch.setitem(build.__globals__, 'load_tool', lambda *args: object())
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'entries').mkdir()
    (tmp_path / 'LICENSE').write_text('notice')
    (tmp_path / 'entries/main.py').write_text('import helper\n')
    if not untracked:
        (tmp_path / 'entries/helper.py').write_text('VALUE = 1\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(tmp_path), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'source'], check=True)
    sha = subprocess.check_output(['git', '-C', str(tmp_path), 'rev-parse', 'HEAD'], text=True).strip()
    (tmp_path / 'entries/helper.py').write_text('VALUE = 2\n')
    manifest = {'schema': 'aoi-distributions/1', 'source': sha,
                'python': f'{sys.version_info.major}.{sys.version_info.minor}',
                'tool': {'sha256': ''}, 'license': 'LICENSE',
                'projects': {'demo': {'entry': 'entries/main.py', 'prefix': 'child',
                                     'paths': ['entries'], 'output': 'dist/demo_min.py'}}}
    with pytest.raises(ValueError, match='distribution source'):
        build(tmp_path, manifest, tmp_path / 'tool.py', check=True)


def test_omit_from_bundle_hides_files_from_minpy_and_keeps_the_checkout(tmp_path, monkeypatch):
    import runpy
    api = runpy.run_path(str(ROOT / 'scripts/build_distributions.py'))
    build = api['build']
    seen = {}

    class Tool:
        @staticmethod
        def bundle(*, root, entry, repository, commit, search_paths, require_clean):
            root = Path(root)
            seen['hidden'] = (root / 'pkg' / 'external.py').exists()
            seen['entry'] = (root / entry).is_file()
            seen['require_clean'] = require_clean
            return 'bundle'

        @staticmethod
        def parse_header(text):
            return {'allow': []}

    monkeypatch.setitem(build.__globals__, 'load_tool', lambda *args: Tool)
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'pkg').mkdir()
    (tmp_path / 'LICENSE').write_text('notice')
    (tmp_path / 'pkg' / 'api.py').write_text('VALUE = 1\n')
    (tmp_path / 'pkg' / 'external.py').write_text('import selectolax\n')
    subprocess.run(['git', '-C', str(tmp_path), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(tmp_path), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'source'], check=True)
    sha = subprocess.check_output(['git', '-C', str(tmp_path), 'rev-parse', 'HEAD'], text=True).strip()
    manifest = {'schema': 'aoi-distributions/1', 'source': sha,
                'python': f'{sys.version_info.major}.{sys.version_info.minor}',
                'tool': {'sha256': ''}, 'license': 'LICENSE',
                'projects': {'demo': {'entry': 'pkg/api.py', 'prefix': 'pkg', 'paths': ['pkg'],
                                     'omit_from_bundle': ['pkg/external.py'],
                                     'output': 'dist/demo_min.py'}}}
    build(tmp_path, manifest, tmp_path / 'tool.py', check=False)
    assert seen == {'hidden': False, 'entry': True, 'require_clean': False}
    assert (tmp_path / 'pkg' / 'external.py').is_file()
    assert (tmp_path / 'dist' / 'demo_min.py').read_text() == 'bundle'


@pytest.mark.parametrize('omit,kind,match', [
    ('pkg/external.py', 'file', 'omit_from_bundle must be a list of relative paths'),
    ([1], 'file', 'omit_from_bundle must be a list of relative paths'),
    (['pkg/absent.py'], 'file', 'omit_from_bundle entry is missing'),
    (['pkg/link.py'], 'symlink-inside', 'omit_from_bundle entry is missing'),
    (['pkg/escape.py'], 'symlink-outside', 'omit_from_bundle escapes the snapshot'),
])
def test_omit_from_bundle_rejects_bad_entries(tmp_path, monkeypatch, omit, kind, match):
    import runpy
    api = runpy.run_path(str(ROOT / 'scripts/build_distributions.py'))
    build = api['build']

    class Tool:
        @staticmethod
        def bundle(**kwargs):
            raise AssertionError('minpy must not run when omit_from_bundle is invalid')

        @staticmethod
        def parse_header(text):
            return {'allow': []}

    monkeypatch.setitem(build.__globals__, 'load_tool', lambda *args: Tool)
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    package = tmp_path / 'pkg'
    package.mkdir()
    (tmp_path / 'LICENSE').write_text('notice')
    (package / 'api.py').write_text('VALUE = 1\n')
    (package / 'external.py').write_text('import selectolax\n')
    if kind == 'symlink-inside':
        (package / 'link.py').symlink_to('api.py')
    elif kind == 'symlink-outside':
        outside = tmp_path.parent / 'omit-outside.txt'
        outside.write_text('outside')
        (package / 'escape.py').symlink_to(outside)
    subprocess.run(['git', '-C', str(tmp_path), 'add', '.'], check=True)
    subprocess.run(['git', '-C', str(tmp_path), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'source'], check=True)
    sha = subprocess.check_output(['git', '-C', str(tmp_path), 'rev-parse', 'HEAD'], text=True).strip()
    manifest = {'schema': 'aoi-distributions/1', 'source': sha,
                'python': f'{sys.version_info.major}.{sys.version_info.minor}',
                'tool': {'sha256': ''}, 'license': 'LICENSE',
                'projects': {'demo': {'entry': 'pkg/api.py', 'prefix': 'pkg', 'paths': ['pkg'],
                                     'omit_from_bundle': omit,
                                     'output': 'dist/demo_min.py'}}}
    with pytest.raises(ValueError, match=match):
        build(tmp_path, manifest, tmp_path / 'tool.py', check=True)
    assert (package / 'external.py').is_file()


# ---- Domain-neutral examples and independent numerical references for min APIs.（旧 tests/test_distribution_kernels.py）

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
