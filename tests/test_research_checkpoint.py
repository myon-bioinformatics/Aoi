"""Offline trust-boundary and real c001 artifact replay regressions."""
import importlib.util
import io
import json
import os
import re
from pathlib import Path
import stat
import struct
import subprocess
import sys
import urllib.error
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("research_checkpoint", ROOT / "scripts/research_checkpoint.py")
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)


@pytest.fixture
def trusted():
    context = {"repository": t.REPOSITORY, "repository_id": 1402862784,
               "head_sha": "a" * 40, "workflow_id": 42, "workflow_path": t.WORKFLOW,
               "workflow_sha256": "b" * 64, "run_id": 200, "run_attempt": 1}
    source = {"id": 100, "run_attempt": 2, "repository": {"full_name": t.REPOSITORY, "id": 1402862784},
              "head_repository": {"id": 1402862784}, "event": "workflow_dispatch", "head_branch": "main",
              "head_sha": context["head_sha"], "workflow_id": 42, "path": t.WORKFLOW,
              "actor": {"login": "myon-bioinformatics"}, "triggering_actor": {"login": "myon-bioinformatics"},
              "status": "completed", "conclusion": "success"}
    return context, source


def make_archive(data, context, source, expected, *, files=None, provenance=None):
    origin = {**context, "run_id": source["id"], "run_attempt": source["run_attempt"]}
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in (files or [("checkpoint.json", data),
            ("provenance.json", t.seal(data, origin, expected) if provenance is None else provenance)]):
            archive.writestr(name, content)
    blob = stream.getvalue()
    metadata = {"id": 99, "name": t.artifact_name(source["id"], source["run_attempt"]),
                "expired": False, "size_in_bytes": len(blob), "digest": "sha256:" + t.sha(blob),
                "workflow_run": {"id": source["id"], "repository_id": context["repository_id"],
                                 "head_repository_id": context["repository_id"], "head_branch": "main",
                                 "head_sha": context["head_sha"]}}
    return blob, metadata


def record(expected):
    payload = {"manifest": expected, "state": {"status": "running", "cursor": 1}}
    return t.encode({"payload": payload, "sha256": t.sha(t.encode(payload))})


class FakeAPI:
    def __init__(self, source, metadata, blob):
        self.source, self.metadata, self.blob = source, metadata, blob
        self.downloads = 0

    def get(self, path):
        if path.startswith("actions/runs/"):
            return self.source
        if path.startswith("actions/artifacts/"):
            return self.metadata
        raise AssertionError(path)

    def archive(self, artifact_id):
        self.downloads += 1
        return self.blob


@pytest.mark.parametrize("field,value", [
    ("event", "pull_request"), ("event", "push"), ("head_branch", "topic"),
    ("head_sha", "c" * 40), ("workflow_id", 77), ("path", ".github/workflows/evil.yml"),
    ("status", "in_progress"), ("conclusion", "failure"), ("conclusion", "cancelled"),
    ("actor.login", "other"), ("triggering_actor.login", "other"),
    ("repository.id", 11), ("repository.full_name", "fork/Aoi"), ("head_repository.id", 11),
    ("id", 101), ("run_attempt", 1),
])
def test_untrusted_source_rejected_before_download_or_state_write(tmp_path, trusted, field, value):
    context, source = trusted
    expected = {"input": "pinned"}
    blob, metadata = make_archive(record(expected), context, source, expected)
    parts = field.split(".")
    target = source
    for key in parts[:-1]:
        target = target[key]
    target[parts[-1]] = value
    api = FakeAPI(source, metadata, blob)
    with pytest.raises(ValueError):
        t.restore(api, context, expected, tmp_path / "state", 100, 2, 99)
    assert api.downloads == 0 and not (tmp_path / "state").exists()


@pytest.mark.parametrize("field,value", [
    ("id", 98), ("name", "research-checkpoint-100-1"), ("expired", True),
    ("size_in_bytes", t.MAX_ARCHIVE + 1), ("digest", None), ("digest", ""),
    ("workflow_run.id", 111), ("workflow_run.repository_id", 11),
    ("workflow_run.head_repository_id", 11), ("workflow_run.head_branch", "topic"),
    ("workflow_run.head_sha", "d" * 40),
])
def test_untrusted_artifact_rejected_before_download(tmp_path, trusted, field, value):
    context, source = trusted
    expected = {"input": "pinned"}
    blob, metadata = make_archive(record(expected), context, source, expected)
    parts = field.split(".")
    target = metadata
    for key in parts[:-1]:
        target = target[key]
    target[parts[-1]] = value
    api = FakeAPI(source, metadata, blob)
    with pytest.raises((ValueError, TypeError)):
        t.restore(api, context, expected, tmp_path / "state", 100, 2, 99)
    assert api.downloads == 0 and not (tmp_path / "state").exists()


