"""Generic log/linear scaling helpers (stdlib only).

The public portfolio Languages bar uses:

    score = top * log(1+x, base) / log(1+anchor, base)

with ``anchor`` defaulting to ``max(values)``. The ratio does not depend on
``base`` (any finite base > 0, ``base != 1``). Callers that then shrink a
narrow footprint should pass ``round_to=None``, apply :func:`adjust_narrow`,
and finally :func:`round_score`. Residual floors and manual overrides stay
with the caller.

Baseball score views that need only ``ln(1+x)`` or a constant factor call
these helpers without the default ``top`` / ``round_to``; baseball-specific
units stay in ``npb/``.
"""
from __future__ import annotations

import math

__all__ = ["log_scale", "linear_scale", "adjust_narrow", "round_score"]


def _require_finite(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be a finite number")
    return value


def _require_nonneg(value, name):
    value = _require_finite(value, name)
    if value < 0:
        raise ValueError(name + " must be nonnegative")
    return value


def _numbers(values):
    if isinstance(values, (str, bytes)) or not hasattr(values, "__iter__"):
        raise ValueError("values must be a nonempty iterable of finite nonnegative numbers")
    items = [_require_nonneg(value, "value") for value in values]
    if not items:
        raise ValueError("values must be a nonempty iterable of finite nonnegative numbers")
    return items


def _log1p(value, base):
    if base == math.e:
        return math.log1p(value)
    if base == 10:
        return math.log10(1 + value)
    if base == 2:
        return math.log2(1 + value)
    return math.log1p(value) / math.log(base)


def round_score(score, *, step=5):
    """Round ``score`` to a multiple of ``step``, half away from zero.

    ``step=None`` returns ``score`` unchanged. ``step`` must be positive.
    """
    score = _require_finite(score, "score")
    if step is None:
        return score
    step = _require_finite(step, "step")
    if step <= 0:
        raise ValueError("step must be positive")
    quotient = score / step
    rounded = math.floor(quotient + 0.5) if quotient >= 0 else math.ceil(quotient - 0.5)
    return rounded * step


def _apply(items, scores, floor, round_to):
    result = []
    for value, score in zip(items, scores):
        if value == 0 and floor is not None:
            result.append(floor)
        else:
            result.append(round_score(score, step=round_to))
    return result


def _optional_floor(floor):
    if floor is None:
        return None
    return _require_finite(floor, "floor")


def log_scale(values, *, anchor=None, top=90, floor=None, round_to=5, base=10):
    """Scale nonnegative values: ``top * log(1+x) / log(1+anchor)``.

    ``anchor`` defaults to the maximum of ``values``. ``round_to`` is the
    step for :func:`round_score`; ``round_to=None`` disables rounding.
    ``top=None`` returns ``log(1+x)`` in the given ``base`` (``anchor`` is
    unused) so callers that need unnormalized log1p can share this helper.

    A zero value uses ``floor`` as the final score when ``floor`` is set
    (it is not rounded). When the resolved anchor is 0, every value must
    be 0: each score is 0, or ``floor`` if set. A positive value with
    anchor 0 raises ValueError, as does a negative value or a negative
    anchor.
    """
    items = _numbers(values)
    base = _require_finite(base, "base")
    if base <= 0 or base == 1:
        raise ValueError("base must be positive and not 1")
    floor = _optional_floor(floor)
    if top is None:
        scores = [_log1p(value, base) for value in items]
        return _apply(items, scores, floor, round_to)
    top = _require_finite(top, "top")
    if anchor is None:
        anchor = max(items)
    else:
        anchor = _require_nonneg(anchor, "anchor")
    if anchor == 0:
        if any(value > 0 for value in items):
            raise ValueError("anchor must be positive when a value is positive")
        scores = [0.0] * len(items)
        return _apply(items, scores, floor, round_to)
    denom = _log1p(anchor, base)
    scores = [top * _log1p(value, base) / denom for value in items]
    return _apply(items, scores, floor, round_to)


def linear_scale(values, *, factor=1.0, floor=None, round_to=None):
    """Scale nonnegative values with ``factor * x``.

    ``round_to=None`` (the default) disables rounding. A zero value uses
    ``floor`` as the final score when ``floor`` is set (it is not rounded).
    """
    items = _numbers(values)
    factor = _require_finite(factor, "factor")
    floor = _optional_floor(floor)
    scores = [factor * value for value in items]
    return _apply(items, scores, floor, round_to)


def adjust_narrow(score, count, *, below=3, factor=0.75):
    """Shrink ``score`` when ``0 < count < below`` (else return ``score``).

    Used for a narrow footprint (default: count 1 or 2). The caller decides
    whether to round before or after; the Languages bar rule applies this
    to the unrounded score, then :func:`round_score`.
    """
    score = _require_finite(score, "score")
    count = _require_finite(count, "count")
    below = _require_finite(below, "below")
    factor = _require_finite(factor, "factor")
    if 0 < count < below:
        return score * factor
    return score
