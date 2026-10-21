"""Local rollout contract; adopted vendor locks are deliberately independent."""
import re
from pathlib import Path

import pytest

PARENT = "myon-bioinformatics/myon-bioinformatics"
PARENT_WORKFLOW_PIN = "2192ff22acafdd09e80ac722df91ee937aaedd5e"
ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows").is_dir())


def test_parent_reusable_workflow_uses_are_one_full_sha():
    """Parent reusable-workflow uses refs are the reviewed 40-character SHA.

    Runtime tool checkouts are resolved separately and are outside this contract.
    """
    at = chr(64)
    pattern = re.compile(
        r"uses:\s*['\"]?"
        + re.escape(PARENT)
        + r"/\.github/workflows/[^\s'\"]+"
        + at
        + r"([^\s'\"]+)"
    )
    pins = []
    for path in sorted((ROOT / ".github/workflows").glob("*")):
        if path.suffix not in (".yml", ".yaml"):
            continue
        pins.extend(pattern.findall(path.read_text(encoding="utf-8")))
    assert pins, "parent reusable workflow uses must remain observable"
    assert set(pins) == {PARENT_WORKFLOW_PIN}, pins


@pytest.mark.parametrize("fault", [None, "repository", "source", "commit", "sha256", "identity", "payload"])
def test_frozen_distribution_compiler_checks_identity_before_saving(tmp_path, monkeypatch, fault):
    """Run the workflow adapter offline, including its refusal paths."""
    import hashlib
    import json
    import subprocess
    import textwrap

    text = (ROOT / ".github/workflows/min-distributions.yml").read_text()
    step = text.split("      - name: Restore approved frozen distribution compiler\n", 1)[1]
    program = textwrap.dedent(step.split("<<'PYCODE'\n", 1)[1].split("\n          PYCODE", 1)[0])
    payload = b"raise RuntimeError('compiler bytes must not execute while being fetched')\n"
    tool = {"repository": PARENT, "source": "tools/minpy.py", "commit": "a" * 40,
            "sha256": hashlib.sha256(payload).hexdigest()}
    if fault in {"repository", "source", "commit", "sha256"}:
        tool[fault] = "untrusted"
    manifest = json.dumps({"tool": tool})
    monkeypatch.chdir(tmp_path)
    (tmp_path / "distributions.json").write_text(manifest)
    (tmp_path / ".test-deps").mkdir()
    calls = []

    def fetch(argv, **kwargs):
        calls.append(argv)
        assert argv == ["git", "-C", ".test-deps/distribution-tools", "fetch", "--depth=1", "origin", "a" * 40]

    def observe(argv, **kwargs):
        if argv[-1] == "FETCH_HEAD":
            return ("b" * 40 if fault == "identity" else "a" * 40) + "\n"
        assert argv[-1] == "a" * 40 + ":tools/minpy.py"
        return b"changed" if fault == "payload" else payload

    monkeypatch.setattr(subprocess, "run", fetch)
    monkeypatch.setattr(subprocess, "check_output", observe)
    if fault:
        with pytest.raises(SystemExit):
            exec(compile(program, "min-distributions.yml", "exec"), {})
        assert not (tmp_path / ".test-deps/frozen-minpy.py").exists()
    else:
        exec(compile(program, "min-distributions.yml", "exec"), {})
        assert (tmp_path / ".test-deps/frozen-minpy.py").read_bytes() == payload
    assert (tmp_path / "distributions.json").read_text() == manifest
    if fault in {"repository", "source", "commit", "sha256"}:
        assert calls == []


def _distribution_step(name):
    """Read the actual shell adapter without adding a test-time YAML dependency."""
    import textwrap

    text = (ROOT / ".github/workflows/min-distributions.yml").read_text()
    step = text.split("      - name: " + name + "\n", 1)[1].split("\n      - ", 1)[0]
    return step, textwrap.dedent(step.split("        run: |\n", 1)[1])


