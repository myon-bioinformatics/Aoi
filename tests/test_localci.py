"""SHA 解決、uses: のピン、シャード、seed 付き入力の差し替え。ネットワークはモックする。"""

import hashlib
import io
import json
import os
import tarfile
import urllib.error
from pathlib import Path

import pytest

import localci


ROOT = Path(__file__).resolve().parents[1]
SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


@pytest.fixture(autouse=True)
def _reset_localci_rng():
    # localci 自身が pytest を子プロセスで走らせるときは、プラグインの seed を消さない。
    if os.environ.get("LOCALCI_INPUT_LOG"):
        yield
        return
    localci._active_rng = None
    localci._substitutions.clear()
    yield
    localci._active_rng = None
    localci._substitutions.clear()


class Proc:
    def __init__(self, rc=0, stdout="", stderr=""):
        self.returncode = rc
        self.stdout = stdout
        self.stderr = stderr


class Body:
    def __init__(self, payload):
        self.data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Opener:
    def __init__(self, routes):
        self.routes = routes
        self.urls = []

    def __call__(self, req, timeout=60):
        self.urls.append(req.full_url)
        if req.full_url not in self.routes:
            raise AssertionError(req.full_url)
        item = self.routes[req.full_url]
        if isinstance(item, Exception):
            raise item
        return Body(item)


def http_error(url, code):
    return urllib.error.HTTPError(url, code, "missing", hdrs=None, fp=io.BytesIO(b""))


def listing(ref, sha):
    return f"{sha}\t{ref}\n"


def test_shards_cover_each_check_once_and_stay_balanced():
    items = [f"c{i}" for i in range(10)]
    shards = localci.split_shards(items, 3, seed=11)
    assert [len(s) for s in shards] == [4, 3, 3]
    flat = [item for shard in shards for item in shard]
    assert sorted(flat) == items
    assert len(flat) == len(set(flat))
    again = localci.split_shards(items, 3, seed=11)
    assert shards == again
    assert localci.split_shards(items, 3, seed=12) != shards


def test_empty_shards_when_repeat_exceeds_checks():
    shards = localci.split_shards(["only"], 3, seed=1)
    assert sum(len(s) for s in shards) == 1
    assert len(shards) == 3
    assert localci.shard_for_round(["only"], 3, 1, 1) == shards[0]


def test_round_seed_is_stable_and_distinct():
    assert localci.mix_seed(7, "round", 1) == localci.mix_seed(7, "round", 1)
    assert localci.mix_seed(7, "round", 1) != localci.mix_seed(7, "round", 2)
    assert localci.mix_seed(7, "round", 1) != localci.mix_seed(8, "round", 1)


def test_substitute_keeps_the_fixed_value_until_a_round_seed_is_active():
    def draw(rng):
        return rng.randrange(10**9)

    # プラグインがセッションの seed を入れていても、明示的に外した状態を検査する。
    previous = localci._active_rng
    localci._active_rng = None
    try:
        assert localci.substitute("n", 1, draw) == 1
        with localci.use_seed(5):
            first = localci.substitute("n", 1, draw)
        with localci.use_seed(5):
            second = localci.substitute("n", 1, draw)
        with localci.use_seed(6):
            third = localci.substitute("n", 1, draw)
        assert first == second and first != 1 and first != third
        assert localci.substitute("n", 1, draw) == 1
    finally:
        localci._active_rng = previous


def test_sha_shape_survives_substitution():
    value = localci.substitute("sha", "ab" * 20, lambda rng: f"{rng.getrandbits(160):040x}")
    assert localci.SHA_RE.fullmatch(str(value))


def test_fail_fast_reports_round_shard_and_seed():
    checks = [localci.Check(name, "resolve", name) for name in ("a", "b", "c")]
    shards = [[checks[0]], [checks[1]], [checks[2]]]
    lines = []

    def execute(check, seed):
        del seed
        if check.id == "b":
            return localci.Outcome("fail", "boom", [])
        return localci.Outcome("pass", "ok", [])

    report = localci.run_plan(shards=shards, master_seed=5, execute=execute, keep_going=False, emit=lines.append)
    text = "\n".join(lines)
    assert report.stopped and report.passed_rounds == 1
    assert [r.number for r in report.rounds] == [1, 2]
    assert report.rounds[1].failed_check == "b"
    assert report.rounds[1].shard == ["b"]
    assert f"seed={report.rounds[1].seed}" in text
    assert "master=5" in text
    assert "confidence: 1/3 rounds passed, 2/3 completed; stopped" in text


