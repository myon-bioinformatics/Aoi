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


def test_missing_observation_metadata_remains_unknown():
    for field in ('generated_at', 'owner'):
        data = snapshot()
        del data[field]
        assert obs.observe(data, 'alpha')['report']['unknown']
    for value in ('invalid', '2026-11-11T00:00:00', None):
        data = snapshot()
        data['generated_at'] = value
        assert obs.observe(data, 'alpha')['report']['unknown']


def test_missing_pr_ci_or_head_preserves_record_and_marks_unknown():
    for field in ('ci', 'head_sha'):
        data = snapshot()
        del data['records'][1][field]
        result = obs.observe(data, 'alpha')
        assert result['report']['counts']['pr'] == 1
        assert result['report']['unknown'][0]['key'] == 'alpha#2'
        assert result['report']['records'][1]['raw'] == data['records'][1]


def test_incomplete_ci_is_observed_without_inventing_success():
    data = snapshot()
    data['records'][1]['ci'] = 'INCOMPLETE'
    result = obs.observe(data, 'alpha')
    assert result['report']['records'][1]['derived']['observed_ci'] == 'INCOMPLETE'


def test_cli_exit_for_failed_collection_and_missing_metadata(tmp_path, capsys):
    import json
    path = tmp_path / 'audit.json'
    data = snapshot()
    for mutation in ({'errors': [{'repository': 'alpha', 'error': 'Timeout'}]},
                     {'truncated': ['alpha']}, {'generated_at': None}, {'errors': None}):
        path.write_text(json.dumps({**data, **mutation}), encoding='utf-8')
        assert obs.main([str(path), 'alpha']) == 2
        assert json.loads(capsys.readouterr().out)['report']['unknown']
    path.write_text(json.dumps(data), encoding='utf-8')
    assert obs.main([str(path), 'alpha']) == 0


def test_real_parent_snapshot_parity_when_supplied():
    import collections
    import json
    import os
    import pytest
    path = os.environ.get('PARENT_AUDIT_SNAPSHOT')
    if not path:
        pytest.skip('set PARENT_AUDIT_SNAPSHOT to a produced parent data.json')
    data = json.loads(__import__('pathlib').Path(path).read_text(encoding='utf-8'))
    for repository in data['repositories']:
        result = obs.observe(data, repository)
        expected = [row for row in data['records'] if row['repository'] == repository]
        assert [row['raw'] for row in result['report']['records']] == expected
        counts = collections.Counter(row['kind'] for row in expected)
        assert result['report']['counts']['issue'] == counts['issue']
        assert result['report']['counts']['pr'] == counts['pr']
        assert result['generated_at'] == data['generated_at']
