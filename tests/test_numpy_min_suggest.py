"""生成した shrink/numpy_min.py を、queryu/ask/suggest.py が使う範囲で本物の numpy と比べる。

Acceptance v2 checks decomposition correctness, not backend-identical scores/rankings.
See docs/numpy-min-acceptance-v2.md. Historical corpus assertions remain in
scripts/legacy_numpy_min_parity.py; they are not silently marked passed.
"""
import importlib.util
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
np = pytest.importorskip("numpy")


def _load(pure: bool):
    spec = importlib.util.spec_from_file_location(f"numpy_min_{pure}", ROOT / "shrink" / "numpy_min.py")
    mod = importlib.util.module_from_spec(spec)
    old = os.environ.pop("NUMPY_MIN_PURE", None)
    if pure:
        os.environ["NUMPY_MIN_PURE"] = "1"
    try:
        spec.loader.exec_module(mod)
    finally:
        os.environ.pop("NUMPY_MIN_PURE", None)
        if old is not None:
            os.environ["NUMPY_MIN_PURE"] = old
    return mod


# 2つの経路: apt の liblapack3 / libblas3 を ctypes で呼ぶ経路と、標準ライブラリだけの経路。
# ライブラリが無い環境では lapack 経路のテストは飛ばす（CI のライブラリなしレーン）
MODS = {"lapack": _load(False), "stdlib": _load(True)}
backends = pytest.mark.parametrize("backend", ["lapack", "stdlib"])


@pytest.fixture
def mn(backend):
    mod = MODS[backend]
    if backend == "lapack" and mod.BACKEND != "lapack":
        pytest.skip("liblapack3 / libblas3 が見つからない")
    assert mod.BACKEND == backend
    return mod


def test_backend_falls_back_without_libraries(tmp_path):
    """ライブラリが読めないときは標準ライブラリの経路になる（numpy も使わない）。"""
    code = ("import sys, importlib.util\n"
            "sys.modules['numpy'] = None\n"
            f"spec = importlib.util.spec_from_file_location('m', {str(ROOT / 'shrink' / 'numpy_min.py')!r})\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "print(m.BACKEND, m.linalg.norm(m.asarray([3.0, 4.0])))\n")
    env = {**os.environ, "NUMPY_MIN_LAPACK": str(tmp_path / "none.so"), "NUMPY_MIN_BLAS": str(tmp_path / "none.so")}
    env.pop("NUMPY_MIN_PURE", None)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True, env=env)
    assert out.stdout.split() == ["stdlib", "5.0"]


def test_expected_backend_from_ci():
    """CI のレーンが NUMPY_MIN_EXPECT=lapack|stdlib で、どちらの経路になるべきかを渡す。"""
    want = os.environ.get("NUMPY_MIN_EXPECT")
    if not want:
        pytest.skip("NUMPY_MIN_EXPECT が無い（手元の実行）")
    assert MODS["lapack"].BACKEND == want


def _m(mn, value, dtype="float64"):
    return mn.asarray(np.asarray(value).tolist(), dtype=dtype)


def _close(got, want, atol):
    got = np.asarray(got.tolist() if hasattr(got, "tolist") else got, dtype=np.float64)
    want = np.asarray(want, dtype=np.float64)
    assert got.shape == want.shape
    np.testing.assert_allclose(got, want, rtol=0, atol=atol)


@pytest.mark.parametrize("shape", [(5, 3), (3, 7), (6, 6), (4, 450)])
@backends
def test_svd_economy_reconstruction_and_singular_values(mn, backend, shape):
    rnd = np.random.default_rng(sum(shape))
    a = rnd.standard_normal(shape)
    u, s, vt = mn.linalg.svd(_m(mn, a), full_matrices=False)
    _ru, rs, _rvt = np.linalg.svd(a, full_matrices=False)
    _close(s, rs, 1e-9)
    U, S, Vt = (np.asarray(x.tolist()) for x in (u, s, vt))
    np.testing.assert_allclose(U @ np.diag(S) @ Vt, a, rtol=0, atol=1e-9)
    np.testing.assert_allclose(U.T @ U, np.eye(U.shape[1]), rtol=0, atol=1e-9)
    # 行は正規直交
    np.testing.assert_allclose(Vt @ Vt.T, np.eye(Vt.shape[0]), rtol=0, atol=1e-9)


