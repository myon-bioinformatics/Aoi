from copy import deepcopy
import pytest
from annual_audit import audit


def observations():
    rows=[]
    for lg in ['C','P']:
        for i in range(6):
            for cat,values in [
                ('standings',{'試合':20,'勝利':10,'敗北':10,'引分':0,'勝率':.5}),
                ('batting',{'試合':20,'打数':100,'安打':25,'二塁打':3,'三塁打':1,'本塁打':2,'打率':.25,'得点':100}),
                ('pitching',{'試合':20,'勝利':10,'敗北':10,'投球回アウト':540,'防御率':3.,'失点':100})]:
                rows.append(dict(key=f'1950-{lg}-{i}-{cat}',season=1950,league=lg,team=f'{lg}{i}',team_name=f'{lg}{i}',category=cat,source_kind='archive',values=values))
    return rows


def test_all_exact_invariants_pass_and_input_is_not_repaired():
    data=observations();before=deepcopy(data)
    r=audit(data,expected_years=[1950])
    assert r['failed']==0 and r['passed']==len(r['checks'])
    assert r['team_seasons']==12
    assert all(u['pythag_fixed']==.5 for u in r['annual'])
    assert data==before


def test_cross_source_disagreement_is_explicit_and_not_averaged():
    data=observations()
    st=deepcopy(data[0]);st.update(key=st['key']+'detail',source_kind='detail')
    st['values']['勝利']=9;data.append(st)
    failures=audit(data)['failures']
    assert any(f['check']=='cross_source:standings:勝利' and f['observed']==10 and f['expected']==9 for f in failures)


def test_published_precision_is_exact_after_rounding_not_floating_epsilon():
    data=observations();bat=data[1]['values']
    bat.update(打数=96,打率=.260)
    assert not any(f['check']=='batting_average' for f in audit(data)['failures'])
    bat['打率']=.261
    assert any(f['check']=='batting_average' for f in audit(data)['failures'])


def test_missing_year_and_duplicate_are_not_success():
    assert any(f['check']=='standings_present' for f in audit(observations(),expected_years=[1950,1951])['failures'])
    data=observations();data.append(deepcopy(data[0]))
    with pytest.raises(ValueError):audit(data)


def test_duplicate_table_identity_cannot_be_hidden_by_another_record_key():
    data=observations();duplicate=deepcopy(data[0]);duplicate['key']='another-key';data.append(duplicate)
    with pytest.raises(ValueError,match='identity'):audit(data)


def test_explicit_scope_rejects_reference_observations():
    data=observations();extra=deepcopy(data[0]);extra.update(key='extra',season=1949);data.append(extra)
    assert any(c['check']=='observation_years' for c in audit(data,expected_years=[1950])['failures'])


def test_opponent_row_sums_and_reciprocal_results_are_verified():
    data=observations()
    # Use two official team IDs for a small opponent-table mutation.
    for row in data:
        if row['league']=='C' and row['team'] in ('C0','C1'):
            row['team']='g' if row['team']=='C0' else 'd'
    for row in data:
        if row['category']=='standings' and row['team'] in ('g','d'):
            row['values']['対中' if row['team']=='g' else '対巨']=dict(W=10,L=10,T=0)
    assert audit(data)['failed']==0
    row=next(r for r in data if r['team']=='g' and r['category']=='standings')
    row['values']['対中']['W']+=1
    failed={c['check'] for c in audit(data)['failures']}
    assert {'opponent_sum:standings:W','opponent_reciprocal:standings:W'}<=failed


def test_bad_outs_and_integer_totals_are_detected():
    data=observations();data[0]['values']['試合']=21;data[1]['values']['得点']=101
    failed={f['check'] for f in audit(data)['failures']}
    assert {'G=W+L+T','G:batting','global_RF=RA'}<=failed


def test_observed_extended_ranking_digits_use_explicit_truncation_policy():
    data=observations()
    bat=data[1]
    bat['values'].update(安打=958,打数=4228,打率=.2265)
    bat['raw_values']={'打率':'.2265'}
    r=audit(data)
    c=next(c for c in r['checks'] if c['check']=='batting_average' and c['unit']=='1950/C/C0/archive')
    assert c['ok'] and c['expected']=='0.2265' and c['precision']==4
    assert c['display_policy']=='observed_extended_truncation'
    bat['values']['打率']=.2264
    assert any(c['check']=='batting_average' for c in audit(data)['failures'])


def test_cross_source_expanded_rate_is_compared_at_common_display_precision():
    data=observations()
    batting=data[1]
    batting['values'].update(打数=4228,安打=958,打率=.2265)
    batting['raw_values']={'打率':'.2265'}
    detail=deepcopy(batting);detail.update(key=detail['key']+'detail',source_kind='detail')
    detail['values']['打率']=.227;detail['raw_values']['打率']='.227';data.append(detail)
    r=audit(data)
    cross=next(c for c in r['checks'] if c['check']=='cross_source:batting:打率' and c['unit']=='1950/C/C0')
    assert cross['ok'] and cross['common_precision']==3
    assert cross['raw_observed']=='.2265' and cross['raw_expected']=='.227'


@pytest.mark.parametrize('tampered',[False,True])
def test_cli_checks_manifest_digest_as_well_as_arithmetic(tmp_path,tampered):
    import hashlib,json,subprocess,sys
    from pathlib import Path
    source=tmp_path/'observations.jsonl'
    source.write_text(''.join(json.dumps(r)+'\n' for r in observations()))
    source.with_suffix('.manifest.json').write_text(json.dumps(dict(unknown=0,sha256='0'*64 if tampered else hashlib.sha256(source.read_bytes()).hexdigest())))
    out,annual=tmp_path/'audit.json',tmp_path/'annual.jsonl'
    result=subprocess.run([sys.executable,'-S',str(Path(__file__).parents[1]/'annual_audit.py'),'--observations',str(source),'--years','1950-1950','--out',str(out),'--annual-out',str(annual)],capture_output=True)
    assert result.returncode==int(tampered)
    report=json.loads(out.read_text())
    assert report['failed']==int(tampered)
    if tampered:assert report['failures'][0]['check']=='source_dataset_sha256'
