import hashlib
import json
from pathlib import Path
import shutil

import pytest
from annual_history_report import audit_files, require_primary_years, summary
from npb_team_annual import pages, parse
from queryu import Cache
from synthetic_league import period_experiment


def test_primary_report_rejects_mixed_historical_or_missing_years():
    assert require_primary_years(range(2013, 2027)) is None
    for years in (range(1950, 2027), range(2014, 2027), [2012]*14):
        with pytest.raises(ValueError, match='2013-2026'):require_primary_years(years)


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def primary_evidence(tmp_path_factory):
    # Small invented team tables exercise the complete cache -> parse -> audit ->
    # calibration -> report chain, with no network or real-data acceptance claim.
    root=tmp_path_factory.mktemp('annual-evidence')
    cache=Cache(root/'raw')
    rows=[]
    tables={
        'std':(['試合','勝利','敗北','引分','勝率'],['20','10','10','0','.500']),
        'tmb':(['試合','打数','安打','二塁打','三塁打','本塁打','打率','得点'],['20','100','25','3','1','2','.250','80']),
        'tmp':(['試合','勝利','敗北','投球回','防御率','失点'],['20','10','10','16.2','3.00','80']),
        'tmf':(['試合','守備機会','刺殺','補殺','失策','守備率'],['20','100','50','50','0','1.000'])}
    for key,url,group in pages(range(2013,2027)):
        lg=key.split('_')[1];cat=key.split('_')[2]
        names=['巨人','中日','阪神','DeNA','ヤクルト','広島'] if lg=='c' else ['ソフトバンク','日本ハム','オリックス','楽天','西武','ロッテ']
        html=''
        for kind in ('std','tmb','tmp') if cat=='archive' else (cat,):
            headers,values=tables[kind]
            html+='<table><tr>'+''.join('<th>'+h+'</th>' for h in ['チーム',*headers])+'</tr>'
            for name in names:
                html+='<tr>'+''.join('<td>'+v+'</td>' for v in [name,*values])+'</tr>'
            html+='</table>'
        cache.put(key,url,group,200,html.encode(),{})
        report=parse(html,url)
        assert not report['unknown']
        rows+=report['records']
    observations=root/'records.jsonl'
    observations.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    parser=Path(__file__).parents[2]/'blueprobe/npb_team_annual.py'
    metadata=dict(unknown=0,sha256=sha(observations),source_code_sha256=sha(parser))
    save(observations.with_suffix('.manifest.json'),metadata)
    result=audit_files(observations,range(2013,2027))
    assert result['failed']==0
    annual=root/'annual.jsonl'
    annual.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in result.pop('annual')),encoding='utf-8')
    result.update(source_sha256=sha(observations),source_parser_sha256=sha(parser))
    save(root/'audit.json',result)
    experiment=period_experiment()
    experiment.update(calibration=dict(years=[2013,2026],units=168,sha256=sha(annual)),
                      generator_sha256='fixture',python_version='fixture')
    save(root/'experiment.json',experiment)
    return root


def summarize(root):
    return summary(root/'records.jsonl',root/'audit.json',root/'annual.jsonl',[root/'experiment.json'],root/'raw/manifest.jsonl')


def test_full_evidence_chain_replays_original_cells_and_game_witnesses(primary_evidence):
    result=summarize(primary_evidence)
    assert result['real']['team_seasons']==168
    assert result['real']['source_replay']['pages']==140
    assert result['synthetic'][0]['games']==36036


@pytest.mark.parametrize('change',['annual','audit_count','audit_flag','audit_extra','source_cell','cache_url','cache_year','cache_body',
                                  'calibration_mean','calibration_units','experiment_annual','experiment_hash','experiment_groups'])
def test_aggregate_rejects_broken_provenance_and_false_saved_success(tmp_path,primary_evidence,change):
    root=tmp_path/'evidence';shutil.copytree(primary_evidence,root)
    a=read(root/'audit.json')
    for c in a['checks']:
        if c['check'].startswith('source_'):c['unit']=str(root/'records.jsonl')
    save(root/'audit.json',a)
    if change=='annual':
        p=root/'annual.jsonl';rows=[json.loads(s) for s in p.read_text().splitlines()];rows[0]['RF']+=1
        p.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        e=read(root/'experiment.json');e['calibration']['sha256']=sha(p);save(root/'experiment.json',e)
    if change in ('audit_count','audit_flag','audit_extra'):
        a=read(root/'audit.json')
        if change=='audit_count':a['passed']+=1
        elif change=='audit_flag':a['checks'][0]['ok']=False
        else:a['checks'].append(dict(check='invented',ok=True));a['passed']+=1
        save(root/'audit.json',a)
    if change=='source_cell':
        p=root/'records.jsonl';rows=[json.loads(s) for s in p.read_text().splitlines()];rows[0]['raw_cells'][0]='changed'
        p.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        m=read(root/'records.manifest.json');m['sha256']=sha(p);save(root/'records.manifest.json',m)
        a=read(root/'audit.json');a['source_sha256']=sha(p);save(root/'audit.json',a)
    if change in ('cache_url','cache_year','cache_body'):
        p=root/'raw/manifest.jsonl';entries=[json.loads(s) for s in p.read_text().splitlines()]
        if change=='cache_url':entries[0]['url']=entries[1]['url']
        if change=='cache_year':entries[0]['group']='2014'
        if change=='cache_body':(root/'raw'/entries[0]['file']).write_bytes(b'bad gzip')
        p.write_text(''.join(json.dumps(e)+'\n' for e in entries))
    if change.startswith('calibration_') or change.startswith('experiment_'):
        e=read(root/'experiment.json')
        if change=='calibration_mean':e['mean_runs']+=.1
        if change=='calibration_units':e['calibration']['units']-=1
        if change=='experiment_annual':e['cases'][0]['annual'][0]['RF']+=1
        if change=='experiment_hash':e['cases'][0]['games_sha256']='0'*64
        if change=='experiment_groups':e['groups'][0]['period_passed']=100
        save(root/'experiment.json',e)
    with pytest.raises(ValueError):summarize(root)
