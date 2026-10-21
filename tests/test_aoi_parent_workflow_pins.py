"""Local rollout contract; adopted vendor locks are deliberately independent."""
import re
from pathlib import Path

import pytest

PARENT = "myon-bioinformatics/myon-bioinformatics"
ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".github/workflows").is_dir())
SHA40 = re.compile(r"[0-9a-f]{40}")


def test_parent_reusable_workflow_uses_are_one_full_sha():
    """uses: refs to parent reusable workflows are one 40-character SHA.

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
    assert len(set(pins)) == 1, pins
    assert SHA40.fullmatch(pins[0]), pins


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
