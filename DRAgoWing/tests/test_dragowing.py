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
