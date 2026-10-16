import json
from pathlib import Path

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


def test_missing_features_and_real_team_scope_are_explicit():
    p=dict(scope=dict(team='d'),then=[dict(col='inning_size',op='<',value=0)])
    got=audit.support(p,{'RF','RA','upper_half'})
    assert got['missing_features']==['inning_size'] and got['needs_identity_adapter']
    assert not got['supported']
