import hashlib
import json
from pathlib import Path
import shutil

import pytest

import proposition_seed_audit as audit

import aoi_paths

ROOT = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
CYCLE = aoi_paths.resolve_cycle_path(ROOT)
OUT=CYCLE/'outputs/exploratory/proposition-evaluation'


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
