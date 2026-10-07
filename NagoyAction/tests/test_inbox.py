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
    def trusted_comments():
        for comment in comments:
            if "id" in comment:
                comment.setdefault("author_association", "COLLABORATOR")
        return list(comments)
    monkeypatch.setattr(api, "comments", trusted_comments)
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


def test_reply_failure_does_not_block_later_intake(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *a: {'fixture': 'one'})
    comments = [{'id': i, 'user': {'login': 'person'}, 'created_at': '2026-01-01', 'body': '/status'} for i in (31, 32)]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    original = api.call
    def flaky(path, body):
        if 'reply-31' in body['body']:
            raise urllib.error.URLError('not sent')
        return original(path, body)
    monkeypatch.setattr(api, 'call', flaky)
    intake(api, state, cycle, 'test')
    assert (state.path/'receipts/32.json').exists()
    assert (state.path/'pending-replies/reply-31.json').exists()
    assert any('reply-32' in c['body'] for c in comments)
    monkeypatch.setattr(api, 'call', original)
    intake(api, state, cycle, 'test')
    assert not list((state.path/'pending-replies').glob('*.json'))
    assert sum('reply-31' in c['body'] for c in comments) == 1
    assert sum('reply-32' in c['body'] for c in comments) == 1


def test_worker_bundled_completion_recovers_lost_response(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *a: {'fixture': 'one'})
    comments = [{'id': i, 'user': {'login': 'person'}, 'created_at': '2026-01-01', 'body': '/explore E1'} for i in (41, 42)]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'test')
    original = api.call
    def flaky(path, body):
        if 'result-41' in body['body']:
            original(path, body)  # response lost after successful POST
            raise urllib.error.URLError('lost response')
        return original(path, body)
    monkeypatch.setattr(api, 'call', flaky)
    worker(api, state, cycle, seconds=10)
    assert len(list((state.path/'pending-replies').glob('run-results-*.json'))) == 1
    assert any('result-42' in c['body'] for c in comments)
    results = {str(p):p.read_bytes() for p in (state.path/'jobs').rglob('*.json')}
    monkeypatch.setattr(api, 'call', original)
    worker(api, state, cycle, seconds=10)
    assert results == {str(p):p.read_bytes() for p in (state.path/'jobs').rglob('*.json')}
    assert not list((state.path/'pending-replies').glob('*.json'))
    assert sum('result-41' in c['body'] for c in comments) == 1


def test_status_distinguishes_request_counts_and_shared_jobs(tmp_path):
    from inbox import status_report
    for cid, job in [(1,'shared'),(2,'shared'),(3,'queued'),(4,'running'),(5,'bounded'),(6,'blocked'),(7,'error')]:
        atomic_json(tmp_path/'requests'/f'{cid}.json', {'comment_id': cid, 'job': job})
    for job,status in [('shared','completed'),('running','running'),('bounded','bounded'),('blocked','blocked'),('error','error'),('automatic','completed')]:
        atomic_json(tmp_path/'jobs'/job/'state.json', {'status':status,'cursor':0,'candidates':[],'results':[],'bounded': status == 'bounded'})
    atomic_json(tmp_path/'stops/2.json', {})
    text = status_report(tmp_path)
    for value in ['累積受付: 7件','待機: 1件','進行・再開待ち: 1件','完了: 1件','上限到達: 1件',
                  '停止: 1件','入力変更で保留: 1件','エラー: 1件','探索job: 6件']:
        assert value in text


def test_worker_comment_get_failure_does_not_interrupt_evaluation(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *a: {'fixture': 'one'})
    comments = [{'id': 51, 'user': {'login': 'person'}, 'created_at': '2026-01-01', 'body': '/explore E1'}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'test')
    def unavailable():
        raise urllib.error.URLError('cannot list comments')
    monkeypatch.setattr(api, 'comments', unavailable)
    worker(api, state, cycle, seconds=10)
    path = next((state.path/'jobs').glob('*/state.json'))
    assert json.loads(path.read_text())['status'] == 'completed'
    assert (state.path/'pending-replies/worker-comments.json').exists()
    monkeypatch.setattr(api, 'comments', lambda: list(comments))
    worker(api, state, cycle, seconds=10)
    assert not list((state.path/'pending-replies').glob('*.json'))
    assert sum('result-51' in c['body'] for c in comments) == 1


def test_buffered_checkpoints_limit_pushes_and_preserve_final(tmp_path, monkeypatch):
    import inbox
    clock = [0]
    monkeypatch.setattr(inbox.time, 'monotonic', lambda: clock[0])
    disk = DiskState(tmp_path)
    buffered = inbox.BufferedState(disk)
    buffered.sync()
    for i in range(1, 301):
        clock[0] = i
        buffered.save()
        buffered.sync()
    assert disk.saves == 1
    clock[0] = 301
    buffered.save()
    buffered.flush()
    assert disk.saves == 2


