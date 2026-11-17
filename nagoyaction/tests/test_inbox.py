"""Regression tests for the initial question-only Aoi inbox.

The answer-cache section at the end: known answers and the intake cache share one key, the
registration label matches on every reply path, and a cached answer never crosses snapshot identity.
"""
import copy, json, urllib.error
from pathlib import Path

import pytest

import bank
import inbox
from ask import Query, answer, answer_results, main, parse, registration_status, validate_query
from bank import cache_key, key_material, lookup, prepare, snapshot_id
from inbox import (
    GitHub,
    State,
    allowed_actor,
    ask_question,
    atomic_json,
    command,
    git,
    intake,
    snapshot,
    status_report,
)


def item(n=2, hold=1, unknown=0, listed=("t-2015",)):
    return {
        "id": "E1",
        "forms": [
            {
                "form": "original",
                "n": n,
                "hold": hold,
                "undetermined": unknown,
                "rate": hold / n if n else None,
                "counterexamples": [{"unit": unit} for unit in listed],
            }
        ],
    }


def test_no_evidence_is_not_no_counterexample():
    q = Query(ask="has_counterexample")
    assert answer(q, [])["answer"] == "判定不能"
    assert answer(q, [{"id": "P1", "forms": []}])["answer"] == "判定不能"
    assert answer(q, [item(0, 0, listed=())])["answer"] == "判定不能"
    assert answer(q, [item(2, 2, unknown=1, listed=())])["answer"] == "判定不能"
    assert answer(q, [item(2, 1, unknown=1)])["answer"] == "はい"
    assert answer(q, [item(2, 2, listed=())])["answer"] == "いいえ"


def test_truncated_lists_exclusion_and_about_remain_unknown():
    data = [item(4, 2, listed=("t-2015",))]
    assert answer(Query(ask="has_counterexample", exclude=["t"]), data)["answer"] == "判定不能"
    assert answer(Query(ask="has_counterexample", about=["d"]), data)["answer"] == "判定不能"
    assert answer(Query(ask="has_counterexample", exclude=["t"]), [item()])["answer"] == "いいえ"


@pytest.mark.parametrize(
    "raw",
    [
        [],
        {"target": "../secret"},
        {"exclude": "d"},
        {"about": ["zz"]},
        {"min_rate": True},
        {"min_rate": -1},
        {"max_rate": float("nan")},
        {"min_rate": .9, "max_rate": .2},
        {"target": "E1", "kind": "proposition"},
        {"form": []},
    ],
)
def test_query_boundary_rejects_invalid_types(raw):
    with pytest.raises((ValueError, TypeError)):
        validate_query(raw)


