import hashlib
import json
from pathlib import Path
import shutil

import pytest

import proposition_seed_audit as audit

ROOT=Path(__file__).resolve().parents[2]
CYCLE=ROOT/'cycles/c001-chunichi'
OUT=CYCLE/'outputs/exploratory/proposition-evaluation'


def test_replay_seed_registry_from_all_2240_plans():
    actual=audit.build(CYCLE,OUT/'skill-seed-plans.jsonl.gz')
    saved=json.loads((OUT/'seed-evaluation.json').read_text())
    assert actual==saved
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


def test_missing_features_and_real_team_scope_are_explicit():
    p=dict(scope=dict(team='d'),then=[dict(col='inning_size',op='<',value=0)])
    got=audit.support(p,{'RF','RA','upper_half'})
    assert got['missing_features']==['inning_size'] and got['needs_identity_adapter']
    assert not got['supported']