def test_stopped_manual_job_is_not_selected_automatically(cycle, tmp_path, monkeypatch):
    import inbox
    from autonomous import next_request
    inputs = {'fixture': 'stop'}
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: inputs)
    comments = [{'id': 501, 'user': {'login': 'anyone'}, 'created_at': '2026-01-01', 'body': '/explore E1'}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    request = json.loads((state.path/'requests/501.json').read_text())
    comments.append({'id': 502, 'user': {'login': 'anyone'}, 'created_at': '2026-01-01', 'body': '/stop 501'})
    intake(api, state, cycle, 'sha')
    assert next_request(cycle, inputs, state.path)['job'] != request['job']
    assert '停止' in inbox.status_report(state.path)
    # A different input fingerprint has a different job and is not suppressed.
    assert next_request(cycle, {'fixture': 'new'}, state.path)['seed'] == 'E1'


def test_trusted_exploration_has_five_pending_requests_per_author(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'quota'})
    comments = [{'id': i, 'user': {'login': 'trusted'}, 'created_at': '2026-01-01', 'body': '/explore E1'} for i in range(511,517)]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    assert len(list((state.path/'requests').glob('*.json'))) == 5
    assert '1人5件' in json.loads((state.path/'receipts/516.json').read_text())['error']
    comments.append({'id': 517, 'user': {'login': 'trusted'}, 'created_at': '2026-01-01', 'body': '/stop 511'})
    comments.append({'id': 518, 'user': {'login': 'trusted'}, 'created_at': '2026-01-01', 'body': '/explore E1'})
    intake(api, state, cycle, 'sha')
    assert (state.path/'requests/518.json').exists()


def test_worker_reads_comments_only_for_completion(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'poll'})
    comments = [{'id': 521, 'user': {'login': 'p'}, 'created_at': '2026-01-01', 'body': '/explore E1'}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    calls = []
    monkeypatch.setattr(api, 'comments', lambda: calls.append(1) or list(comments))
    original = inbox.Explorer.advance
    batches = []
    def small(self, saved, **kwargs):
        batches.append(1)
        return original(self, saved, seconds=10, max_steps=1)
    monkeypatch.setattr(inbox.Explorer, 'advance', small)
    worker(api, state, cycle, seconds=20)
    assert len(batches) > 2 and len(calls) == 1
    assert state.saves < len(batches)


def test_finished_stop_does_not_create_stop_record(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'terminal'})
    comments = [{'id': 531, 'user': {'login': 'p'}, 'created_at': '2026-01-01', 'body': '/explore E1'}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    worker(api, state, cycle, seconds=20)
    comments.append({'id': 532, 'user': {'login': 'p'}, 'created_at': '2026-01-01', 'body': '/stop 531'})
    intake(api, state, cycle, 'sha')
    assert not (state.path/'stops/531.json').exists()
    assert 'すでに終了' in json.loads((state.path/'receipts/532.json').read_text())['reply_body']


def test_missing_target_and_exclusion_are_unambiguous():
    from ask import render
    q = Query(target='E99', ask='has_counterexample')
    assert '答え: 判定不能' in render('', q, [], answer(q, [item()]))
    q = Query(ask='has_counterexample', exclude=['t'])
    text = render('', q, [], answer(q, [item(4,2)]))
    assert '元の成立率 2/4' in text and '除外後の判例 不明' in text
    assert 'None' not in text


def test_html_observation_failure_keeps_previous_and_worker_continues(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'html'})
    def bad(path):
        raise ValueError('unknown report')
    monkeypatch.setattr(inbox, 'observe_report', bad)
    (cycle/'outputs/sets.jsonl').write_text(json.dumps(item())+'\n')
    state = DiskState(tmp_path/'state')
    atomic_json(state.path/'feedback/blueprobe.json', {'previous': True})
    worker(None, state, cycle, seconds=20, autonomous=True)
    assert json.loads((state.path/'feedback/blueprobe.json').read_text()) == {'previous': True}
    assert (state.path/'feedback/report-error.json').exists()
    assert all(json.loads(p.read_text())['status'] == 'completed' for p in (state.path/'jobs').glob('*/state.json'))


@pytest.mark.parametrize('enabled', ['', '0', '1'])
def test_inbox_configuration_does_not_enable_automatic_research(monkeypatch, tmp_path, enabled):
    import inbox
    monkeypatch.setenv('AOI_RESEARCH_ENABLED', enabled)
    seen = []
    monkeypatch.setattr(inbox, 'State', lambda *args, **kwargs: DiskState(tmp_path))
    monkeypatch.setattr(inbox, 'worker', lambda *args, **kwargs: seen.append(kwargs['autonomous']))
    inbox.main(['worker', '--repository', 'owner/repo', '--issue', '1', '--state-dir', str(tmp_path)])
    assert seen == [enabled == '1']


def test_completion_bundles_use_run_id_without_run_api(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'run'})
    monkeypatch.setenv('GITHUB_RUN_ID', '98765')
    monkeypatch.setenv('GITHUB_REPOSITORY', 'owner/repo')
    comments = [{'id': i, 'user': {'login': 'p'}, 'created_at': '2026-01-01', 'body': '/explore E1'} for i in (601, 602)]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    calls, original = [], api.call
    def record(path, body):
        calls.append(path)
        return original(path, body)
    monkeypatch.setattr(api, 'call', record)
    worker(api, state, cycle, seconds=20)
    assert calls == ['/issues/1/comments']
    body = comments[-1]['body']
    assert 'run `98765`' in body and 'result-601' in body and 'result-602' in body
    worker(api, state, cycle, seconds=20)
    assert len(calls) == 1