def test_keep_going_finishes_every_round():
    checks = [localci.Check(name, "resolve", name) for name in ("a", "b")]
    shards = [[checks[0]], [checks[1]]]

    def execute(check, seed):
        del seed
        return localci.Outcome("fail" if check.id == "a" else "pass", check.id, [])

    report = localci.run_plan(shards=shards, master_seed=1, execute=execute, keep_going=True, emit=lambda _line: None)
    assert not report.stopped
    assert [r.passed for r in report.rounds] == [False, True]
    assert report.passed_rounds == 1


def test_parse_uses_skips_local_docker_and_comments():
    text = """
jobs:
  a:
    uses: myon-bioinformatics/myon-bioinformatics/.github/workflows/reusable-actionlint.yml@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    steps:
      - uses: actions/checkout@v7
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: ./local
      - uses: docker://alpine:3
      # uses: actions/not-really@v1
      - uses: "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97"
"""
    found = localci.parse_uses(text)
    assert [item["raw"] for item in found] == [
        "myon-bioinformatics/myon-bioinformatics/.github/workflows/reusable-actionlint.yml@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "actions/checkout@v7",
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
    ]
    assert found[2]["repo"] == "actions/checkout"
    assert found[2]["ref"] == "3d3c42e5aac5ba805825da76410c181273ba90b1"
    assert found[0]["repo"] == "myon-bioinformatics/myon-bioinformatics"


def test_classify_pin():
    latest = ("v1.2.3", SHA_B)
    assert localci.classify_pin(SHA_B, latest) == "match"
    assert localci.classify_pin(SHA_A, latest) == "outdated"
    assert localci.classify_pin("v1", latest) == "unpinned"
    assert localci.classify_pin(SHA_A, None) == "no-release"
    assert localci.classify_pin("v1", None) == "unpinned"
    assert localci.pin_fails("outdated", strict=False) is False
    assert localci.pin_fails("outdated", strict=True) is True
    assert localci.pin_fails("no-release", strict=True) is False


def test_pin_check_reports_outdated_unless_strict_and_rejects_a_random_probe():
    url = "https://api.github.com/repos/actions/checkout/releases/latest"
    opener = Opener({url: {"tag_name": "v7.0.1"}})

    def runner(argv, **kwargs):
        assert argv[:2] == ["git", "ls-remote"]
        assert kwargs["env"]["GIT_TERMINAL_PROMPT"] == "0"
        return Proc(stdout=listing("refs/tags/v7.0.1", SHA_B))

    session = localci.Session(ROOT, opener=opener, runner=runner, actionlint=None)
    old = localci.Check("pin:old", "pin", "actions/checkout@" + SHA_A, ref=SHA_A, repo="actions/checkout")
    with localci.use_seed(9):
        outcome = session._pin(old)
        inputs = localci.take_substitutions()
    assert outcome.ok and "outdated" in outcome.detail
    assert inputs[0]["name"] == "sha_probe" and inputs[0]["value"] != "0" * 40
    session.strict = True
    assert session._pin(old).status == "fail"
    current = localci.Check("pin:new", "pin", "actions/checkout@" + SHA_B, ref=SHA_B, repo="actions/checkout")
    assert session._pin(current).status == "pass"
    assert "matches v7.0.1" in session._pin(current).detail


def test_pin_without_a_release_is_not_a_strict_failure():
    url = "https://api.github.com/repos/myon-bioinformatics/myon-bioinformatics/releases/latest"
    opener = Opener({url: http_error(url, 404)})
    session = localci.Session(ROOT, opener=opener, runner=lambda *a, **k: (_ for _ in ()).throw(AssertionError("git")), strict=True)
    check = localci.Check("pin:re", "pin", "org/repo@" + SHA_A, ref=SHA_A, repo="myon-bioinformatics/myon-bioinformatics")
    outcome = session._pin(check)
    assert outcome.ok and "no release" in outcome.detail


