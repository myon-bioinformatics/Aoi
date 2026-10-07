"""Regression tests for the initial question-only Aoi inbox."""
import json
from pathlib import Path
import urllib.error

import pytest

from ask import Query, answer, main, parse, validate_query
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
    first, _ = ask_question(text, results, cache=cache)
    assert first["result"]["answer"] == "はい"
    path.write_text(json.dumps(item(2, 2, listed=())), encoding="utf-8")
    second, _ = ask_question(text, results, cache=cache)
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
    with pytest.raises(FileNotFoundError, match="結果が読めません"):
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
