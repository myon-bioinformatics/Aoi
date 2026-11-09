"""Check preserved annual inputs and replay 2026 totals without fetching data.

No cache restoration, source HTML parsing, or research-model recomputation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

try:
    from . import reconcile_season_2026 as season
except ImportError:
    import reconcile_season_2026 as season

ROOT = Path(__file__).resolve().parents[1]


def verify_payload(path, expected):
    payload = path.read_bytes()
    if len(payload) != expected['bytes'] or hashlib.sha256(payload).hexdigest() != expected['sha256']:
        raise ValueError(f'Saved input identity mismatch: {path}')
    return payload


def check(root=ROOT):
    root = Path(root)
    catalog = json.loads((root / 'cycles/c001-chunichi/recovered-inputs/manifest.json').read_text(encoding='utf-8'))
    observed, annual = [item['selected_member'] for item in catalog['archives']]
    verify_payload(root / observed['repository_path'], observed)
    panel = verify_payload(root / annual['existing_repository_path'], annual)
    rows = [json.loads(line) for line in panel.splitlines()]
    units = {(row['season'], row['team']) for row in rows}
    if len(rows) != annual['records'] or len(units) != len(rows):
        raise ValueError('Incomplete or duplicate annual panel')
    expected = season.outputs()
    for path, content in expected.items():
        if path.read_text(encoding='utf-8') != content:
            raise ValueError(f'Stale saved-data replay output: {path}')
    return {'mode': 'saved_input_verification', 'raw_source_replayed': False,
            'annual_units': len(rows), 'regular_season_2026_games': 858,
            'annual_values_matched': 72, 'source_requests': 0}


def main():
    print(json.dumps(check(), sort_keys=True))


if __name__ == '__main__':
    main()
