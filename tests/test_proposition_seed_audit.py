import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

import proposition_seed_audit as audit

import aoi_paths

ROOT = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
CYCLE = aoi_paths.resolve_cycle_path(ROOT)
OUT=CYCLE/'outputs/exploratory/proposition-evaluation'
CHILD = Path(__file__).resolve().parents[1]
PENDING_PATH = CHILD / 'expected-source-divergence.json'
# 証跡がソースの SHA-256 を見ている、このリポジトリのファイル。
# ピンした Aoi のコピーとバイトが違うものだけを expected-source-divergence.json に書く。
PROVENANCE_SOURCES = (
    'proposition_seed_audit.py',
    'league_laboratory.py',
    'synthetic_league.py',
)


def _recorded_source_sha(out, artifact, field, recorded, source):
    """記録の生成元ハッシュを確かめる。記録は書き換えない（自動で基準を更新しない）。

    今のファイルが記録と同じなら、それで終わり。違うなら、source-divergence.json に
    その差（記録時のハッシュ → 今のハッシュ、生成物は作り直していない）が書いてあることを求める。
    """
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    path = out / 'source-divergence.json'
    rows = json.loads(path.read_text(encoding='utf-8'))['source_divergence'] if path.exists() else []
    rel = source.relative_to(ROOT).as_posix()
    matching = [r for r in rows if r['path'] == rel and r['field'] == field]
    assert len(matching) <= 1
    if current == recorded:
        assert not matching, f'{rel}: divergence recorded but the file matches the evidence'
        return
    assert matching, f'{rel}: SHA-256 drift in {artifact} {field}; review provenance, never auto-rebaseline'
    row = matching[0]
    assert row['evidence_sha256'] == recorded and row['current_sha256'] == current
    assert row['artifacts_regenerated'] is False and row['inputs_regenerated'] is False
    assert isinstance(row['reason'], str) and row['reason'].strip()


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _running_as_child():
    """単独リポジトリの CI。Aoi に埋め込まれているときはソースとピンが同じツリー。"""
    return ROOT.resolve() != CHILD.resolve().parent


def _workflow_aoi_sha():
    found = []
    for line in (CHILD / '.github/workflows/ci.yml').read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if stripped.startswith('AOI_SHA:'):
            found.append(stripped.split(':', 1)[1].strip())
    assert len(found) == 1
    pinned = found[0]
    assert len(pinned) == 40 and set(pinned) <= set('0123456789abcdef')
    return pinned


def _pinned_aoi_sha():
    pinned = _workflow_aoi_sha()
    head = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == pinned, f'AOI_ROOT HEAD {head} != workflow AOI_SHA {pinned}'
    return pinned


def _pending_manifest():
    if not PENDING_PATH.is_file():
        return None
    data = json.loads(PENDING_PATH.read_text(encoding='utf-8'))
    assert data['schema'] == 'sakanalytics-pending-source-divergence/1'
    assert isinstance(data['updates'], list)
    return data


def _child_source_sha(field, recorded, name):
    """実行したソースと、ピンした Aoi のコピーと、証跡の三つを突き合わせる。

    バイトが同じなら、source-divergence.json の検査だけで終わる。
    このリポジトリだけが進んでいるときは expected-source-divergence.json の1件と
    ハッシュが完全に一致しなければならない。宣言のない差、宣言と違う差、
    もう一致しているのに残った宣言は失敗する。生成物のハッシュは書き換えない。
    """
    child = CHILD / name
    aoi = ROOT / 'sakanalytics' / name
    child_sha = _sha256(child)
    aoi_sha = _sha256(aoi)
    pending = _pending_manifest()
    rows = []
    if pending:
        rows = [row for row in pending['updates'] if row['path'] == f'sakanalytics/{name}' and row['field'] == field]
    assert len(rows) <= 1
    if child_sha == aoi_sha:
        assert not rows, f'{name}: pending divergence is stale; bytes match the pinned Aoi tree'
        return child_sha
    assert _running_as_child(), f'{name}: embedded tree must be one file, hashes differ'
    assert pending is not None and rows, (
        f'{name}: SHA-256 differs from pinned Aoi; declare it in expected-source-divergence.json'
    )
    row = rows[0]
    assert pending['aoi_sha'] == _pinned_aoi_sha()
    assert row['sidecar'].startswith('cycles/') and row['sidecar'].endswith('/source-divergence.json')
    assert row['evidence_sha256'] == recorded
    assert row['aoi_current_sha256'] == aoi_sha
    assert row['child_sha256'] == child_sha
    assert row['child_sha256'] != row['aoi_current_sha256']
    assert row['artifacts_regenerated'] is False and row['inputs_regenerated'] is False
    assert isinstance(row['reason'], str) and 'was not regenerated' in row['reason']
    sidecar = json.loads((ROOT / row['sidecar']).read_text(encoding='utf-8'))
    recorded_rows = [item for item in sidecar['source_divergence']
                     if item['path'] == row['path'] and item['field'] == row['field']]
    assert len(recorded_rows) == 1
    prior = recorded_rows[0]
    assert prior['evidence_sha256'] == row['evidence_sha256']
    assert prior['current_sha256'] == row['aoi_current_sha256']
    assert prior['current_sha256'] != row['child_sha256']
    assert prior['artifacts_regenerated'] is False and prior['inputs_regenerated'] is False
    return child_sha


def test_replay_seed_registry_from_all_2240_plans():
    actual=audit.build(CYCLE,OUT/'skill-seed-plans.jsonl.gz')
    saved=json.loads((OUT/'seed-evaluation.json').read_text())
    # 証跡の analysis_sha256 は記録のまま。ピンした Aoi との差は source-divergence.json、
    # このリポジトリがさらに進んでいる差は expected-source-divergence.json。
    _recorded_source_sha(OUT, 'seed-evaluation.json', 'analysis_sha256', saved['analysis_sha256'],
                         ROOT/'sakanalytics/proposition_seed_audit.py')
    child_sha = _child_source_sha('analysis_sha256', saved['analysis_sha256'], 'proposition_seed_audit.py')
    assert actual['analysis_sha256']==child_sha
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


def test_pending_source_divergence_covers_only_real_drift():
    if not _running_as_child():
        assert not PENDING_PATH.exists()
        return
    assert _pinned_aoi_sha()
    pending = _pending_manifest()
    drifted = []
    for name in PROVENANCE_SOURCES:
        child_sha = _sha256(CHILD / name)
        aoi_sha = _sha256(ROOT / 'sakanalytics' / name)
        if child_sha != aoi_sha:
            drifted.append(f'sakanalytics/{name}')
    assert pending is not None
    listed = [row['path'] for row in pending['updates']]
    assert listed == drifted == ['sakanalytics/proposition_seed_audit.py']
    assert pending['updates'][0]['field'] == 'analysis_sha256'
    assert pending['updates'][0]['sidecar'] == (
        'cycles/c001-chunichi/outputs/exploratory/proposition-evaluation/source-divergence.json')
    _child_source_sha('analysis_sha256',
                      json.loads((OUT / 'seed-evaluation.json').read_text())['analysis_sha256'],
                      'proposition_seed_audit.py')


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
