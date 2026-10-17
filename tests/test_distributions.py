"""Run all five min artifacts together with no source checkout or site packages."""
import json
from pathlib import Path
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
curve = pyth.threshold_curve([.1, .4, .9], [False, True, True], [.1, .4, 1.])
assert curve[1]['mcc'] == 1. and curve[2]['mcc'] is None
assert pyth.shape(curve)['covered_span'] == .4-.1
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