def test_known_sources_and_vendor_lock(tmp_path):
    ids = {s.repo: s.repository_id for s in localci.SOURCES}
    assert ids == {
        "myon-bioinformatics/Aoi": 1402862784,
        "myon-bioinformatics/myon-bioinformatics": 638801160,
        "myon-bioinformatics/markdown": 1374546518,
        "myon-bioinformatics/web-ui": 1382466695,
    }
    (tmp_path / "vendor.lock.json").write_text(json.dumps({"files": [
        {"repository": "myon-bioinformatics/markdown"},
        {"repository": "example/new-vendor"},
    ]}), encoding="utf-8")
    repos = [s.repo for s in localci.sources_for(tmp_path)]
    assert repos.count("myon-bioinformatics/markdown") == 1
    extra = next(s for s in localci.sources_for(tmp_path) if s.repo == "example/new-vendor")
    assert extra.repository_id is None


def test_resolve_checks_repository_id_and_ref_forms():
    repo = "myon-bioinformatics/Aoi"
    api = f"https://api.github.com/repos/{repo}"
    opener = Opener({api: {"id": 1402862784, "full_name": "Myon-Bioinformatics/Aoi", "visibility": "public", "private": False}})
    calls = []

    def runner(argv, **kwargs):
        calls.append(argv)
        assert kwargs["env"]["GIT_SSH_COMMAND"].startswith("ssh ")
        return Proc(stdout=listing(argv[-1], SHA_C))

    source = localci.SOURCES[0]
    direct = localci.resolve_source(source, SHA_A.upper(), opener=opener, runner=runner)
    assert direct.sha == SHA_A and direct.how == "workflow_dispatch input" and calls == []
    branched = localci.resolve_source(source, "topic", opener=opener, runner=runner)
    assert branched.sha == SHA_C and branched.how == "refs/heads/topic"
    explicit = localci.resolve_source(source, "refs/heads/feature", opener=opener, runner=runner)
    assert explicit.how == "refs/heads/feature"
    with pytest.raises(localci.LocalCIError, match="invalid aoi_ref"):
        localci.resolve_ref(repo, "bad ref", runner=runner)


def test_ls_remote_prefers_peeled_tag_and_rejects_a_mismatch():
    def runner(argv, **kwargs):
        del kwargs
        ref = argv[-1]
        return Proc(stdout=f"{SHA_A}\t{ref}\n{SHA_B}\t{ref}^{{}}\n")

    assert localci.ls_remote("actions/checkout", "refs/tags/v1", runner=runner) == SHA_B
    bad = Opener({"https://api.github.com/repos/myon-bioinformatics/Aoi": {
        "id": 1, "full_name": "myon-bioinformatics/Aoi", "visibility": "public", "private": False,
    }})
    with pytest.raises(localci.LocalCIError, match="repository id mismatch"):
        localci.resolve_source(localci.SOURCES[0], "", opener=bad, runner=lambda *a, **k: Proc())
    private = Opener({"https://api.github.com/repos/myon-bioinformatics/Aoi": {
        "id": 1402862784, "full_name": "myon-bioinformatics/Aoi", "visibility": "private", "private": True,
    }})
    with pytest.raises(localci.LocalCIError, match="not public"):
        localci.resolve_source(localci.SOURCES[0], SHA_A, opener=private, runner=lambda *a, **k: Proc())


