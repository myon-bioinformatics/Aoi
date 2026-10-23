"""Properties of the bitwise surrogate. Each run draws a seed and logs it.

Fidelity claims from the external proposal are not pass conditions. Exact
agreement is asserted only where the generator makes the repaired rule
equivalent to the oracle on every eval row.
"""

import ast
from pathlib import Path
import random
import secrets
import subprocess
import sys
import warnings

import polars as pl
import pytest

import bitwise_surrogate as bs
import rule_search

ROOT = Path(__file__).resolve().parents[1]


def _seed():
    seed = secrets.randbits(63)
    warnings.warn("bitwise_surrogate seed=%d" % seed, UserWarning, stacklevel=2)
    return seed


def _small(seed):
    return bs.synthetic_report(seed, n_initial=32, n_repair=16, n_eval=64, measure_time=False)


def test_evaluate_fast_matches_the_set_reference():
    seed = _seed()
    rng = random.Random(seed)
    for _ in range(40):
        rule = bs.BitwiseSymbolicSurrogate(
            rng.randrange(1 << 12),
            tuple(rng.randrange(1, 1 << 12) for _ in range(rng.randrange(4))),
            rng.randrange(1 << 12),
        )
        for _ in range(30):
            x = rng.randrange(1 << 12)
            assert rule.evaluate_fast(x) is rule.evaluate_reference(x)


def test_rejects_bools_empty_clauses_and_negative_masks():
    with pytest.raises(ValueError):
        bs.BitwiseSymbolicSurrogate(True, (), 0)
    with pytest.raises(ValueError):
        bs.BitwiseSymbolicSurrogate(0, (0,), 0)
    with pytest.raises(ValueError):
        bs.BitwiseSymbolicSurrogate(-1, (), 0)
    rule = bs.BitwiseSymbolicSurrogate()
    with pytest.raises(ValueError):
        rule.evaluate_fast(-1)
    with pytest.raises(ValueError):
        bs.repair_disagreement(rule, 0, 1, lambda x: True)


def test_copy_does_not_alias_and_agreement_does_not_probe():
    rule = bs.BitwiseSymbolicSurrogate(1, (2,), 4)
    copied = rule.copy()
    copied.m_and = 0
    copied.or_clauses.append(8)
    copied.m_not = 0
    assert rule.describe() == {"m_and_bits": [0], "or_clauses": [[1]], "m_not_bits": [2]}
    calls = []

    def oracle(x):
        calls.append(x)
        return True

    trace = bs.repair_disagreement(rule, 1 | 2, True, oracle)
    assert trace["kind"] == "agree" and calls == []


def test_same_seed_rebuilds_the_same_report_when_timing_is_off():
    seed = _seed()
    first = _small(seed)
    second = _small(seed)
    assert first == second


def test_dead_slide_is_exact_on_a_disjoint_holdout_and_unrepaired_never_fires():
    seed = _seed()
    report = _small(seed)
    dead = report["scenarios"]["feature_shift_dead"]
    assert dead["ids_disjoint"] is True
    assert set(dead["repair_ids"]).isdisjoint(dead["eval_ids"])
    initial = dead["initial"]
    assert initial["fp"] == 0 and initial["fn"] == 0 and initial["tp"] + initial["tn"] == initial["n"]
    unrepaired = dead["unrepaired_eval"]
    assert unrepaired["tp"] == 0 and unrepaired["fp"] == 0
    assert unrepaired["fn"] == unrepaired["tn"] == unrepaired["n"] // 2
    repaired = dead["repaired_one_eval"]
    assert repaired["fp"] == 0 and repaired["fn"] == 0
    assert repaired["tp"] == repaired["tn"] == repaired["n"] // 2
    assert dead["repaired_all_eval"] == repaired
    assert dead["repairs_one"] == 1 and dead["repairs_all"] == 1
    assert dead["probe_queries_one"] == sum(len(trace["probes"]) for trace in dead["traces_one"])
    trace = dead["traces_one"][0]
    assert trace["id"] == "dead-repair-canonical"
    assert trace["edits"] == [{"op": "relax_or", "lost": bs.CLAIMED_AND[1], "replacement": bs.CLAIMED_SLIDE_TO}]
    probes = trace["probes"]
    assert probes[-1]["candidate"] == bs.CLAIMED_SLIDE_TO and probes[-1]["oracle_true"] is False
    assert all(probe["oracle_true"] is True for probe in probes[:-1])
    assert dead["repaired_one_on_repair_rows"]["fp"] == 0
    assert dead["repaired_one_on_repair_rows"]["fn"] == 0