@pytest.mark.parametrize('body', ['/ask E1 の判例', '/explore E1', '/status', '/stop 1'])
def test_untrusted_commands_are_ignored_before_work_and_reply(cycle, tmp_path, monkeypatch, body):
    import inbox
    monkeypatch.setenv('AOI_INBOX_ALLOWED_ACTORS', '[]')
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'gate'})
    def unexpected(*args, **kwargs):
        pytest.fail('untrusted comment must not invoke computation, status, or persistence')
    monkeypatch.setattr(inbox, 'ask_question', unexpected)
    monkeypatch.setattr(inbox, 'plan', unexpected)
    monkeypatch.setattr(inbox, 'status_report', unexpected)
    comments = [{'id': 701, 'user': {'login': 'outsider'}, 'author_association': 'NONE',
                 'created_at': '2026-01-01', 'body': body}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    monkeypatch.setattr(state, 'save', unexpected)
    intake(api, state, cycle, 'sha')
    assert len(comments) == 1 and not state.path.exists()


@pytest.mark.parametrize('login,association', [('owner','NONE'), ('someone','OWNER'),
    ('someone','MEMBER'), ('someone','COLLABORATOR'), ('github-actions[bot]','NONE'), ('allowed[bot]','NONE')])
def test_allowed_actor_handles_owner_members_and_explicit_bots(monkeypatch, login, association):
    from inbox import allowed_actor
    monkeypatch.setenv('AOI_INBOX_ALLOWED_ACTORS', '["Allowed[bot]"]')
    assert allowed_actor({'user': {'login': login}, 'author_association': association}, 'owner/repo')
    assert not allowed_actor({'user': {'login': 'other[bot]'}, 'author_association': 'NONE'}, 'owner/repo')


def test_allowlisted_bot_is_accepted_during_polling(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setenv('AOI_INBOX_ALLOWED_ACTORS', '["agent[bot]"]')
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'allowlist'})
    comments = [{'id': 711, 'user': {'login': 'agent[bot]'}, 'author_association': 'NONE',
                 'created_at': '2026-01-01', 'body': '/status'}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    assert (state.path/'receipts/711.json').exists() and len(comments) == 2


def test_total_pending_limit_still_applies_to_trusted_users(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, 'snapshot', lambda *args: {'fixture': 'global'})
    comments = [{'id': 720+i, 'user': {'login': f'trusted{i//5}'}, 'created_at': '2026-01-01',
                 'body': '/explore E1'} for i in range(21)]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path/'state')
    intake(api, state, cycle, 'sha')
    assert len(list((state.path/'requests').glob('*.json'))) == 20
    assert '全体20件' in json.loads((state.path/'receipts/740.json').read_text())['error']


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
    q = Query(target="E1", form="contrapositive")
    result = answer(q, [posthoc])
    assert result["rows"][0]["registration"] == "事後構成"
    assert "［事後構成］" in render("E1 の対偶", q, [], result)
    assert "対偶の成立率" in render("E1 の対偶", q, [], result)


def test_explore_is_not_saved_when_research_disabled(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.delenv("AOI_RESEARCH_ENABLED", raising=False)
    monkeypatch.setattr(inbox, "snapshot", lambda *args: {"fixture": "disabled"})
    comments = [{"id": 801, "user": {"login": "owner"}, "author_association": "OWNER",
                 "created_at": "2026-01-01", "body": "/explore E1"}]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    intake(api, state, cycle, "code", cycle_name="c001", result_sha="result")
    assert not list((state.path / "requests").glob("*.json"))
    assert "探索は未稼働" in comments[-1]["body"]
    assert "対象サイクル: `c001`" in comments[-1]["body"] and "結果SHA: `result`" in comments[-1]["body"]


def test_internal_error_isolated_and_next_comment_runs(cycle, tmp_path, monkeypatch):
    import inbox
    monkeypatch.setattr(inbox, "snapshot", lambda *args: {"fixture": "errors"})
    comments = [
        {"id": 811, "user": {"login": "owner"}, "author_association": "OWNER",
         "created_at": "2026-01-01", "body": "/ask broken"},
        {"id": 812, "user": {"login": "owner"}, "author_association": "OWNER",
         "created_at": "2026-01-01", "body": "/status"},
    ]
    api, state = fake_api(monkeypatch, comments), DiskState(tmp_path / "state")
    monkeypatch.setattr(inbox, "ask_question", lambda *args, **kwargs: (_ for _ in ()).throw(KeyError("choices")))
    intake(api, state, cycle, "code", cycle_name="c001", result_sha="result")
    receipt = json.loads((state.path / "receipts/811.json").read_text())
    assert receipt["error_type"] == "KeyError"
    assert (state.path / "receipts/812.json").exists()
    assert any("コマンド累積受付" in c["body"] for c in comments if c.get("user", {}).get("login") == "github-actions[bot]")
