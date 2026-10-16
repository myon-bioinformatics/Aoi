"""既知回答と受付キャッシュは同じ鍵を使う。印は三つの経路で一致する。"""
import json
from pathlib import Path

import pytest

from ask import Query, answer, registration_status
from bank import cache_key, key_material, lookup, prepare
from inbox import ask_question


def row(pid, **meta):
    item = {
        "id": pid,
        "forms": [{
            "form": "original", "n": 2, "hold": 1, "rate": 0.5, "undetermined": 0,
            "counterexamples": [{"unit": "t-2015"}],
        }],
    }
    item.update(meta)
    return item


def write_results(path: Path, rows):
    path.mkdir(parents=True, exist_ok=True)
    (path / "sets.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def test_key_is_cycle_results_code_and_query(tmp_path):
    results = tmp_path / "results"
    write_results(results, [row("E1", posthoc=True)])
    query = Query(ask="has_counterexample", target="E1")
    body = key_material("c001", results, "abc123", query)
    assert set(body) == {"cycle", "results", "answer_code", "query"}
    assert body["cycle"] == "c001"
    assert body["results"]["sha"] == "abc123"
    assert body["results"]["files"]["sets.jsonl"]
    assert body["results"]["files"]["propositions.jsonl"] is None
    assert body["query"]["target"] == "E1"
    other_cycle = cache_key("c002", results, query, "abc123")
    other_sha = cache_key("c001", results, query, "def456")
    other_query = cache_key("c001", results, Query(ask="counterexamples", target="E1"), "abc123")
    own = cache_key("c001", results, query, "abc123")
    assert len({own, other_cycle, other_sha, other_query}) == 4
    with pytest.raises(ValueError):
        cache_key("", results, query, "abc123")


def test_known_directory_is_the_one_the_caller_passes(tmp_path, monkeypatch):
    import inbox
    results = tmp_path / "results"
    write_results(results, [row("E1", posthoc=True)])
    cache = tmp_path / "cache-answers"
    known = tmp_path / "explicit-known"
    poison = cache.parent / "known"
    poison.mkdir(parents=True)
    (poison / "do-not-read").write_text("poison", encoding="utf-8")
    seen = []
    real = inbox.lookup

    def spy(query, results_path, destination, **kwargs):
        seen.append(Path(destination))
        return real(query, results_path, destination, **kwargs)

    monkeypatch.setattr(inbox, "lookup", spy)
    text = '{"ask":"has_counterexample","target":"E1"}'
    got, _ = ask_question(text, results, cache=cache, known=known, cycle="c001", result_sha="sha")
    assert got["result"]["rows"][0]["registration"] == "事後構成"
    assert seen == [known]
    assert known != poison
    assert not (poison / "manifest.json").exists()


def test_registration_matches_on_direct_known_and_cache_paths(tmp_path, monkeypatch):
    import inbox
    rows = [
        row("E1", posthoc=True),
        row("E2"),
        row("E3", posthoc=False),
        row("E4", preregistered=True),
    ]
    expected = {"E1": "事後構成", "E2": "不明", "E3": "不明", "E4": "事前登録"}
    for item in rows:
        assert registration_status(item) == expected[item["id"]]
    results = tmp_path / "results"
    write_results(results, rows)
    known = tmp_path / "known"
    cache = tmp_path / "answers"
    prepare(results, known, cycle="c001", result_sha="sha")
    calls = {"n": 0}
    real = inbox.answer_results

    def counting(query, path):
        calls["n"] += 1
        return real(query, path)

    monkeypatch.setattr(inbox, "answer_results", counting)
    for item in rows:
        pid = item["id"]
        query = Query(ask="has_counterexample", target=pid)
        direct = answer(query, [item])
        known_res = lookup(query, results, known, cycle="c001", result_sha="sha")
        text = json.dumps({"ask": "has_counterexample", "target": pid})
        cached, rendered = ask_question(
            text, results, cache=cache, known=None, cycle="c001", result_sha="sha",
        )
        again, _ = ask_question(
            text, results, cache=cache, known=None, cycle="c001", result_sha="sha",
        )
        label = expected[pid]
        assert direct["rows"][0]["registration"] == label
        assert known_res["rows"][0]["registration"] == label
        assert cached["result"]["rows"][0]["registration"] == label
        assert again["result"]["rows"][0]["registration"] == label
        assert f"［{label}］" in rendered
    assert calls["n"] == len(rows)
