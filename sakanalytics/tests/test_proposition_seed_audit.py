import hashlib
import json
import os
from pathlib import Path
import shutil
import warnings

import pytest

import proposition_seed_audit as audit

import aoi_paths

ROOT = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
CYCLE = aoi_paths.resolve_cycle_path(ROOT)
OUT=CYCLE/'outputs/exploratory/proposition-evaluation'


def _source_hash_report_only():
    """SOURCE_HASH_CHECK=report のときだけ警告で続ける。未設定やそれ以外は失敗する。"""
    return os.environ.get('SOURCE_HASH_CHECK') == 'report'


def _finish_source_hash(problems):
    if not problems:
        return
    text = '\n'.join(problems)
    if _source_hash_report_only():
        warnings.warn(text, UserWarning, stacklevel=3)
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            print('::warning::' + ' '.join(text.split()))
        return
    raise AssertionError(text)


def _recorded_source_sha(out, artifact, field, recorded, source):
    """記録の生成元ハッシュを確かめる。記録は書き換えない（自動で基準を更新しない）。

    今のファイルが記録と同じなら、それで終わり。違うなら、source-divergence.json に
    その差（記録時のハッシュ → 今のハッシュ、生成物は作り直していない）が書いてあることを求める。
    pull_request の CI は SOURCE_HASH_CHECK=report を渡し、不一致を警告にする。
    """
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    path = out / 'source-divergence.json'
    rows = json.loads(path.read_text(encoding='utf-8'))['source_divergence'] if path.exists() else []
    rel = source.relative_to(ROOT).as_posix()
    matching = [r for r in rows if r['path'] == rel and r['field'] == field]
    problems = []
    if len(matching) > 1:
        problems.append(f'{rel}: multiple source-divergence rows for {field}')
    elif current == recorded:
        if matching:
            problems.append(f'{rel}: divergence recorded but the file matches the evidence')
    elif not matching:
        problems.append(
            f'{rel}: SHA-256 drift in {artifact} {field}; review provenance, never auto-rebaseline')
    else:
        row = matching[0]
        if row['evidence_sha256'] != recorded or row['current_sha256'] != current:
            problems.append(f'{rel}: source-divergence row does not match {artifact} {field}')
        if row['artifacts_regenerated'] is not False or row['inputs_regenerated'] is not False:
            problems.append(f'{rel}: source-divergence must keep artifacts_regenerated and inputs_regenerated false')
        reason = row['reason']
        if not isinstance(reason, str) or not reason.strip():
            problems.append(f'{rel}: source-divergence reason is empty')
    _finish_source_hash(problems)


def _divergence_row(source, recorded, current):
    return {
        'source_divergence': [{
            'path': source.relative_to(ROOT).as_posix(),
            'field': 'analysis_sha256',
            'evidence_sha256': recorded,
            'current_sha256': current,
            'artifacts_regenerated': False,
            'inputs_regenerated': False,
            'reason': 'explained drift',
        }],
    }


def test_source_hash_check_fails_closed_unless_report(tmp_path, monkeypatch):
    source = ROOT / 'sakanalytics/proposition_seed_audit.py'
    recorded = '0' * 64
    monkeypatch.delenv('SOURCE_HASH_CHECK', raising=False)
    with pytest.raises(AssertionError, match='SHA-256 drift'):
        _recorded_source_sha(tmp_path, 'seed-evaluation.json', 'analysis_sha256', recorded, source)
    monkeypatch.setenv('SOURCE_HASH_CHECK', 'strict')
    with pytest.raises(AssertionError, match='SHA-256 drift'):
        _recorded_source_sha(tmp_path, 'seed-evaluation.json', 'analysis_sha256', recorded, source)
    monkeypatch.setenv('SOURCE_HASH_CHECK', 'warn')
    with pytest.raises(AssertionError, match='SHA-256 drift'):
        _recorded_source_sha(tmp_path, 'seed-evaluation.json', 'analysis_sha256', recorded, source)
    monkeypatch.setenv('SOURCE_HASH_CHECK', 'report')
    with pytest.warns(UserWarning, match='SHA-256 drift'):
        _recorded_source_sha(tmp_path, 'seed-evaluation.json', 'analysis_sha256', recorded, source)


def test_source_hash_check_accepts_recorded_divergence_and_quiet_match(tmp_path, monkeypatch, recwarn):
    source = ROOT / 'sakanalytics/proposition_seed_audit.py'
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    recorded = 'ab' * 32
    explained = tmp_path / 'explained'
    explained.mkdir()
    (explained / 'source-divergence.json').write_text(
        json.dumps(_divergence_row(source, recorded, current)), encoding='utf-8')
    monkeypatch.delenv('SOURCE_HASH_CHECK', raising=False)
    _recorded_source_sha(explained, 'seed-evaluation.json', 'analysis_sha256', recorded, source)
    assert recwarn.list == []
    quiet = tmp_path / 'quiet'
    quiet.mkdir()
    monkeypatch.setenv('SOURCE_HASH_CHECK', 'report')
    _recorded_source_sha(quiet, 'seed-evaluation.json', 'analysis_sha256', current, source)
    assert recwarn.list == []


def test_ci_resolves_aoi_at_runtime_and_sets_source_hash_mode():
    text = (Path(__file__).resolve().parents[1] / '.github/workflows/ci.yml').read_text(encoding='utf-8')
    assert 'AOI_SHA' not in text
    assert 'e43f7d2087f3928e3e55908b03ae2554879990e1' not in text
    assert 'git ls-remote' in text
    assert 'https://github.com/myon-bioinformatics/Aoi' in text
    assert 'refs/heads/main' in text
    assert '1402862784' in text
    assert 'SOURCE_HASH_CHECK' in text
    assert "github.event_name == 'pull_request' && 'report' || 'strict'" in text
    assert 'schedule:' in text
    assert 'actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7.1.0' in text
    assert 'astral-sh/setup-uv@07a047e608db84b3d8c06cd9a7c7dcc9c355c18e # v10.3.2' in text
    assert 'rev-parse' not in text


