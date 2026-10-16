"""Independent cache freshness and candidate/answer separation across all reply paths."""
import copy
import json

import pytest

import bank
import inbox
from ask import Query, answer_results
from bank import cache_key, lookup, prepare, snapshot_id
from inbox import ask_question


def write_result(results, hold):
    results.mkdir(exist_ok=True)
    item = {"id": "E1", "statement": "反例の確認", "posthoc": True,
            "forms": [{"form": "original", "n": 2, "hold": hold, "rate": hold / 2,
                       "counterexamples": [] if hold == 2 else [{"unit": "t-2015"}]}]}
    (results / "sets.jsonl").write_text(json.dumps(item) + "\n")


@pytest.mark.parametrize("change", ["content", "missing", "cycle", "sha", "code"])
def test_old_known_and_cached_answers_never_cross_snapshot_identity(tmp_path, monkeypatch, change):
    results, known, cache = [tmp_path / name for name in ("results", "known", "answers")]
    write_result(results, 1)
    query = Query(ask="has_counterexample", target="E1")
    cycle, sha = "c001", "first"
    text = json.dumps({"ask": query.ask, "target": query.target})
    prepare(results, known, cycle=cycle, result_sha=sha)
    response, _ = ask_question(text, results, cache=cache, cycle=cycle, result_sha=sha)
    assert response["result"]["answer"] == "はい"
    old_key, old_snapshot = cache_key(cycle, results, query, sha), snapshot_id(cycle, results, sha)
    if change == "content":
        write_result(results, 2)
    elif change == "missing":
        (results / "sets.jsonl").unlink()
    elif change == "cycle":
        cycle = "c002"
    elif change == "sha":
        sha = "second"
    else:
        monkeypatch.setattr(bank, "answer_code_hash", lambda: "changed-code")
    assert cache_key(cycle, results, query, sha) != old_key
    assert snapshot_id(cycle, results, sha) != old_snapshot
    assert lookup(query, results, known, cycle=cycle, result_sha=sha) is None
    direct = answer_results(query, results)
    calls, real_answer = [], inbox.answer_results

    def observed(*args, **kwargs):
        calls.append(True)
        return real_answer(*args, **kwargs)

    monkeypatch.setattr(inbox, "answer_results", observed)
    cached_response, _ = ask_question(text, results, cache=cache, cycle=cycle, result_sha=sha)
    assert calls == [True]
    assert cached_response["result"] == direct
    assert len(list(cache.glob("*.json"))) == 2
    known_response, _ = ask_question(text, results, known=known, cycle=cycle, result_sha=sha)
    assert known_response["result"] == direct


def test_newly_available_results_invalidate_missing_file_cache(tmp_path):
    results, cache = tmp_path / "results", tmp_path / "answers"
    results.mkdir()
    text = '{"ask":"has_counterexample","target":"E1"}'
    missing, _ = ask_question(text, results, cache=cache, cycle="c001", result_sha="same-sha")
    assert "結果が読めない" in missing["result"]["error"]
    write_result(results, 2)
    present, _ = ask_question(text, results, cache=cache, cycle="c001", result_sha="same-sha")
    assert present["result"]["answer"] == "いいえ"


def test_inbox_missing_results_with_unread_text_has_no_candidates(tmp_path):
    (tmp_path / "propositions.jsonl").write_text(json.dumps({"id": "P1", "statement": "雨の日", "forms": []}))
    got, shown = ask_question("E25 に雨の日だけの反例はある？", tmp_path, suggest_threshold=0)
    assert got["result"]["answer"] == "判定不能"
    assert got["query"]["target"] == "E25"
    assert got["suggestions"] == []
    assert "もしかして" not in shown


def test_unread_text_cannot_consume_or_poison_valid_query_cache(tmp_path):
    results, known, cache = [tmp_path / name for name in ("results", "known", "answers")]
    write_result(results, 2)
    valid = "E1 の反例はある？"
    response, _ = ask_question(valid, results, known=known, cache=cache, cycle="c001", result_sha="sha")
    before = copy.deepcopy(response)
    unknown, shown = ask_question("E1 に雨の日だけの反例はある？", results, known=known, cache=cache,
                                 cycle="c001", result_sha="sha", suggest_threshold=0)
    assert unknown["query"] == response["query"]
    assert unknown["result"]["answer"] == "判定不能"
    assert unknown["result"]["rows"] == []
    assert "候補。答えではない" in shown
    repeated, _ = ask_question(valid, results, known=known, cache=cache, cycle="c001", result_sha="sha")
    assert repeated == before
