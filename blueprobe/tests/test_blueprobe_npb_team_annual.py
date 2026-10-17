"""Real team-table fixtures plus adversarial layouts; no live HTTP in tests."""
import hashlib
import json
from pathlib import Path
import pytest
from npb_team_annual import parse, pages

ROOT=Path(__file__).parent/'fixtures/npb_annual'


def fixture(name):
    provenance=json.loads((ROOT/'provenance.json').read_text())
    meta=next(r for r in provenance if r['file']==name+'.html')
    p=ROOT/meta['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['fixture_sha256']
    return p.read_text(),meta['source_url']


@pytest.mark.parametrize('name,expected', [('1950_c_archive',24),('2005_c_std',12),('2005_c_tmb',6),('2005_c_tmp',6),('2005_c_tmf',6),('2026_c_tmf',6)])
def test_real_complete_tables_are_read_without_individual_rows(name,expected):
    r=parse(*fixture(name))
    assert not r['unknown']
    assert len(r['records'])==expected
    assert all(u['category'] in {'standings','interleague','batting','pitching','fielding'} for u in r['records'])
    assert len({u['key'] for u in r['records']})==expected
    assert all(u['headers'] and u['raw_cells'] and u['source_url'] for u in r['records'])


def test_2005_chunichi_full_batting_and_historical_yokohama_identity():
    records=parse(*fixture('2005_c_tmb'))['records']
    d=next(r for r in records if r['team']=='d')['values']
    assert (d['試合'],d['得点'],d['安打'],d['本塁打'],d['打席'])==(146,680,1323,139,5610)
    assert len(d)==22
    assert any(r['team']=='db' for r in records)


def test_innings_split_is_integer_outs_not_decimal_arithmetic():
    rows=parse(*fixture('2005_c_tmp'))['records']
    t=next(r for r in rows if r['team']=='t')['values']
    assert t['投球回']=='1326.1' and t['投球回アウト']==3979
    assert t['ホールド']==104
    s=next(r for r in rows if r['team']=='s')['values']
    assert s['投球回アウト']==1293*3


def test_fielding_multilevel_header_keeps_both_doubleplay_columns():
    rows=parse(*fixture('2005_c_tmf'))['records']
    d=next(r for r in rows if r['team']=='d')['values']
    assert (d['守備機会'],d['併殺/参加'],d['併殺/球団'])==(5569,396,145)


def test_old_unrecorded_saves_are_null_and_eight_teams_are_not_forced_to_six():
    rows=parse(*fixture('1950_c_archive'))['records']
    assert len([r for r in rows if r['category']=='standings'])==8
    assert all(r['values']['セーブ'] is None for r in rows if r['category']=='pitching')
    assert any(r['team']=='historical:松竹ロビンス' for r in rows)


def test_new_header_or_empty_page_is_visible_not_silently_accepted():
    html,url=fixture('2005_c_tmb')
    r=parse(html.replace('出<br>塁<br>率','新指標'),url)
    assert r['unknown']
    assert parse('',url)['unknown']


def test_personal_table_cannot_be_mistaken_for_a_team_table():
    html,url=fixture('2005_c_tmb')
    personal='<table><tr><th>順位</th><th>選手</th><th>打率</th></tr><tr><td>1</td><td>個人</td><td>.400</td></tr></table>'
    assert parse(html+personal,url)==parse(html,url)


def test_unknown_inning_fraction_is_rejected():
    html,url=fixture('2005_c_tmp')
    assert parse(html.replace('>.1<','>.7<'),url)['unknown']


def test_source_scope_covers_both_leagues_and_available_detail_years():
    assert len(pages([1950]))==2
    assert len(pages([2005]))==10
    with pytest.raises(ValueError):pages([1949])


def test_split_season_standings_preserve_both_half_ranks():
    r=parse(*fixture('1973_p_archive'))
    assert not r['unknown']
    st=[u for u in r['records'] if u['category']=='standings']
    assert len(st)==6
    assert st[0]['values']['半期順位']=={'first_half':1,'second_half':3}


def test_extended_precision_batting_rate_is_not_rounded_on_read():
    r=parse(*fixture('1961_c_archive'))
    g=next(u for u in r['records'] if u['category']=='batting' and u['team']=='g')
    assert g['raw_values']['打率']=='.2265'
    assert g['values']['打率']==.2265


def test_fractional_count_is_unknown_not_rounded_to_an_integer():
    html,url=fixture('2005_c_tmb')
    assert parse(html.replace('>146<','>146.5<'),url)['unknown']