@pytest.mark.parametrize("mutation", ["digest", "crc", "provenance", "workflow", "manifest", "checksum",
    "traversal", "code", "duplicate", "symlink", "oversized", "nonfinite", "duplicate_json"])
def test_corrupt_archive_never_installs_state(tmp_path, trusted, mutation):
    context, source = trusted
    expected = {"input": "pinned"}
    data = record(expected)
    blob, metadata = make_archive(data, context, source, expected)
    if mutation == "digest":
        blob = blob[:-1] + bytes([blob[-1] ^ 1])
    else:
        origin = {**context, "run_id": 100, "run_attempt": 2}
        prov = t.decode(t.seal(data, origin, expected))
        files = [("checkpoint.json", data), ("provenance.json", t.encode(prov))]
        if mutation == "provenance":
            prov["origin"]["run_id"] = 101
        elif mutation == "workflow":
            prov["origin"]["workflow_sha256"] = "e" * 64
        elif mutation == "manifest":
            expected = {"input": "changed"}
        elif mutation == "checksum":
            files[0] = ("checkpoint.json", data.replace(b'"cursor":1', b'"cursor":2'))
        elif mutation == "traversal":
            files[0] = ("../checkpoint.json", data)
        elif mutation == "code":
            files.append(("worker.py", b'raise RuntimeError("downloaded code")'))
        elif mutation == "duplicate":
            files.append(("checkpoint.json", data))
        elif mutation == "symlink":
            info = zipfile.ZipInfo("checkpoint.json")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            files[0] = (info, data)
        elif mutation == "oversized":
            files[0] = ("checkpoint.json", b"x" * (t.MAX_CHECKPOINT + 1))
        elif mutation == "nonfinite":
            files[0] = ("checkpoint.json", b'{"x":NaN}')
        elif mutation == "duplicate_json":
            files[0] = ("checkpoint.json", b'{"x":1,"x":2}')
        files[1] = ("provenance.json", t.encode(prov))
        blob, metadata = make_archive(data, context, source, {"input": "pinned"}, files=files)
        if mutation == "crc":
            # Mutate the compressed checkpoint while retaining valid ZIP directory.
            damaged = bytearray(blob)
            damaged[50] ^= 0xff
            blob = bytes(damaged)
            metadata["digest"] = "sha256:" + t.sha(blob)
    api = FakeAPI(source, metadata, blob)
    with pytest.raises((ValueError, KeyError, zipfile.BadZipFile)):
        t.restore(api, context, expected, tmp_path / "state", 100, 2, 99)
    assert not (tmp_path / "state").exists()


def test_forged_zip_sizes_never_trigger_unbounded_decompression(tmp_path, trusted, monkeypatch):
    context, source = trusted
    expected = {"input": "pinned"}
    data = record(expected)
    blob, metadata = make_archive(data, context, source, expected,
        files=[("checkpoint.json", b"x" * (2 * 1024 * 1024)), ("provenance.json", b"{}")])
    forged = bytearray(blob)
    directory = forged.index(b"PK\x01\x02")
    struct.pack_into("<I", forged, directory + 24, 1)
    blob = bytes(forged)
    metadata["digest"] = "sha256:" + t.sha(blob)
    reads = []
    original = zipfile.ZipExtFile.read
    def read(member, n=-1):
        reads.append(n)
        assert 0 < n <= t.MAX_CHECKPOINT + 1
        return original(member, n)
    monkeypatch.setattr(zipfile.ZipExtFile, "read", read)
    with pytest.raises(ValueError, match="corrupt archive member"):
        t.restore(FakeAPI(source, metadata, blob), context, expected, tmp_path / "state", 100, 2, 99)
    assert reads == [2] and not (tmp_path / "state").exists()


