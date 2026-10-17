"""保証付き枝刈りは既定ではオフで、オンにしたときの上位は厳密計算と一致する。"""

from pathlib import Path

import numpy as np
import polars as pl
import pytest

import rule_search as rs
from littlebit_prune import mcc_upper
from rule_search import search

import aoi_paths

ROOT = aoi_paths.resolve_aoi_root(anchor=Path(__file__))
CYCLE = aoi_paths.resolve_cycle_path(ROOT)

ROWS = [
    ("a", 40, 1, 2.0, True), ("b", 10, 3, -5.0, False), ("c", -20, 2, 4.0, True),
    ("d", -60, 5, 1.0, False), ("e", 5, 3, 0.5, True), ("f", -10, 6, -1.0, False),
    ("g", 30, 2, -6.0, False), ("h", -30, 5, 3.0, False), ("i", 60, 1, 0.0, True),
]
DF = pl.DataFrame([{"rd": rd, "rank_ra": ra, "wins_vs_pythag": w, "upper_half": u} for _, rd, ra, w, u in ROWS])
TARGET = [{"col": "upper_half", "op": "==", "value": False}]
CANDS = [{"col": "rd", "op": "<", "value": 0}, {"col": "rank_ra", "op": ">=", "value": 4},
         {"col": "wins_vs_pythag", "op": "<", "value": -4}, {"col": "rd", "op": "<", "value": 20}]


def ranking(rows):
    return [(round(r["mcc"], 12), r["conditions"], r["tp"], r["fp"], str(r["if_any"])) for r in rows]


def test_prune_is_off_by_default(monkeypatch):
    def boom(*_a, **_k):
        raise AssertionError("littlebit が既定で呼ばれた")

    monkeypatch.setattr("littlebit_prune.search_guaranteed", boom)
    got = search(DF, TARGET, CANDS, top=5)
    assert ranking(got) == ranking(search(DF, TARGET, CANDS, top=5, backend="bitset"))


def test_small_table_matches_bitset():
    exact = search(DF, TARGET, CANDS, max_terms=2, max_conds=2, top=20, backend="bitset")
    for rank, stages in ((2, 1), (8, 2)):
        assert ranking(search(DF, TARGET, CANDS, top=20, prune="littlebit", rank=rank, stages=stages)) == ranking(exact)
    with pytest.raises(rs.PropositionError):
        search(DF, TARGET, CANDS, max_terms=3, prune="littlebit")


def random_case(seed, n=48, ncol=4, ncand=8):
    rng = np.random.default_rng(seed)
    cols = {f"c{j}": rng.integers(0, 5, n) for j in range(ncol)}
    cols["y"] = rng.random(n) < 0.5
    cands = [{"col": f"c{int(rng.integers(ncol))}", "op": "<", "value": int(rng.integers(1, 5))} for _ in range(ncand)]
    return pl.DataFrame(cols), cands


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("top", [1, 5])
@pytest.mark.parametrize("rank", [1, 4])
def test_random_guaranteed_matches_bitset(seed, top, rank):
    df, cands = random_case(seed)
    target = [{"col": "y", "op": "==", "value": True}]
    exact = search(df, target, cands, 2, 2, top, backend="bitset")
    got = search(df, target, cands, 2, 2, top, prune="littlebit", rank=rank, stages=2)
    assert ranking(got) == ranking(exact)


def test_real_season_matches_bitset():
    import tomllib

    from pythdragoras import apply_exclusions

    cfg = tomllib.loads((CYCLE / "analysis.toml").read_text(encoding="utf-8"))
    spec = tomllib.loads((CYCLE / "rule_candidates.toml").read_text(encoding="utf-8"))
    st = pl.read_ndjson(CYCLE / "outputs" / "season.jsonl")
    st, _ = apply_exclusions(st, cfg.get("exclude", []))
    cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
    usable = st.drop_nulls(cols)
    kw = dict(max_terms=int(spec["max_terms"]), max_conds=int(spec["max_conds"]), top=20)
    exact = search(usable, spec["target"], spec["candidate"], backend="bitset", **kw)
    got = search(usable, spec["target"], spec["candidate"], prune="littlebit", rank=8, stages=2, **kw)
    assert ranking(got) == ranking(exact)


def test_mcc_upper_is_an_upper_bound():
    rng = np.random.default_rng(0)
    for _ in range(300):
        n_pos, n_neg = int(rng.integers(1, 40)), int(rng.integers(1, 40))
        tl, fl = int(rng.integers(0, n_pos + 1)), int(rng.integers(0, n_neg + 1))
        th, fh = int(rng.integers(tl, n_pos + 1)), int(rng.integers(fl, n_neg + 1))
        tp, fp = np.meshgrid(np.arange(tl, th + 1), np.arange(fl, fh + 1))
        true_max = rs._mcc_vec(tp.ravel().astype(float), fp.ravel().astype(float), n_pos, n_neg).max()
        ub = mcc_upper(np.array([tl]), np.array([th]), np.array([fl]), np.array([fh]), n_pos, n_neg)[0]
        assert ub >= true_max - 1e-9


def test_zero_units_matches_exact():
    empty = DF.clear()
    exact = search(empty, TARGET, CANDS, top=20, backend="bitset")
    assert exact and all(r["tp"] == r["fp"] == r["fn"] == r["tn"] == 0 for r in exact)
    assert ranking(search(empty, TARGET, CANDS, top=20, prune="littlebit")) == ranking(exact)


@pytest.mark.parametrize("backend", ["bitset", "bitmatrix"])
def test_prune_and_backend_together_is_an_error(backend):
    with pytest.raises(ValueError, match="同時に指定できない"):
        search(DF, TARGET, CANDS, prune="littlebit", backend=backend)


def test_prune_respects_matrix_memory_cap(monkeypatch):
    def boom(*_a, **_k):
        raise AssertionError("上限を超えたのに littlebit が呼ばれた")

    monkeypatch.setattr("littlebit_prune.search_guaranteed", boom)
    monkeypatch.setattr(rs, "_MATRIX_BYTES", 1)
    with pytest.raises(rs.PropositionError, match="見積りメモリ"):
        search(DF, TARGET, CANDS, prune="littlebit")


def test_all_ties_bound_retained_result_rows(monkeypatch):
    import littlebit_prune as lp

    class TrackedRow(dict):
        live = peak = 0

        def __init__(self, row):
            super().__init__(row)
            type(self).live += 1
            type(self).peak = max(type(self).peak, type(self).live)

        def __del__(self):
            type(self).live -= 1

    original = lp._record

    def tracked(*args):
        key, row = original(*args)
        return key, TrackedRow(row)

    cands = [{"col": f"c{i}", "op": "==", "value": 1} for i in range(32)]
    df = pl.DataFrame({**{f"c{i}": [1, 1] for i in range(32)}, "y": [True, True]})
    target = [{"col": "y", "op": "==", "value": True}]
    expected = search(df, target, cands, max_conds=1, top=3, backend="bitset")
    monkeypatch.setattr(lp, "_record", tracked)
    actual = search(df, target, cands, max_conds=1, top=3, prune="littlebit")
    assert actual == expected
    assert TrackedRow.peak <= 5
