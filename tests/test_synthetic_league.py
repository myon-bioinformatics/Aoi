from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import pytest
from synthetic_league import (InfeasibleScenario,expand,experiment,plan,validate_games,validate_plan,period_experiment,validate_period)


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
