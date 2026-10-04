import importlib.util
import json
from pathlib import Path
import pytest
from dragowing import render_report

ROOT=Path(__file__).resolve().parents[2]


def test_script_and_title_escaping():
    spec={'title':'</script><script>alert(1)</script>','default':'x','frames':{'x':{}},'note':'<>&'}
    result=render_report(spec)
    assert '<script>alert(1)' not in result
    payload=result.split('type="application/json">')[1].split('</script>')[0]
    assert json.loads(payload)==spec


def test_invalid_default_and_nonfinite():
    with pytest.raises(ValueError):render_report({'frames':{},'default':'x'})
    with pytest.raises(ValueError):render_report({'frames':{'x':{}},'default':'x','title':'x','bad':float('nan')})


def test_real_aggregate_mapping():
    path=ROOT/'research/gpt-r001-score-allocation/render_score_report.py'
    module_spec=importlib.util.spec_from_file_location('score_report',path)
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    outputs=path.parent/'outputs'
    early=json.loads((outputs/'early_scoring.json').read_text())
    late=json.loads((outputs/'late_reaction.json').read_text())
    spec=module.build_spec(early,late)
    assert len(spec['frames'])==26
    panels=spec['frames']['2022|7']['panels']
    assert panels[1]['data'][0]['y'][0]==34/143
    assert panels[2]['data'][0]['y'][1]==22/75
    assert panels[2]['data'][1]['y'][1]==117/342
    assert panels[3]['data'][1]['y']==[12/66,56/267]
    assert '参考' in spec['frames']['2020|7']['caption']
    assert panels[0]['data'][0]['y'][7] is None
    assert render_report(spec)==render_report(spec)
    early['rows'].append(early['rows'][0])
    with pytest.raises(ValueError):module.build_spec(early,late)
