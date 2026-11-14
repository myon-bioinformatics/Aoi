"""research_loop/: #48 の前の NagoyAction/tests/test_inbox.py から、復元したモジュールに関わるテストを移した。

元のテストのうち、旧 inbox.py（worker の autonomous=True など）に依存するものは、
今の nagoyaction/inbox/inbox.py がその機能を持たないため移していない（PR 本文の「未接続」を参照）。

旧 test_research_worker_gate.py もここにまとめた（節の頭に旧ファイルの名前を書いた）。
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research_loop"))

import pytest  # noqa: E402
from exploration import atomic_json, Explorer, plan, read_state, save_state, snapshot  # noqa: E402


# ==== loop（旧 test_research_loop.py）

def item(n=2, hold=1, unknown=0, listed=("t-2015",)):
    return {"id": "E1", "forms": [{"form": "original", "n": n, "hold": hold, "undetermined": unknown,
            "rate": hold / n if n else None, "counterexamples": [{"unit": u} for u in listed]}]}


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


def test_snapshot_fingerprints_the_lowercase_layout():
    real = ROOT / "cycles/c001-chunichi"
    keys = set(snapshot(ROOT, real))
    assert {"pythdragoras/pythdragoras.py", "pythdragoras/sets.py", "pythdragoras/propositions.py",
            "research_loop/exploration.py"} <= keys


def test_stopped_job_is_not_selected_automatically(cycle, tmp_path):
    from autonomous import next_request
    from exploration import digest
    state = tmp_path / "state"
    inputs = {"fixture": "stop"}
    first = next_request(cycle, inputs, state)
    assert first["seed"] == "E1" and first["origin"] == "automatic"
    atomic_json(state / "requests/501.json", {"job": first["job"]})
    atomic_json(state / "stops/501.json", {"by": "anyone"})
    second = next_request(cycle, inputs, state)
    assert second["job"] != first["job"] and second["seed"] == "all"
    # 入力が違えば別の仕事なので、止めた仕事として扱わない
    assert next_request(cycle, {"fixture": "new"}, state)["seed"] == "E1"
    # 終わった仕事は二度と出さない
    atomic_json(state / "jobs" / second["job"] / "state.json", {"status": "completed"})
    assert next_request(cycle, inputs, state) is None
    assert len(digest({"x": 1})) == 64


def test_neighbor_feedback_html_roundtrip_and_restart(cycle, tmp_path):
    from autonomous import next_request
    from dragowing_inspect import inspect
    from feedback import observe_report, prepare_feedback
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
    prepare_feedback(ROOT, cycle, state)
    observe_report(state)
    observation = json.loads((state/'feedback/blueprobe.json').read_text())
    assert observation['baseline'] and observation['added']
    pair = observation['rows']['d-2021|t-2021']
    assert pair['findings'][0]['target'] == 'E1'
    assert '未確認' in pair['findings'][0]['other_status']
    assert next_request(cycle, {'test': 1}, state)['seed'] == 'E1'
    before = {str(p): p.read_bytes() for p in state.rglob('*') if p.is_file()}
    prepare_feedback(ROOT, cycle, state)
    observe_report(state)
    assert before == {str(p): p.read_bytes() for p in state.rglob('*') if p.is_file()}
    rows[0]['rf_adv'] = -1.1
    (cycle/'outputs/season.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
    prepare_feedback(ROOT, cycle, state)
    observe_report(state)
    assert 'd-2021|t-2021' in json.loads((state/'feedback/blueprobe.json').read_text())['changed']
    assert len(list((state/'feedback/history').glob('*.json'))) == 2
    with pytest.raises(ValueError, match='未知'):
        inspect('<script id="report-data">{"research_observations":{"version":99}}</script>')
    with pytest.raises(ValueError, match='一意'):
        inspect('<script src="https://example.invalid"></script>')


# ==== gate（旧 test_research_worker_gate.py）
# Keep Actions activation deferred while NagoyAction's offline worker is reviewed.
#
# No live Actions entry point is restored before exact-head CI, independent review
# and a separate canary decision. The question inbox remains independent.


WORKFLOWS = ROOT / ".github" / "workflows"


def test_worker_has_no_actions_entry_point_before_canary_review():
    # Check all live workflows, not only the former research-worker filename:
    # otherwise a renamed cron job could reproduce the failure.
    assert not (WORKFLOWS / "research-worker.yml").exists()
    for workflow in (*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")):
        assert "nagoyaction/pipelines/research.toml" not in workflow.read_text(
            encoding="utf-8"
        ), workflow.name


def test_inbox_schedule_and_intake_pipeline_are_preserved():
    workflow = (WORKFLOWS / "research-inbox.yml").read_text(encoding="utf-8")
    assert "schedule:" in workflow
    assert "vars.AOI_INBOX_ISSUE" in workflow
    assert "nagoyaction/pipelines/inbox.toml" in workflow
    assert "nagoyaction/pipelines/research.toml" not in workflow

    with (ROOT / "nagoyaction/pipelines/inbox.toml").open("rb") as source:
        pipeline = tomllib.load(source)
    assert len(pipeline["step"]) == 1
    assert pipeline["step"][0]["name"] == "intake"
    assert pipeline["step"][0]["run"] == [
        "python", "nagoyaction/inbox/inbox.py", "intake"
    ]


def test_research_cli_requires_explicit_enablement():
    import os
    for enabled in ("", "0"):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "nagoyaction/inbox/inbox.py"), "worker", "--seconds", "1"],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=False,
            env={**os.environ, "AOI_RESEARCH_ENABLED": enabled, "AOI_INBOX_ISSUE": "1"},
        )
        assert completed.returncode == 1
        assert "worker disabled" in completed.stderr


def test_owner_pipeline_is_offline_and_bounded():
    with (ROOT / "nagoyaction/pipelines/research.toml").open("rb") as source:
        pipeline = tomllib.load(source)
    assert len(pipeline["step"]) == 1
    assert pipeline["step"][0]["network"] is False
    assert "18000" not in pipeline["step"][0]["run"]
