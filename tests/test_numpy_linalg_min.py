"""shrink/numpy_linalg_min.py を本物の numpy と、c001 より小さい行列で比べる。

c001 全体の SVD はこのファイルでは走らせない。
"""
import importlib.util
import ast
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import linalg_feasibility as lf  # noqa: E402

np = pytest.importorskip("numpy")


def _load():
    spec = importlib.util.spec_from_file_location("numpy_linalg_min", ROOT / "shrink" / "numpy_linalg_min.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mn = _load()


def _arr(value, dtype="float64"):
    return mn.array(np.asarray(value).tolist(), dtype=dtype)


def test_numpy_min_is_the_generated_file():
    # numpy_min.py は生成物。load_overlap と suggest の2つの入口から作る（手では直さない）
    text = (ROOT / "shrink" / "numpy_min.py").read_text(encoding="utf-8")
    assert text.startswith("\"\"\"numpy の最小版。scripts/shrink_module.py が生成した。手で直さない。")
    assert "入口: dragowing/overlap.py:load_overlap, queryu/ask/suggest.py:suggest\n" in text
    assert "staticmethod(svd)" in text and "staticmethod(norm)" in text
    assert "def lstsq(" not in text and "def einsum(" not in text


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


def test_ast_reaches_the_heavy_calls_and_not_bitmatrix_svd():
    found = lf.analyze(lf.ENTRIES)
    suggest = found["queryu/ask/suggest.py:Index"]["uses"]
    assert "linalg.svd" in suggest and "linalg.norm" in suggest
    little = {}
    for key in (
        "pythdragoras/littlebit_prune.py:littlebit",
        "pythdragoras/littlebit_prune.py:overlap_bounds",
        "pythdragoras/littlebit_prune.py:search_guaranteed",
    ):
        little.update(found[key]["uses"])
    assert {"linalg.svd", "linalg.lstsq", "einsum"} <= set(little)
    assert "linalg.pinv" in found["pythdragoras/littlebit_holdout.py:fit"]["uses"]
    bit = found["pythdragoras/rule_search.py:_search_bitmatrix"]["uses"]
    for name in ("linalg.svd", "linalg.lstsq", "linalg.pinv", "einsum"):
        assert name not in bit
    visited = found["queryu/ask/suggest.py:suggest"]["visited"]
    assert any(item.endswith("Index.__init__") for item in visited)
    assert any(item.endswith("Index.query") for item in visited)


def test_absent_probe_runs_queryu_index_without_numpy():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "linalg_feasibility.py"), "absent"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "ran without touching numpy" in proc.stdout


def test_absent_probe_fails_if_queryu_imports_numpy(tmp_path):
    """QueRyu が import numpy に戻ったら probe が失敗することを確かめる。"""
    import shutil
    work = tmp_path / "repo"
    for part in ("scripts", "queryu", "pythdragoras", "vendor"):
        if (ROOT / part).exists():
            shutil.copytree(ROOT / part, work / part)
    target = work / "queryu" / "ask" / "suggest.py"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace("np = _load_numpy_min()", "import numpy as np", 1), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(work / "scripts" / "linalg_feasibility.py"), "absent"],
        cwd=work, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "touched numpy" in proc.stderr


def test_min_refuses_when_numpy_is_installed(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "shrink" / "run_linalg.py"), "--numpy", "min", "--scope", "fixture",
         str(tmp_path / "out.json")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert proc.returncode != 0
    assert "numpy が入っている" in proc.stderr


