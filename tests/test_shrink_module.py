"""scripts/shrink_module.py と、生成した shrink/numpy_min.py の同値性（本物の numpy と比べる）。"""
import importlib.util
import random
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import shrink_module as sm  # noqa: E402

ENTRY = "dragowing/overlap.py:load_overlap"


def _min():
    spec = importlib.util.spec_from_file_location("numpy_min", ROOT / "shrink" / "numpy_min.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_analyze_follows_into_rule_search():
    used, visited = sm.analyze("numpy", [ENTRY])
    assert "pythdragoras/rule_search.py:_masks_to_matrix" in visited
    assert {"asarray", "ones", "flatnonzero", "zeros", "frombuffer", "uint8", "unpackbits"} <= set(used)


def test_generated_file_is_current():
    out = subprocess.run([sys.executable, "scripts/shrink_module.py", "generate", "numpy", ENTRY,
                          "--out", "shrink/numpy_min.py", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr


def test_generate_refuses_unknown_names():
    with pytest.raises(SystemExit, match="linalg.svd"):
        sm.generate_numpy(["linalg.svd"], ["x.py:f"])


np = pytest.importorskip("numpy")


def _same(a, b):
    assert a.shape == b.shape
    assert a.tolist() == b.tolist()


@pytest.mark.parametrize("seed", range(20))
def test_masks_to_matrix_path_matches_numpy(seed):
    """rule_search._masks_to_matrix と同じ手順を両方で行う。"""
    rnd = random.Random(seed)
    n = rnd.randint(1, 70)
    masks = [rnd.getrandbits(n) for _ in range(rnd.randint(1, 4))]
    width = (n + 7) // 8
    buf = b"".join(m.to_bytes(width, "little") for m in masks)
    results = []
    for mod in (np, _min()):
        raw = mod.frombuffer(buf, dtype=mod.uint8).reshape(len(masks), width)
        results.append(mod.unpackbits(raw, axis=1, bitorder="little")[:, :n].astype(bool))
    _same(*results)
    for i in range(len(masks)):
        for j in range(n):
            assert bool(results[0][i, j]) == bool(results[1][i, j])
    _same(np.zeros((len(masks), n), dtype=bool), _min().zeros((len(masks), n), dtype=bool))


@pytest.mark.parametrize("seed", range(20))
def test_region_counting_matches_numpy(seed):
    """overlap.load_overlap の領域の数え方を両方で行う。"""
    rnd = random.Random(seed)
    k, n = rnd.randint(1, 3), rnd.randint(0, 40)
    bits = [[rnd.random() < 0.5 for _ in range(n)] for _ in range(k)]
    for pattern in range(2**k):
        outs = []
        for mod in (np, _min()):
            arr = mod.asarray(bits, dtype=bool)
            selected = mod.ones(n, dtype=bool)
            for i in range(k):
                selected &= arr[i] if pattern >> i & 1 else ~arr[i]
            outs.append(([int(i) for i in mod.flatnonzero(selected)], int(selected.sum())))
        assert outs[0] == outs[1]