def test_unread_restriction_stops_answer(tmp_path, capsys):
    assert parse("E1 に雨の日だけの反例はある？")[1]
    assert parse("E1 の2025年だけの反例はある？")[1]
    assert parse("成立率95%未満の式")[1]
    (tmp_path / "sets.jsonl").write_text(json.dumps(item()), encoding="utf-8")
    assert main(["E1 に雨の日だけの反例はある？", "--results", str(tmp_path), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["answer"] == "判定不能"


def test_command_boundary_and_reply_marker():
    for author in ("someone", "claude[bot]", "github-actions[bot]"):
        assert command({"body": "/ask E1 の判例", "user": {"login": author}}) == (
            "ask",
            "E1 の判例",
        )
    assert command({"body": "<!-- aoi-inbox:reply-1 -->\n/ask E1 の判例"}) is None
    assert command({"body": "普通の会話 /ask E1"}) is None
    assert command({"body": "/ask " + "x" * 4000}) is None


def test_same_query_cache_invalidated_when_results_change(tmp_path):
    results, cache = tmp_path / "results", tmp_path / "answers"
    results.mkdir()
    path = results / "sets.jsonl"
    path.write_text(json.dumps(item()), encoding="utf-8")
    text = '{"ask":"has_counterexample", "target":"E1"}'
    first, _ = ask_question(text, results, cache=cache, cycle="c001", result_sha="r1")
    assert first["result"]["answer"] == "はい"
    path.write_text(json.dumps(item(2, 2, listed=())), encoding="utf-8")
    second, _ = ask_question(text, results, cache=cache, cycle="c001", result_sha="r1")
    assert second["result"]["answer"] == "いいえ"
    assert len(list(cache.glob("*.json"))) == 2


@pytest.fixture
def cycle(tmp_path):
    path = tmp_path / "cycle"
    (path / "outputs").mkdir(parents=True)
    (path / "outputs/sets.jsonl").write_text(json.dumps(item()) + "\n", encoding="utf-8")
    return path


def test_snapshot_uses_real_main_layout(cycle):
    root = Path(__file__).resolve().parents[2]
    got = snapshot(root, cycle)
    assert "queryu/ask/ask.py" in got
    assert "queryu/ask/bank.py" in got
    assert "nagoyaction/inbox/inbox.py" in got
    assert "results/outputs/sets.jsonl" in got
    assert all("PythDRagoras" not in key and "DRAgoWing" not in key for key in got)


def test_snapshot_requires_readable_result(cycle):
    (cycle / "outputs/sets.jsonl").unlink()
    with pytest.raises(FileNotFoundError, match="結果が読めない"):
        snapshot(Path(__file__).resolve().parents[2], cycle)


def test_git_state_concurrent_writers_keep_receipts(tmp_path):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", str(remote))
    source = tmp_path / "source"
    git(tmp_path, "init", str(source))
    git(source, "config", "user.name", "test")
    git(source, "config", "user.email", "test@example.invalid")
    (source / "README").write_text("source")
    git(source, "add", ".")
    git(source, "commit", "-m", "initial")
    git(source, "remote", "add", "origin", str(remote))
    first = State(source, tmp_path / "first", create=True)
    second = State(source, tmp_path / "second")
    atomic_json(first.path / "receipts/1.json", {"kind": "ask"})
    first.save()
    atomic_json(second.path / "receipts/2.json", {"kind": "status"})
    second.save()
    first.sync()
    assert (first.path / "receipts/2.json").exists()
    assert (second.path / "receipts/1.json").exists()
    assert (source / "README").read_text() == "source"


def test_reply_retry_only_accepts_bot_authored_marker(monkeypatch):
    api = GitHub("owner/repo", 1)
    comments = [{"user": {"login": "other"}, "body": "<!-- aoi-inbox:reply-1 -->"}]
    sent = []

    def call(path, body):
        sent.append(body)
        return {"user": {"login": "github-actions[bot]"}, **body}

    monkeypatch.setattr(api, "call", call)
    api.reply("reply-1", "answer", comments)
    api.reply("reply-1", "answer", comments)
    assert len(sent) == 1


class DiskState:
    def __init__(self, path):
        self.path = path
        self.saves = 0

    def save(self):
        self.saves += 1


def fake_api(monkeypatch, comments):
    api = GitHub("owner/repo", 1)

    def trusted_comments():
        for row in comments:
            if "id" in row:
                row.setdefault("author_association", "COLLABORATOR")
        return list(comments)

    monkeypatch.setattr(api, "comments", trusted_comments)

    def call(path, body):
        reply = {"user": {"login": "github-actions[bot]"}, **body}
        comments.append(reply)
        return reply

    monkeypatch.setattr(api, "call", call)
    return api


def test_existing_ask_and_status_comments_are_processed(cycle, tmp_path, monkeypatch):
    comments = [
        {
            "id": 1,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": '{"ignored":"not a command"}',
        },
        {
            "id": 2,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": '/ask {"ask":"has_counterexample","target":"E1"}',
        },
        {
            "id": 3,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/status",
        },
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "test-sha", "c001", "result-sha")
    assert (state.path / "receipts/2.json").exists()
    assert (state.path / "receipts/3.json").exists()
    assert not (state.path / "receipts/1.json").exists()
    assert sum("aoi-inbox:reply-" in row.get("body", "") for row in comments) == 2


def test_q5_receipt_durably_keeps_original_input_and_spans(cycle, tmp_path, monkeypatch):
    question = "P121 は 2026 年で確かめられた？"
    comments = [{"id": 5, "user": {"login": "person"}, "created_at": "2026-10-16",
                 "body": "/ask " + question}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "code-sha", "c001", "result-sha")
    receipt = json.loads((state.path / "receipts/5.json").read_text(encoding="utf-8"))
    response = receipt["response"]
    assert receipt["body"] == "/ask " + question
    assert response["raw_text"] == question
    assert response["parse_status"] == "undetermined"
    assert response["unread_spans"] == [{"start": 7, "end": 20, "raw_text": "2026 年で確かめられた"}]
    assert response["result"]["reason_codes"] == ["unrecognized_ask", "unsupported_text"]
    assert response["result"]["answer"] == "判定不能" and response["result"]["rows"] == []
    assert "2026 年で確かめられた" in receipt["reply_body"]
    assert not list(state.path.glob("**/answers/*.json"))
    assert not list(state.path.glob("**/known/manifest.json"))


def test_processed_comment_edit_is_not_reprocessed(cycle, tmp_path, monkeypatch):
    comments = [
        {
            "id": 11,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/status",
        }
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "test-sha")
    comments[0]["body"] = "/explore all"
    intake(api, state, cycle, "different-sha")
    assert len(list((state.path / "receipts").glob("*.json"))) == 1
    assert sum("reply-11" in row.get("body", "") for row in comments) == 1


def test_reply_failure_does_not_block_later_intake(cycle, tmp_path, monkeypatch):
    comments = [
        {
            "id": i,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/status",
        }
        for i in (31, 32)
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    original = api.call

    def flaky(path, body):
        if "reply-31" in body["body"]:
            raise urllib.error.URLError("not sent")
        return original(path, body)

    monkeypatch.setattr(api, "call", flaky)
    intake(api, state, cycle, "test")
    assert (state.path / "receipts/32.json").exists()
    assert (state.path / "pending-replies/reply-31.json").exists()
    assert any("reply-32" in row.get("body", "") for row in comments)


def test_one_comment_exception_does_not_block_later_comment(cycle, tmp_path, monkeypatch):
    import inbox

    comments = [
        {
            "id": 41,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/ask E1 の判例",
        },
        {
            "id": 42,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/status",
        },
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")

    def broken(*args, **kwargs):
        raise KeyError("choices")

    monkeypatch.setattr(inbox, "ask_question", broken)
    intake(api, state, cycle, "test")
    failed = json.loads((state.path / "receipts/41.json").read_text())
    assert failed["error_type"] == "KeyError"
    assert (state.path / "receipts/42.json").exists()
    assert any("reply-42" in row.get("body", "") for row in comments)


def test_explore_and_stop_are_explicitly_deferred(cycle, tmp_path, monkeypatch):
    comments = [
        {
            "id": 51,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/explore E1",
        },
        {
            "id": 52,
            "user": {"login": "person"},
            "created_at": "2026-01-01",
            "body": "/stop 51",
        },
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "test")
    assert "未導入" in json.loads((state.path / "receipts/51.json").read_text())["reply_body"]
    assert "停止対象はありません" in json.loads((state.path / "receipts/52.json").read_text())["reply_body"]
    assert not (state.path / "requests").exists()


def test_status_is_question_only(tmp_path):
    atomic_json(tmp_path / "receipts/1.json", {"kind": "ask"})
    text = status_report(tmp_path)
    assert "コマンド累積受付: 1件" in text
    assert "探索ワーカー: 未導入" in text


@pytest.mark.parametrize(
    "body", ["/ask E1 の判例", "/explore E1", "/status", "/stop 1"]
)
def test_untrusted_commands_are_ignored_before_work_and_reply(
    cycle, tmp_path, monkeypatch, body
):
    import inbox

    monkeypatch.setenv("AOI_INBOX_ALLOWED_ACTORS", "[]")

    def unexpected(*args, **kwargs):
        pytest.fail("untrusted comment must not invoke computation")

    monkeypatch.setattr(inbox, "ask_question", unexpected)
    monkeypatch.setattr(inbox, "status_report", unexpected)
    comments = [
        {
            "id": 701,
            "user": {"login": "outsider"},
            "author_association": "NONE",
            "created_at": "2026-01-01",
            "body": body,
        }
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    monkeypatch.setattr(state, "save", unexpected)
    intake(api, state, cycle, "sha")
    assert len(comments) == 1 and not state.path.exists()


@pytest.mark.parametrize(
    "login,association",
    [
        ("owner", "NONE"),
        ("someone", "OWNER"),
        ("someone", "MEMBER"),
        ("someone", "COLLABORATOR"),
        ("github-actions[bot]", "NONE"),
        ("allowed[bot]", "NONE"),
    ],
)
def test_allowed_actor_handles_owner_members_and_explicit_bots(
    monkeypatch, login, association
):
    monkeypatch.setenv("AOI_INBOX_ALLOWED_ACTORS", '["Allowed[bot]"]')
    assert allowed_actor(
        {"user": {"login": login}, "author_association": association},
        "owner/repo",
    )
    assert not allowed_actor(
        {"user": {"login": "other[bot]"}, "author_association": "NONE"},
        "owner/repo",
    )


def test_registration_status_is_conservative_and_rendered():
    from ask import registration_status, render

    posthoc = item()
    posthoc["posthoc"] = True
    unknown = item()
    unknown["id"] = "E2"
    prereg = item()
    prereg["id"] = "E3"
    prereg["preregistered"] = True
    assert registration_status(posthoc) == "事後構成"
    assert registration_status(unknown) == "不明"
    assert registration_status(prereg) == "事前登録"
    posthoc["forms"].append({
        **posthoc["forms"][0],
        "form": "contrapositive",
    })
    q = Query(target="E1", form="contrapositive")
    text = render("", q, [], answer(q, [posthoc]))
    assert "対偶の成立率" in text
    assert "事後構成" in text



def test_git_never_waits_for_a_credential_prompt(monkeypatch, tmp_path):
    """fetch-guard: fetch/push/ls-remote run without a credential or SSH prompt, within 60 s."""
    import subprocess as sp
    import inbox as inbox_module
    for name in ("GIT_TERMINAL_PROMPT", "GCM_INTERACTIVE", "GIT_SSH_COMMAND"):
        monkeypatch.delenv(name, raising=False)
    seen = {}

    def fake_run(argv, **kwargs):
        seen.update(kwargs)
        return sp.CompletedProcess(argv, 0, "", "")
    monkeypatch.setattr(inbox_module.subprocess, "run", fake_run)
    git(tmp_path, "ls-remote", "origin")
    env = seen["env"]
    assert (env["GIT_TERMINAL_PROMPT"], env["GCM_INTERACTIVE"], env["GIT_SSH_COMMAND"]) == (
        "0", "never", "ssh -o BatchMode=yes")
    assert seen["timeout"] == 60


# ──── answer cache: known answers and the intake cache use the same key; labels match on three paths ────


def row(pid, **meta):
    return {**item(), "id": pid, **meta}  # item() defaults: n=2, hold=1, one listed counterexample


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


# ──── answer cache: snapshot freshness and candidate/answer separation across all reply paths ────


def write_result(results, hold):
    write_results(results, [{"id": "E1", "statement": "反例の確認", "posthoc": True,
                             "forms": [{"form": "original", "n": 2, "hold": hold, "rate": hold / 2,
                                        "counterexamples": [] if hold == 2 else [{"unit": "t-2015"}]}]}])


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
