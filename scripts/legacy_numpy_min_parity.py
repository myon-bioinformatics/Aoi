"""Archived v1 corpus compatibility test, NOT a v2 acceptance gate.

Manual reproduction only: pytest scripts/legacy_numpy_min_parity.py -s
This executes the corpus comparison; do not run without measurement authorization.
Original assertions/thresholds from 0284b2198077d9b8c04b3cffde1b36b8e75961b6 are preserved verbatim below.
A v2 CI pass does not mean this historical comparison passes.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
np = pytest.importorskip("numpy")


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
        "out = {'numpy': numpy.__name__ + ':' + str(getattr(numpy, '__version__', '')), 'runs': [],\n"
        "       'backend': getattr(numpy, 'BACKEND', 'numpy')}\n"
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
    # numpy の wheel の OpenBLAS は CPU ごとに計算核を選び、float32 の丸めが runner の CPU で変わる
    # （AVX-512 の SkylakeX と AVX2 の Haswell で実測の最大差が違った）。比べる相手を揃えるため Haswell に固定する
    ref_env = {**os.environ, "OPENBLAS_CORETYPE": "Haswell", "OPENBLAS_NUM_THREADS": "1"}
    real = subprocess.run([sys.executable, str(script), str(ROOT)], capture_output=True, text=True, check=True,
                          env=ref_env)
    shim = tmp_path / "shim"
    shim.mkdir()
    (shim / "numpy.py").write_text((ROOT / "shrink" / "numpy_min.py").read_text(encoding="utf-8"), encoding="utf-8")
    got = subprocess.run([sys.executable, str(script), str(ROOT)], capture_output=True, text=True, check=True,
                         env={"PYTHONPATH": str(shim), "PATH": "",
                              **{k: os.environ[k] for k in ("NUMPY_MIN_PURE",) if k in os.environ}})
    a, b = json.loads(real.stdout), json.loads(got.stdout)
    assert b["numpy"].endswith(":0+min")
    assert a["bits_shape"] == b["bits_shape"]
    # 許容誤差は numpy 2.5.4（uv.lock、OPENBLAS_CORETYPE=Haswell）と比べた実測の最大値そのもの（丸めない）。
    # lapack: float32 の SVD は numpy と同じ sgesdd だが、numpy の wheel は OpenBLAS の sgesdd、
    # こちらは Debian の参照 LAPACK 3.12.1 の sgesdd。float32 の計算順の違いが Zf とスコアに出る
    # （dgesdd で解いて float32 に戻していたときは、スコア差の最大 1.41833292e-06 だった）。
    # stdlib: float64 で解いて float32 に戻す。
    gram_atol, score_atol = {
        "lapack": (6.08561626694315e-06, 7.598784890094912e-06),
        "stdlib": (9.38496750535478e-07, 6.854534149169922e-07),
    }[b["backend"]]
    gram_max = float(np.max(np.abs(np.asarray(b["gram"]) - np.asarray(a["gram"]))))
    score_max = max(abs(p[1] - q[1]) for x, y in zip(a["runs"], b["runs"]) for p, q in zip(x, y))
    print("numpy_min measured", b["backend"], "gram_max", repr(gram_max), "score_max", repr(score_max))
    np.testing.assert_allclose(b["gram"], a["gram"], rtol=0, atol=gram_atol)
    for x, y in zip(a["runs"], b["runs"], strict=True):
        assert [i for i, _ in x] == [i for i, _ in y]
        np.testing.assert_allclose([s for _, s in y], [s for _, s in x], rtol=0, atol=score_atol)
