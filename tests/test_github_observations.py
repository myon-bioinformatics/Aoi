import github_observations as obs


def snapshot():
    return {"schema": "parent-audit/1", "owner": "example", "generated_at": "2026-11-10T00:00:00Z",
            "repositories": ["alpha", "beta"], "truncated": [], "errors": [], "records": [
                {"id": "alpha#1", "repository": "alpha", "kind": "issue", "labels": ["bug"], "title": "broken"},
                {"id": "alpha#2", "repository": "alpha", "kind": "pr", "ci": "FAILED", "head_sha": "a" * 40},
                {"id": "beta#1", "repository": "beta", "kind": "issue"}]}


def test_observe_repository_preserves_raw_evidence():
    data = snapshot()
    result = obs.observe(data, "alpha")
    assert len(result["report"]["records"]) == 2
    assert result["report"]["records"][1]["raw"] == data["records"][1]
    assert not result["report"]["unknown"]


def test_absence_and_incomplete_are_unknown():
    data = snapshot()
    data["truncated"] = ["missing"]
    data["errors"] = [{"repository": "missing", "error": "unavailable"}]
    result = obs.observe(data, "missing")
    assert len(result["report"]["unknown"]) == 3
    assert result["report"]["records"] == []


def test_unrelated_collection_errors_do_not_mark_target_incomplete():
    data = snapshot()
    data["truncated"] = ["beta"]
    data["errors"] = [{"repository": "beta", "error": "unavailable"}]
    assert not obs.observe(data, "alpha")["report"]["unknown"]