def test_env_file_github_output_and_provenance(tmp_path, monkeypatch):
    resolved = [localci.Resolved(localci.SOURCES[0], SHA_A, "refs/heads/main", 1402862784)]
    text = localci.format_env(resolved)
    assert f"AOI_SHA={SHA_A}" in text
    assert "AOI_REPOSITORY_ID=1402862784" in text
    output = localci.format_github_output(resolved)
    assert f"sha={SHA_A}" in output and f"aoi_sha={SHA_A}" in output
    assert localci.provenance_mode("schedule", "refs/heads/main") == "strict"
    assert localci.provenance_mode("push", "refs/heads/main") == "strict"
    assert localci.provenance_mode("push", "refs/heads/other") == "report-only"
    assert localci.provenance_mode("pull_request", "refs/pull/1/merge") == "report-only"
    summary = localci.format_step_summary(resolved, "report-only")
    assert f"Resolved `{SHA_A}` from `refs/heads/main`." in summary
    assert "Source-hash provenance: report-only." in summary

    monkeypatch.setattr(localci, "resolve_sources", lambda *a, **k: resolved)
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "gh.out"))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "sum.md"))
    monkeypatch.setenv("EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    assert localci.main(["resolve", "--root", str(tmp_path), "--github-output", "--env-file", str(tmp_path / "refs.env")]) == 0
    assert "strict" in (tmp_path / "sum.md").read_text(encoding="utf-8")
    assert f"AOI_SHA={SHA_A}" in (tmp_path / "refs.env").read_text(encoding="utf-8")


def test_checksum_and_actionlint_cache(tmp_path):
    payload = b"#!/bin/sh\necho actionlint\n"
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as tar:
        info = tarfile.TarInfo("actionlint")
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(payload))
    blob = archive.getvalue()
    digest = hashlib.sha256(blob).hexdigest()
    checksums = f"{digest}  actionlint_9.9.9_linux_amd64.tar.gz\n".encode()
    checksum_digest = hashlib.sha256(checksums).hexdigest()
    release = {"tag_name": "v9.9.9", "assets": [
        {"name": "actionlint_9.9.9_linux_amd64.tar.gz", "browser_download_url": "https://example.test/a.tar.gz", "digest": "sha256:" + digest},
        {"name": "actionlint_9.9.9_checksums.txt", "browser_download_url": "https://example.test/checksums.txt", "digest": "sha256:" + checksum_digest},
    ]}
    routes = {
        "https://api.github.com/repos/rhysd/actionlint/releases/latest": release,
        "https://example.test/a.tar.gz": blob,
        "https://example.test/checksums.txt": checksums,
    }
    opener = Opener(routes)
    path = localci.ensure_actionlint(tmp_path, opener=opener, system="Linux", machine="x86_64")
    assert path.read_bytes() == payload
    before = len(opener.urls)
    assert localci.ensure_actionlint(tmp_path, opener=opener, system="Linux", machine="x86_64") == path
    assert opener.urls[before:] == ["https://api.github.com/repos/rhysd/actionlint/releases/latest"]
    routes["https://example.test/a.tar.gz"] = b"tampered"
    with pytest.raises(localci.LocalCIError, match="checksum mismatch"):
        localci.ensure_actionlint(tmp_path / "other", opener=Opener(routes), system="Linux", machine="x86_64")
    assert localci.checksum_for(digest + " *actionlint_9.9.9_linux_amd64.tar.gz\n", "actionlint_9.9.9_linux_amd64.tar.gz") == digest
    argv = localci.actionlint_argv(None, ["ci.yml"], None)
    assert argv[:3] == ["go", "run", "github.com/rhysd/actionlint/cmd/actionlint@latest"]
    assert "-shellcheck=" in argv
    assert localci.actionlint_argv(path, ["ci.yml"], "/usr/bin/shellcheck")[-3:] == ["-shellcheck", "/usr/bin/shellcheck", "ci.yml"]


def test_parse_collect_only_and_collection(tmp_path):
    stdout = "tests/test_a.py::test_one\n\nERROR tests/test_b.py\n2 tests collected\n"
    assert localci.parse_collect_only(stdout) == ["tests/test_a.py::test_one"]
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (tmp_path / "test_bad.py").write_text("import does_not_exist_localci\n", encoding="utf-8")
    nodeids, limits = localci.collect_pytest(["test_ok.py", "test_bad.py"], tmp_path)
    assert nodeids == ["test_ok.py::test_ok"]
    assert limits


