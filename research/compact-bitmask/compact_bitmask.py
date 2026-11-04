"""Opt-in, stdlib-only feature projection and non-destructive scene matching.

Projection is lossless on the selected features, not on arbitrary source data.
Scene matches are compatible hypotheses, not a unique factorization or a
reconstruction of hidden objects. No learning occurs during inference/audit.
"""
from __future__ import annotations

from dataclasses import dataclass

from bitwise_surrogate import BitwiseSymbolicSurrogate, _mask_value, iter_bits


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
