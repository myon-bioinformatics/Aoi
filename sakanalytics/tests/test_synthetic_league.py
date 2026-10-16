from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import pytest
from synthetic_league import (InfeasibleScenario,expand,experiment,plan,validate_games,validate_plan,period_experiment,validate_period,calibration_mean,_flow)


@pytest.mark.parametrize('profile',['aligned','same_totals','reversed'])
@pytest.mark.parametrize('leagues',[1,2])
def test_annual_first_then_games_exactly_match_every_team_stat(profile,leagues):
    p=plan(seed=19,profile=profile,leagues=leagues)
    frozen=deepcopy(p)
    assert validate_plan(p)
    games=expand(p)
    assert p==frozen
    assert len(p['annual'])==6*leagues
    assert all(r['synthetic'] is True for r in p['annual'])
    assert all(r['G']==(143 if leagues==2 else 125) for r in p['annual'])
    # Independent scoreboard, not the generator's aggregate helper.
    actual={r['team']:Counter() for r in p['annual']}
    for g in games:
        for t,rf,ra in [(g['home'],g['hs'],g['as']),(g['away'],g['as'],g['hs'])]:
            actual[t]['G']+=1;actual[t]['RF']+=rf;actual[t]['RA']+=ra
            actual[t]['W' if rf>ra else 'L' if rf<ra else 'T']+=1
    for r in p['annual']:
        for col in ('G','W','L','T','RF','RA'):assert actual[r['team']][col]==r[col]
    assert sum(r['W'] for r in p['annual'])==sum(r['L'] for r in p['annual'])
    assert sum(r['RF'] for r in p['annual'])==sum(r['RA'] for r in p['annual'])
    assert all(abs(r['expected_schedule_wins']-r['W'])<1 for r in p['annual'])


def test_same_annual_run_totals_admit_different_feasible_win_records():
    a=plan(seed=0,profile='same_totals',conversion=1)
    b=plan(seed=0,profile='same_totals',conversion=-1)
    assert [(r['RF'],r['RA'],r['pythag_fixed']) for r in a['annual']]==[(r['RF'],r['RA'],r['pythag_fixed']) for r in b['annual']]
    assert [r['W'] for r in a['annual']]!=[r['W'] for r in b['annual']]
    assert validate_games(a,expand(a)) and validate_games(b,expand(b))


def test_seed_reproducibility_and_explicit_synthetic_identity():
    p=plan(seed=71)
    assert p==plan(seed=71)
    assert expand(p)==expand(p)
    assert all(g['synthetic'] is True for g in expand(p))
    assert p['synthetic'] is True


@pytest.mark.parametrize('profile',['aligned','same_totals','reversed'])
def test_minimum_pair_counts_and_zero_score_draws_are_valid(profile):
    p=plan(seed=0,profile=profile,within=3,inter=3,mean_runs=1,conversion=0)
    games=expand(p)
    assert validate_games(p,games)
    assert any(g['hs']==g['as']==0 for g in games)


def test_season_labels_are_part_of_the_game_witness():
    from synthetic_league import _season_witness
    p=plan();games=_season_witness(p,2013)
    games[0]['season']=2012
    with pytest.raises(ValueError,match='season'):validate_games(p,games)


def test_impossible_annual_constraints_are_not_silently_relaxed():
    p=plan()
    targets={r['team']:r['W'] for r in p['annual']}
    targets['C1']+=1
    with pytest.raises(InfeasibleScenario,match='conserve'):plan(win_quotas=targets)
    targets['C1']=-1
    with pytest.raises(InfeasibleScenario):plan(win_quotas=targets)


def test_balanced_but_pairwise_unrealizable_constraints_fail_maxflow():
    # Totals pass, but the top three demand 330 wins and can collectively win at
    # most 75 internal + 225 external games, even before accounting for draws.
    decisive=sum(r['W'] for r in plan(leagues=1)['annual'])
    low,extra=divmod(decisive-330,3)
    targets={f'C{i}':(110 if i<=3 else low+int(i-4<extra)) for i in range(1,7)}
    assert sum(targets.values())==decisive
    with pytest.raises(InfeasibleScenario,match='no pair allocation'):plan(leagues=1,win_quotas=targets)


@pytest.mark.parametrize('change',['annual','margin','duplicate_pair','game_score','duplicate_game','expectation','ranking'])
def test_corruption_is_rejected(change):
    p=plan(seed=3);games=expand(p)
    if change=='annual':p['annual'][0]['RF']+=1
    if change=='margin':p['pairs'][0]['margin_a']=0
    if change=='duplicate_pair':p['pairs'].append(deepcopy(p['pairs'][0]))
    if change=='game_score':games[0]['hs']+=1
    if change=='duplicate_game':games.append(dict(games[0]))
    if change=='expectation':p['annual'][0]['pythag_expected_wins']+=1
    if change=='ranking':p['annual'][0]['rank']+=1
    with pytest.raises(ValueError):
        if change in ['annual','margin','duplicate_pair','expectation','ranking']:validate_plan(p)
        else:validate_games(p,games)


def test_conditional_counts_are_separate_model_checks_not_real_samples():
    r=experiment(range(3))
    assert r['synthetic'] is True
    assert len(r['cases'])==9
    for group in r['groups']:
        assert group['year_passed']==group['game_passed']==group['cases']==3
        assert sum(group['counts'].values())==3*12
    matched=next(g for g in r['groups'] if g['profile']=='same_totals')
    assert matched['p_upper_given_pythag_at_least_half']==.5


