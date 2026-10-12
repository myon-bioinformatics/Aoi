"""ビット行列の数え方が、Python 整数のビット集合と上位の並びまで一致すること。

並べる鍵は MCC（小数第12位で丸める）→ 条件の少なさ → 式の文字列。
実データはリポジトリ内の cycles/c001-chunichi だけを読む。NPB には取りに行かない。
"""

import json
from pathlib import Path

import numpy as np
import polars as pl
import pytest

import rule_search as rs
from rule_search import rule_text, search

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "cycles" / "c001-chunichi"

ROWS = [
    ("a", 2020, 40, 1, 2.0, True), ("b", 2020, 10, 3, -5.0, False), ("c", 2020, -20, 2, 4.0, True),
    ("d", 2020, -60, 5, 1.0, False), ("e", 2020, 5, 3, 0.5, True), ("f", 2020, -10, 6, -1.0, False),
    ("g", 2021, 30, 2, -6.0, False), ("h", 2021, -30, 5, 3.0, False), ("i", 2021, 60, 1, 0.0, True),
]
DF = pl.DataFrame([{"team": t, "season": s, "rd": rd, "rank_ra": ra, "wins_vs_pythag": w, "upper_half": u}
                   for t, s, rd, ra, w, u in ROWS])
TARGET = [{"col": "upper_half", "op": "==", "value": False}]
CANDS = [{"col": "rd", "op": "<", "value": 0}, {"col": "rank_ra", "op": ">=", "value": 4},
         {"col": "wins_vs_pythag", "op": "<", "value": -4}, {"col": "rd", "op": "<", "value": 20},
         {"col": "rank_ra", "op": ">=", "value": 3}, {"col": "wins_vs_pythag", "op": "<", "value": 0}]


def ranking(rows):
    return [(round(r["mcc"], 12), r["conditions"], rule_text(r), r["tp"], r["fp"], r["fn"], r["tn"],
             r["precision"], r["recall"]) for r in rows]


def assert_same(a, b):
    assert ranking(a) == ranking(b)
    assert [r["if_any"] for r in a] == [r["if_any"] for r in b]


def test_default_uses_bitmatrix_only_when_the_count_stays_exact(monkeypatch):
    called = {"matrix": 0, "bits": 0}
    matrix, bits = rs._search_bitmatrix, rs._search_bitset

    def wrap_matrix(*a, **k):
        called["matrix"] += 1
        return matrix(*a, **k)

    def wrap_bits(*a, **k):
        called["bits"] += 1
        return bits(*a, **k)

    monkeypatch.setattr(rs, "_search_bitmatrix", wrap_matrix)
    monkeypatch.setattr(rs, "_search_bitset", wrap_bits)
    search(DF, TARGET, CANDS, max_terms=2)
    assert called == {"matrix": 1, "bits": 0}
    search(DF, TARGET, CANDS, max_terms=3)
    assert called == {"matrix": 1, "bits": 1}
    with pytest.raises(rs.PropositionError):
        search(DF, TARGET, CANDS, max_terms=3, backend="bitmatrix")


def test_small_table_matches_bitset_including_ties():
    for top in (1, 3, 12, 50):
        bitset = search(DF, TARGET, CANDS, max_terms=2, max_conds=2, top=top, backend="bitset")
        matrix = search(DF, TARGET, CANDS, max_terms=2, max_conds=2, top=top, backend="bitmatrix")
        default = search(DF, TARGET, CANDS, max_terms=2, max_conds=2, top=top)
        assert_same(matrix, bitset)
        assert_same(default, bitset)
    best = search(DF, TARGET, CANDS, top=1)[0]
    assert best["mcc"] == pytest.approx(1.0) and best["conditions"] == 2
    assert rule_text(best) == "[rank_ra >= 4] または [wins_vs_pythag < -4]"
    # 同点のときは条件が少ない式が先、条件数も同じなら式の文字列
    ordered = search(DF, TARGET, CANDS, top=30)
    keys = [(-round(r["mcc"], 12), r["conditions"], json.dumps(r["if_any"], ensure_ascii=False)) for r in ordered]
    assert keys == sorted(keys)
    assert len({k[0] for k in keys}) < len(keys)  # MCC の同点がある


def random_case(seed, n=60, ncol=5, ncand=10):
    rng = np.random.default_rng(seed)
    cols = {f"c{j}": rng.integers(0, 6, n) for j in range(ncol)}  # 小さい整数なので同点が多い
    cols["y"] = rng.random(n) < 0.5
    cands = [{"col": f"c{int(rng.integers(ncol))}", "op": "<", "value": int(rng.integers(1, 6))} for _ in range(ncand)]
    return pl.DataFrame(cols), cands


@pytest.mark.parametrize("seed", range(12))
@pytest.mark.parametrize("top", [1, 5, 20])
def test_random_tables_match_bitset(seed, top):
    df, cands = random_case(seed)
    target = [{"col": "y", "op": "==", "value": True}]
    assert_same(search(df, target, cands, 2, 2, top), search(df, target, cands, 2, 2, top, backend="bitset"))
    assert_same(search(df, target, cands, 1, 2, top), search(df, target, cands, 1, 2, top, backend="bitset"))


def test_real_season_top20_matches_bitset():
    import tomllib

    from pythdragoras import apply_exclusions

    cfg = tomllib.loads((CYCLE / "analysis.toml").read_text(encoding="utf-8"))
    spec = tomllib.loads((CYCLE / "rule_candidates.toml").read_text(encoding="utf-8"))
    st = pl.read_ndjson(CYCLE / "outputs" / "season.jsonl")
    st, _ = apply_exclusions(st, cfg.get("exclude", []))
    cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
    usable = st.drop_nulls(cols)
    assert usable.height > 100 and len(spec["candidate"]) >= 17
    kw = dict(max_terms=int(spec["max_terms"]), max_conds=int(spec["max_conds"]), top=20)
    assert_same(search(usable, spec["target"], spec["candidate"], **kw),
                search(usable, spec["target"], spec["candidate"], backend="bitset", **kw))
