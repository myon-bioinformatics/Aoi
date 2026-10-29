"""ε as a symbol: one place that detects a value sitting exactly on a boundary and, only when asked, lifts it by ε.

The value of ε and how to treat a lifted value afterwards are not decided. So:

* nothing here chooses a number: ``eps`` is always passed in by the caller, and ``None`` (the default everywhere) means
  "do not lift". With ``eps=None`` every output is what it was before; the boundary is still detected and counted.
* a lifted value is always reported next to the original (``lift`` returns ``(value, hit)``; the sites keep the cells or
  rows that were lifted), so the result can be re-read, or redone with another ε, once the handling is decided.

What is lifted: a value that is a *boundary of a parameter or of a table* and sits there exactly, so that a formula
further on degenerates. Today that is the undamped wave λ = 0 (sakanalytics.wave_basis) and a zero cell of a real 2x2
table (moshimo_box.anchor, where it makes a rate exactly 0 or 1 and its logit infinite).

What is not lifted, on purpose:

* 0/0, an empty row or column: the quantity is undefined, not small. It stays null / "no unit".
* a true zero in the data, or a value that is correctly 0 (sin(0) = 0 for the first point of a wave: the angle is not a
  boundary of anything).
* the denominator of a noisy ratio (k_eff = logit / log(RF/RA)): lifting it pulls the value toward a fake number, so it
  stays null behind a named threshold (K_EFF_MIN_LOG_RATIO).

``lift`` tests ``x == bound`` exactly. A near-zero that is not exactly on the bound is the business of the named
tolerances (sakanalytics.TOLERANCES), not of ε.
"""
from __future__ import annotations

import math


class EpsilonError(ValueError):
    pass


def check_eps(eps, name: str = "eps") -> float | None:
    """``None`` (do not lift) or a finite number strictly greater than 0. There is no default value."""
    if eps is None:
        return None
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) or not math.isfinite(eps) or eps <= 0:
        raise EpsilonError(f"{name} must be None or a finite number greater than 0, got {eps!r}")
    return float(eps)


def lift(x: float, eps: float | None, *, lo: float | None = None, hi: float | None = None) -> tuple[float, bool]:
    """``(value, hit)``: ``hit`` is True when ``x`` is exactly on ``lo`` or ``hi``.

    With ``eps`` the value is moved inside by ε (``lo + eps`` or ``hi - eps``); with ``eps=None`` it is returned as it
    was, so a caller can detect the boundary without lifting. Other values pass through untouched.
    """
    eps = check_eps(eps)
    if lo is None and hi is None:
        raise EpsilonError("lift needs a bound: lo, hi or both")
    if None not in (lo, hi) and eps is not None and not 2 * eps < hi - lo:
        raise EpsilonError(f"eps={eps:g} does not fit inside [{lo}, {hi}]")
    if lo is not None and x == lo:
        return (lo if eps is None else lo + eps), True
    if hi is not None and x == hi:
        return (hi if eps is None else hi - eps), True
    return x, False