@backends
def test_norm_axis_keepdims_and_divide_where(mn, backend):
    a = np.array([[3.0, 4.0], [0.0, 0.0], [1.0, 2.0]], dtype=np.float32)
    for kw in ({}, {"axis": -1}, {"axis": -1, "keepdims": True}, {"axis": 0}):
        _close(mn.linalg.norm(_m(mn, a, "float32"), **kw), np.linalg.norm(a, **kw), 1e-6)
    n = np.linalg.norm(a, axis=-1, keepdims=True)
    want = np.divide(a, n, out=np.zeros_like(a), where=n > 0)
    mnn = mn.linalg.norm(_m(mn, a, "float32"), axis=-1, keepdims=True)
    got = mn.divide(_m(mn, a, "float32"), mnn, out=mn.zeros_like(_m(mn, a, "float32")), where=mnn > 0)
    _close(got, want, 1e-6)


@backends
def test_argsort_stable_keeps_ties_in_order(mn, backend):
    vals = [0.5, 0.25, 0.5, 0.5, 0.125, 0.25]
    _close(mn.argsort(-_m(mn, vals), kind="stable"), np.argsort(-np.asarray(vals), kind="stable"), 0)


@pytest.mark.parametrize("seed", range(5))
@backends
def test_packbits_sign_astype(mn, backend, seed):
    rnd = random.Random(seed)
    width = rnd.randint(1, 19)
    a = [[rnd.choice([-1.5, 0.0, 2.0]) for _ in range(width)] for _ in range(3)]
    s, rs = mn.sign(_m(mn, a)), np.sign(np.asarray(a))
    _close(s, rs, 0)
    assert mn.packbits(s > 0, axis=1).tolist() == np.packbits(rs > 0, axis=1).tolist()
    assert s.astype(mn.int8).tolist() == rs.astype(np.int8).tolist()
    _close(mn.abs(_m(mn, a)).mean(0), np.abs(np.asarray(a)).mean(0), 1e-12)


@backends
def test_log_nan_to_num_and_transpose(mn, backend):
    x = np.array([1.0, 2.0, 3.5], dtype=np.float32)
    _close(mn.log(_m(mn, x, "float32")), np.log(x), 1e-6)
    v = [float("nan"), float("inf"), -float("inf"), 0.5]
    kw = dict(nan=-np.inf, posinf=np.inf, neginf=-np.inf)
    got = mn.nan_to_num(_m(mn, v), nan=-mn.inf, posinf=mn.inf, neginf=-mn.inf).tolist()
    assert got == np.nan_to_num(np.asarray(v), **kw).tolist()
    m = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    assert _m(mn, m).T.tolist() == np.asarray(m).T.tolist()




@backends
@pytest.mark.parametrize("left,right", [((3, 0), (0, 2)), ((0, 3), (3, 2)), ((3, 2), (2, 0)), ((2, 0), (0,))])
@pytest.mark.parametrize("dtype", ["float32", "float64"])
def test_matmul_with_empty_dimension_matches_numpy(mn, backend, left, right, dtype):
    """次元が 0 の行列積は BLAS を呼ばずにゼロを返す（cblas は lda=0 で xerbla が exit してしまう）。"""
    want = np.zeros(left, dtype=dtype) @ np.zeros(right, dtype=dtype)
    got = mn.zeros(left, dtype=dtype) @ mn.zeros(right, dtype=dtype)
    assert got.shape == want.shape and got.dtype == want.dtype.name
    assert got.tolist() == want.tolist()


