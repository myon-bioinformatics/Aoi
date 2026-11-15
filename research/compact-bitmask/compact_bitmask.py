"""Opt-in, stdlib-only feature projection and non-destructive scene matching.

Projection is lossless on the selected features, not on arbitrary source data.
Scene matches are compatible hypotheses, not a unique factorization or a
reconstruction of hidden objects. No learning occurs during inference/audit.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import gzip
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2].joinpath('pythdragoras', 'core')))   # joinpath: the core has no '/'
from bitwise_surrogate import BitwiseSymbolicSurrogate, iter_bits  # noqa: E402


def _mask_value(value, name):
    if type(value) is not int or value < 0:
        raise ValueError("%s must be a nonnegative int" % name)
    return value


@dataclass(frozen=True)
class FeatureLayout:
    """Ascending original positions define the dense wire feature order."""
    positions: tuple[int, ...]

    def __post_init__(self):
        if type(self.positions) is not tuple:
            raise ValueError("positions must be a tuple")
        for position in self.positions:
            _mask_value(position, "position")
        if tuple(sorted(set(self.positions))) != self.positions:
            raise ValueError("positions must be unique and ascending")

    @classmethod
    def from_masks(cls, masks):
        used = 0
        for mask in masks:
            used |= _mask_value(mask, "mask")
        return cls(tuple(iter_bits(used)))

    @property
    def width(self):
        return len(self.positions)

    @property
    def byte_width(self):
        return (self.width + 7) >> 3

    def project(self, source):
        _mask_value(source, "source")
        dense = 0
        for index, position in enumerate(self.positions):
            if source & (1 << position):
                dense |= 1 << index
        return dense

    def expand(self, dense):
        _mask_value(dense, "dense")
        if dense.bit_length() > self.width:
            raise ValueError("dense mask exceeds layout")
        source = 0
        for index, position in enumerate(self.positions):
            if dense & (1 << index):
                source |= 1 << position
        return source

    def encode(self, source):
        """Fixed-size row payload; transmit the layout once per schema/session."""
        return self.project(source).to_bytes(self.byte_width, "little")

    def decode(self, payload):
        if not isinstance(payload, bytes) or len(payload) != self.byte_width:
            raise ValueError("payload length differs from layout")
        return self.expand(int.from_bytes(payload, "little"))


class CompactRule:
    """Snapshot a two-valued surrogate; convert rows once for repeated use.

    Null-aware frame evaluation remains in bitwise_surrogate and is unchanged.
    """
    def __init__(self, rule):
        self.layout = FeatureLayout.from_masks(
            (rule.m_and, rule.m_not, *rule.or_clauses)
        )
        self.rule = BitwiseSymbolicSurrogate(
            self.layout.project(rule.m_and),
            tuple(self.layout.project(mask) for mask in rule.or_clauses),
            self.layout.project(rule.m_not),
        )

    def evaluate_source(self, source):
        return self.rule.evaluate_fast(self.layout.project(source))

    def evaluate_dense(self, dense):
        _mask_value(dense, "dense")
        if dense.bit_length() > self.layout.width:
            raise ValueError("dense mask exceeds layout")
        return self.rule.evaluate_fast(dense)


@dataclass(frozen=True)
class Part:
    name: str
    required: int
    forbidden: int = 0

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("part name must be nonempty")
        _mask_value(self.required, "required")
        _mask_value(self.forbidden, "forbidden")
        if not self.required or self.required & self.forbidden:
            raise ValueError("required must be nonzero and disjoint from forbidden")


def match_scene(board, parts, observed=None):
    """Check every part against the original board, never a peeled board.

    A set forbidden bit contradicts the part. Unknown required/forbidden bits
    leave it pending. Unexplained bits are evidence only: shared ownership
    cannot be recovered from OR alone. Board bits must all be observed.
    """
    _mask_value(board, "board")
    parts = tuple(parts)
    if len({part.name for part in parts}) != len(parts):
        raise ValueError("part names must be unique")
    if observed is None:
        observed = board
        for part in parts:
            observed |= part.required | part.forbidden
    _mask_value(observed, "observed")
    if board & ~observed:
        raise ValueError("board contains unobserved bits")
    matches, pending, rejected = [], [], []
    explained = 0
    for part in parts:
        if part.required & observed & ~board or part.forbidden & board:
            rejected.append(part.name)
        elif (part.required | part.forbidden) & ~observed:
            pending.append(part.name)
        else:
            matches.append(part.name)
            explained |= part.required
    return {
        "compatible_parts": matches,
        "pending_parts": pending,
        "rejected_parts": rejected,
        "explained_mask": explained,
        "unexplained_mask": board & ~explained,
        "unique_decomposition_proven": False,
    }


# ==== 速さの目安（--benchmark）
# Reproducible synthetic payload + evaluation comparison, seven repeats.


def benchmark():
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--benchmark', action='store_true', required=True,
                    help='⏱ 合成 4096 行で、容量と評価時間（7 回）を JSON で出す')
    ap.parse_args(argv)
    print(json.dumps(benchmark(), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