def cli(state, steps):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "AOI_RESEARCH_"))}
    env.update(AOI_RESEARCH_ENABLED="1", AOI_RESEARCH_ACTOR="offline-artifact-test",
               AOI_RESEARCH_ALLOWED_ACTORS='["offline-artifact-test"]', GITHUB_REPOSITORY=t.REPOSITORY)
    result = subprocess.run([sys.executable, str(ROOT / "nagoyaction/inbox/worker.py"), "worker",
        "--root", str(ROOT), "--cycle", t.CYCLE, "--input-bundle", t.BUNDLE, "--seed", t.SEED,
        "--seconds", "60", "--max-steps", str(steps), "--state-dir", str(state)],
        env=env, capture_output=True, text=True, timeout=65)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_real_c001_artifact_roundtrip_resume_equality_and_completed_noop(tmp_path, trusted):
    context, source = trusted
    expected = t.manifest()
    cycle = ROOT / "cycles" / t.CYCLE
    before = {str(p): t.sha(p.read_bytes()) for p in cycle.rglob("*") if p.is_file()}
    whole, interrupted, restored = [tmp_path / name for name in ("whole", "interrupted", "restored")]
    cli(whole, 5)
    cli(interrupted, 2)
    blob, metadata = make_archive((interrupted / "checkpoint.json").read_bytes(), context, source, expected)
    t.restore(FakeAPI(source, metadata, blob), context, expected, restored, 100, 2, 99)
    cli(restored, 3)
    assert (restored / "checkpoint.json").read_bytes() == (whole / "checkpoint.json").read_bytes()
    # Finish the real E1 plan, then transport the terminal checkpoint to a fresh
    # runner directory and assert zero units and byte-identical checkpoint.
    done = cli(restored, 1000)
    assert done["status"] == "completed"
    data = (restored / "checkpoint.json").read_bytes()
    blob, metadata = make_archive(data, context, source, expected)
    terminal = tmp_path / "terminal"
    t.restore(FakeAPI(source, metadata, blob), context, expected, terminal, 100, 2, 99)
    path = terminal / "checkpoint.json"
    old_mtime = path.stat().st_mtime_ns
    report = cli(terminal, 5)
    assert report["units"] == 0 and report["reason"] == "completed"
    assert path.read_bytes() == data and path.stat().st_mtime_ns == old_mtime
    assert before == {str(p): t.sha(p.read_bytes()) for p in cycle.rglob("*") if p.is_file()}


def test_current_context_requires_trusted_dispatch_and_api_metadata(tmp_path, monkeypatch, trusted):
    context, source = trusted
    (tmp_path / t.WORKFLOW).parent.mkdir(parents=True)
    (tmp_path / t.WORKFLOW).write_text("reviewed workflow")
    current = {**source, "id": 200, "run_attempt": 1, "status": "in_progress", "conclusion": None}
    class API:
        def get(self, path):
            if path == "":
                return {"id": context["repository_id"], "full_name": t.REPOSITORY, "fork": False, "default_branch": "main"}
            if path.startswith("actions/workflows/"):
                return {"path": t.WORKFLOW, "id": 42, "state": "active"}
            assert path == "actions/runs/200/attempts/1"
            return current
    env = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": t.REPOSITORY, "GITHUB_EVENT_NAME": "workflow_dispatch",
           "GITHUB_REF": "refs/heads/main", "GITHUB_ACTOR": "myon-bioinformatics",
           "GITHUB_TRIGGERING_ACTOR": "myon-bioinformatics", "GITHUB_SHA": "a" * 40,
           "GITHUB_WORKFLOW_REF": f"{t.REPOSITORY}/{t.WORKFLOW}@refs/heads/main",
           "GITHUB_WORKFLOW_SHA": "a" * 40, "AOI_RESEARCH_ENABLED": "1", "CANARY_ENABLE": "true",
           "GITHUB_RUN_ID": "200", "GITHUB_RUN_ATTEMPT": "1", "GITHUB_REPOSITORY_ID": str(context["repository_id"])}
    monkeypatch.setattr(t.subprocess, "check_output", lambda cmd, **kw: "a" * 40 if cmd[1] == "rev-parse" else "")
    assert t.current_context(API(), env, tmp_path)["head_sha"] == "a" * 40
    for key, value in [("GITHUB_EVENT_NAME", "push"), ("GITHUB_REF", "refs/pull/1/merge"),
                       ("GITHUB_REPOSITORY", "fork/Aoi"), ("GITHUB_TRIGGERING_ACTOR", "other"),
                       ("GITHUB_ACTOR", "other"), ("AOI_RESEARCH_ENABLED", "0"), ("CANARY_ENABLE", "false"),
                       ("GITHUB_WORKFLOW_SHA", "b" * 40), ("GITHUB_WORKFLOW_REF", "untrusted"),
                       ("GITHUB_REPOSITORY_ID", "1")]:
        with pytest.raises(ValueError):
            t.current_context(API(), {**env, key: value}, tmp_path)
    current["head_sha"] = "b" * 40
    with pytest.raises(ValueError):
        t.current_context(API(), env, tmp_path)