def test_single_decoy_binary_search_finds_that_bit_and_eval_is_exact():
    seed = _seed()
    decoy = _small(seed)["scenarios"]["new_decoy"]
    trace = decoy["traces_one"][0]
    assert trace["kind"] == "false_positive"
    assert trace["edits"] == [{"op": "add_not", "bit": bs.CLAIMED_DECOY}]
    for probe in trace["probes"]:
        assert probe["oracle_true"] is (bs.CLAIMED_DECOY in probe["left_bits"])
    assert len(trace["probes"]) <= max(0, (len(bs.bit_list(trace["x"] & ~bs.mask_of(bs.CLAIMED_AND))) - 1).bit_length())
    repaired = decoy["repaired_one_eval"]
    assert repaired["fp"] == 0 and repaired["fn"] == 0
    assert decoy["repairs_all"] == 1
    assert decoy["probe_queries_one"] == len(trace["probes"])


def test_residual_or_still_accepts_the_injected_old_feature_row():
    seed = _seed()
    residual = _small(seed)["scenarios"]["feature_shift_residual"]
    injected = residual["injected_false_positive"]
    assert injected["id"] in residual["eval_ids"]
    assert injected["id"] not in residual["repair_ids"]
    assert injected["y"] is False
    rule = bs.rule_from_describe(residual["repaired_one_rule"])
    assert rule.evaluate_fast(injected["x"]) is True
    assert residual["repaired_one_eval"]["fp"] >= 1
    assert residual["repaired_one_rule"]["or_clauses"] == [[bs.CLAIMED_AND[1], bs.CLAIMED_SLIDE_TO]]


def test_documented_flaws_are_forced_by_the_edit_rules():
    seed = _seed()
    flaws = _small(seed)["flaws_exercised_by_construction"]
    first = flaws["first_candidate"]
    assert first["replacement"] == first["trap"]
    assert first["replacement"] != first["later_necessary_bit"]
    assert first["false_positive_accepted"] is True
    several = flaws["multiple_lost_bits"]
    assert several["replacements"] == [several["low_new_bit"], several["low_new_bit"]]
    assert several["low_new_bit"] != several["high_new_bit"]
    assert several["false_positive_accepted"] is True
    noisy = flaws["noisy_clear_not"]
    assert noisy["cleared"] == [noisy["banned"]]
    assert noisy["positive_with_banned_bit_now_accepted"] is True
    missing = flaws["false_positive_on_a_missing_bit"]
    assert missing["flipping_culprit_restores_true"] is False
    assert missing["true_positive_rejected_after_commit"] is True


def test_prune_when_no_candidate_flips_and_no_extra_bit_on_a_false_positive():
    seed = _seed()
    rng = random.Random(seed)
    keep, lost, noise_a, noise_b = rng.sample(range(bs.N_FEATURES), 4)
    rule = bs.distill_literals([(keep, True), (lost, True)])
    oracle = lambda x: bs.label_of(x, (keep,), ())
    row = bs.mask_of((keep, noise_a, noise_b))
    calls = []

    def counting(x):
        calls.append(x)
        return oracle(x)

    trace = bs.repair_disagreement(rule, row, True, counting)
    assert {"op": "prune", "lost": lost} in trace["edits"]
    assert all(probe["oracle_true"] is True for probe in trace["probes"])
    assert len(calls) == len(trace["probes"])
    assert rule.evaluate_fast(bs.mask_of((keep,))) is True
    assert rule.evaluate_fast(bs.mask_of((noise_a,))) is False

    empty = bs.BitwiseSymbolicSurrogate()
    none_trace = bs.repair_disagreement(empty, 0, False, lambda x: False)
    assert none_trace["edits"] == [{"op": "no_extra_bit"}]
    assert empty.evaluate_fast(0) is True


