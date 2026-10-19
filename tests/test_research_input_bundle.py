"""Real c001 bundle contracts: no acquisition, publication, or live activation."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest
import polars as pl

ROOT = Path(__file__).resolve().parents[1]
# Integration always uses the imported owner tree. During development the owner
# checkout can be selected without patching Aoi's child subtree.
ENGINE = Path(os.environ.get('AOI_BUNDLE_WORKER', ROOT / 'nagoyaction/inbox/worker.py'))
spec = importlib.util.spec_from_file_location('bundle_worker', ENGINE)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
from research_loop.exploration import Explorer, plan


@pytest.fixture
def selected(tmp_path):
    root = tmp_path / 'aoi'
    cycle = root / 'cycles/c001-chunichi'
    shutil.copytree(ROOT / 'cycles/c001-chunichi/input-bundles', cycle / 'input-bundles')
    for name in ('analysis.toml', 'propositions.toml', 'sets.toml', 'outputs/season.jsonl'):
        dest = cycle / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'cycles/c001-chunichi' / name, dest)
    for name in ('analysis.toml', 'propositions.toml', 'outputs/season.jsonl'):
        dest = cycle / 'from-cycle-001' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'cycles/c001-chunichi/from-cycle-001' / name, dest)
    return root, cycle


def load(root, cycle):
    bundle = w.resolve_bundle(root, cycle, 'extended-v1')
    return Explorer(cycle, plan('E1', cycle, inputs=bundle), inputs=bundle)


def edit(selected, role, change):
    root, cycle = selected
    bundle = w.resolve_bundle(root, cycle, 'extended-v1')
    path = bundle['paths'][role]
    change(path)
    # Deliberately repin changed files: semantic checks must also reject broken
    # inputs when an editor has updated the manifest hashes.
    manifest = bundle['manifest']
    data = json.loads(manifest.read_text())
    data['sha256'][role] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))


def test_real_c001_validates_every_reference_and_keeps_canonical_bytes(selected):
    root, cycle = selected
    before = {str(p): p.read_bytes() for p in cycle.rglob('*') if p.is_file()}
    explorer = load(root, cycle)
    report = explorer.input_validation
    assert (report['propositions'], report['sets'], report['expressions'], report['rows']) == (210, 32, 31, 168)
    assert explorer.included.height == 156 and explorer.excluded.height == 12
    assert report['excluded_rows'] == 12
    assert report['null_counts']  # explicit unknown observations are retained
    assert len(report['required_columns']) > 100
    assert before == {str(p): p.read_bytes() for p in cycle.rglob('*') if p.is_file()}


@pytest.mark.parametrize('mutation,match', [
    ('canonical_season', 'missing columns'), ('canonical_props', '命題がない'),
    ('canonical_analysis', 'configuration'), ('missing_row_column', 'missing columns'),
    ('missing_all_column', 'missing columns'), ('missing_reference', '命題がない'),
    ('missing_confirmation', 'configuration'), ('exclusion', 'configuration'),
    ('duplicate_unit', 'units mismatch'), ('type', 'incompatible type'),
    ('bool_metric', 'incompatible type'), ('nonfinite', 'nonfinite|JSON|json|TapeError'),
    ('unselected_expression', '集合|unknown|存在|定義'), ('missing_context', 'missing columns'),
])
def test_broken_re_pinned_bundles_fail_before_initial_state(selected, mutation, match):
    root, cycle = selected
    def rewrite_rows(path, fn):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        fn(rows)
        path.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    if mutation.startswith('canonical_'):
        role = {'canonical_season': 'season', 'canonical_props': 'propositions', 'canonical_analysis': 'analysis'}[mutation]
        canonical = {'season': 'outputs/season.jsonl', 'propositions': 'propositions.toml', 'analysis': 'analysis.toml'}[role]
        edit(selected, role, lambda p: shutil.copyfile(cycle / canonical, p))
    elif mutation in ('missing_row_column', 'missing_all_column', 'type', 'duplicate_unit', 'missing_context', 'bool_metric', 'nonfinite'):
        def change(rows):
            if mutation == 'missing_row_column':
                del rows[0]['upper_half']
            elif mutation == 'missing_all_column':
                for row in rows:
                    del row['upper_half']
            elif mutation == 'missing_context':
                # Required by P1 even though E1 does not use it.
                del rows[0]['rank_pythag']
            elif mutation in ('type', 'bool_metric', 'nonfinite'):
                for row in rows:
                    row['rd'] = {'type': 'incompatible', 'bool_metric': True, 'nonfinite': float('nan')}[mutation]
            else:
                rows[0] = rows[1]
        edit(selected, 'season', lambda p: rewrite_rows(p, change))
    elif mutation == 'missing_reference':
        edit(selected, 'sets', lambda p: p.write_text(p.read_text().replace('from = "P147"', 'from = "P9999"')))
    elif mutation == 'unselected_expression':
        edit(selected, 'sets', lambda p: p.write_text(p.read_text().replace('expr = "F52"', 'expr = "NO_SUCH_SET"')))
    elif mutation == 'missing_confirmation':
        edit(selected, 'analysis', lambda p: p.write_text(p.read_text().replace('"P52",', '"P9999",')))
    else:
        edit(selected, 'analysis', lambda p: p.write_text(p.read_text().replace('season = 2020', 'season = 2019')))
    with pytest.raises((ValueError, pl.exceptions.PolarsError), match=match):
        load(root, cycle)


def cli(state, steps):
    env = {k: v for k, v in os.environ.items() if not k.startswith(('GITHUB_', 'AOI_RESEARCH_'))}
    env.update(AOI_RESEARCH_ENABLED='1', AOI_RESEARCH_ACTOR='local-offline-test',
               AOI_RESEARCH_ALLOWED_ACTORS='["local-offline-test"]', GITHUB_REPOSITORY='myon-bioinformatics/Aoi')
    result = subprocess.run([sys.executable, str(ENGINE), 'worker', '--root', str(ROOT),
        '--cycle', 'c001-chunichi', '--input-bundle', 'extended-v1', '--seed', 'E1',
        '--seconds', '30', '--max-steps', str(steps), '--state-dir', str(state)],
        env=env, capture_output=True, text=True, timeout=35)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_real_c001_offline_worker_resumes_without_mixing_or_source_writes(tmp_path):
    cycle = ROOT / 'cycles/c001-chunichi'
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in cycle.rglob('*') if p.is_file()}
    whole, resumed = tmp_path / 'whole', tmp_path / 'resumed'
    report = cli(whole, 5)
    cli(resumed, 2)
    cli(resumed, 3)
    a, b = w.load_checkpoint(whole / 'checkpoint.json'), w.load_checkpoint(resumed / 'checkpoint.json')
    assert a == b and report['cursor'] == 4
    assert a['state']['input_validation']['sets'] == 32
    assert any('coverage' in r for r in a['state']['results'])
    assert all('error' not in r or '空集合の式' in r['error'] for r in a['state']['results'])
    assert all(r['exploratory'] and not r.get('independently_confirmed', False) for r in a['state']['results'])
    assert a['manifest']['input_bundle'] == 'extended-v1'
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in cycle.rglob('*') if p.is_file()}


@pytest.mark.parametrize("corruption", ["hash", "semantic"])
def test_real_cli_rejects_bad_bundle_without_checkpoint(selected, tmp_path, corruption):
    root, cycle = selected
    for folder in ("research_loop", "pythdragoras"):
        shutil.copytree(ROOT / folder, root / folder, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for name in ("uv.lock", "pyproject.toml"):
        shutil.copyfile(ROOT / name, root / name)
    if corruption == "hash":
        p = cycle / "from-cycle-001/analysis.toml"
        p.write_text(p.read_text() + "\n# changed")
    else:
        edit(selected, "sets", lambda p: p.write_text(p.read_text().replace('from = "P147"', 'from = "P9999"')))
    state = tmp_path / "refused"
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "AOI_RESEARCH_"))}
    env.update(AOI_RESEARCH_ENABLED="1", AOI_RESEARCH_ACTOR="local-offline-test",
               AOI_RESEARCH_ALLOWED_ACTORS='["local-offline-test"]', GITHUB_REPOSITORY="myon-bioinformatics/Aoi")
    result = subprocess.run([sys.executable, str(ENGINE), "worker", "--root", str(root),
        "--cycle", "c001-chunichi", "--input-bundle", "extended-v1", "--seed", "E1",
        "--seconds", "30", "--max-steps", "1", "--state-dir", str(state)],
        env=env, capture_output=True, text=True, timeout=35)
    assert result.returncode == 1 and ("hash mismatch" in result.stderr or "P9999" in result.stderr)
    assert not (state / "checkpoint.json").exists()
