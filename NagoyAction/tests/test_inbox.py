"""Public inbox: real evaluator, restart, missing evidence, bot requests, Git races."""
import json
from pathlib import Path
import urllib.error

import pytest

from ask import Query, answer, main, parse, validate_query
from inbox import GitHub, State, ask_question, command, git, intake, worker
from exploration import Explorer, atomic_json, plan, snapshot, save_state, read_state


def item(n=2, hold=1, unknown=0, listed=("t-2015",)):
    return {"id": "E1", "forms": [{"form": "original", "n": n, "hold": hold, "undetermined": unknown,
            "rate": hold / n if n else None, "counterexamples": [{"unit": u} for u in listed]}]}


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


@pytest.mark.parametrize("raw", [[], {"target": "../secret"}, {"exclude": "d"}, {"about": ["zz"]},
    {"min_rate": True}, {"min_rate": -1}, {"max_rate": float("nan")}, {"min_rate": .9, "max_rate": .2},
    {"target": "E1", "kind": "proposition"}, {"form": []}])
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


def test_humans_and_other_actions_can_request_but_replies_cannot():
    for author in ("someone", "claude[bot]", "github-actions[bot]"):
        assert command({"body": "/ask E1 の判例", "user": {"login": author}}) == ("ask", "E1 の判例")
    assert command({"body": "<!-- aoi-inbox:reply-1 -->\n/ask E1 の判例"}) is None
    assert command({"body": "普通の会話 /ask E1"}) is None
    assert command({"body": "/ask " + "x" * 4000}) is None


def test_same_query_cache_invalidated_when_results_change(tmp_path):
    results, cache = tmp_path / "results", tmp_path / "answers"
    results.mkdir()
    p = results / "sets.jsonl"
    p.write_text(json.dumps(item()), encoding="utf-8")
    text = '{"ask":"has_counterexample", "target":"E1"}'
    first, _ = ask_question(text, results, cache=cache)
    assert first["result"]["answer"] == "はい"
    p.write_text(json.dumps(item(2, 2, listed=())), encoding="utf-8")
    second, _ = ask_question(text, results, cache=cache)
    assert second["result"]["answer"] == "いいえ"
    assert len(list(cache.glob("*.json"))) == 2


