"""Reproducible synthetic payload + evaluation comparison, seven repeats."""
import gzip
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'pythdragoras'))
from bitwise_surrogate import BitwiseSymbolicSurrogate
from compact_bitmask import CompactRule, FeatureLayout


def run():
    rng = random.Random(20261104)
    layout = FeatureLayout((0, 31, 63, 95, 127, 159, 191, 255))
    dense_rows = [rng.randrange(256) for _ in range(4096)]
    rows = [layout.expand(row) for row in dense_rows]
    rule = BitwiseSymbolicSurrogate(layout.expand(1), (layout.expand(6),), layout.expand(128))
    compact = CompactRule(rule)
    projected = [compact.layout.project(row) for row in rows]
    expected = [rule.evaluate_fast(row) for row in rows]
    if [compact.evaluate_dense(row) for row in projected] != expected:
        raise SystemExit("dense evaluation mismatch")
    raw = b''.join(row.to_bytes(32, 'little') for row in rows)
    packed = b''.join(layout.encode(row) for row in rows)
    schema = json.dumps({'version': 1, 'positions': layout.positions}, separators=(',', ':')).encode()
    if [layout.decode(packed[i:i+1]) for i in range(len(rows))] != rows:
        raise SystemExit("packed roundtrip mismatch")

    def measure(fn):
        fn()  # warmup
        samples = []
        for _ in range(7):
            start = time.perf_counter_ns()
            result = fn()
            samples.append(time.perf_counter_ns() - start)
            if result != expected:
                raise SystemExit("timed evaluation mismatch")
        return {'samples_ns': samples, 'median_ns': statistics.median(samples)}

    result = {
        'scope': 'synthetic 4096 rows; full rows contain only the selected features',
        'seed': 20261104, 'python': sys.version, 'platform': platform.platform(),
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'feature_width_before': 256, 'feature_width_after': layout.width,
        'raw_bytes': len(raw), 'packed_bytes': len(packed), 'schema_bytes': len(schema),
        'gzip_raw_bytes': len(gzip.compress(raw, mtime=0)),
        'gzip_packed_with_schema_bytes': len(gzip.compress(schema + b'\n' + packed, mtime=0)),
        'evaluation': measure(lambda: [rule.evaluate_fast(row) for row in rows]),
        'preprojected_core_evaluation': measure(lambda: [compact.rule.evaluate_fast(row) for row in projected]),
        'preprojected_checked_evaluation': measure(lambda: [compact.evaluate_dense(row) for row in projected]),
        'project_and_evaluate': measure(lambda: [compact.evaluate_source(row) for row in rows]),
        'build_time_improvement': None,
        'build_note': 'Aoi wheel excludes research modules; no package build optimization claimed.',
        'dependencies_added': 0,
    }
    return result


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