def test_replay_seed_registry_from_all_2240_plans():
    actual=audit.build(CYCLE,OUT/'skill-seed-plans.jsonl.gz')
    saved=json.loads((OUT/'seed-evaluation.json').read_text())
    # 生成元のハッシュは Aoi の source-divergence.json だけが説明する。ローカルな上書きはしない。
    source = ROOT/'sakanalytics/proposition_seed_audit.py'
    _recorded_source_sha(OUT, 'seed-evaluation.json', 'analysis_sha256', saved['analysis_sha256'], source)
    assert actual['analysis_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
    assert {**actual, 'analysis_sha256': saved['analysis_sha256']}==saved
    assert actual['plan_count']==2240 and len(actual['propositions'])==114
    assert sum(v['groups'] is not None for v in actual['propositions'].values())==13
    for item in actual['propositions'].values():
        for group in item['groups'] or []:
            condition=group['condition']
            if condition['dataset']=='annual-score-witness':
                expected=[0,1,2] if condition['conversion']==1 else [3]
            else:
                expected=list(range(10))
            assert group['expected_seeds']==expected
            assert [run['seed'] for run in group['runs']]==expected


@pytest.fixture
def annual_input(tmp_path):
    (tmp_path/'outputs').mkdir()
    for name in ('league-laboratory.toml','propositions.toml',
                 'outputs/synthetic_p96_units.jsonl','outputs/synthetic_p96_provenance.json'):
        shutil.copyfile(CYCLE/name,tmp_path/name)
    return tmp_path


def rewrite_annual(cycle, rows):
    """Keep the file SHA valid so coverage checks, rather than hashes, must fail."""
    units=cycle/'outputs/synthetic_p96_units.jsonl'
    units.write_text(''.join(json.dumps(row)+'\n' for row in rows))
    provenance_path=cycle/'outputs/synthetic_p96_provenance.json'
    provenance=json.loads(provenance_path.read_text())
    provenance['files'][units.name]=hashlib.sha256(units.read_bytes()).hexdigest()
    provenance_path.write_text(json.dumps(provenance))


@pytest.mark.parametrize('seed,conversion',[(0,1.),(1,1.),(2,1.),(3,.5)])
@pytest.mark.parametrize('profile',['aligned','same_totals','reversed'])
def test_whole_annual_cohort_missing_with_valid_sha_fails(annual_input,seed,conversion,profile):
    rows=list(map(json.loads,(annual_input/'outputs/synthetic_p96_units.jsonl').read_text().splitlines()))
    remaining=[r for r in rows if (r['batch_seed'],r['profile'],r['conversion'])!=(seed,profile,conversion)]
    assert len(rows)-len(remaining)==168
    rewrite_annual(annual_input,remaining)
    with pytest.raises(ValueError,match='missing or unexpected annual cohorts'):
        audit.build(annual_input,OUT/'skill-seed-plans.jsonl.gz')


@pytest.mark.parametrize('field,value',[('batch_seed',4),('profile','unknown'),('conversion',.5)])
def test_replaced_annual_cohort_with_same_total_and_valid_sha_fails(annual_input,field,value):
    rows=list(map(json.loads,(annual_input/'outputs/synthetic_p96_units.jsonl').read_text().splitlines()))
    changed=0
    for row in rows:
        if (row['batch_seed'],row['profile'],row['conversion'])==(0,'aligned',1.):
            row[field]=value
            changed+=1
    assert changed==168 and len(rows)==2016
    rewrite_annual(annual_input,rows)
    with pytest.raises(ValueError,match='missing or unexpected annual cohorts'):
        audit.build(annual_input,OUT/'skill-seed-plans.jsonl.gz')


@pytest.mark.parametrize('units',[None,0,1848,2016.,True])
def test_provenance_must_declare_fixed_2016_units(annual_input,units):
    path=annual_input/'outputs/synthetic_p96_provenance.json'
    provenance=json.loads(path.read_text())
    provenance['units']=units
    path.write_text(json.dumps(provenance))
    with pytest.raises(ValueError,match='annual provenance must declare exactly 2016 units'):
        audit.build(annual_input,OUT/'skill-seed-plans.jsonl.gz')


@pytest.mark.parametrize('change',['missing','duplicate'])
def test_annual_row_count_matches_declared_units(annual_input,change):
    rows=list(map(json.loads,(annual_input/'outputs/synthetic_p96_units.jsonl').read_text().splitlines()))
    if change=='missing':
        rows.pop()
    else:
        rows.append(rows[0].copy())
    rewrite_annual(annual_input,rows)
    with pytest.raises(ValueError,match='annual unit count differs from declared provenance'):
        audit.build(annual_input,OUT/'skill-seed-plans.jsonl.gz')


def test_cli_takes_cycle_dir_without_resolving_aoi_paths():
    text = Path(audit.__file__).read_text(encoding='utf-8')
    assert 'aoi_layout' not in text and 'aoi_paths' not in text
    with pytest.raises(SystemExit) as caught:
        audit.main([])
    assert caught.value.code == 2


def test_missing_features_and_real_team_scope_are_explicit():
    p=dict(scope=dict(team='d'),then=[dict(col='inning_size',op='<',value=0)])
    got=audit.support(p,{'RF','RA','upper_half'})
    assert got['missing_features']==['inning_size'] and got['needs_identity_adapter']
    assert not got['supported']