def test_clear_not_is_the_whole_edit_when_the_and_mask_already_holds():
    seed = _seed()
    required, banned = random.Random(seed).sample(range(bs.N_FEATURES), 2)
    rule = bs.distill_literals([(required, True), (banned, False)])
    row = bs.mask_of((required, banned))
    trace = bs.repair_disagreement(rule, row, True, lambda x: bs.label_of(x, (required,), ()))
    assert trace["probes"] == []
    assert trace["edits"] == [{"op": "clear_not", "bits": [banned]}]
    assert rule.evaluate_fast(row) is True


def test_compile_bit_dnf_covers_the_fragment_and_rejects_a_general_dnf():
    assert bs.compile_bit_dnf([[0, 1]]).describe()["m_and_bits"] == [0, 1]
    factored = bs.compile_bit_dnf([[0, 1], [0, 2]])
    assert factored.describe() == {"m_and_bits": [0], "or_clauses": [[1, 2]], "m_not_bits": []}
    assert bs.compile_bit_dnf([[0], [0, 1]]).describe()["m_and_bits"] == [0]
    assert bs.compile_bit_dnf([[0], [1]]).describe()["or_clauses"] == [[0, 1]]
    assert bs.compile_bit_dnf([[0, 1], [2, 3]]) is None
    distilled = bs.distill_literals([(1, True), (4, False)])
    assert distilled.evaluate_fast(bs.mask_of((1,))) is True
    assert distilled.evaluate_fast(bs.mask_of((1, 4))) is False


def test_compiled_singleton_or_matches_rule_search_on_the_toy_frame():
    rows = [
        ("a", 2020, 40, 1, 2.0, True), ("b", 2020, 10, 3, -5.0, False), ("c", 2020, -20, 2, 4.0, True),
        ("d", 2020, -60, 5, 1.0, False), ("e", 2020, 5, 3, 0.5, True), ("f", 2020, -10, 6, -1.0, False),
        ("g", 2021, 30, 2, -6.0, False), ("h", 2021, -30, 5, 3.0, False), ("i", 2021, 60, 1, 0.0, True),
    ]
    frame = pl.DataFrame([
        {"team": team, "season": season, "rd": rd, "rank_ra": rank_ra, "wins_vs_pythag": wins, "upper_half": upper}
        for team, season, rd, rank_ra, wins, upper in rows
    ])
    target = [{"col": "upper_half", "op": "==", "value": False}]
    candidates = [
        {"col": "rd", "op": "<", "value": 0},
        {"col": "rank_ra", "op": ">=", "value": 4},
        {"col": "wins_vs_pythag", "op": "<", "value": -4},
    ]
    best = rule_search.search(frame, target, candidates, max_terms=2, max_conds=2, top=1)[0]
    groups = []
    for group in best["if_any"]:
        indexes = []
        for cond in group:
            indexes.append(next(
                i for i, candidate in enumerate(candidates)
                if (candidate["col"], candidate["op"], candidate["value"]) == (cond["col"], cond["op"], cond["value"])
            ))
        groups.append(indexes)
    compiled = bs.compile_bit_dnf(groups)
    assert compiled is not None
    masks = []
    for row in rows:
        flags = (
            row[2] < 0,
            row[3] >= 4,
            row[4] < -4,
        )
        masks.append(bs.mask_of(i for i, flag in enumerate(flags) if flag))
    # The toy's best rule is a disjunction of two single conditions, so the surrogate has one OR clause.
    assert compiled.describe()["m_and_bits"] == []
    for mask, row in zip(masks, rows):
        antecedent = (row[3] >= 4) or (row[4] < -4)
        assert compiled.evaluate_fast(mask) is antecedent


