"""レポート: 📄 reports/build_reports.py（Markdown の版比較）、📊 research_report.py（集計図の HTML）。"""
import hashlib, importlib.util, json, subprocess
from pathlib import Path

import pytest

import aoi_paths
from dragowing.research_report import render_report
from reports.build_reports import build, revision

ROOT=aoi_paths.resolve_aoi_root(anchor=Path(__file__))


# ==== 📄 reports/build_reports.py（旧 test_build_reports.py）

def commit(root, message):
    subprocess.run(['git','-C',str(root),'add','.'],check=True,capture_output=True)
    subprocess.run(['git','-C',str(root),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm',message],check=True)
    return revision(root,'HEAD')


@pytest.fixture
def repos(tmp_path):
    root=tmp_path/'aoi';upstream=tmp_path/'markdown'
    for p in [root,upstream]:
        p.mkdir();subprocess.run(['git','-C',str(p),'init','-q'],check=True)
    (root/'research').mkdir();(root/'dragowing').mkdir()
    (root/'dragowing/README.md').write_text('# DRAgoWing\n')
    (root/'research/report.md').write_text('# Old\n\n[Source](other.md)\n')
    old=commit(root,'old')
    (root/'research/report.md').write_text('# New\n\n<script>unsafe</script>\n')
    (root/'research/added.md').write_text('')
    commit(root,'new')
    # A stand-in verifies delegation, not the upstream Markdown parser.
    (upstream/'markdown.py').write_text('from __future__ import annotations\nfrom dataclasses import dataclass\n@dataclass\nclass Marker:\n value: str = \"loaded\"\nimport html\ndef markdown_to_html(text):\n return "<p>delegated:"+html.escape(text)+"</p>"\ndef default_stylesheet():\n return "p { color: black; }"\n')
    (upstream/'LICENSE').write_text('test fixture license\n')
    commit(upstream,'renderer')
    return root,upstream,tmp_path/'out',old


def test_previous_comparison_and_provenance(repos):
    root,upstream,out,old=repos
    manifest=build(root,upstream,out,old)
    status={v['path']:v['status'] for v in manifest['documents']}
    assert status['research/added.md']=='added' # empty creation still a change
    assert status['research/report.md']=='modified'
    assert status['dragowing/README.md']=='unchanged'
    rendered=(out/'research/report.html').read_text()
    diff=(out/'research/report.diff.html').read_text()
    assert 'delegated:' in rendered
    assert '<script>unsafe' not in diff
    assert 'diff_add' in diff
    assert manifest['markdown_commit']==revision(upstream,'HEAD')
    assert manifest['markdown_sha256']==hashlib.sha256((upstream/'markdown.py').read_bytes()).hexdigest()
    assert (out/'_renderer/markdown.py').read_bytes()==(upstream/'markdown.py').read_bytes()
    assert (out/'_renderer/LICENSE').read_bytes()==(upstream/'LICENSE').read_bytes()


def test_unavailable_previous_is_not_unchanged(repos):
    root,upstream,out,_=repos
    manifest=build(root,upstream,out,'f'*40)
    assert manifest['previous_status']=='unavailable'
    assert all(v['status']=='current_only' for v in manifest['documents'])
    assert '変更なしとは判定しません' in (out/'research/report.diff.html').read_text()


def test_dirty_upstream_rejected_before_output(repos):
    root,upstream,out,old=repos
    (upstream/'markdown.py').write_text((upstream/'markdown.py').read_text()+'\n# dirty')
    with pytest.raises(ValueError,match='differs'):build(root,upstream,out,old)
    assert not out.exists()


def test_deleted_document_kept(repos):
    root,upstream,out,old=repos
    (root/'research/report.md').unlink();commit(root,'deleted')
    manifest=build(root,upstream,out,old)
    assert next(v['status'] for v in manifest['documents'] if v['path']=='research/report.md')=='deleted'
    assert '# Old' in (out/'research/report.diff.html').read_text()


def test_nonempty_output_rejected(repos):
    root,upstream,out,old=repos
    out.mkdir();(out/'keep').write_text('keep')
    with pytest.raises(ValueError,match='empty'):build(root,upstream,out,old)
    assert (out/'keep').read_text()=='keep'


# ==== 📊 research_report.py（旧 test_research_report.py）

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
