"""Aoi が生成した shrink/numpy_min.py を、本物の numpy のビット行列と比べる。"""
import importlib.util
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SURFACE = ("asarray", "flatnonzero", "frombuffer", "ones", "uint8", "unpackbits", "zeros")


def _min():
    path = ROOT / "shrink" / "numpy_min.py"
    spec = importlib.util.spec_from_file_location("numpy_min_under_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["numpy_min_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _same(left, right):
    assert left.shape == right.shape
    assert left.tolist() == right.tolist()


def test_ported_file_names_the_overlap_surface():
    text = (ROOT / "shrink" / "numpy_min.py").read_text(encoding="utf-8")
    assert "手で直さない" in text
    assert "load_overlap" in text
    header = text.split("使う名前:", 1)[1].split('"""', 1)[0]
    for name in SURFACE:
        assert name in header
    module = _min()
    for name in (*SURFACE, "ndarray"):
        assert hasattr(module, name)


def test_masks_to_matrix_path_matches_numpy():
    """rule_search._masks_to_matrix と同じ手順を両方で行う。"""
    for seed in range(20):
        rnd = random.Random(seed)
        n = rnd.randint(1, 70)
        masks = [rnd.getrandbits(n) for _ in range(rnd.randint(1, 4))]
        width = (n + 7) // 8
        buf = b"".join(m.to_bytes(width, "little") for m in masks)
        minimal = _min()
        results = []
        for mod in (np, minimal):
            raw = mod.frombuffer(buf, dtype=mod.uint8).reshape(len(masks), width)
            results.append(mod.unpackbits(raw, axis=1, bitorder="little")[:, :n].astype(bool))
        _same(*results)
        for i in range(len(masks)):
            for j in range(n):
                assert bool(results[0][i, j]) == bool(results[1][i, j])
        _same(np.zeros((len(masks), n), dtype=bool), minimal.zeros((len(masks), n), dtype=bool))


def test_region_counting_matches_numpy():
    """overlap.load_overlap の領域の数え方を両方で行う。"""
    for seed in range(20):
        rnd = random.Random(seed)
        k, n = rnd.randint(1, 3), rnd.randint(0, 40)
        bits = [[rnd.random() < 0.5 for _ in range(n)] for _ in range(k)]
        minimal = _min()
        for pattern in range(2**k):
            outs = []
            for mod in (np, minimal):
                arr = mod.asarray(bits, dtype=bool)
                selected = mod.ones(n, dtype=bool)
                for i in range(k):
                    selected &= arr[i] if pattern >> i & 1 else ~arr[i]
                outs.append(([int(i) for i in mod.flatnonzero(selected)], int(selected.sum())))
            assert outs[0] == outs[1]
