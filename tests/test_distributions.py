"""Run all five min artifacts together with no source checkout or site packages."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

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
rows = [dict(team='A', season=2025, league='C', upper_half=True, rf_adv=1., ra_adv=-1., vs_lower_wpct=.4),
        dict(team='B', season=2025, league='C', upper_half=False, rf_adv=-1., ra_adv=1., vs_lower_wpct=.6)]
assert saka.discover(rows)['pairs'][0]['units'] == ['A-2025', 'B-2025']
state = pyth.ScoreState()
state.update(3, 1)
state.update(0, 0)
assert (state.metrics()['W'], state.metrics()['T'], state.metrics()['RF']) == (1, 1, 3)
assert pyth.classify({'posthoc': False}).status == 'unknown'
assert pyth.classify({'posthoc': True}).status == 'posthoc'
report = draw.render_report({'title': '<unsafe>', 'frames': {'x': {}}, 'default': 'x'})
assert '&lt;unsafe&gt;' in report
assert draw.class_mark(True) != draw.class_mark(False)
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
