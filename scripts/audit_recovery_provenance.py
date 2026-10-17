"""Verify recovery evidence against immutable Git history, without rewriting it.

Requires the two pinned commits locally (CI checks out full history). No network,
regeneration, fitting, rounding, or updates to any evidence file are performed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_REF = '50f508d44b1d13ce820dcdd3d5bd9ab837503512'
EXPERIMENT_REF = 'db15d3a33af701a1317871b80c63340cfcb33786'
OUT = 'cycles/c001-chunichi/outputs/exploratory'


def historical_bytes(root, ref, path):
    return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=root,
                          check=True, capture_output=True).stdout


def verify_source(root, path, recorded, rows, historical):
    """A divergence declaration cannot replace verification of original bytes."""
    if hashlib.sha256(historical).hexdigest() != recorded:
        raise ValueError(f'{path}: recorded hash does not match pinned history')
    current = hashlib.sha256((root / path).read_bytes()).hexdigest()
    matching = [r for r in rows if r['path'] == path]
    if current == recorded:
        if matching:
            raise ValueError(f'{path}: stale divergence')
        return
    if len(matching) != 1:
        raise ValueError(f'{path}: missing or duplicate divergence')
    row = matching[0]
    if (row['evidence_sha256'] != recorded or row['current_sha256'] != current
            or row['artifacts_regenerated'] is not False
            or row['inputs_regenerated'] is not False
            or not isinstance(row['reason'], str) or not row['reason'].strip()):
        raise ValueError(f'{path}: invalid divergence')


def audit(root=ROOT, read_history=historical_bytes):
    root = Path(root)
    manifest = json.loads((root / OUT / 'littlebit-holdout/holdout.provenance.json').read_text())
    if manifest['source_reference'] != HOLDOUT_REF:
        raise ValueError('holdout source_reference changed')
    rows = manifest.get('source_divergence', [])
    if set(r['path'] for r in rows) - set(manifest['source_sha256']):
        raise ValueError('unexpected holdout divergence path')
    for path, recorded in manifest['source_sha256'].items():
        verify_source(root, path, recorded, rows, read_history(root, HOLDOUT_REF, path))
    for group in ('inputs_sha256', 'artifacts_sha256'):
        for path, recorded in manifest[group].items():
            if hashlib.sha256((root / path).read_bytes()).hexdigest() != recorded:
                raise ValueError(f'{path}: frozen input/artifact changed')
    checked = len(manifest['source_sha256'])
    for folder, artifact, source, field in (
        ('league-laboratory', 'results.json', 'league_laboratory.py', 'inputs.analysis_sha256'),
        ('proposition-evaluation', 'seed-evaluation.json', 'proposition_seed_audit.py', 'analysis_sha256'),
    ):
        rel = f'{OUT}/{folder}/{artifact}'
        data = (root / rel).read_bytes()
        if data != read_history(root, EXPERIMENT_REF, rel):
            raise ValueError(f'{rel}: frozen experiment bytes differ from pinned history')
        sidecar = json.loads((root / OUT / folder / 'source-divergence.json').read_text())
        if sidecar['schema'] != 'aoi-source-divergence/1' or sidecar['artifact'] != artifact:
            raise ValueError(f'{rel}: incorrect sidecar identity')
        rows = sidecar['source_divergence']
        path = f'sakanalytics/{source}'
        if len(rows) != 1 or rows[0]['path'] != path or rows[0]['field'] != field:
            raise ValueError(f'{rel}: incorrect divergence coverage')
        recorded = json.loads(data)
        for key in field.split('.'):
            recorded = recorded[key]
        verify_source(root, path, recorded, rows, read_history(root, EXPERIMENT_REF, path))
        checked += 1
    return {'verified_sources': checked, 'frozen_experiments': 2,
            'holdout_reference': HOLDOUT_REF, 'experiment_reference': EXPERIMENT_REF}


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