def test_manual_workflow_remains_double_disabled_and_read_only():
    text = (ROOT / t.WORKFLOW).read_text()
    assert "schedule:" not in text and "pull_request:" not in text and "push:" not in text
    assert "default: false" in text and "vars.AOI_RESEARCH_ENABLED == '1'" in text
    assert "github.triggering_actor == 'myon-bioinformatics'" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "contents: read" in text and "actions: read" in text and ": write" not in text
    assert "persist-credentials: false" in text and "timeout-minutes: 8" in text


def test_trusted_canary_bootstrap_is_immutable():
    text = (ROOT / t.WORKFLOW).read_text()
    # The project lock cannot pin the setup actions that interpret it.
    # Those stay on the parent form: a release commit plus # vX.Y.Z.
    # checkout and upload-artifact are pinned the same way (2026-10-31).
    uses = re.findall(r"^\s*(?:-\s*)?uses:\s*(\S+)", text, re.MULTILINE)
    assert uses == [
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2",
        "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9",
    ]
    # The interpreter comes from uv (exact patch), not from a second setup action.
    assert "actions/setup-python" not in text
    assert 'python-version: "3.14.8"' in text
    assert "astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3" in text
    assert 'version: "latest"' in text
    assert "pip install" not in text
    assert "uv sync --frozen" in text


def test_signed_download_never_forwards_token_and_checks_length():
    api = t.GitHub("test-secret-must-not-leave-api")
    calls = []
    class Response:
        headers = {"Content-Length": "3"}
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def read(self, limit):
            return b"zip"
    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            if len(calls) == 1:
                raise urllib.error.HTTPError(request.full_url, 302, "redirect",
                    {"Location": "https://blob.example.net/signed?secret=signature"}, None)
            return Response()
    api.opener = Opener()
    assert api.archive(99) == b"zip"
    assert calls[0].get_header("Authorization") == "Bearer test-secret-must-not-leave-api"
    assert calls[1].get_header("Authorization") is None
    assert t.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other/") is None
    with pytest.raises(ValueError, match="response size"):
        api.request("https://blob.example.net/", authenticated=False, limit=2)
    with pytest.raises(ValueError, match="API origin"):
        api.request("https://other.example/", authenticated=True, limit=10)


@pytest.mark.parametrize("location", ["http://blob.example/x", "file:///etc/passwd", "https://u:p@blob.example/x"])
def test_unsafe_download_redirect_is_refused(location):
    api = t.GitHub("test-secret")
    class Opener:
        def open(self, request, timeout):
            raise urllib.error.HTTPError(request.full_url, 302, "redirect", {"Location": location}, None)
    api.opener = Opener()
    with pytest.raises(ValueError, match="unsafe artifact redirect"):
        api.archive(99)


def test_worker_mode_strips_credentials_and_enforces_budgets(tmp_path, monkeypatch):
    env = {"RUNNER_TEMP": str(tmp_path), "CANARY_SECONDS": "30", "CANARY_STEPS": "2",
           "AOI_RESEARCH_ENABLED": "1", "GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": t.REPOSITORY,
           "GITHUB_ACTOR": "myon-bioinformatics", "GITHUB_EVENT_NAME": "workflow_dispatch",
           "GITHUB_REF": "refs/heads/main", "GH_TOKEN": "secret", "GITHUB_TOKEN": "secret",
           "ACTIONS_RUNTIME_TOKEN": "secret", "PYTHONPATH": "untrusted", "HOME": "untrusted"}
    monkeypatch.setattr(t.os, "environ", env)
    argv = ["run", "--state", str(tmp_path / "aoi-research-state"),
            "--output", str(tmp_path / "aoi-research-export")]
    calls = []
    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 124)
    monkeypatch.setattr(t.subprocess, "run", run)
    assert t.main(argv) == 0
    clean = calls[0][1]["env"]
    assert not {"GH_TOKEN", "GITHUB_TOKEN", "ACTIONS_RUNTIME_TOKEN", "PYTHONPATH"} & set(clean)
    assert clean["HOME"] == "/nonexistent" and calls[0][1]["timeout"] == 40
    for key, value in [("CANARY_SECONDS", "61"), ("CANARY_STEPS", "6"),
                       ("CANARY_SECONDS", "0"), ("CANARY_STEPS", "$(echo bad)")]:
        with monkeypatch.context() as patch:
            patch.setitem(env, key, value)
            with pytest.raises(ValueError):
                t.main(argv)
    assert len(calls) == 1
