import hashlib
import json
from pathlib import Path
import subprocess
import pytest
from build_reports import build, revision


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
