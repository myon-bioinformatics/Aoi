"""Offline CI regression of the *exploratory*, unregistered Issue #9 candidates."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/check_c001_exploratory_candidates.py"
FIXTURE = Path(__file__).parent / "fixtures/c001_exploratory_snapshot.json"
spec = importlib.util.spec_from_file_location("c001_exploratory", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


@pytest.fixture(scope="module")
def snapshot():
    return mod.read_snapshot(FIXTURE)


def test_pinned_cohort_and_2020_sensitivity(snapshot):
    assert snapshot["research_sha"] == mod.RESEARCH_SHA
    report = mod.report(snapshot)
    assert report["status"] == "unregistered_posthoc_exploration"
    assert report["independently_validated"] is False
    assert report["causally_explained"] is False
    base, sensitivity = report["main"], report["include_2020"]
    assert base["cohort"] == {"years": "2013-2025", "exclude": [2020], "units": 144,
                               "outcome": "final rank >= 4 (B); not CS participation"}
    assert sensitivity["cohort"]["units"] == 156
    years = sorted(set(range(2013, 2026)) - {2020})
    for candidate, expected, restored in (("OR_A", 32, (33, 34)),
                                           ("OR_B", 54, (58, 59)),
                                           ("E7_AND_E22", 59, (64, 64))):
        a, b = base["candidates"][candidate], sensitivity["candidates"][candidate]
        assert (a["hold"], a["n"], a["undetermined"]) == (expected, expected, 0)
        assert a["focus_coverage"] == "12/12"
        assert a["focus_covered"] == years
        assert not a["counterexamples"]
        assert (b["hold"], b["n"], b["undetermined"]) == (*restored, 0)
        assert b["focus_coverage"] == "12/12"
    for candidate in ("OR_A", "OR_B"):
        assert sensitivity["candidates"][candidate]["counterexamples"] == [
            {"unit": "d-2020", "rank": 3, "upper_half": True}]
    assert sensitivity["candidates"]["E7_AND_E22"]["counterexamples"] == []
    assert 2020 not in sensitivity["candidates"]["E7_AND_E22"]["focus_covered"]


def test_p62_2012_undefined_and_2020_streak_retained(snapshot):
    rows = {(r["season"], r["team"]): r for r in snapshot["rows"]}
    assert rows[2012, "d"]["inn_size_low_streak"] is None  # not false
    assert [rows[y, "d"]["inn_size_low_streak"] for y in (2019, 2020, 2021)] == [3, 4, 5]
    assert mod.verdict(rows[2020, "d"], "P62", snapshot["definitions"]) is True
    assert mod.verdict(rows[2020, "d"], "E22", snapshot["definitions"]) is False
    assert rows[2020, "d"]["q_wl_4"] == 8


def test_focus_coverage_paths_are_recalculated(snapshot):
    values = mod.report(snapshot)["main"]["candidates"]
    assert values["OR_A"]["focus_paths"]["2013"] == ["P196"]
    assert values["OR_A"]["focus_paths"]["2014"] == ["P62"]
    assert values["OR_B"]["focus_paths"]["2017"] == ["P189"]
    assert values["OR_A"]["focus_paths"]["2017"] == ["P138"]
    assert values["OR_B"]["focus_paths"]["2023"] == ["P62", "P189", "P196"]


def test_incomplete_cohort_fails_closed(snapshot):
    altered = copy.deepcopy(snapshot)
    altered["rows"] = altered["rows"][:-1]
    with pytest.raises(ValueError, match="168 unique"):
        mod.calculate(altered)


def test_missing_premise_is_unknown_not_false(snapshot):
    row = copy.deepcopy(next(x for x in snapshot["rows"] if x["season"] == 2020 and x["team"] == "d"))
    row["rf_adv"] = None
    assert mod.verdict(row, "P138", snapshot["definitions"]) is None
    row["course_rank_q3"] = None
    assert mod.verdict(row, "E22", snapshot["definitions"]) is None


def test_safe_ast_rejects_python_evaluation():
    with pytest.raises(ValueError, match="unsupported"):
        mod.evaluate("__import__('os').system('echo unsafe')", lambda _: True)


def test_snapshot_provenance_cannot_be_silently_repointed(snapshot, tmp_path):
    path = tmp_path / "input.json"
    path.write_text(FIXTURE.read_text(encoding="utf-8").replace(mod.RESEARCH_SHA, "0" * 40), encoding="utf-8")
    with pytest.raises(ValueError, match="provenance"):
        mod.read_snapshot(path)
