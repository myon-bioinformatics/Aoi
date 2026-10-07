import json
from pathlib import Path
import pytest
from inbox import git, State
from target import fetch_dataset, validate_target


@pytest.mark.parametrize('cycle,ref', [('..','main'), ('a/b','main'), ('x','../main'),
                                     ('x','--upload-pack=x'), ('x','a//b'), ('x','a;echo')])
def test_invalid_target(cycle, ref):
    with pytest.raises(ValueError):
        validate_target(cycle, ref)


def test_real_git_dataset_reads_only_data_and_pins_sha(tmp_path):
    remote = tmp_path/'remote'
    git(tmp_path, 'init', str(remote))
    git(remote, 'config', 'user.name', 'test')
    git(remote, 'config', 'user.email', 'test@example.invalid')
    cycle = remote/'cycles/example'
    (cycle/'outputs').mkdir(parents=True)
    (cycle/'outputs/sets.jsonl').write_text('{"id":"E1"}\n')
    (cycle/'payload.py').write_text('raise RuntimeError("must not run")')
    git(remote,'add','.')
    git(remote,'commit','-m','data')
    sha = git(remote,'rev-parse','HEAD').stdout.strip()
    source = tmp_path/'code'
    git(tmp_path,'clone',str(remote),str(source))
    path, identity = fetch_dataset(source,'example',sha,tmp_path/'data')
    assert identity['results_sha'] == sha
    assert not (path/'payload.py').exists()
    assert json.loads((path/'outputs/sets.jsonl').read_text())['id'] == 'E1'
    with pytest.raises(ValueError, match='結果が読めません'):
        fetch_dataset(source,'missing',sha,tmp_path/'missing')
    first = State(source,tmp_path/'first',create=True,branch=validate_target('example',sha))
    second = State(source,tmp_path/'second',create=True,branch=validate_target('other',sha))
    (first.path/'only-first').write_text('one')
    first.save()
    second.sync()
    assert not (second.path/'only-first').exists()
