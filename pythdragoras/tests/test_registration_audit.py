"""Registration provenance must be explicit and conservative."""
from pathlib import Path

from registration_audit import audit_record, classify, load_exprs, narrative_candidates


def test_posthoc_false_or_missing_is_unknown():
    assert classify({}).status == "unknown"
    assert classify({"posthoc": False}).status == "unknown"


def test_explicit_posthoc_is_posthoc():
    assert classify({"posthoc": True}).status == "posthoc"


def test_preregistration_needs_pre_evaluation_evidence():
    good = {"preregistration": {"recorded_before_evaluation": True, "evidence": "R73"}}
    assert classify(good).status == "preregistered"
    assert classify(good).evidence == "R73"
    assert audit_record(good) == []
    assert audit_record({"preregistration": {"recorded_before_evaluation": True}})
    assert audit_record({"preregistration": {"evidence": "R73"}})


def test_conflicting_assertions_are_rejected():
    rec = {"posthoc": True, "preregistration": {"recorded_before_evaluation": True, "evidence": "R73"}}
    assert audit_record(rec)


def test_c001_current_metadata_does_not_guess_preregistration():
    path = Path("cycles/c001-chunichi/sets.toml")
    if not path.exists():
        return  # results live on the cycle ref, not main
    exprs = {e["id"]: e for e in load_exprs(path)}
    assert classify(exprs["E26"]).status == "posthoc"
    assert classify(exprs["E30"]).status == "posthoc"
    assert classify(exprs["E25"]).status == "unknown"


def test_narrative_is_only_an_audit_lead(tmp_path):
    path = tmp_path / "sets.toml"
    path.write_text(
        '# R73（計算前に書いた式）\n[[expr]]\nid = "E25"\nexpr = "A"\n',
        encoding="utf-8",
    )
    assert "E25" in narrative_candidates(path)
    # Narrative text alone must never become machine-readable preregistration.
    assert classify({"id": "E25"}).status == "unknown"


def test_all_machine_readable_registration_records_are_self_consistent():
    """Any future explicit registration metadata must satisfy the same contract."""
    path = Path("cycles/c001-chunichi/sets.toml")
    if not path.exists():
        return
    for expr in load_exprs(path):
        assert audit_record(expr) == [], f"{expr.get('id')}: {audit_record(expr)}"


def test_classification_does_not_depend_on_successful_results():
    """A perfect observed rate is evidence about the result, never about when it was defined."""
    assert classify({"forms": [{"n": 60, "hold": 60, "rate": 1.0}]}).status == "unknown"
    assert classify({"posthoc": True, "forms": [{"n": 60, "hold": 60, "rate": 1.0}]}).status == "posthoc"


def test_real_c001_audit_sample_from_r72_r73_r76():
    """Frozen sample copied from cycle-001/chunichi@0723d11 for regression.

    This deliberately mixes narrative 'written before evaluation' families with
    explicit posthoc children.  The classifier must not flatten either side.
    """
    sample = {
        "E20": {},
        "E25": {},
        "E26": {"posthoc": True},
        "E29": {"posthoc": True},
        "E30": {"posthoc": True},
        "E31": {"posthoc": True},
        "E32": {"posthoc": True},
    }
    got = {key: classify(value).status for key, value in sample.items()}
    assert got == {
        "E20": "unknown",
        "E25": "unknown",
        "E26": "posthoc",
        "E29": "posthoc",
        "E30": "posthoc",
        "E31": "posthoc",
        "E32": "posthoc",
    }


def test_real_history_claim_does_not_override_machine_metadata():
    """R73's narrative is an audit lead, not permission to silently relabel E25."""
    historical_note = "R73（計算前に書いた式）"
    assert "計算前に書いた" in historical_note
    assert classify({"id": "E25"}).status == "unknown"
    # R76 has the same tension: family note says pre-evaluation, individual
    # expressions E29-E32 explicitly say posthoc. Explicit contradictory-looking
    # history must be investigated, not normalized to the family note.
    assert classify({"id": "E30", "posthoc": True}).status == "posthoc"
