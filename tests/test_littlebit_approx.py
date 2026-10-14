"""潜在パターン由来の条件。seed で再現し、目的列を因子に入れず、判定は厳密なまま。"""

import json
from pathlib import Path

import numpy as np
import polars as pl
import pytest

import littlebit_approx as la
import littlebit_prune
import propositions as pr
import rule_search as rs
from littlebit_approx import (
    attach_loadings, compare, derive, indicator_matrix, load_cycle, pattern_sign, top_view,
)
from registration_audit import audit_record, classify
from rule_search import search

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "cycles" / "c001-chunichi"
ART = CYCLE / "outputs" / "exploratory" / "littlebit-approx" / "comparison.json"

ROWS = [
    ("a", 2020, 40, 1, 2.0, True), ("b", 2020, 10, 3, -5.0, False), ("c", 2020, -20, 2, 4.0, True),
    ("d", 2020, -60, 5, 1.0, False), ("e", 2020, 5, 3, 0.5, True), ("f", 2020, -10, 6, -1.0, False),
    ("g", 2021, 30, 2, -6.0, False), ("h", 2021, -30, 5, 3.0, False), ("i", 2021, 60, 1, 0.0, True),
]
DF = pl.DataFrame([{"team": t, "season": s, "rd": rd, "rank_ra": ra, "wins_vs_pythag": w, "upper_half": u}
                   for t, s, rd, ra, w, u in ROWS])
TARGET = [{"col": "upper_half", "op": "==", "value": False}]
CANDS = [{"col": "rd", "op": "<", "value": 0}, {"col": "rank_ra", "op": ">=", "value": 4},
         {"col": "wins_vs_pythag", "op": "<", "value": -4}, {"col": "rd", "op": "<", "value": 20}]


def block_frame():
    rows = []
    for i in range(4):
        rows.append({"team": "a", "team_name": "A", "season": 2000 + i, "c0": 1, "c1": 1, "c2": 0, "c3": 0, "y": i % 2 == 0})
    for i in range(4):
        rows.append({"team": "b", "team_name": "B", "season": 2100 + i, "c0": 0, "c1": 0, "c2": 1, "c3": 1, "y": i % 2 == 0})
    df = pl.DataFrame(rows)
    cands = [{"col": f"c{j}", "op": "==", "value": 1} for j in range(4)]
    target = [{"col": "y", "op": "==", "value": True}]
    return df, target, cands


def test_pattern_sign_is_stable_and_seed_breaks_only_ties():
    positive = np.array([1.0, 0.2, -0.1])
    negative = np.array([-2.0, -0.3, 0.1])
    assert pattern_sign(positive, 0) == pattern_sign(positive, 99) == 1
    assert pattern_sign(negative, 0) == pattern_sign(negative, 3) == -1
    tied = np.array([1.0, -1.0, 0.0])
    assert pattern_sign(tied, 0) == pattern_sign(tied, 0)
    assert {pattern_sign(tied, seed) for seed in range(40)} == {1, -1}
    assert pattern_sign(np.zeros(3), 1) == 1


def test_indicator_matches_search_masks_and_is_units_by_candidates():
    matrix = indicator_matrix(DF, CANDS)
    assert matrix.shape == (DF.height, len(CANDS))
    assert matrix.dtype == bool
    for j, cand in enumerate(CANDS):
        bits = rs._mask_bits(rs._mask(DF, [cand]), DF.height)
        assert np.array_equal(matrix[:, j], bits)


def test_same_seed_reproduces_candidates_and_residuals():
    df, _, cands = block_frame()
    first = derive(df, cands, rank=2, stages=2, seed=4)
    second = derive(df, cands, rank=2, stages=2, seed=4)
    assert first["candidates"] == second["candidates"]
    assert first["report"]["residual_units"] == second["report"]["residual_units"]
    assert first["report"]["drop_reasons"] == second["report"]["drop_reasons"]
    cols = [c["col"] for c in first["candidates"]]
    assert first["frame"].select(cols).equals(second["frame"].select(cols))


def test_seed_is_recorded_and_does_not_reshuffle_without_a_tie():
    df, _, cands = block_frame()
    left = derive(df, cands, rank=2, stages=1, seed=0)
    right = derive(df, cands, rank=2, stages=1, seed=1)
    assert left["report"]["candidates_added"] >= 1
    assert {c["seed"] for c in left["candidates"]} == {0}
    assert {c["seed"] for c in right["candidates"]} == {1}
    if left["report"]["sign_ties"] == 0 and right["report"]["sign_ties"] == 0:
        assert [c["loading_units"] for c in left["report"]["derived_candidates"]] == [
            c["loading_units"] for c in right["report"]["derived_candidates"]]


