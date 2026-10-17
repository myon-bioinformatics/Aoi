"""A self-consistent hash rewrite must still fail against independent history."""
import hashlib

import pytest

from scripts.audit_recovery_provenance import verify_source


def test_provenance_rejects_consistent_rebaseline(tmp_path):
    source = tmp_path / 'source.py'
    source.write_bytes(b'changed CLI')
    current = hashlib.sha256(source.read_bytes()).hexdigest()
    # Both the recorded hash and current file agree, but history says otherwise.
    with pytest.raises(ValueError, match='pinned history'):
        verify_source(tmp_path, 'source.py', current, [], b'original CLI')


def test_provenance_requires_both_historical_and_current_bytes(tmp_path):
    old, current = b'original CLI', b'changed CLI'
    (tmp_path / 'source.py').write_bytes(current)
    recorded = hashlib.sha256(old).hexdigest()
    row = dict(path='source.py', evidence_sha256=recorded,
               current_sha256=hashlib.sha256(current).hexdigest(),
               artifacts_regenerated=False, inputs_regenerated=False, reason='CLI-only change')
    verify_source(tmp_path, 'source.py', recorded, [row], old)
    for rows in ([], [row, row], [{**row, 'current_sha256': '0'*64}],
                 [{**row, 'artifacts_regenerated': True}], [{**row, 'reason': ''}]):
        with pytest.raises(ValueError):
            verify_source(tmp_path, 'source.py', recorded, rows, old)
    (tmp_path / 'source.py').write_bytes(old)
    with pytest.raises(ValueError, match='stale'):
        verify_source(tmp_path, 'source.py', recorded, [row], old)
