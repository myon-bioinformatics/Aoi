"""Semantic checks for an optional analysis, not an acceptance gate on accuracy."""
from copy import deepcopy

import pytest

from synthetic_rule_discovery import characterize, discover, features, predictions, score
from synthetic_league import period_experiment


def test_confusion_counts_and_counterexample_identity():
    rows=[dict(unit_id=str(i),upper_half=upper) for i,upper in enumerate([False,True,False,True])]
    r=score(rows,[True,True,False,False])
    assert (r['tp'],r['fp'],r['fn'],r['tn'])==(1,1,1,1)
    assert r['precision']==r['recall']==.5
    assert r['ids']['fp']==['1'] and r['ids']['fn']==['2']
    with pytest.raises(ValueError):score(rows,[True])
    assert score(rows,[False]*4)['precision'] is None


def test_unknown_feature_refuses_silent_negative():
    with pytest.raises(ValueError,match='undetermined'):
        predictions({'if':[dict(col='x',op='<',value=0)]},[{'x':None}])


def test_discovery_refuses_holdout_or_incomplete_training():
    with pytest.raises(ValueError,match='only batch 0'):
        discover([dict(batch_seed=1,profile='reversed')],{})


def test_witness_tampering_refused_before_measurement():
    # The first case fails before the relatively expensive distribution step.
    source=period_experiment()
    broken=deepcopy(source)
    broken['cases'][0]['games_sha256']='0'*64
    with pytest.raises(ValueError,match='witness'):
        features(broken)
    broken=deepcopy(source)
    broken['cases'][0]['annual'][0]['W']+=1
    with pytest.raises(ValueError,match='witness'):
        features(broken)


def test_characterization_retains_null_denominator():
    r=characterize([dict(rd=50,wins_vs_pythag=-2,sim_p_upper=.7,alloc_z_strat=None)])
    assert r['n']==1 and r['features']['alloc_z_strat']['n']==0
    assert r['rd_ge_50']==r['sim_ge_half']==r['wins_below_expectation']==1