def test_factorization_does_not_read_the_target(monkeypatch):
    df, target, cands = block_frame()
    flipped = df.with_columns(pl.col("y").not_())
    no_target = df.drop("y")
    kwargs = {"rank": 2, "stages": 1, "seed": 0}
    base = derive(df, cands, **kwargs)
    assert derive(flipped, cands, **kwargs)["candidates"] == base["candidates"]
    assert derive(no_target, cands, **kwargs)["report"]["residual_leads"] == base["report"]["residual_leads"]
    seen = []
    captured = {}
    real_mask = rs._mask
    real_littlebit = littlebit_prune.littlebit

    def spy_mask(frame, conds):
        seen.extend(cond["col"] for cond in conds)
        return real_mask(frame, conds)

    def spy_littlebit(matrix, rank, stages=2, als_iters=6):
        captured["shape"] = np.shape(matrix)
        captured["matrix"] = np.array(matrix, copy=True)
        return real_littlebit(matrix, rank, stages, als_iters=als_iters)

    monkeypatch.setattr(rs, "_mask", spy_mask)
    monkeypatch.setattr(littlebit_prune, "littlebit", spy_littlebit)
    noisy = df.with_columns(pl.Series("decoy", np.arange(df.height)))
    got = derive(noisy, cands, **kwargs)
    assert "y" not in seen and "upper_half" not in seen and "decoy" not in seen
    assert captured["shape"] == (df.height, len(cands))
    assert np.array_equal(captured["matrix"], indicator_matrix(df, cands))
    assert got["report"]["matrix_shape"] == [df.height, len(cands)]
    assert target[0]["col"] not in {cond["col"] for cond in cands}


def test_provenance_fields_and_registration():
    df, _, cands = block_frame()
    got = derive(df, cands, rank=2, stages=1, seed=3)
    assert got["report"]["candidates_added"] == len(got["candidates"])
    assert got["report"]["candidates_added"] + got["report"]["candidates_dropped"] == got["report"]["patterns_requested"]
    assert got["candidates"]
    for cand in got["candidates"]:
        assert cand["source"] == "littlebit-approx"
        assert cand["rank"] == 2 and cand["seed"] == 3
        assert cand["posthoc"] is True and cand["exploratory"] is True
        assert cand["rule"] == "canonical-sign-of-F"
        assert cand["registration"] == "posthoc"
        assert classify(cand).status == "posthoc"
        assert audit_record(cand) == []
        assert "preregistration" not in cand
        assert len(cand["bundle"]) == len(cands)
        assert all(set(item) == {"col", "op", "value", "weight"} and isinstance(item["weight"], float)
                   for item in cand["bundle"])
        assert {item["col"] for item in cand["bundle"]} == {c["col"] for c in cands}


def test_unknown_provenance_key_is_rejected_and_known_keys_do_not_change_judging():
    with pytest.raises(pr.PropositionError):
        search(DF, TARGET, [{**CANDS[0], "note": "x"}])
    marked = [{**c, "source": "littlebit-approx", "rank": 8, "seed": 0, "posthoc": True,
               "exploratory": True, "registration": "posthoc",
               "bundle": [{"col": c["col"], "op": c["op"], "value": c["value"], "weight": 0.5}]}
              for c in CANDS]
    plain = search(DF, TARGET, CANDS, top=20, backend="bitset")
    extra = search(DF, TARGET, marked, top=20, backend="bitset")
    assert top_view(plain, set()) == top_view(extra, set())
    matrix = search(DF, TARGET, marked, top=20, backend="bitmatrix")
    assert top_view(matrix, set()) == top_view(plain, set())


def test_exact_judging_matches_bitset_and_proposition_engine():
    df, target, cands = block_frame()
    got = derive(df, cands, rank=2, stages=2, seed=0)
    cols = {c["col"] for c in got["candidates"]}
    combined = cands + got["candidates"]
    bit = search(got["frame"], target, combined, max_terms=2, max_conds=2, top=30, backend="bitset")
    mat = search(got["frame"], target, combined, max_terms=2, max_conds=2, top=30, backend="bitmatrix")
    assert top_view(bit, cols) == top_view(mat, cols)
    assert bit
    for row in bit:
        forms = {item["form"]: item for item in pr.evaluate(
            {"id": "X", "statement": "s", "strength": "usually", "min_n": 1, "if_any": row["if_any"], "then": target},
            got["frame"])["forms"]}
        assert (forms["original"]["n"], forms["original"]["hold"]) == (row["tp"] + row["fp"], row["tp"])
    base = search(df, target, cands, top=10**6, backend="bitset")
    base_map = {la.rule_text(row): (row["tp"], row["fp"], row["fn"], row["tn"]) for row in base}
    for row in search(got["frame"], target, combined, top=10**6, backend="bitset"):
        if "littlebit_" not in la.rule_text(row):
            assert base_map[la.rule_text(row)] == (row["tp"], row["fp"], row["fn"], row["tn"])