def test_workflow_delegates_resolution_and_pins_actions_by_sha():
    text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "python localci.py resolve --github-output" in text
    assert "AOI_REPOSITORY_ID" not in text
    uses = localci.parse_uses(text)
    checkout = [item["ref"] for item in uses if item["repo"] == "actions/checkout"]
    assert checkout and set(checkout) == {"3d3c42e5aac5ba805825da76410c181273ba90b1"}
    setup = [item["ref"] for item in uses if item["repo"] == "actions/setup-python"]
    assert set(setup) == {"5fda3b95a4ea91299a34e894583c3862153e4b97"}
    uv = [item["ref"] for item in uses if item["repo"] == "astral-sh/setup-uv"]
    assert set(uv) == {"1c37ad07a6a961277cf70c0d37d6f313000f5884"}
    upload = [item["ref"] for item in uses if item["repo"] == "actions/upload-artifact"]
    assert upload == ["cf430e030ddbb5b0abf93d22962f4752f3646cd9"]


def test_pytest_plugin_shards_are_disjoint_and_cover_every_test(tmp_path):
    (tmp_path / "test_nums.py").write_text(
        "def test_a():\n    open('seen', 'a', encoding='utf-8').write('a\\n')\n"
        "def test_b():\n    open('seen', 'a', encoding='utf-8').write('b\\n')\n"
        "def test_c():\n    open('seen', 'a', encoding='utf-8').write('c\\n')\n"
        "def test_d():\n    open('seen', 'a', encoding='utf-8').write('d\\n')\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("LOCALCI_INPUT_LOG", None)
    seen = []
    for round_no in (1, 2):
        marker = tmp_path / "seen"
        marker.unlink(missing_ok=True)
        proc = __import__("subprocess").run(
            [__import__("sys").executable, "-m", "pytest", "-p", "localci_pytest", "-q",
             "--localci-repeat", "2", "--localci-round", str(round_no), "--localci-seed", "11"],
            cwd=tmp_path, env=env, capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        seen.append(marker.read_text(encoding="utf-8").split())
    assert sorted(seen[0] + seen[1]) == ["a", "b", "c", "d"]
    assert set(seen[0]).isdisjoint(seen[1])
    assert all(len(part) == 2 for part in seen)


def test_pytest_plugin_monkeypatches_substitute(tmp_path):
    (tmp_path / "test_sub.py").write_text(
        "import localci\n"
        "def test_sub():\n"
        "    values = [localci.substitute('n', 1, lambda rng: rng.randrange(10**9)) for _ in range(4)]\n"
        "    open('value.txt', 'w', encoding='utf-8').write(','.join(map(str, values)))\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env.pop("LOCALCI_INPUT_LOG", None)

    def once(seed):
        proc = __import__("subprocess").run(
            [__import__("sys").executable, "-m", "pytest", "-p", "localci_pytest", "-q",
             "--localci-seed", str(seed), "--localci-activate"],
            cwd=tmp_path, env=env, capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        return (tmp_path / "value.txt").read_text(encoding="utf-8")

    first = once(4)
    assert once(4) == first
    assert first != "1,1,1,1"
    assert once(5) != first


def test_run_local_is_fail_fast_and_prints_the_master_seed(tmp_path, monkeypatch):
    checks = [localci.Check(name, "resolve", name, repo=name) for name in ("a", "b")]
    monkeypatch.setattr(localci, "build_checks", lambda *a, **k: (checks, ["pytest が見つからない"]))

    class FakeSession:
        def __init__(self, *args, **kwargs):
            self.resolved = {}

        def execute(self, check):
            if check.id == "b":
                return localci.Outcome("fail", "boom", [])
            return localci.Outcome("pass", "ok", [])

    monkeypatch.setattr(localci, "Session", FakeSession)
    lines = []
    rc = localci.run_local(
        tmp_path, repeat=2, seed=3, keep_going=False, strict=False,
        pytest_paths=None, skip_pytest=True, env_file=None, emit=lines.append,
    )
    text = "\n".join(lines)
    assert rc == 1
    assert "localci seed=3" in text
    assert "pytest が見つからない" in text
    assert "; stopped" in text
    assert "b" in text