def test_module_imports_under_python_s_and_stays_free_of_py310_syntax():
    completed = subprocess.run(
        [sys.executable, "-S", "-c", "import bitwise_surrogate"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stderr
    source = (ROOT / "bitwise_surrogate.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert not any(isinstance(node, ast.Match) for node in ast.walk(tree))
    assert not any(isinstance(node, ast.Attribute) and node.attr == "bit_count" for node in ast.walk(tree))
    top_level = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            top_level.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            top_level.append(node.module.split(".")[0])
    assert set(top_level) <= set(sys.stdlib_module_names)


def test_tight_loop_timing_is_a_positive_duration_not_a_claimed_band():
    seed = _seed()
    report = bs.synthetic_report(seed, n_initial=16, n_repair=8, n_eval=16, measure_time=True)
    timing = report["timing"]["evaluate_fast"]
    assert timing["calls"] >= 2000
    assert timing["seconds"] > 0
    assert timing["seconds_per_call"] == timing["seconds"] / timing["calls"]
    # The external 2–8 µs band is a hypothesis. This test only checks the clock moved.


def test_file_order_and_random_roles_are_exact_when_the_old_bit_is_cleared(aoi_root):
    seed = _seed()
    season = bs.season_report(aoi_root, seed)
    assert season["claimed_indexes_12_19_25_fit"] is False
    assert season["n_candidates"] == 17
    assert season["candidate_index_12_text"] == "rank_ra >= 3"
    assert season["natural_target"]["repair_ran"] is False
    assert season["natural_target"]["counterfactual_oracle"] is False
    assert max(season["train_seasons"]) < min(season["repair_seasons"])
    assert max(season["repair_seasons"]) < min(season["eval_seasons"])
    assert 2020 not in season["train_seasons"] + season["repair_seasons"] + season["eval_seasons"]
    assert season["season_ids_disjoint"] is True
    searched = season["natural_target"]["train_counts_from_search"]
    compiled = season["natural_target"]["initial"]
    assert (compiled["tp"], compiled["fp"], compiled["fn"], compiled["tn"]) == (
        searched["tp"], searched["fp"], searched["fn"], searched["tn"])
    for bundle in (season["planted_file_order"], season["planted_prevalence_window"]):
        dead = bundle["dead_old_bit"]
        assert dead["ids_disjoint"] is True
        assert dead["repaired_one_eval"]["fp"] == 0 and dead["repaired_one_eval"]["fn"] == 0
        eval_ids = set(dead["eval_ids"])
        assert eval_ids.isdisjoint(dead["repair_ids"])
        for trace in bundle["observational"]["traces_one"]:
            assert trace["id"] not in eval_ids
    loaded = bs.load_candidate_rows(aoi_root)
    rng = random.Random(seed)
    picked = rng.sample(range(season["n_candidates"]), 4)
    roles = {"and": picked[0], "old": picked[1], "new": picked[2], "not": picked[3]}
    random_bundle = bs._planted_bundle(
        [row for row in loaded["rows"] if row["season"] in season["train_seasons"]],
        [row for row in loaded["rows"] if row["season"] in season["repair_seasons"]],
        [row for row in loaded["rows"] if row["season"] in season["eval_seasons"]],
        roles,
    )
    random_dead = random_bundle["dead_old_bit"]["repaired_one_eval"]
    assert random_dead["fp"] == 0 and random_dead["fn"] == 0
    search = season["natural_target"]["search_seconds_max_terms_2_top_20"]
    assert search["min_seconds"] <= search["median_seconds"] <= search["max_seconds"]
    assert search["min_seconds"] > 0
    assert season["surrogate_timing"]["calls"] >= 2000
    assert season["surrogate_timing"]["seconds_per_call"] > 0
