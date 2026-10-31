"""生成した shrink/numpy_min.py を、queryu/ask/suggest.py が使う範囲で本物の numpy と比べる。

SVD は符号が決まらないので、再構成 U·diag(S)·Vt と特異値（端から端までは Zf·Zfᵀ）で比べる。許容誤差はそれぞれの assert に明記する。
実データの端から端までの比較は、c001 の命題の先頭 40 件だけ（全件は CPython で数分かかる）。
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


def test_suggest_on_c001_subset_matches_numpy(tmp_path):
    """suggest.Index を c001 の命題の先頭 40 件で、本物の numpy と numpy_min で作って比べる。"""
    script = tmp_path / "run.py"
    script.write_text(
        "import json, sys\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, str(Path(sys.argv[1]) / 'queryu' / 'ask'))\n"
        "import numpy, suggest\n"
        "docs = suggest.load_docs(Path(sys.argv[1]) / 'cycles/c001-chunichi/outputs')[:40]\n"
        "qs = ['得失点差がプラスなら上位か', '連勝が続くと首位になるか', 'ホームで勝つ確率']\n"
        "out = {'numpy': numpy.__name__ + ':' + str(getattr(numpy, '__version__', '')), 'runs': []}\n"
        "for dim in (8, 32):\n"
        "    idx = suggest.Index(docs, dim=dim)\n"
        "    for mode in ('float', 'binary'):\n"
        "        for q in qs:\n"
        "            out['runs'].append(idx.query(q, mode, 5))\n"
        "    # SVD の各次元の符号は決まらないので、符号に依らない Zf·Zfᵀ と bits の大きさで比べる\n"
        "    z = idx.Zf.tolist()\n"
        "    out.setdefault('gram', []).append([[sum(p * q for p, q in zip(r, t)) for t in z] for r in z])\n"
        "    out.setdefault('bits_shape', []).append(list(idx.bits.shape))\n"
        "print(json.dumps(out))\n",
        encoding="utf-8",
    )
    real = subprocess.run([sys.executable, str(script), str(ROOT)], capture_output=True, text=True, check=True)
    shim = tmp_path / "shim"
    shim.mkdir()
    (shim / "numpy.py").write_text((ROOT / "shrink" / "numpy_min.py").read_text(encoding="utf-8"), encoding="utf-8")
    got = subprocess.run([sys.executable, str(script), str(ROOT)], capture_output=True, text=True, check=True,
                         env={"PYTHONPATH": str(shim), "PATH": "",
                              **{k: os.environ[k] for k in ("NUMPY_MIN_PURE",) if k in os.environ}})
    a, b = json.loads(real.stdout), json.loads(got.stdout)
    assert b["numpy"].endswith(":0+min")
    assert a["bits_shape"] == b["bits_shape"]
    # Zf は float32。32 次元の内積に積もる丸め分（実測の最大 1.87122308e-06）まで許す
    np.testing.assert_allclose(b["gram"], a["gram"], rtol=0, atol=5e-6)
    for x, y in zip(a["runs"], b["runs"], strict=True):
        assert [i for i, _ in x] == [i for i, _ in y]
        # float32 の丸め分だけ違ってよい（lapack 経路の実測の最大 1.41833292e-06）
        np.testing.assert_allclose([s for _, s in y], [s for _, s in x], rtol=0, atol=5e-6)
