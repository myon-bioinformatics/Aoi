"""Tiny public-path regressions; no corpus or performance measurement."""
import importlib.util
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("shape", [(2, 401), (401, 2)])
@pytest.mark.parametrize("small,uses_fallback", [(1e-13, True), (1e-10, False), (0.0, False)])
def test_gram_preserves_strictly_positive_small_component(monkeypatch, shape, small, uses_fallback):
    monkeypatch.setenv("NUMPY_MIN_PURE", "1")
    spec = importlib.util.spec_from_file_location("numpy_min_gram", ROOT / "shrink/numpy_min.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    a = np.zeros(shape)
    a[0, 0], a[1, 1] = 1.0, small
    calls = []
    original = mod._svd_onesided
    def observed(data, rows, cols):
        calls.append((rows, cols))
        return original(data, rows, cols)
    monkeypatch.setattr(mod, "_svd_onesided", observed)
    u, s, vt = mod.linalg.svd(mod.asarray(a.tolist(), dtype="float64"), full_matrices=False)
    U, S, Vt = (np.asarray(x.tolist()) for x in (u, s, vt))
    assert calls == ([shape] if uses_fallback else [])
    np.testing.assert_array_equal(S, [1.0, small])
    np.testing.assert_allclose(U.T @ U, np.eye(2), rtol=0, atol=1e-12)
    np.testing.assert_allclose(Vt @ Vt.T, np.eye(2), rtol=0, atol=1e-12)
    # Check the small component itself, not merely its negligible relative norm.
    np.testing.assert_allclose(U @ np.diag(S) @ Vt, a, rtol=1e-12, atol=0)
