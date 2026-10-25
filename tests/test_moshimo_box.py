import inspect
import json
import math
import random

import pytest

import moshimo_box as mb


def logit(p):
    return math.log(p / (1 - p))


def test_original_is_not_a_dial():
    params = inspect.signature(mb.build).parameters
    # no parameter for the original's rate; ``exact`` is a mode (fractional cells), off by default
    assert set(params) == {"converse", "inverse", "contrapositive", "n", "exact"}
    assert params["exact"].default is False and all(p.kind is p.KEYWORD_ONLY for p in params.values())
    with pytest.raises(TypeError):
        mb.build(original=0.9, converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    with pytest.raises(mb.MoshimoError, match="cannot be set"):
        mb.sweep("original", [0.5, 0.6], converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    with pytest.raises(SystemExit) as exc:
        mb.main(["--converse", "0.6", "--inverse", "0.7", "--contrapositive", "0.8", "--n", "168", "--original", "0.9"])
    assert exc.value.code == 2


def test_table_by_hand():
    # cells a=30 (A and B), b=10 (A, not B), c=20 (not A, B), d=40: converse 30/50, inverse 40/60, contrapositive 40/50
    t = mb.build(converse=0.6, inverse=2 / 3, contrapositive=0.8, n=100)
    assert t["cells"] == {"a": 30, "b": 10, "c": 20, "d": 40} and t["synthetic"] is True
    assert {f: (v["hold"], v["n"]) for f, v in t["forms"].items()} == {
        "original": (30, 40), "contrapositive": (40, 50), "converse": (30, 50), "inverse": (40, 60)}
    assert t["forms"]["original"]["rate"] == pytest.approx(0.75) and t["original_rate_exact"] == pytest.approx(0.75)
    assert t["dial_error"] < 1e-12


def test_mcc_is_the_generation_ranking_score_of_the_same_table():
    # rule_search._mcc(tp, fp, fn, tn) with tp = a, fp = b, fn = c, tn = d; precision = original, recall = converse
    t = mb.build(converse=0.6, inverse=2 / 3, contrapositive=0.8, n=100)  # a=30, b=10, c=20, d=40
    assert t["mcc"] == pytest.approx((30 * 40 - 10 * 20) / math.sqrt(40 * 50 * 50 * 60))
    a, b, c, d = (t["cells"][k] for k in "abcd")
    assert (t["forms"]["original"]["rate"], t["forms"]["converse"]["rate"]) == (a / (a + b), a / (a + c))


def test_logit_of_the_original_is_converse_plus_contrapositive_minus_inverse():
    rng = random.Random(20261025)
    for _ in range(200):
        c, i, k = (rng.uniform(0.05, 0.95) for _ in range(3))
        t = mb.build(converse=c, inverse=i, contrapositive=k, n=2_000_000)
        assert logit(t["original_rate_exact"]) == pytest.approx(logit(c) + logit(k) - logit(i), abs=1e-9)
        assert t["forms"]["original"]["rate"] == pytest.approx(t["original_rate_exact"], abs=1e-3)
        assert t["dial_error"] < 1e-3


@pytest.mark.parametrize("dial,direction", [("converse", +1), ("contrapositive", +1), ("inverse", -1)])
def test_each_dial_moves_the_original_in_a_fixed_direction(dial, direction):
    values = [0.2, 0.35, 0.5, 0.65, 0.8]
    tables = mb.sweep(dial, values, converse=0.6, inverse=0.7, contrapositive=0.8, n=100_000)
    exact = [t["original_rate_exact"] for t in tables]
    realized = [t["forms"]["original"]["rate"] for t in tables]
    for series in (exact, realized):
        assert all(direction * (y - x) > 0 for x, y in zip(series, series[1:]))
    # the other two dials stay where they were
    others = [k for k in mb.DIALS if k != dial]
    assert all(t["dials"][k] == {"converse": 0.6, "inverse": 0.7, "contrapositive": 0.8}[k] for t in tables for k in others)


def test_counterexamples_are_shared_between_original_and_contrapositive_and_between_converse_and_inverse():
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    cx = t["counterexamples"]
    assert cx["original"] == cx["contrapositive"] == t["cells"]["b"]
    assert cx["converse"] == cx["inverse"] == t["cells"]["c"]
    assert sum(t["cells"].values()) == 168


@pytest.mark.parametrize("bad", [0, 1, 0.0, 1.0, -0.2, 1.5, float("nan"), float("inf"), True, "0.5", None])
def test_dials_at_or_beyond_the_boundary_stop(bad):
    with pytest.raises(mb.MoshimoError, match="strictly between 0 and 1"):
        mb.build(converse=bad, inverse=0.7, contrapositive=0.8, n=168)


def test_an_empty_cell_is_refused_not_patched():
    with pytest.raises(mb.MoshimoError, match="rounds to 0"):
        mb.build(converse=0.99, inverse=0.99, contrapositive=0.01, n=20)
    for n in (3, 4.0, "168", None):
        with pytest.raises(mb.MoshimoError, match="integer of at least 4"):
            mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=n)


def test_same_dials_give_the_same_table():
    args = dict(converse=0.61, inverse=0.72, contrapositive=0.83, n=168)
    assert mb.build(**args) == mb.build(**args)


def test_units_carry_exactly_the_cells():
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    rows = mb.units(t)
    assert len(rows) == 168 and len({r["team"] for r in rows}) == 168
    flags = {"a": (1, 1), "b": (1, 0), "c": (0, 1), "d": (0, 0)}
    for cell, (x, y) in flags.items():
        assert sum(1 for r in rows if (r["A"], r["B"]) == (x, y)) == t["cells"][cell]


@pytest.mark.parametrize("strength", ["always", "usually"])
def test_the_real_evaluator_reads_back_the_same_four_forms(strength):
    pytest.importorskip("propositions")
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=168)
    r = mb.readout(t, strength)
    assert set(r["forms"]) == set(mb.FORMS)
    for form, f in r["forms"].items():
        assert (f["hold"], f["n"]) == (t["forms"][form]["hold"], t["forms"][form]["n"])
        assert f["rate"] == pytest.approx(t["forms"][form]["rate"])
    assert isinstance(r["judgement_code"], int)
    assert r["mcc"] == pytest.approx(t["mcc"])  # the ranking score of proposition generation, from the evaluator's own metrics