@pytest.fixture
def cycle(tmp_path):
    p = tmp_path / "cycle"
    (p / "outputs").mkdir(parents=True)
    (p / "analysis.toml").write_text('[focus]\nteam="d"\n[[exclude]]\nseason=2020\nreason="short"\n')
    (p / "propositions.toml").write_text('''[[proposition]]
id="P1"
statement="a implies B"
strength="usually"
if=[{col="a",op=">",value=0}]
then=[{col="upper_half",op="==",value=false}]
[[proposition]]
id="P2"
statement="b implies B"
strength="usually"
if=[{col="b",op=">",value=0}]
then=[{col="upper_half",op="==",value=false}]
''')
    (p / "sets.toml").write_text('''[[set]]
id="A"
from="P1"
[[set]]
id="B"
from="P2"
[[expr]]
id="E1"
expr="A"
''')
    rows = [{"team": t, "team_name": t, "league": "C", "season": s, "a": a, "b": b, "upper_half": u}
            for t, s, a, b, u in [("d", 2021, 1, 1, False), ("d", 2022, 0, 1, False),
                                  ("t", 2021, 1, 0, True), ("t", 2022, 0, 0, True), ("d", 2020, 1, 1, True)]]
    (p / "outputs/season.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    return p


def test_real_exploration_resume_matches_uninterrupted(cycle, tmp_path):
    spec = plan('{"sets":["A","B"],"max_depth":2}', cycle)
    ex = Explorer(cycle, spec)
    whole = ex.initial({"fixture": "1"})
    ex.advance(whole, seconds=60, max_steps=1000)
    resumed = ex.initial({"fixture": "1"})
    ex.advance(resumed, seconds=60, max_steps=1)
    checkpoint = tmp_path / "checkpoint/state.json"
    save_state(checkpoint, resumed)
    resumed = read_state(checkpoint)
    ex = Explorer(cycle, spec)
    ex.advance(resumed, seconds=60, max_steps=1000)
    assert resumed == whole
    assert whole["status"] == "completed"
    assert len(whole["results"]) > 4
    children = [r for r in whole["results"] if r["parent"] and "forms" in r]
    assert children and all(r["motivated_by"] and r["held_out"] for r in children)
    assert all("d-2020" not in f["counterexamples"] for r in whole["results"] if "forms" in r for f in r["forms"])
    signatures = [r["signature"] for r in whole["results"] if "signature" in r]
    assert len(signatures) == len(set(signatures))


def test_exploration_deadline_and_candidate_bound(cycle):
    spec = plan('{"sets":["A","B"]}', cycle)
    spec["max_candidates"] = 5
    ex = Explorer(cycle, spec)
    state = ex.initial({})
    ex.advance(state, seconds=0)
    assert state["cursor"] == 0
    ex.advance(state, seconds=60, max_steps=1000)
    assert state["bounded"] and state["status"] == "bounded"
    assert len(state["candidates"]) <= 5


def test_unrecognized_exploration_theme_is_not_silently_ignored(cycle):
    with pytest.raises(ValueError):
        plan("雨の日の式を探して", cycle)
    assert plan("E1", cycle)["sets"] == ["A"]
    with pytest.raises(ValueError):
        plan('{"sets":["A"],"seed":"E99"}', cycle)


def test_git_state_concurrent_writers_keep_requests_and_results(tmp_path):
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
    atomic_json(first.path / "requests/1.json", {"job": "one"})
    first.save()
    atomic_json(second.path / "jobs/one/state.json", {"status": "running"})
    second.save()
    first.sync()
    assert json.loads((first.path / "jobs/one/state.json").read_text())["status"] == "running"
    assert (second.path / "requests/1.json").exists()
    assert (source / "README").read_text() == "source"


def test_reply_retry_only_accepts_bot_authored_receipt(monkeypatch):
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
    def sync(self):
        pass


def fake_api(monkeypatch, comments):
    api = GitHub("owner/repo", 1)
    monkeypatch.setattr(api, "comments", lambda: list(comments))
    def call(path, body):
        reply = {"user": {"login": "github-actions[bot]"}, **body}
        comments.append(reply)
        return reply
    monkeypatch.setattr(api, "call", call)
    return api


def test_bot_intake_worker_completion_and_retry(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, "snapshot", lambda *args: {"fixture": "one"})
    comments = [{"id": 10, "user": {"login": "github-actions[bot]"}, "created_at": "2026-01-01",
                 "body": '/explore {"sets":["A","B"],"max_depth":2}'}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "test-sha")
    intake(api, state, cycle, "test-sha")
    assert len(list((state.path / "requests").glob("*.json"))) == 1
    assert len(comments) == 2
    worker(api, state, cycle, seconds=20)
    results = list((state.path / "jobs").glob("*/state.json"))
    assert json.loads(results[0].read_text())["status"] == "completed"
    saved = results[0].read_bytes()
    worker(api, state, cycle, seconds=20)
    assert results[0].read_bytes() == saved and len(comments) == 3


def test_accepted_reply_with_lost_response_is_not_posted_twice(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, "snapshot", lambda *args: {"fixture": "one"})
    comments = [{"id": 11, "user": {"login": "person"}, "created_at": "2026-01-01", "body": "/status"}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    original = api.call
    def lost(path, body):
        original(path, body)
        raise urllib.error.URLError("response lost after POST")
    monkeypatch.setattr(api, "call", lost)
    with pytest.raises(urllib.error.URLError):
        intake(api, state, cycle, "test-sha")
    assert (state.path / "receipts/11.json").exists()
    comments[0]["body"] = "/explore all"  # editing a processed comment is not a new request
    monkeypatch.setattr(api, "call", original)
    intake(api, state, cycle, "different-sha")
    assert len(comments) == 2 and not list((state.path / "requests").glob("*.json"))


def test_worker_refuses_to_mix_changed_inputs(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, "snapshot", lambda *args: {"fixture": "one"})
    comments = [{"id": 12, "user": {"login": "person"}, "created_at": "2026-01-01", "body": "/explore E1"}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "test-sha")
    monkeypatch.setattr(inbox, "snapshot", lambda *args: {"fixture": "two"})
    worker(api, state, cycle, seconds=20)
    saved = json.loads(next((state.path / "jobs").glob("*/state.json")).read_text())
    assert saved["status"] == "blocked" and saved["cursor"] == 0


def test_automatic_worker_without_comments_prepares_and_finishes(cycle, tmp_path, monkeypatch):
    import inbox
    import bank
    from autonomous import next_request
    inputs = {"fixture": "automatic"}
    monkeypatch.setattr(inbox, "snapshot", lambda *args: inputs)
    (cycle / "outputs/sets.jsonl").write_text(json.dumps(item()) + "\n")
    state = DiskState(tmp_path / "autostate")
    worker(None, state, cycle, seconds=20, autonomous=True)
    assert next_request(cycle, inputs, state.path) is None
    manifest = json.loads((state.path / "known/manifest.json").read_text())
    assert manifest["questions"] == 16
    q = Query(target="E1", ask="has_counterexample")
    assert bank.lookup(q, cycle / "outputs", state.path / "known") == answer(q, [item()])
    assert (state.path / "public/index.html").exists()
    before = {str(p): p.read_bytes() for p in state.path.rglob("*.json")}
    worker(None, state, cycle, seconds=20, autonomous=True)
    assert before == {str(p): p.read_bytes() for p in state.path.rglob("*.json")}
    assert next_request(cycle, {"fixture": "changed"}, state.path) is not None
    (cycle / "outputs/sets.jsonl").write_text(json.dumps(item(2, 2, listed=())) + "\n")
    assert bank.lookup(q, cycle / "outputs", state.path / "known") is None
    bank.prepare(cycle / "outputs", state.path / "known")
    assert bank.lookup(q, cycle / "outputs", state.path / "known")["answer"] == "いいえ"


def test_inbox_uses_prepared_bank(cycle, tmp_path, monkeypatch):
    import bank
    import inbox
    (cycle / "outputs/sets.jsonl").write_text(json.dumps(item()) + "\n")
    bank.prepare(cycle / "outputs", tmp_path / "known")
    monkeypatch.setattr(inbox, "answer", lambda *a: pytest.fail("prepared answer should be reused"))
    record, _ = ask_question('E1 に判例はある？', cycle / "outputs", cache=tmp_path / "answers")
    assert record["result"]["answer"] == "はい"


def test_neighbor_feedback_html_roundtrip_and_restart(cycle, tmp_path):
    from feedback import prepare_feedback, observe_report
    from autonomous import next_request
    from dragowing_inspect import inspect
    from neighbors import discover
    rows = [
        {'team': 'd', 'season': 2021, 'league': 'C', 'upper_half': False, 'rf_adv': -1., 'ra_adv': 1., 'vs_lower_wpct': .5},
        {'team': 't', 'season': 2021, 'league': 'C', 'upper_half': True, 'rf_adv': -.9, 'ra_adv': .9, 'vs_lower_wpct': .51},
        {'team': 'g', 'season': 2021, 'league': 'C', 'upper_half': True, 'rf_adv': 2., 'ra_adv': 2., 'vs_lower_wpct': .8},
        {'team': 's', 'season': 2020, 'league': 'C', 'upper_half': True, 'rf_adv': -1., 'ra_adv': 1., 'vs_lower_wpct': .5}]
    measured = discover(rows, excluded=[2020])
    assert measured['pairs'][0]['units'] == ['d-2021', 't-2021']
    assert measured['skipped'] == ['s-2020']
    assert discover(list(reversed(rows)), excluded=[2020]) == measured
    (cycle/'outputs/season.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
    (cycle/'outputs/sets.jsonl').write_text(json.dumps(item(listed=('d-2021',))) + '\n')
    # E2 is first in the registry; feedback must prioritize E1 instead.
    with (cycle/'sets.toml').open('a') as f:
        f.write('\n[[expr]]\nid="E2"\nexpr="B"\n')
    registry = cycle/'sets.toml'
    registry.write_text(registry.read_text().replace('[[expr]]\nid="E1"\nexpr="A"\n', '').replace('[[expr]]\nid="E2"\nexpr="B"\n', '[[expr]]\nid="E2"\nexpr="B"\n[[expr]]\nid="E1"\nexpr="A"\n'))
    state = tmp_path / 'feedback-state'
    root = Path(__file__).resolve().parents[2]
    prepare_feedback(root, cycle, state)
    observe_report(state)
    observation = json.loads((state/'feedback/blueprobe.json').read_text())
    assert observation['baseline'] and observation['added']
    pair = observation['rows']['d-2021|t-2021']
    assert pair['findings'][0]['target'] == 'E1'
    assert '未確認' in pair['findings'][0]['other_status']
    assert next_request(cycle, {'test': 1}, state)['seed'] == 'E1'
    before = {str(p): p.read_bytes() for p in state.rglob('*') if p.is_file()}
    prepare_feedback(root, cycle, state)
    observe_report(state)
    assert before == {str(p): p.read_bytes() for p in state.rglob('*') if p.is_file()}
    rows[0]['rf_adv'] = -1.1
    (cycle/'outputs/season.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
    prepare_feedback(root, cycle, state)
    observe_report(state)
    assert 'd-2021|t-2021' in json.loads((state/'feedback/blueprobe.json').read_text())['changed']
    assert len(list((state/'feedback/history').glob('*.json'))) == 2
    with pytest.raises(ValueError, match='未知'):
        inspect('<script id="report-data">{"research_observations":{"version":99}}</script>')
    with pytest.raises(ValueError, match='一意'):
        inspect('<script src="https://example.invalid"></script>')