@backends
def test_empty_matmul_does_not_kill_the_process(mn, backend):
    """BLAS が exit すると例外にならず終了コード 0 で抜けるので、別プロセスで最後の行まで届くかを見る。"""
    code = ("import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('m', {str(ROOT / 'shrink' / 'numpy_min.py')!r})\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "print(m.BACKEND)\n"
            "for l, r in [((3, 0), (0, 2)), ((0, 3), (3, 2)), ((2, 0), (0,))]:\n"
            "    (m.zeros(l) @ m.zeros(r)).tolist()\n"
            "print('reached-end')\n")
    env = {k: v for k, v in os.environ.items() if k != "NUMPY_MIN_PURE"}
    if backend == "stdlib":
        env["NUMPY_MIN_PURE"] = "1"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    assert out.stdout.split() == [backend, "reached-end"], out.stdout + out.stderr
    assert "illegal" not in (out.stdout + out.stderr)


@backends
@pytest.mark.parametrize("dtype", ["float32", "float64"])
def test_svd_singular_values_only_matches_numpy(mn, backend, dtype):
    x = np.asarray(random.Random(3).choices(range(-9, 10), k=35), dtype=dtype).reshape(7, 5) / 3
    want = np.linalg.svd(x, compute_uv=False)
    got = mn.linalg.svd(_m(mn, x, dtype), full_matrices=False, compute_uv=False)
    assert got.dtype == dtype
    _close(got, want, 1e-5 if dtype == "float32" else 1e-12)


def test_lapack_info_sign_gives_distinct_errors(monkeypatch):
    """info<0 は引数の誤り（LinAlgIllegalArgument）、info>0 は収束しなかった（ValueError）。"""
    mod = _load(False)

    class Fake:
        def __init__(self, value):
            self.value = value

        def dgesdd_(self, *args):
            args[13]._obj.value = self.value  # info

    a = mod.asarray([[1.0, 2.0], [3.0, 4.0]])
    monkeypatch.setattr(mod, "_lapack", Fake(-4))
    with pytest.raises(mod.LinAlgIllegalArgument, match="argument 4 had an illegal value"):
        mod._svd_lapack(a, True)
    monkeypatch.setattr(mod, "_lapack", Fake(2))
    with pytest.raises(ValueError, match="did not converge") as err:
        mod._svd_lapack(a, True)
    assert not isinstance(err.value, mod.LinAlgIllegalArgument)


@backends
def test_integer_matmul_uses_builtin_round(mn, backend):
    dtype = "int64"
    left, right = [[1, 2], [3, 4]], [[5], [6]]
    got = mn.asarray(left, dtype=dtype) @ mn.asarray(right, dtype=dtype)
    want = np.asarray(left, dtype=dtype) @ np.asarray(right, dtype=dtype)
    assert got.tolist() == want.tolist()
    assert got.dtype == want.dtype.name