@pytest.fixture(scope="module", params=["auto", "stdlib"])
def fixture_payloads(tmp_path_factory, request):
    tmp_path = tmp_path_factory.mktemp("linalg-" + request.param)
    script = str(ROOT / "shrink" / "run_linalg.py")
    real = tmp_path / "real.json"
    got = tmp_path / "got.json"
    first = subprocess.run(
        [sys.executable, script, "--numpy", "real", "--scope", "fixture", str(real)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert first.returncode == 0, first.stderr
    second = subprocess.run(
        [sys.executable, script, "--numpy", "min", "--allow-installed", "--scope", "fixture", str(got)],
        cwd=ROOT, capture_output=True, text=True, check=False,
        env={**os.environ, "NUMPY_MIN_PURE": "1" if request.param == "stdlib" else ""},
    )
    assert second.returncode == 0, second.stderr
    assert second.stdout.strip().endswith("numpy_linalg_min.py") or "numpy_linalg_min.py" in second.stdout
    compared = subprocess.run(
        [sys.executable, script, "--compare", str(real), str(got)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert compared.returncode == 0, compared.stdout + compared.stderr



    return json.loads(real.read_text()), json.loads(got.read_text())


def _harness():
    spec = importlib.util.spec_from_file_location("test_run_linalg", ROOT / "shrink" / "run_linalg.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_fixture_code_paths_match_numpy(fixture_payloads):
    real, mini = fixture_payloads
    harness = _harness()
    assert harness.compare(real, mini) == []
    for consumer, operations in harness.REQUIRED_CALLS.items():
        r = real["backend_evidence"]["consumers"][consumer]
        m = mini["backend_evidence"]["consumers"][consumer]
        assert r["identity"]["kind"] == "real"
        assert r["identity"]["sha256"] != m["identity"]["sha256"]
        for op in operations:
            assert r["calls"][op] > 0 and m["calls"][op] > 0
    assert mini["backend_evidence"]["consumers"]["suggest"]["identity"]["file"].endswith("queryu/vendor/aoi/shrink/numpy_min.py")


@pytest.mark.parametrize("damage", ["same-real", "same-min", "missing", "missing-consumer", "zero-call", "missing-call", "bool-call", "fake-kind", "fake-hash", "fake-module", "fake-mini-module", "fake-mini-version", "wrong-suggest"])
def test_compare_rejects_invalid_execution_evidence(fixture_payloads, damage):
    real, mini = copy.deepcopy(fixture_payloads)
    if damage == "same-real":
        mini = copy.deepcopy(real)
    elif damage == "same-min":
        real = copy.deepcopy(mini)
    elif damage == "missing":
        del mini["backend_evidence"]
    elif damage == "missing-consumer":
        del mini["backend_evidence"]["consumers"]["suggest"]
    else:
        row = mini["backend_evidence"]["consumers"]["suggest"]
        if damage == "zero-call":
            row["calls"]["linalg.svd"] = 0
        elif damage == "missing-call":
            del row["calls"]["linalg.svd"]
        elif damage == "bool-call":
            row["calls"]["linalg.svd"] = True
        elif damage == "fake-kind":
            row["identity"]["kind"] = "real"
        elif damage == "fake-hash":
            row["identity"]["sha256"] = "0" * 64
        elif damage == "fake-module":
            real["backend_evidence"]["consumers"]["suggest"]["identity"]["module"] = "queryu_numpy_min"
        elif damage == "fake-mini-module":
            row["identity"]["module"] = "unrelated"
        elif damage == "fake-mini-version":
            row["identity"]["version"] = ""
        elif damage == "wrong-suggest":
            row["identity"] = copy.deepcopy(mini["backend_evidence"]["consumers"]["harness"]["identity"])
    assert _harness().compare(real, mini)


@pytest.mark.parametrize("loader", ["_load_numpy_metadata", "_load_numpy_min_fake", "_load_numpy_min"])
def test_ast_does_not_infer_numpy_from_loader_name(loader):
    tree = ast.parse(f"def {loader}(): return object()\nnp = {loader}()\ndef run(): return np.linalg.svd([])\n")
    module = lf._Module(Path("unrelated.py"), tree)
    assert not module.numpy_aliases


def test_ast_keeps_ordinary_numpy_aliases():
    module = lf._Module(Path("ordinary.py"), ast.parse("import numpy as num\nfrom numpy.linalg import svd as decompose\n"))
    assert module.numpy_aliases == {"num"}
    assert module.numpy_names == {"decompose": "linalg.svd"}


def test_real_collection_rebinds_production_suggest_and_restores_it(monkeypatch):
    harness = _harness()
    harness._prepare("real", allow_installed=True)
    import suggest
    import littlebit_prune
    original = suggest.np
    assert original is not np
    observed = {}
    def check(scope, backend, lp, rs, module):
        observed["suggest"] = module.np._source
        observed["littlebit"] = lp.np._source
        raise RuntimeError("stop before numerical work")
    monkeypatch.setattr(harness, "_collect", check)
    with pytest.raises(RuntimeError, match="stop before"):
        harness.collect("fixture", "real")
    assert observed == {"suggest": np, "littlebit": np}
    assert suggest.np is original
    assert littlebit_prune.np is np


def test_ast_rejects_decoy_loader_with_supported_names_in_dead_code():
    tree = ast.parse((ROOT / "queryu" / "ask" / "suggest.py").read_text())
    loader = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_load_numpy_min")
    loader.body = [ast.If(test=ast.Constant(False), body=loader.body, orelse=[]),
                   ast.Return(value=ast.Call(func=ast.Name(id="object", ctx=ast.Load()), args=[], keywords=[]))]
    assert not lf._vendored_numpy_loader(tree)
    assert not lf._Module(Path("decoy.py"), tree).numpy_aliases
