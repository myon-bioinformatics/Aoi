"""Fetch an immutable research dataset; never import code from its ref."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

DATA_FILES = ('analysis.toml', 'propositions.toml', 'sets.toml',
              'outputs/season.jsonl', 'outputs/propositions.jsonl', 'outputs/sets.jsonl')


def validate_target(cycle, ref):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,79}', cycle):
        raise ValueError('サイクル名は小文字英数字とハイフン（最大80文字）')
    if not ref or len(ref) > 200 or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]*', ref):
        raise ValueError('結果refが不正')
    if any(x in ref for x in ('..', '//', '@{')) or ref.endswith(('/', '.', '.lock')):
        raise ValueError('結果refが不正')
    return 'aoi-research-state-' + cycle


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True,
                          capture_output=True, timeout=120).stdout


def fetch_dataset(root: Path, cycle: str, ref: str, destination: Path):
    validate_target(cycle, ref)
    run(root, 'fetch', '--no-tags', 'origin', ref)
    sha = run(root, 'rev-parse', 'FETCH_HEAD^{commit}').decode().strip()
    directory = destination / sha
    directory.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in DATA_FILES:
        source = f'cycles/{cycle}/{name}'
        entry = run(root, 'ls-tree', sha, '--', source).decode().strip()
        if not entry:
            continue
        if entry.split()[0] != '100644' or entry.split()[1] != 'blob':
            raise ValueError(f'結果には通常のデータファイルだけを使用できます: {name}')
        data = run(root, 'show', f'{sha}:{source}')
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    if not any(name in hashes for name in ('outputs/propositions.jsonl', 'outputs/sets.jsonl')):
        raise ValueError(f'結果が読めません: {cycle} @ {sha} に判定結果がありません')
    identity = {'cycle': cycle, 'results_ref': ref, 'results_sha': sha, 'files': hashes}
    (directory / 'target.json').write_text(json.dumps(identity, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return directory, identity


def dataset_identity(cycle: Path):
    path = cycle / 'target.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