@pytest.mark.parametrize("values", [
    [[0.0, 0.0], [0.0, 0.0]],
    [[1.0, 0.0], [0.0, 0.0]],
    [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
    [[1.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
])
@pytest.mark.parametrize("algorithm", ["_svd_onesided", "_svd_gram"])
def test_exact_zero_singular_vectors_are_orthonormal(values, algorithm):
    """Reconstruction alone cannot detect zero-filled null-space vectors."""
    a = np.asarray(values)
    rows, cols = a.shape
    k = min(rows, cols)
    u, s, vt = getattr(MODS["stdlib"], algorithm)(a.ravel().tolist(), rows, cols)
    U, S, Vt = np.asarray(u).reshape(rows, k), np.asarray(s), np.asarray(vt).reshape(k, cols)
    np.testing.assert_allclose(U.T @ U, np.eye(k), rtol=0, atol=1e-12)
    np.testing.assert_allclose(Vt @ Vt.T, np.eye(k), rtol=0, atol=1e-12)
    np.testing.assert_allclose(U @ np.diag(S) @ Vt, a, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(S, np.linalg.svd(a, compute_uv=False))


def test_zero_completion_preserves_existing_directions():
    values = [0.6, 0.0, 0.8, 0.0, 0.0, 0.0]
    original = values[::2]
    MODS["stdlib"]._complete_zero_columns(values, 3, 2, [1])
    assert values[::2] == original
    q = np.asarray(values).reshape(3, 2)
    np.testing.assert_allclose(q.T @ q, np.eye(2), rtol=0, atol=1e-12)


@backends
@pytest.mark.parametrize("dtype", ["float32", "float64"])
@pytest.mark.parametrize("scale", [0.125, 1.0, 8.0])
@pytest.mark.parametrize("values,exact_values", [
    ([[3., 0.], [0., 1.]], [3., 1.]),
    ([[1., 0.], [0., 1.]], [1., 1.]),  # repeated values: do not compare vectors
    ([[1., 0.], [0., 0.]], [1., 0.]),
    ([[0., 0.], [0., 0.]], [0., 0.]),
    ([[3., 0., 0.], [0., 1., 0.]], [3., 1.]),
    ([[3., 0.], [0., 1.], [0., 0.]], [3., 1.]),
    ([[3., 4.], [0., 0.]], [5., 0.]),
    ([[3., 0.], [4., 0.], [0., 0.]], [5., 0.]),
])
def test_v2_scaled_decomposition_contract(mn, backend, dtype, scale, values, exact_values):
    """Predeclared normalized-residual policy, not a fitted corpus maximum."""
    a = np.asarray(values, dtype=dtype) * scale
    u, s, vt = mn.linalg.svd(_m(mn, a, dtype), full_matrices=False)
    U, S, Vt = (np.asarray(x.tolist(), dtype=np.float64) for x in (u, s, vt))
    k = min(a.shape)
    assert all(x.dtype == dtype for x in (u, s, vt))
    assert U.shape == (a.shape[0], k) and Vt.shape == (k, a.shape[1])
    assert np.isfinite(U).all() and np.isfinite(S).all() and np.isfinite(Vt).all()
    assert np.all(S >= 0) and np.all(S[:-1] >= S[1:])
    eps = np.finfo(dtype).eps
    budget = 32 * max(a.shape) * eps
    norm_a = float(np.linalg.norm(a.astype(np.float64), ord=1))
    residual = float(np.linalg.norm(U @ np.diag(S) @ Vt - a, ord=1))
    if norm_a == 0:
        assert residual == 0 and np.all(S == 0)
    else:
        assert residual / norm_a <= budget
    assert np.linalg.norm(U.T @ U - np.eye(k), ord=1) <= budget
    assert np.linalg.norm(Vt @ Vt.T - np.eye(k), ord=1) <= budget
    # Exact singular values of these diagonal/rectangular fixtures, not a backend oracle.
    exact = np.asarray(exact_values) * scale
    assert np.max(np.abs(S - exact), initial=0) <= budget * norm_a


def test_v2_binary_rotation_counterexample_is_retained():
    """Exact-arithmetic mechanism behind the saved three-document observation."""
    z = np.eye(2)
    query = np.asarray([1., 0.])
    rotation = np.asarray([[0.6, 0.8], [-0.8, 0.6]])

    def score(rows, q):
        signs = np.sign(rows)
        signs[signs == 0] = 1
        scales = np.abs(rows).mean(0)
        return ((signs * scales) @ q) / np.linalg.norm(scales)

    np.testing.assert_allclose(z @ z.T, (z @ rotation) @ (z @ rotation).T, atol=1e-15)
    # Same Gram/float geometry does NOT imply the same compressed binary scores.
    assert not np.allclose(score(z, query), score(z @ rotation, query @ rotation))
