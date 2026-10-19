"""Supervisor safety contracts plus a real Aoi Explorer subprocess round trip."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import pytest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("research_worker", SOURCE / "inbox/worker.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
AOI = Path(os.environ.get("AOI_WORKER_TEST_ROOT", SOURCE.parent))


@pytest.fixture
def enabled(monkeypatch):
    for key in ("GITHUB_ACTIONS", "GITHUB_ACTOR", "GITHUB_EVENT_NAME", "GITHUB_REF", "AOI_RESEARCH_ALLOWED_ACTORS"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AOI_RESEARCH_ENABLED", "1")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/Aoi")
    monkeypatch.setenv("AOI_RESEARCH_ACTOR", "owner")


@pytest.fixture
def research(tmp_path):
    root = tmp_path / "aoi"
    root.mkdir()
    for folder in ("research_loop", "pythdragoras"):
        (root / folder).mkdir()
        names = ["exploration.py"] if folder == "research_loop" else ["pythdragoras.py", "sets.py", "propositions.py"]
        for name in names:
            shutil.copyfile(AOI / folder / name, root / folder / name)
    for name in ("uv.lock", "pyproject.toml"):
        shutil.copyfile(AOI / name, root / name)
    cycle = root / "cycles/test"
    (cycle / "outputs").mkdir(parents=True)
    (cycle / "analysis.toml").write_text('[focus]\nteam="d"\n')
    (cycle / "propositions.toml").write_text('''[[proposition]]
id="P1"
statement="a implies lower half"
strength="usually"
if=[{col="a",op=">",value=0}]
then=[{col="upper_half",op="==",value=false}]
''')
    (cycle / "sets.toml").write_text('[[set]]\nid="A"\nfrom="P1"\n[[expr]]\nid="E1"\nexpr="A"\n')
    rows = [{"team": t, "team_name": t, "league": "C", "season": 2021,
             "a": a, "upper_half": upper} for t, a, upper in [("d", 1, False), ("t", 0, True)]]
    (cycle / "outputs/season.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    return root


def args(root, state, **kw):
    return argparse.Namespace(root=root, cycle="test", seed="all", state_dir=state,
                              seconds=kw.get("seconds", 30), max_steps=kw.get("max_steps", 20))


def test_disabled_and_actor_gates():
    base = {"GITHUB_REPOSITORY": "owner/Aoi", "AOI_RESEARCH_ACTOR": "owner"}
    for value in (None, "", "0", "true"):
        with pytest.raises(ValueError, match="disabled"):
            w.authorize({**base, **({"AOI_RESEARCH_ENABLED": value} if value else {})})
    with pytest.raises(ValueError, match="actor"):
        w.authorize({**base, "AOI_RESEARCH_ENABLED": "1", "AOI_RESEARCH_ACTOR": "outsider"})
    assert w.authorize({**base, "AOI_RESEARCH_ENABLED": "1"})["actor"] == "owner"
    for event, ref in [("pull_request", "refs/heads/main"), ("schedule", "refs/heads/main"),
                       ("workflow_dispatch", "refs/heads/topic")]:
        with pytest.raises(ValueError, match="trusted main"):
            w.authorize({**base, "AOI_RESEARCH_ENABLED": "1", "GITHUB_ACTIONS": "true",
                         "GITHUB_EVENT_NAME": event, "GITHUB_REF": ref})
    assert w.authorize({**base, "AOI_RESEARCH_ENABLED": "1", "GITHUB_ACTIONS": "true",
                        "GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main"})
    with pytest.raises(ValueError, match="array"):
        w.authorize({**base, "AOI_RESEARCH_ENABLED": "1", "AOI_RESEARCH_ALLOWED_ACTORS": '"owner"'})


def test_real_restart_exactly_matches_uninterrupted(research, tmp_path, enabled):
    before = {str(p): p.read_bytes() for p in research.rglob("*") if p.is_file()}
    one, resumed = tmp_path / "whole", tmp_path / "resumed"
    full = w.run(args(research, one))
    first = w.run(args(research, resumed, max_steps=2))
    assert first["status"] == "running" and first["cursor"] == 1
    w.run(args(research, resumed))
    assert w.load_checkpoint(one / "checkpoint.json") == w.load_checkpoint(resumed / "checkpoint.json")
    checkpoint = (resumed / "checkpoint.json").read_bytes()
    assert w.run(args(research, resumed))["units"] == 0
    assert (resumed / "checkpoint.json").read_bytes() == checkpoint
    assert full["status"] == "completed"
    results = w.load_checkpoint(one / "checkpoint.json")["state"]["results"]
    assert any(r["parent"] and r["motivated_by"] for r in results)
    signatures = [r["signature"] for r in results if "signature" in r]
    assert len(signatures) == len(set(signatures))
    assert before == {str(p): p.read_bytes() for p in research.rglob("*") if p.is_file()}


def test_timeout_keeps_last_committed_unit(research, tmp_path, enabled):
    state = tmp_path / "state"
    w.run(args(research, state, max_steps=1))
    original = (state / "checkpoint.json").read_bytes()
    def slow(*params):
        raise subprocess.TimeoutExpired("fixture", params[-1])
    result = w.run(args(research, state), evaluate_unit=slow)
    assert result["reason"] == "deadline"
    assert (state / "checkpoint.json").read_bytes() == original
    w.run(args(research, state))
    assert w.load_checkpoint(state / "checkpoint.json")["state"]["status"] == "completed"


def test_actual_subprocess_is_killed_at_deadline(research, enabled):
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        (research / "research_loop/exploration.py").write_text("import time; time.sleep(10)\n")
        w.evaluate(research, research / "cycles/test", "all", None, .15)
    assert time.monotonic() - started < 3


def test_stop_input_changes_corruption_lock_and_write_limit(research, tmp_path, enabled):
    state = tmp_path / "state"
    w.run(args(research, state, max_steps=1))
    checkpoint = state / "checkpoint.json"
    original = checkpoint.read_bytes()
    (state / "STOP").touch()
    assert w.run(args(research, state))["reason"] == "stopped"
    assert checkpoint.read_bytes() == original
    (state / "STOP").unlink()
    with w.lock_state(state), pytest.raises(ValueError, match="another worker"):
        w.run(args(research, state))
    with pytest.raises(ValueError, match="32 MiB"):
        w.atomic_checkpoint(checkpoint, "x" * w.MAX_BYTES)
    assert checkpoint.read_bytes() == original
    source = research / "cycles/test/sets.toml"
    source.write_text(source.read_text() + "\n# changed\n")
    with pytest.raises(ValueError, match="changed"):
        w.run(args(research, state))
    assert checkpoint.read_bytes() == original
    record = json.loads(original)
    record["payload"]["state"]["cursor"] += 1
    checkpoint.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="checksum"):
        w.load_checkpoint(checkpoint)


def test_inflight_change_is_not_committed(research, tmp_path, enabled):
    state = tmp_path / "state"
    def change(*params):
        result = w.evaluate(*params)
        (research / "cycles/test/analysis.toml").write_text('[focus]\nteam="t"\n')
        return result
    with pytest.raises(ValueError, match="during evaluation"):
        w.run(args(research, state), evaluate_unit=change)
    assert not (state / "checkpoint.json").exists()


def test_paths_and_offline_capabilities(research, tmp_path, enabled):
    with pytest.raises(ValueError, match="in-tree"):
        w.run(args(research, research / "cycles/test"))
    state = tmp_path / "state"
    state.mkdir()
    (state / "checkpoint.json").symlink_to(research / "uv.lock")
    with pytest.raises(ValueError, match="symlink"):
        w.run(args(research, state))
    for event, params in [("socket.connect", ()), ("subprocess.Popen", ()),
                           ("open", ("file", "w", 0)), ("os.rename", ())]:
        with pytest.raises(PermissionError):
            w._readonly_audit(event, params)
    assert "GH_TOKEN" not in w.child_env() and "HTTP_PROXY" not in w.child_env()
    for seconds in (0, 301):
        with pytest.raises(ValueError, match="seconds"):
            w.run(args(research, tmp_path / "unused", seconds=seconds))


def test_inbox_cli_worker_dispatch_needs_no_reader_dependencies(tmp_path):
    env = {**os.environ, "AOI_RESEARCH_ENABLED": "0"}
    result = subprocess.run([sys.executable, str(SOURCE / "inbox/inbox.py"), "worker", "--seconds", "1"],
                            env=env, text=True, capture_output=True, timeout=10)
    assert result.returncode == 1 and "worker disabled" in result.stderr


def test_normalized_state_path_cannot_escape_containment(research, tmp_path, enabled):
    alias = tmp_path / "aoi" / ".." / "aoi" / "cycles/test"
    with pytest.raises(ValueError, match="in-tree"):
        w.run(args(research, alias))


def test_cli_watchdog_also_bounds_snapshot(research, tmp_path, enabled):
    engine = tmp_path / "slow-worker.py"
    text = (SOURCE / "inbox/worker.py").read_text()
    engine.write_text(text.replace('def snapshot(root, cycle, seed):',
                                   'def snapshot(root, cycle, seed):\n    time.sleep(30)'))
    started = time.monotonic()
    result = subprocess.run([sys.executable, str(engine), "worker", "--root", str(research),
                             "--cycle", "test", "--seconds", "1", "--state-dir", str(tmp_path / "state")],
                            capture_output=True, text=True, timeout=5)
    assert result.returncode == 124
    assert time.monotonic() - started < 4
    assert "wall-clock deadline" in result.stderr


@pytest.mark.parametrize("sig", [15, 2])
def test_cli_signals_do_not_orphan_worker(research, tmp_path, enabled, sig):
    marker = tmp_path / "pid"
    engine = tmp_path / "slow-worker.py"
    text = (SOURCE / "inbox/worker.py").read_text()
    engine.write_text(text.replace('def snapshot(root, cycle, seed):',
        f'def snapshot(root, cycle, seed):\n    Path({str(marker)!r}).write_text(str(os.getpid()))\n    time.sleep(30)'))
    with subprocess.Popen([sys.executable, str(engine), "worker", "--root", str(research),
                            "--cycle", "test", "--seconds", "2", "--state-dir", str(tmp_path / "state")],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) as cli:
        until = time.monotonic() + 3
        while not marker.exists() and time.monotonic() < until:
            time.sleep(.01)
        assert marker.exists()
        pid = int(marker.read_text())
        cli.send_signal(sig)
        cli.communicate(timeout=4)
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)
        assert cli.returncode == 124


@pytest.mark.parametrize("mode", ["_step", "_run"])
def test_internal_entry_points_also_require_opt_in(mode):
    result = subprocess.run([sys.executable, str(SOURCE / "inbox/worker.py"), mode],
                            env={**os.environ, "AOI_RESEARCH_ENABLED": "0"},
                            text=True, capture_output=True, timeout=5)
    assert result.returncode == 1 and "worker disabled" in result.stderr


@pytest.fixture
def bundle(research):
    import hashlib
    cycle = research / "cycles/test"
    extended = cycle / "extended"
    shutil.copytree(cycle / "outputs", extended / "outputs")
    for name in ("analysis.toml", "propositions.toml"):
        shutil.copyfile(cycle / name, extended / name)
    paths = {"analysis": extended / "analysis.toml", "propositions": extended / "propositions.toml",
             "season": extended / "outputs/season.jsonl", "sets": cycle / "sets.toml"}
    data = {"schema": 1, "id": "test-v1", "source": "extended", "contract": {},
            "sha256": {role: hashlib.sha256(path.read_bytes()).hexdigest() for role, path in paths.items()}}
    directory = cycle / "input-bundles"
    directory.mkdir()
    manifest = directory / "test-v1.json"
    manifest.write_text(json.dumps(data))
    return research, cycle, manifest, data


def test_bundle_explicit_paths_and_manifest_in_snapshot(bundle):
    root, cycle, manifest, data = bundle
    selected = w.resolve_bundle(root, cycle, "test-v1")
    assert selected["paths"]["analysis"] == cycle / "extended/analysis.toml"
    snapshot = w.bundle_snapshot(root, cycle, "all", "test-v1")
    assert snapshot["input_bundle"] == "test-v1"
    assert manifest.relative_to(root).as_posix() in snapshot["files"]
    assert all(p.relative_to(root).as_posix() in snapshot["files"] for p in selected["paths"].values())
    assert "input_bundle" not in w.bundle_snapshot(root, cycle, "all", None)
    for name in ("../test-v1", "/test-v1", "test-v2"):
        with pytest.raises((ValueError, FileNotFoundError)):
            w.resolve_bundle(root, cycle, name)


@pytest.mark.parametrize("mutation", ["hash", "missing", "symlink", "parent_symlink", "source_escape", "overlay", "role", "id"])
def test_bundle_rejects_mixed_missing_or_unsafe_inputs(bundle, tmp_path, mutation):
    root, cycle, manifest, data = bundle
    source = cycle / "extended/propositions.toml"
    if mutation == "hash":
        source.write_text(source.read_text() + "\n# drift")
    elif mutation == "missing":
        source.unlink()
    elif mutation == "symlink":
        source.unlink()
        source.symlink_to(cycle / "propositions.toml")
    elif mutation == "parent_symlink":
        shutil.move(cycle / "extended", tmp_path / "external")
        (cycle / "extended").symlink_to(tmp_path / "external", target_is_directory=True)
    elif mutation == "source_escape":
        data["source"] = "../test"
    elif mutation == "overlay":
        data["paths"] = {"propositions": "propositions.toml"}
    elif mutation == "role":
        data["sha256"].pop("analysis")
    elif mutation == "id":
        data["id"] = "other"
    manifest.write_text(json.dumps(data))
    with pytest.raises((ValueError, FileNotFoundError)):
        w.resolve_bundle(root, cycle, "test-v1")


def test_bundle_selection_and_manifest_change_refuse_resume(bundle, tmp_path, enabled):
    root, cycle, manifest, data = bundle
    state = tmp_path / "selected-state"
    selected = args(root, state, max_steps=1)
    selected.input_bundle = "test-v1"
    # Pinned pre-bundle Aoi may not support the new Explorer API yet. This test
    # isolates the supervisor manifest contract; real c001 replay belongs to Aoi.
    def initial(*a, **kw):
        assert kw == {"input_bundle": "test-v1"}
        return {"status": "running", "cursor": 0}
    w.run(selected, evaluate_unit=initial)
    before = (state / "checkpoint.json").read_bytes()
    with pytest.raises(ValueError, match="changed"):
        w.run(args(root, state), evaluate_unit=initial)
    data["contract"] = {"changed": True}
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="changed"):
        w.run(selected, evaluate_unit=initial)
    assert (state / "checkpoint.json").read_bytes() == before