def test_cli_without_site_packages(tmp_path):
    out=tmp_path/'synthetic.json'
    witnesses=tmp_path/'witnesses'
    subprocess.run([sys.executable,'-S',str(Path(__file__).parents[1]/'synthetic_league.py'),'--seeds','1','--out',str(out),'--witness-dir',str(witnesses)],check=True)
    assert len(json.loads(out.read_text())['cases'])==42
    assert len(json.loads((witnesses/'manifest.json').read_text())['files'])==84
    for path in witnesses.glob('*.annual.json'):
        p=json.loads(path.read_text())
        games=[json.loads(line) for line in path.with_name(path.name.replace('.annual.json','.games.jsonl')).read_text().splitlines()]
        assert validate_games(p,games)


@pytest.fixture(scope='module')
def primary_period():
    return period_experiment()


def test_complete_14_year_period_is_the_acceptance_unit(primary_period):
    assert validate_period(primary_period)
    assert len(primary_period['cases']) == 3*14
    for group in primary_period['groups']:
        assert group['period_passed'] == group['period_cases'] == 1
        assert group['year_passed'] == group['game_passed'] == 14
    assert all({r['season'] for r in c['annual']} == {c['season']} for c in primary_period['cases'])
    assert len(primary_period['negative_controls']) == 42


@pytest.mark.parametrize('change', ['missing_year', 'duplicate_year', 'old_year', 'failed_check', 'missing_control', 'accepted_control'])
def test_partial_or_historical_data_cannot_satisfy_period(primary_period, change):
    r = deepcopy(primary_period)
    if change == 'missing_year':r['cases'].pop()
    if change == 'duplicate_year':r['cases'][-1]['season'] = 2013
    if change == 'old_year':r['cases'][-1]['season'] = 2012
    if change == 'failed_check':r['cases'][-1]['game_check'] = False
    if change == 'missing_control':r['negative_controls'].pop()
    if change == 'accepted_control':r['negative_controls'][-1]['rejected'] = False
    with pytest.raises(ValueError):validate_period(r)


@pytest.mark.parametrize('field,value', [('annual',[]),('games',0),('games_sha256','0'*64),
                                      ('seed',999),('conditional_counts',{}),('profile','other')])
def test_saved_period_cases_are_replayed_instead_of_trusting_success(primary_period,field,value):
    r=deepcopy(primary_period)
    r['cases'][0][field]=value
    with pytest.raises(ValueError):validate_period(r)


def test_saved_period_group_totals_and_control_seeds_are_replayed(primary_period):
    r=deepcopy(primary_period);r['groups'][0]['period_passed']=100
    with pytest.raises(ValueError,match='replay'):validate_period(r)
    r=deepcopy(primary_period);r['negative_controls'][0]['seed']+=1
    with pytest.raises(ValueError,match='replay'):validate_period(r)


@pytest.mark.parametrize('change',['identity','league','pair_missing','pair_count'])
def test_declared_family_membership_and_schedule_cannot_drift(change):
    p=plan()
    if change=='identity':p['annual'][0]['synthetic']=False
    if change=='league':p['annual'][0]['league']='P'
    if change=='pair_missing':p['pairs'].pop()
    if change=='pair_count':p['within']+=1
    with pytest.raises(ValueError):validate_plan(p)


def test_game_pair_budgets_are_checked_even_when_every_annual_total_is_unchanged():
    p=plan(seed=8);games=expand(p)
    # A balanced four-edge cycle leaves each team's W/L/T/RF/RA intact.
    for pair,delta in [(('C1','C2'),1),(('C2','C3'),-1),(('C3','C4'),1),(('C1','C4'),-1)]:
        g=next(g for g in games if tuple(sorted((g['home'],g['away'])))==pair and min(g['hs'],g['as'])>=1)
        g['hs']+=delta;g['as']+=delta
    with pytest.raises(ValueError,match='pair budget'):validate_games(p,games)


def test_maxflow_feasibility_matches_exhaustive_small_graph():
    from itertools import product
    pairs=[('a','b',2),('a','c',1),('b','c',1)]
    possible=set()
    for ab,ac,bc in product(range(3),range(2),range(2)):
        possible.add((ab+ac,2-ab+bc,2-ac-bc))
    for quotas in product(range(5),repeat=3):
        if quotas in possible:
            allocation=_flow(dict(zip('abc',quotas)),pairs)
            assert all(a+b==n for (a,b),(_,_,n) in zip(allocation,pairs))
            actual=Counter()
            for (a,b,_),(wa,wb) in zip(pairs,allocation):actual[a]+=wa;actual[b]+=wb
            assert tuple(actual[t] for t in 'abc')==quotas
        else:
            with pytest.raises(InfeasibleScenario):_flow(dict(zip('abc',quotas)),pairs)


@pytest.fixture
def calibration_rows():
    return [dict(season=y,league=lg,team=f'{lg}{i}',RF=400,G=100) for y in range(2013,2027) for lg in ('C','P') for i in range(6)]


@pytest.mark.parametrize('change',['missing','duplicate','history','synthetic','bad_games','bad_runs'])
def test_calibration_requires_complete_distinct_real_primary_rows(calibration_rows,change):
    rows=calibration_rows
    assert calibration_mean(rows)==4
    if change=='missing':rows.pop()
    if change=='duplicate':rows[-1]=dict(rows[-2])
    if change=='history':rows.append(dict(rows[0],season=2012))
    if change=='synthetic':rows[0]['synthetic']=True
    if change=='bad_games':rows[0]['G']=0
    if change=='bad_runs':rows[0]['RF']=-1
    with pytest.raises(ValueError):calibration_mean(rows)