def test_residual_leads_are_above_mean_and_ignore_target():
    df, _, cands = block_frame()
    report = derive(df, cands, rank=2, stages=1, seed=0)["report"]
    mean = report["residual_mean_energy"]
    for unit in report["residual_units"]:
        assert unit["lead"] is (unit["residual_energy"] > mean)
    assert report["residual_leads"] == [unit for unit in report["residual_units"] if unit["lead"]]
    flipped = derive(df.with_columns(pl.Series("y", [True] * df.height)), cands, rank=2, stages=1, seed=0)
    assert flipped["report"]["residual_leads"] == report["residual_leads"]


def test_compare_report_marks_exploration_and_splits_observation():
    df, target, cands = block_frame()
    report = compare(df, target, cands, rank=2, stages=1, seed=0, top=5, max_terms=2, max_conds=2)
    assert report["record_kind"] == "exploratory" and report["exploratory"] is True
    assert report["posthoc"] is True and report["registration"] == "posthoc"
    assert classify(report).status == "posthoc"
    assert report["approximation"]["backends_agree"] is True
    assert report["approximation"]["candidates_added"] >= 1
    md = la.render_markdown(report)
    assert "\n## 観測\n" in md and "\n## 解釈\n" in md
    assert "0.040" not in md and "0.060" not in md


def _cycle_kw(spec, top):
    return {"max_terms": int(spec["max_terms"]), "max_conds": int(spec["max_conds"]), "top": top}


def test_saved_c001_comparison_matches_exact_search_of_saved_masks():
    report = json.loads(ART.read_text(encoding="utf-8"))
    assert report["record_kind"] == "exploratory" and report["exploratory"] is True
    assert report["registration"] == "posthoc" and report["posthoc"] is True
    assert report["confirmation_file"] == "outputs/confirmation.md"
    assert report["issue"] == 22
    approx = report["approximation"]
    assert approx["candidates_added"] >= 1
    assert approx["candidates_added"] + approx["candidates_dropped"] == approx["patterns_requested"]
    assert approx["rank"] == 8 and approx["stages"] == 2 and approx["seed"] == 0
    assert approx["backends_agree"] is True
    assert len(report["derived_candidates"]) == approx["candidates_added"]
    for cand in report["derived_candidates"]:
        assert cand["source"] == "littlebit-approx" and cand["rank"] == 8 and cand["seed"] == 0
        assert cand["posthoc"] is True and cand["exploratory"] is True and cand["registration"] == "posthoc"
        assert cand["bundle"] and all("weight" in item for item in cand["bundle"])
        assert classify(cand).status == "posthoc"
        assert len(cand["loading_units"]) == cand["n_loading"]
    df, spec, meta = load_cycle(CYCLE)
    assert report["data"]["units"] == meta["units"] == df.height
    assert approx["matrix_shape"] == [df.height, len(spec["candidate"])]
    kw = _cycle_kw(spec, approx["top"])
    assert top_view(search(df, spec["target"], spec["candidate"], **kw), set()) == report["baseline"]["top"]
    frame = attach_loadings(df, report["derived_candidates"])
    extra = [la.as_search_candidate(cand) for cand in report["derived_candidates"]]
    cols = {cand["col"] for cand in extra}
    both = search(frame, spec["target"], [*spec["candidate"], *extra], **kw)
    both_bits = search(frame, spec["target"], [*spec["candidate"], *extra], backend="bitset", **kw)
    assert top_view(both, cols) == report["with_derived"]["top"]
    assert top_view(both_bits, cols) == report["with_derived"]["top"]
    entered = {cand["col"] for cand in report["derived_in_top"]}
    assert entered == {col for row in report["with_derived"]["top"] for col in row["derived_columns"]}
    mean = report["residual"]["mean_energy"]
    leads = [unit for unit in report["residual_units"] if unit["lead"]]
    assert len(leads) == report["residual"]["n_leads"]
    assert all(unit["residual_energy"] > mean for unit in leads)
    md = (ART.parent / "comparison.md").read_text(encoding="utf-8")
    assert "\n## 観測\n" in md and "\n## 解釈\n" in md
    assert "0.040" not in md and "0.060" not in md


def test_c001_fresh_derivation_ignores_b_class(monkeypatch):
    df, spec, _ = load_cycle(CYCLE)
    seen = []
    real_mask = rs._mask

    def spy(frame, conds):
        seen.extend(cond["col"] for cond in conds)
        return real_mask(frame, conds)

    monkeypatch.setattr(rs, "_mask", spy)
    scrambled = df.with_columns(pl.Series("upper_half", np.zeros(df.height, dtype=bool)))
    got = derive(scrambled, spec["candidate"], rank=8, stages=2, seed=0)
    assert "upper_half" not in seen
    info = got["report"]
    assert info["candidates_added"] >= 1
    assert info["candidates_added"] + info["candidates_dropped"] == info["patterns_requested"]
    assert info["matrix_shape"] == [df.height, len(spec["candidate"])]
    assert all(cand["source"] == "littlebit-approx" and cand["registration"] == "posthoc" for cand in got["candidates"])
