"""Local measurements -> existing judgments -> HTML -> observed changes."""
import hashlib
import json
import tomllib
from pathlib import Path
from neighbors import discover
from neighbor_checks import check_pairs
from dragowing_inspect import inspect
from exploration import atomic_json, digest
from ask import load
from research import build


def prepare_feedback(root, cycle, state):
    files = [cycle / 'outputs/season.jsonl', cycle / 'outputs/sets.jsonl', cycle / 'outputs/propositions.jsonl',
             cycle / 'analysis.toml', Path(__file__), root / 'sakanalytics/neighbors.py',
             root / 'pythdragoras/neighbor_checks.py']
    identity = digest({str(p.relative_to(root)) if p.is_relative_to(root) else p.name: hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None for p in files})
    path = state / 'feedback/observations.json'
    if path.exists() and json.loads(path.read_text())['input'] == identity:
        return
    rows = [json.loads(line) for line in (cycle/'outputs/season.jsonl').read_text().splitlines() if line.strip()]
    cfg = tomllib.loads((cycle/'analysis.toml').read_text())
    measured = discover(rows, sorted({2012, *(int(e['season']) for e in cfg.get('exclude', []))}))
    pairs = check_pairs(measured, load(cycle/'outputs'))
    atomic_json(path, {'version': 1, 'input': identity, 'measurement': measured, 'pairs': pairs})


def observe_report(state):
    html = build(state).read_text()
    path = state / 'feedback/blueprobe.json'
    previous = json.loads(path.read_text()) if path.exists() else None
    observed = inspect(html, previous)
    if previous and previous['input'] == observed['input'] and previous['rows'] == observed['rows'] and previous.get('discoveries', []) == observed['discoveries']:
        return
    # Content-addressed history prevents repeat events on identical reruns.
    atomic_json(state / 'feedback/history' / (digest(observed) + '.json'), observed)
    atomic_json(path, observed)
    targets = sorted({f['target'] for key in observed['rows']
                      for f in observed['rows'][key].get('findings', []) if f['target'].startswith('E')}, key=lambda t: int(t[1:]))
    atomic_json(state / 'feedback/priority.json', {'input': observed['input'], 'targets': targets,
                'reason': 'BlueProbe がHTMLの構造化観測から読み取った現在のペアの反例に関連する式'})
