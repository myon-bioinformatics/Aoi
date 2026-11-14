import sys
from pathlib import Path
import pytest
import aoi

@pytest.fixture
def root(tmp_path, monkeypatch):
    root = tmp_path / 'checkout'
    (root / 'queryu').mkdir(parents=True)
    (root / 'queryu/queryu.py').write_text('')
    monkeypatch.setattr(aoi, 'ROOT', root.resolve())
    return root

@pytest.mark.parametrize('target', ['queryu', 'QueRyu', 'queryu/queryu.py', 'queryu/../queryu/queryu.py'])
def test_inside_targets_preserve_args(root, target):
    assert aoi.command([target, '--help', 'with spaces']) == [sys.executable, str(root / 'queryu/queryu.py'), '--help', 'with spaces']

def test_inside_absolute_target(root):
    target = root / 'queryu/queryu.py'
    assert aoi.command([str(target)]) == [sys.executable, str(target)]

@pytest.mark.parametrize('absolute', [False, True])
def test_outside_file_rejected(root, absolute):
    outside = root.parent / 'outside.py'
    outside.write_text('')
    with pytest.raises(SystemExit, match='under Aoi'):
        aoi.command([str(outside) if absolute else '../outside.py'])

def test_outside_symlink_rejected(root):
    outside = root.parent / 'outside.py'
    outside.write_text('')
    link = root / 'linked.py'
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f'symlinks unavailable: {exc}')
    with pytest.raises(SystemExit, match='under Aoi'):
        aoi.command(['linked.py'])

def test_module_mode_is_not_restricted(root):
    assert aoi.command(['-m', 'dragowing', 'results']) == [sys.executable, '-m', 'dragowing', 'results']
