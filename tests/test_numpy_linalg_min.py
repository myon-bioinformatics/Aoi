"""shrink/numpy_linalg_min.py を本物の numpy と、c001 より小さい行列で比べる。

c001 全体の SVD はこのファイルでは走らせない。
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
np = pytest.importorskip("numpy")


def _load():
    spec = importlib.util.spec_from_file_location("numpy_linalg_min", ROOT / "shrink" / "numpy_linalg_min.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mn = _load()


def _arr(value, dtype="float64"):
    return mn.array(np.asarray(value).tolist(), dtype=dtype)


def test_numpy_min_load_overlap_file_is_untouched():
    text = (ROOT / "shrink" / "numpy_min.py").read_text(encoding="utf-8")
    assert text.startswith("\"\"\"numpy の最小版。scripts/shrink_module.py が生成した。手で直さない。")
    assert "dragowing/overlap.py:load_overlap" in text
    assert "linalg" not in text


def test_svd_economy_matches_singular_values_and_reconstruction():
    rng = np.random.default_rng(1)
    source = rng.normal(size=(30, 40))
    u, s, vt = mn.linalg.svd(_arr(source), full_matrices=False)
    _u, sr, _vt = np.linalg.svd(source, full_matrices=False)
    assert np.allclose(s.tolist(), sr, rtol=1e-8, atol=1e-8)
    recon = (np.asarray(u.tolist()) * np.asarray(s.tolist())) @ np.asarray(vt.tolist())
    assert np.allclose(recon, source, rtol=1e-8, atol=1e-8)
    only = mn.linalg.svd(_arr(source), full_matrices=False, compute_uv=False)
    assert np.allclose(only.tolist(), sr, rtol=1e-8, atol=1e-8)


def test_wide_matrix_uses_gram_and_matches_numpy():
    """suggest と同じ分岐（長い方 > 400）。特異値はよく離れている。"""
    rng = np.random.default_rng(2)
    source = rng.normal(size=(12, 420))
    _u, s, _vt = mn.linalg.svd(_arr(source), full_matrices=False)
    _ur, sr, _vtr = np.linalg.svd(source, full_matrices=False)
    assert np.allclose(s.tolist(), sr, rtol=1e-6, atol=1e-6)


def test_svd_full_matrices_on_non_square_is_refused():
    with pytest.raises(NotImplementedError):
        mn.linalg.svd(_arr(np.ones((3, 5))), full_matrices=True)


def test_rank_deficient_lstsq_matches_numpy_cutoff():
    rng = np.random.default_rng(3)
    matrix = rng.normal(size=(8, 8))
    matrix[:, -1] = matrix[:, 0] + matrix[:, 1]
    rhs = matrix[:, :7] @ rng.normal(size=7)
    got = mn.linalg.lstsq(_arr(matrix), _arr(rhs), rcond=None)
    ref = np.linalg.lstsq(matrix, rhs, rcond=None)
    assert got[2] == int(ref[2]) == 7
    assert np.allclose(got[0].tolist(), ref[0], rtol=1e-8, atol=1e-8)


def test_pinv_rcond_matches_numpy():
    rng = np.random.default_rng(4)
    matrix = rng.normal(size=(8, 17))
    got = mn.linalg.pinv(_arr(matrix), rcond=1e-12)
    ref = np.linalg.pinv(matrix, rcond=1e-12)
    assert got.shape == ref.shape
    assert np.allclose(got.tolist(), ref, rtol=1e-8, atol=1e-8)


def test_einsum_ik_ij_jk():
    rng = np.random.default_rng(5)
    hu = rng.normal(size=(24, 4))
    mat = rng.normal(size=(24, 9))
    gv = rng.normal(size=(9, 4))
    got = mn.einsum("ik,ij,jk->k", _arr(hu), _arr(mat), _arr(gv))
    ref = np.einsum("ik,ij,jk->k", hu, mat, gv)
    assert np.allclose(got.tolist(), ref, rtol=1e-8, atol=1e-8)
    with pytest.raises(NotImplementedError):
        mn.einsum("ij->i", _arr(hu))


def test_norm_float32_keepdims():
    source = np.array([[3, 4], [0, 0]], np.float32)
    got = mn.linalg.norm(_arr(source, "float32"), axis=-1, keepdims=True)
    ref = np.linalg.norm(source, axis=-1, keepdims=True)
    assert got.dtype == "float32"
    assert got.shape == (2, 1)
    assert np.allclose(got.tolist(), ref, rtol=0, atol=0)


def test_zero_division_is_masked_by_where():
    denom = mn.array([0.0, 2.0, 4.0])
    numer = mn.array([1.0, 4.0, 3.0])
    got = mn.where(denom > 0, numer / denom, 0.0)
    assert got.tolist() == [0.0, 2.0, 0.75]
    out = mn.zeros_like(numer)
    mn.divide(numer, denom, out=out, where=denom > 0)
    assert out.tolist() == [0.0, 2.0, 0.75]


def test_packbits_and_unpackbits_little():
    bits = [1, 1, 1, 0, 0, 0, 0, 1]
    assert mn.packbits(mn.array(bits)).tolist() == [225]
    assert np.packbits(np.array(bits)).tolist() == [225]
    raw = mn.array([0b10000001], dtype="uint8")
    assert mn.unpackbits(raw, bitorder="little").tolist() == np.unpackbits(np.array([0b10000001], np.uint8), bitorder="little").tolist()


def test_triu_stable_argsort_and_exact_matmul():
    ii, jj = mn.triu_indices(4, 1)
    rii, rjj = np.triu_indices(4, 1)
    assert ii.tolist() == rii.tolist() and jj.tolist() == rjj.tolist()
    values = [1.0, 0.0, 1.0, 0.0]
    assert mn.argsort(mn.array(values), kind="stable").tolist() == np.argsort(np.array(values), kind="stable").tolist()
    left = np.array([[1.0, 0.0, 1.0], [1.0, 1.0, 0.0]])
    got = _arr(left) @ _arr(left.T)
    assert got.tolist() == (left @ left.T).tolist()


def test_broadcast_add():
    got = mn.array([[1.0], [2.0]]) + mn.array([10.0, 20.0])
    ref = np.array([[1.0], [2.0]]) + np.array([10.0, 20.0])
    assert got.shape == (2, 2)
    assert got.tolist() == ref.tolist()