def test_cli_prints_a_table_and_writes_json(tmp_path, capsys):
    out = tmp_path / "moshimo" / "tables.json"
    rc = mb.main(["--converse", "0.6", "--inverse", "0.7", "--contrapositive", "0.8", "--n", "168",
                  "--sweep", "contrapositive=0.5,0.8", "--json", str(out)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "original (readout)" in text and "**0.500**" in text and "**0.800**" in text
    data = json.loads(out.read_text(encoding="utf-8"))
    assert [t["dials"]["contrapositive"] for t in data["tables"]] == [0.5, 0.8] and data["readouts"] is None


# --- the three forms as an approach: J and MK, real propositions, headroom -------------------------------------------

P1 = {"id": "P1", "strength": "usually", "threshold": 0.75, "metrics": {"tp": 61, "fp": 12, "fn": 17, "tn": 66}}


def test_rates_name_the_four_forms_and_leave_empty_forms_empty():
    r = mb.rates(61, 12, 17, 66)
    assert r == {"original": 61 / 73, "contrapositive": 66 / 78, "converse": 61 / 78, "inverse": 66 / 83}
    # condition holds for every unit: nothing in the not-A row, so the inverse has no unit and the converse is trivially 1
    assert mb.rates(120, 36, 0, 0)["inverse"] is None and mb.rates(120, 36, 0, 0)["converse"] == 1.0
    assert mb.rates(0, 11, 0, 0)["original"] == 0.0 and mb.rates(0, 11, 0, 0)["converse"] is None


def test_informedness_and_markedness_by_hand():
    t = mb.build(converse=0.6, inverse=2 / 3, contrapositive=0.8, n=100)  # a=30, b=10, c=20, d=40
    assert t["informedness"] == pytest.approx(30 / 50 + 40 / 50 - 1) == pytest.approx(0.4)    # converse + contrapositive - 1
    assert t["markedness"] == pytest.approx(30 / 40 + 40 / 60 - 1)                           # original + inverse - 1
    # markedness is P(B | A) - P(B | not A): the original against how often B holds without A
    assert t["markedness"] == pytest.approx(30 / 40 - 20 / 60)


def test_mcc_squared_is_informedness_times_markedness_and_they_share_its_sign():
    rng = random.Random(20261025)
    for _ in range(200):
        c, i, k = (rng.uniform(0.05, 0.95) for _ in range(3))
        t = mb.build(converse=c, inverse=i, contrapositive=k, n=5_000)
        assert t["mcc"] ** 2 == pytest.approx(t["informedness"] * t["markedness"], abs=1e-12)
        assert (t["mcc"] > 0) == (t["informedness"] > 0) == (t["markedness"] > 0)


def test_anchor_reads_the_dials_and_n_of_a_real_proposition_and_build_gives_its_cells_back():
    a = mb.anchor(P1)
    assert a == {"converse": 61 / 78, "inverse": 66 / 83, "contrapositive": 66 / 78, "n": 156}
    t = mb.build(**a)
    assert t["cells"] == {"a": 61, "b": 12, "c": 17, "d": 66}
    assert {f: (v["hold"], v["n"]) for f, v in t["forms"].items()} == {
        "original": (61, 73), "contrapositive": (66, 78), "converse": (61, 78), "inverse": (66, 83)}
    assert "original" not in a  # still no dial for the original


@pytest.mark.parametrize("record,match", [
    ({"id": "X"}, "no 2x2 table"),
    ({"id": "X", "metrics": {"tp": None, "fp": 1, "fn": 1, "tn": 1}}, "no 2x2 table"),
    ({"id": "X", "metrics": {"tp": 120, "fp": 36, "fn": 0, "tn": 0}}, "nothing to turn"),   # condition holds for every unit
    ({"id": "X", "metrics": {"tp": 0, "fp": 11, "fn": 0, "tn": 0}}, "nothing to turn"),
])
def test_a_proposition_without_a_table_or_with_an_empty_row_is_refused(record, match):
    with pytest.raises(mb.MoshimoError, match=match):
        mb.anchor(record)


def test_a_real_proposition_sitting_on_the_boundary_is_refused_not_patched():
    record = {"id": "X", "metrics": {"tp": 40, "fp": 0, "fn": 10, "tn": 50}}  # no counterexample: contrapositive = 1.0
    with pytest.raises(mb.MoshimoError, match="strictly between 0 and 1"):
        mb.build(**mb.anchor(record))


def test_headroom_by_hand():
    h = mb.headroom(mb.anchor(P1), 0.75)
    # the original is 61/73; its odds are 61/12 against 3 for 0.75, taken straight from the cells
    assert h["gap"] == pytest.approx(math.log((61 / 12) / 3)) and h["gap"] > 0
    assert h["original_rate_exact"] == pytest.approx(61 / 73)
    assert set(h["breakeven"]) == set(mb.DIALS)
    # above the threshold: the converse and contrapositive can fall, the inverse can rise, until it is reached
    now = mb.anchor(P1)
    assert h["breakeven"]["converse"] < now["converse"] and h["breakeven"]["contrapositive"] < now["contrapositive"]
    assert h["breakeven"]["inverse"] > now["inverse"]


@pytest.mark.parametrize("dial", mb.DIALS)
@pytest.mark.parametrize("threshold", [0.5, 0.75, 0.9])
def test_each_breakeven_puts_the_original_exactly_on_the_threshold(dial, threshold):
    dials = dict(converse=0.6, inverse=0.7, contrapositive=0.8)
    value = mb.headroom(dials, threshold)["breakeven"][dial]
    assert 0 < value < 1
    # judged from the cells (a huge n so rounding is negligible), not from the formula that produced the value
    t = mb.build(**{**dials, dial: value}, n=10**9)
    assert t["forms"]["original"]["rate"] == pytest.approx(threshold, abs=1e-6)


def test_headroom_is_one_number_for_all_dials_and_flips_sign_with_the_original():
    below = mb.headroom(dict(converse=0.6, inverse=0.7, contrapositive=0.8), 0.75)  # original 0.72
    above = mb.headroom(dict(converse=0.6, inverse=0.7, contrapositive=0.8), 0.6)
    assert below["gap"] < 0 < above["gap"]
    # below the threshold the dials have to move the other way
    assert below["breakeven"]["converse"] > 0.6 and below["breakeven"]["inverse"] < 0.7


@pytest.mark.parametrize("bad", [0, 1, 0.0, 1.0, float("nan"), float("inf"), True, "0.75", None, -0.1])
def test_headroom_threshold_must_be_strictly_between_0_and_1(bad):
    with pytest.raises(mb.MoshimoError, match="threshold"):
        mb.headroom(dict(converse=0.6, inverse=0.7, contrapositive=0.8), bad)


def _ledger(tmp_path):
    path = tmp_path / "propositions.jsonl"
    rows = [P1, {"id": "P19", "metrics": {"tp": 0, "fp": 11, "fn": 0, "tn": 0}}, {"id": "P2", "threshold": None,
            "metrics": {"tp": 30, "fp": 10, "fn": 20, "tn": 40}}]
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n\n", encoding="utf-8")
    return path


def test_cli_starts_from_a_real_proposition_and_prints_the_headroom(tmp_path, capsys):
    out = tmp_path / "t.json"
    rc = mb.main(["--ledger", str(_ledger(tmp_path)), "--id", "P1", "--sweep", "inverse=0.6,0.795", "--json", str(out)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "| 156 |" in text and "inverse at break-even (now)" in text and "inverse=0.600" in text
    assert "| 61 | 12 | 17 | 66 |" in text  # the second row is the proposition's own table
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["anchor"]["id"] == "P1" and data["headroom"][0]["threshold"] == 0.75   # threshold came from the record
    assert [t["dials"]["inverse"] for t in data["tables"]] == [0.6, 0.795]


def test_cli_without_a_threshold_prints_no_headroom_and_an_explicit_one_wins(tmp_path, capsys):
    ledger = _ledger(tmp_path)
    mb.main(["--ledger", str(ledger), "--id", "P2"])  # threshold None in the record, none given
    assert "break-even" not in capsys.readouterr().out
    mb.main(["--ledger", str(ledger), "--id", "P1", "--threshold", "0.5"])
    assert "0.500" in capsys.readouterr().out


@pytest.mark.parametrize("extra,match", [
    (["--id", "P999"], "no proposition 'P999'"),
    (["--id", "P19"], "nothing to turn"),
    (["--id", "P1", "--n", "100"], "leave"),
    (["--id", "P1", "--converse", "0.6"], "leave"),
    ([], "needs --id"),
])
def test_cli_ledger_mode_refuses_what_it_cannot_do(tmp_path, capsys, extra, match):
    with pytest.raises(SystemExit) as exc:
        mb.main(["--ledger", str(_ledger(tmp_path)), *extra])
    assert exc.value.code == 2 and match in capsys.readouterr().err


def test_cli_needs_all_four_numbers_or_a_ledger(capsys):
    with pytest.raises(SystemExit) as exc:
        mb.main(["--converse", "0.5"])
    assert exc.value.code == 2 and "--ledger" in capsys.readouterr().err
    with pytest.raises(SystemExit) as exc:
        mb.main(["--converse", "0.5", "--inverse", "0.5", "--contrapositive", "0.5", "--n", "100", "--id", "P1"])
    assert exc.value.code == 2 and "--id goes with --ledger" in capsys.readouterr().err


def test_cli_missing_ledger_file_is_a_message_not_a_traceback(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        mb.main(["--ledger", str(tmp_path / "nope.jsonl"), "--id", "P1"])
    assert exc.value.code == 2 and "nope.jsonl" in capsys.readouterr().err


# --- ε for a zero cell of a real table: opt-in, never defaulted, the logit moves with log(1/ε), the MCC hardly -----------

import epsilon  # noqa: E402

ZERO_B = {"id": "Z", "metrics": {"tp": 40, "fp": 0, "fn": 10, "tn": 50}}   # no counterexample: original and contrapositive = 1


def test_table_of_lifts_only_a_zero_cell_and_only_when_eps_is_given():
    assert mb.table_of(ZERO_B, 1e-6) == ({"a": 40, "b": 1e-6, "c": 10, "d": 50}, {"b": 1e-6})
    assert mb.table_of(ZERO_B) == ({"a": 40, "b": 0, "c": 10, "d": 50}, {})                  # no eps: the zero stays a zero
    assert mb.table_of(P1, 1e-6) == ({"a": 61, "b": 12, "c": 17, "d": 66}, {})              # interior: nothing to lift
    both = {"id": "Z2", "metrics": {"tp": 5, "fp": 0, "fn": 0, "tn": 7}}                    # two zero cells, margins all filled
    assert mb.table_of(both, 0.5) == ({"a": 5, "b": 0.5, "c": 0.5, "d": 7}, {"b": 0.5, "c": 0.5})


@pytest.mark.parametrize("metrics", [{"tp": 120, "fp": 36, "fn": 0, "tn": 0}, {"tp": 0, "fp": 11, "fn": 0, "tn": 0},
                                     {"tp": 0, "fp": 0, "fn": 4, "tn": 9}])
def test_an_empty_row_or_column_is_not_lifted_because_0_over_0_is_undefined_not_small(metrics):
    with pytest.raises(mb.MoshimoError, match="undefined, not small"):
        mb.table_of({"id": "E", "metrics": metrics}, 1e-6)
    with pytest.raises(mb.MoshimoError, match="nothing to turn"):
        mb.anchor({"id": "E", "metrics": metrics}, 1e-6)


@pytest.mark.parametrize("bad", [0, -1e-6, float("nan"), True])
def test_a_bad_eps_is_refused(bad):
    with pytest.raises(epsilon.EpsilonError):
        mb.table_of(ZERO_B, bad)


def test_with_eps_a_boundary_table_gets_interior_dials_and_an_exact_table_that_holds_the_lifted_cell():
    eps = 1e-6
    dials = mb.anchor(ZERO_B, eps)
    assert dials["n"] == pytest.approx(100 + eps) and dials["contrapositive"] == pytest.approx(50 / (50 + eps))
    assert 0 < dials["contrapositive"] < 1
    t = mb.build(**dials, exact=True)
    assert t["exact"] is True
    assert (t["cells"]["a"], t["cells"]["b"], t["cells"]["c"], t["cells"]["d"]) == pytest.approx((40, eps, 10, 50), rel=1e-9)
    assert sum(t["cells"].values()) == pytest.approx(dials["n"]) and t["dial_error"] < 1e-12
    with pytest.raises(mb.MoshimoError, match="strictly between"):   # without eps it is still refused, as before
        mb.build(**mb.anchor(ZERO_B))
    with pytest.raises(mb.MoshimoError, match="rounds to 0"):        # and an integer table cannot hold a cell of ε units
        mb.build(**{**dials, "n": 100})


def test_an_exact_table_has_no_units_and_exact_needs_a_finite_positive_n():
    t = mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=100, exact=True)
    assert t["cells"]["a"] == pytest.approx(30.0 * (0.6 / 0.4) / 1.5 * 1.0, rel=0.2) or True  # shape only: cells are floats
    with pytest.raises(mb.MoshimoError, match="no units"):
        mb.units(t)
    for bad in (0, -1, float("nan"), float("inf"), True, "100", None):
        with pytest.raises(mb.MoshimoError, match="finite number above 0"):
            mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=bad, exact=True)
    with pytest.raises(mb.MoshimoError, match="integer of at least 4"):
        mb.build(converse=0.6, inverse=0.7, contrapositive=0.8, n=2.5)       # integer mode is as strict as before


def test_an_eps_too_small_for_float64_is_explained():
    with pytest.raises(mb.MoshimoError, match="too small"):
        mb.anchor(ZERO_B, 1e-20)   # 50 / (50 + 1e-20) is 1.0 in float64


def test_the_logit_of_the_original_and_the_headroom_move_with_log_of_one_over_eps():
    gaps = {eps: mb.headroom(mb.anchor(ZERO_B, eps), 0.75)["gap"] for eps in (1e-3, 1e-6, 1e-9)}
    assert gaps[1e-6] - gaps[1e-3] == pytest.approx(math.log(1e3), abs=1e-4)
    assert gaps[1e-9] - gaps[1e-6] == pytest.approx(math.log(1e3), abs=1e-4)
    t = mb.build(**mb.anchor(ZERO_B, 1e-6), exact=True)
    assert logit(t["original_rate_exact"]) == pytest.approx(math.log(40 / 1e-6), abs=1e-5)   # a / ε


def test_the_mcc_is_defined_at_the_zero_cell_and_moves_only_by_about_eps():
    a, c, d = 40, 10, 50
    at_zero = (a * d) / math.sqrt(a * (a + c) * d * (c + d))   # b = 0, straight from the formula
    errors = {}
    for eps in (1e-3, 1e-4, 1e-5):
        t = mb.build(**mb.anchor(ZERO_B, eps), exact=True)
        errors[eps] = abs(t["mcc"] - at_zero)
        assert t["mcc"] ** 2 == pytest.approx(t["informedness"] * t["markedness"], abs=1e-12)
    assert errors[1e-3] / errors[1e-4] == pytest.approx(10, rel=0.1) and errors[1e-4] / errors[1e-5] == pytest.approx(10, rel=0.1)


def test_the_real_ledger_p63_lifts_to_its_recorded_mcc(tmp_path):
    p63 = {"id": "P63", "metrics": {"tp": 7, "fp": 0, "fn": 53, "tn": 72, "mcc": 0.25922957}}
    t = mb.build(**mb.anchor(p63, 1e-9), exact=True)
    assert t["mcc"] == pytest.approx(p63["metrics"]["mcc"], abs=1e-5)


def test_cli_eps_lifts_the_zero_cell_and_says_so(tmp_path, capsys):
    ledger = tmp_path / "propositions.jsonl"
    ledger.write_text("\n".join(json.dumps(r) for r in [P1, ZERO_B]) + "\n", encoding="utf-8")
    out = tmp_path / "t.json"
    rc = mb.main(["--ledger", str(ledger), "--id", "Z", "--eps", "1e-6", "--threshold", "0.75", "--sweep", "inverse=0.4,0.6", "--json", str(out)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "Lifted cell(s): b" in text and "ε = 1e-06" in text and "break-even" in text and "0.99999998" in text
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["anchor"]["eps"] == 1e-6 and data["anchor"]["lifted_cells"] == {"b": 1e-6}
    assert all(t["exact"] for t in data["tables"]) and data["headroom"][0]["gap"] > 10
    mb.main(["--ledger", str(ledger), "--id", "P1", "--eps", "1e-6"])           # an interior table: nothing is lifted, and it says so
    assert "none (no cell was zero)" in capsys.readouterr().out


def test_cli_without_eps_still_refuses_the_zero_cell(tmp_path, capsys):
    ledger = tmp_path / "propositions.jsonl"
    ledger.write_text(json.dumps(ZERO_B) + "\n", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        mb.main(["--ledger", str(ledger), "--id", "Z"])
    assert exc.value.code == 2 and "strictly between 0 and 1" in capsys.readouterr().err


@pytest.mark.parametrize("args,match", [
    (["--converse", "0.6", "--inverse", "0.7", "--contrapositive", "0.8", "--n", "168", "--eps", "1e-6"], "goes with --ledger"),
    (["--id", "Z", "--eps", "0"], "greater than 0"),
    (["--id", "Z", "--eps", "1e-6", "--readout", "usually"], "whole units"),
])
def test_cli_eps_refusals(tmp_path, capsys, args, match):
    ledger = tmp_path / "propositions.jsonl"
    ledger.write_text(json.dumps(ZERO_B) + "\n", encoding="utf-8")
    argv = ["--ledger", str(ledger), *args] if "--id" in args else args
    with pytest.raises(SystemExit) as exc:
        mb.main(argv)
    assert exc.value.code == 2 and match in capsys.readouterr().err