def test_distribution_parent_resolution_does_not_use_frozen_compiler(tmp_path, monkeypatch):
    """A conflict-free merge must still resolve live main, not tool.commit."""
    import json
    import os
    import subprocess
    import sys

    text = (ROOT / ".github/workflows/min-distributions.yml").read_text()
    # The checkout and provenance gate must consume the live resolver output.
    assert "ref: ${{ steps.resolved.outputs.parent_sha }}\n          path: .test-deps/distribution-tools" in text
    assert "PARENT_SHA: ${{ steps.resolved.outputs.parent_sha }}" in text
    name = next(line.removeprefix("      - name: ") for line in text.splitlines()
                if line.startswith("      - name: Resolve "))
    _, program = _distribution_step(name)
    live, frozen, queryu = "b" * 40, "a" * 40, "c" * 40
    monkeypatch.chdir(tmp_path)
    manifest = json.dumps({"tool": {"commit": frozen}})
    (tmp_path / "distributions.json").write_text(manifest)
    (tmp_path / "child-heads.json").write_text(json.dumps({"heads": {
        "myon-bioinformatics/QueRyu": {"sha": queryu}}}))
    tools = tmp_path / "bin"
    tools.mkdir()
    git = tools / "git"
    git.write_text("#!/bin/sh\n"
                   'test "$*" = "ls-remote https://github.com/myon-bioinformatics/myon-bioinformatics.git refs/heads/main" || exit 91\n'
                   'printf "%s\\n" "$*" >> "$GIT_CALLS"\n'
                   f"printf '{live}\\trefs/heads/main\\n'\n")
    git.chmod(0o755)
    # Mock only the repository-identity HTTP response; run the workflow's Python.
    python = tools / "python"
    python.write_text(f"#!{sys.executable}\n" + '''import io, json, sys, urllib.request

def response(request, timeout):
    assert request.full_url == "https://api.github.com/repos/myon-bioinformatics/myon-bioinformatics"
    return io.StringIO(json.dumps({"id": 638801160, "full_name": "myon-bioinformatics/myon-bioinformatics"}))

urllib.request.urlopen = response
assert sys.argv[1] == "-S"
if sys.argv[2] == "-":
    exec(compile(sys.stdin.read(), "workflow-identity", "exec"), {})
else:
    assert sys.argv[2] == "-c"
    exec(compile(sys.argv[3], "workflow-ref", "exec"), {})
''')
    python.chmod(0o755)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    for key, value in {"PARENT_REF": "", "QUERYU_REF": "", "GITHUB_TOKEN": "",
                       "PARENT_REPOSITORY_ID": "638801160", "GIT_CALLS": str(tmp_path / "git-calls"),
                       "GITHUB_OUTPUT": str(tmp_path / "output"),
                       "GITHUB_STEP_SUMMARY": str(tmp_path / "summary")}.items():
        monkeypatch.setenv(key, value)
    result = subprocess.run(["bash", "-c", program], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output").read_text().splitlines() == [
        "parent_sha=" + live, "queryu_sha=" + queryu]
    assert "refs/heads/main" in (tmp_path / "git-calls").read_text()
    summary = (tmp_path / "summary").read_text()
    assert live in summary and "repository_id 638801160" in summary
    assert frozen not in summary
    assert (tmp_path / "distributions.json").read_text() == manifest


@pytest.mark.parametrize("event", ["pull_request", "push", "schedule", "workflow_dispatch"])
@pytest.mark.parametrize("mismatch", [False, True])
def test_distribution_live_provenance_event_policy(tmp_path, monkeypatch, event, mismatch):
    """Frozen bytes cannot mask live drift; PR warns, all other events fail."""
    import hashlib
    import json
    import os
    import subprocess
    import sys

    _, program = _distribution_step("Compare resolved parent tool provenance")
    frozen = b"approved compiler\n"
    live = b"different live compiler\n" if mismatch else frozen
    live_sha, frozen_sha = "b" * 40, "a" * 40
    manifest = json.dumps({"tool": {"repository": PARENT, "source": "tools/minpy.py",
        "commit": frozen_sha, "sha256": hashlib.sha256(frozen).hexdigest()}})
    monkeypatch.chdir(tmp_path)
    (tmp_path / "distributions.json").write_text(manifest)
    checkout = tmp_path / ".test-deps/distribution-tools/tools"
    checkout.mkdir(parents=True)
    (checkout / "minpy.py").write_bytes(live)
    (tmp_path / ".test-deps/frozen-minpy.py").write_bytes(frozen)
    tools = tmp_path / "bin"
    tools.mkdir()
    git = tools / "git"
    git.write_text("#!/bin/sh\n"
                   'test "$*" = "-C .test-deps/distribution-tools rev-parse HEAD" || exit 91\n'
                   f"printf '{live_sha}\\n'\n")
    git.chmod(0o755)
    (tools / "python").symlink_to(sys.executable)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("PARENT_SHA", live_sha)
    monkeypatch.setenv("EVENT_NAME", event)
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "summary"))
    result = subprocess.run(["bash", "-c", program], capture_output=True, text=True, timeout=10)
    strict = event != "pull_request"
    assert result.returncode == (1 if mismatch and strict else 0), result.stderr
    summary = (tmp_path / "summary").read_text()
    assert f"- resolved_sha: `{live_sha}`" in summary
    assert f"- approved_commit: `{frozen_sha}`" in summary
    assert f"- checkout_sha256: `{hashlib.sha256(live).hexdigest()}`" in summary
    assert "- mode: " + ("strict" if strict else "report-only") in summary
    assert "- result: " + ("mismatch" if mismatch else "match") in summary
    if mismatch:
        assert ("::error::" if strict else "::warning::") in result.stderr
    else:
        assert not result.stderr
    assert (checkout / "minpy.py").read_bytes() == live
    assert (tmp_path / ".test-deps/frozen-minpy.py").read_bytes() == frozen
    assert (tmp_path / "distributions.json").read_text() == manifest
