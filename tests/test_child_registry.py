"""子リポジトリの登録（child-heads.json / vendor-consumers.json）と scripts/check_child_heads.py。

ネットワークは使わない。子はローカルの bare リポジトリ（file://）、親 myon-bioinformatics の
vendor_sync / vendor_consumers は tmp_path に置いた小さな偽物で代える。
"""
import copy
import json
import os
import re
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_child_heads.py"
sys.path.insert(0, str(ROOT / "scripts"))

import check_child_heads as cch  # noqa: E402

SHA = "a" * 40
NAME = "o/child"


def _load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


# --- このリポジトリの登録 -------------------------------------------------------------------

def test_child_heads_shape_and_prefixes_exist():
    heads = cch.validate_heads(_load("child-heads.json"))
    assert heads["ref"] == "main"
    for name, entry in heads["heads"].items():
        prefix = entry["optional"]["subtree_prefix"]
        assert (ROOT / prefix).is_dir(), (name, prefix)


def test_pythdragoras_registered_with_exact_ids_and_mirrors():
    entry = _load("child-heads.json")["heads"]["myon-bioinformatics/PythDRagoras"]
    assert entry["repository_id"] == 1423045231
    assert entry["optional"]["subtree_prefix"] == "pythdragoras"
    assert entry["optional"]["mirrored_from_parent"] == {"aoi_paths.py": "aoi_paths.py"}
    for path in entry["optional"]["not_in_parent"]:
        assert not (ROOT / "pythdragoras" / path.rstrip("/")).exists(), path


def test_queryu_registered_with_exact_ids():
    entry = _load("child-heads.json")["heads"]["myon-bioinformatics/QueRyu"]
    assert entry["repository_id"] == 1423051557
    assert entry["optional"]["subtree_prefix"] == "queryu"
    # queryu/aoi_paths.py は subtree add のあとにできる。それまでは mirrored_from_parent に書かない
    # （書くと copy_missing で失敗する）。blob の一致は tests/test_mirrored_root_files.py が確かめる
    assert "mirrored_from_parent" not in entry["optional"]


def test_registered_mirrors_are_blob_identical_to_aoi_originals():
    report = cch.check(ROOT, cch.validate_heads(_load("child-heads.json")), None, network=False, tools=None)
    for row in report["children"]:
        assert set(row["mirrors"].values()) <= {"identical"}, row
        assert row["excluded_in_parent"] == [], row


def test_offline_cli_passes():
    out = subprocess.run([sys.executable, "-S", str(SCRIPT), "--offline", "--fail-on-diff"],
                         capture_output=True, text=True, check=False)
    assert out.returncode == 0, out.stderr
    report = json.loads(out.stdout)
    assert report["schema"] == "aoi-child-heads-check/1"
    assert [c["repository"] for c in report["children"]] == ["myon-bioinformatics/PythDRagoras", "myon-bioinformatics/QueRyu"]


# --- ローカルの Git -------------------------------------------------------------------------

def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "init.defaultBranch=main",
                           "-c", "commit.gpgsign=false", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def _commit(repo: Path, files: dict) -> str:
    """files: path -> bytes | str | (bytes, 'x')。'x' は実行可能。"""
    if not (repo / ".git").exists():
        repo.mkdir(parents=True, exist_ok=True)
        _git(repo, "init", "-q")
    for path, value in files.items():
        mode = None
        if isinstance(value, tuple):
            value, mode = value
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value.encode() if isinstance(value, str) else value)
        _git(repo, "add", "--", path)
        if mode == "x":
            _git(repo, "update-index", "--chmod=+x", "--", path)
    _git(repo, "commit", "-q", "--allow-empty", "-m", "c")
    return _git(repo, "rev-parse", "HEAD")


def _child(tmp_path, files, name=NAME):
    work = tmp_path / "work" / name
    sha = _commit(work, files)
    bare = tmp_path / "remotes" / f"{name}.git"
    bare.parent.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "clone", "-q", "--bare", str(work), str(bare))
    return sha


def _url(tmp_path):
    return (tmp_path / "remotes").as_uri() + "/{repository}.git"


def _heads(sha, **optional):
    base = {"subtree_prefix": "sub"}
    base.update(optional)
    return {"schema": "child-heads/1", "ref": "main", "heads": {NAME: {"sha": sha, "repository_id": 7,
                                                                        "optional": base}}}


def _consumers(**consumer):
    base = {"repository": NAME, "state": "locked", "lock": "vendor.lock.json",
            "entries": [{"repository": "o/Aoi", "source": "s.py", "destination": "d.py"}]}
    base.update(consumer)
    return {"schema": "vendor-consumers/1", "consumers": [base]}


LOCK = {"schema": "vendor-lock/1", "files": [{"repository": "o/aoi", "source": "s.py", "destination": "D.py"}]}


def _parent(tmp_path, files):
    root = tmp_path / "parent"
    _commit(root, files)
    return root


def _run(tmp_path, root, heads, consumers=None, *, tools=None, network=True):
    return cch.check(root, cch.validate_heads(heads), consumers, network=network, tools=tools,
                     url_template=_url(tmp_path))


# --- 形 ----------------------------------------------------------------------------------

@pytest.mark.parametrize(("mutate", "message"), [
    (lambda d: [], 'expected child-heads/1'),
    (lambda d: d.update(schema="x"), 'expected child-heads/1'),
    (lambda d: d.update(extra=1), 'expected child-heads/1'),
    (lambda d: d.update(ref=""), 'child-heads ref must be a nonempty string'),
    (lambda d: d.update(ref=1), 'child-heads ref must be a nonempty string'),
    (lambda d: d.update(heads={}), 'child heads must be a nonempty object'),
    (lambda d: d.update(heads=[]), 'child heads must be a nonempty object'),
    (lambda d: d["heads"].update({"no-slash": d["heads"][NAME]}), 'expected owner/repository: no-slash'),
    (lambda d: d["heads"][NAME].update(sha="A" * 40), 'o/child: sha must be 40 hex'),
    (lambda d: d["heads"][NAME].update(sha=1), 'o/child: sha must be 40 hex'),
    (lambda d: d["heads"][NAME].pop("sha"), 'o/child: sha must be 40 hex'),
    (lambda d: d["heads"].update({NAME: "x"}), 'o/child: sha must be 40 hex'),
    (lambda d: d["heads"][NAME].update(repository_id=0), 'o/child: repository_id must be a positive int'),
    (lambda d: d["heads"][NAME].update(repository_id=True), 'o/child: repository_id must be a positive int'),
    (lambda d: d["heads"][NAME].update(repository_id="7"), 'o/child: repository_id must be a positive int'),
    (lambda d: d["heads"][NAME].pop("optional"), 'o/child: optional must be an object'),
    (lambda d: d["heads"][NAME].update(optional=[]), 'o/child: optional must be an object'),
    (lambda d: d["heads"][NAME]["optional"].pop("subtree_prefix"), 'o/child: optional.subtree_prefix is required'),
    (lambda d: d["heads"][NAME]["optional"].update(subtree_prefix=""), 'o/child: optional.subtree_prefix is required'),
    (lambda d: d["heads"][NAME]["optional"].update(subtree_prefix="/abs"), 'o/child: optional.subtree_prefix is required'),
    (lambda d: d["heads"][NAME]["optional"].update(subtree_prefix="a/../b"), 'o/child: optional.subtree_prefix is required'),
    (lambda d: d["heads"][NAME]["optional"].update(not_in_parent="x"), 'o/child: optional.not_in_parent must be a list of paths'),
    (lambda d: d["heads"][NAME]["optional"].update(not_in_parent=[""]), 'o/child: optional.not_in_parent must be a list of paths'),
    (lambda d: d["heads"][NAME]["optional"].update(not_in_parent=[1]), 'o/child: optional.not_in_parent must be a list of paths'),
    (lambda d: d["heads"][NAME]["optional"].update(child_preamble=[1]), 'o/child: optional.child_preamble must be a list of paths'),
    (lambda d: d["heads"][NAME]["optional"].update(not_in_parent=["docs/"], child_preamble=["docs/README.md"]), 'o/child: optional.child_preamble overlaps not_in_parent'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent=[]), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent={"a": ""}), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent={"": "a"}), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent={"a": 1}), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(not_in_parent=["a"], mirrored_from_parent={"a": "a"}), 'o/child: optional.mirrored_from_parent overlaps not_in_parent'),
])
def test_validate_heads_rejects(mutate, message):
    doc = _heads(SHA)
    out = mutate(doc)
    with pytest.raises(ValueError, match="^" + re.escape(message) + "$"):
        cch.validate_heads(out if isinstance(out, list) else doc)


def test_validate_heads_accepts_repository_id_one():
    doc = _heads(SHA)
    doc["heads"][NAME]["repository_id"] = 1
    assert cch.validate_heads(doc) is doc


def test_validate_heads_accepts_full_optional():
    doc = _heads(SHA, not_in_parent=["a/", "b"], child_preamble=["README.md"],
                 mirrored_from_parent={"p.py": "p.py"}, other="free")
    assert cch.validate_heads(doc) is doc


@pytest.mark.parametrize(("mutate", "message"), [
    (lambda d: [], 'expected vendor-consumers/1'),
    (lambda d: d.update(schema="x"), 'expected vendor-consumers/1'),
    (lambda d: d.update(extra=1), 'expected vendor-consumers/1'),
    (lambda d: d.update(consumers=[]), 'consumers must be a nonempty list'),
    (lambda d: d.update(consumers={}), 'consumers must be a nonempty list'),
    (lambda d: d.update(consumers=["x"]), 'consumer repository must be owner/repository'),
    (lambda d: d["consumers"][0].update(repository=1), 'consumer repository must be owner/repository'),
    (lambda d: d["consumers"][0].update(repository="noslash"), 'consumer repository must be owner/repository'),
    (lambda d: d["consumers"][0].update(state="other"), 'consumer state must be locked or legacy'),
    (lambda d: d["consumers"][0].update(lock=None), 'locked consumer requires lock path'),
    (lambda d: d["consumers"][0].update(lock=""), 'locked consumer requires lock path'),
    (lambda d: d["consumers"][0].update(entries=[]), 'consumer entries must be a nonempty list'),
    (lambda d: d["consumers"][0].update(entries={}), 'consumer entries must be a nonempty list'),
    (lambda d: d["consumers"][0].update(entries=["x"]), 'invalid consumer entry fields'),
    (lambda d: d["consumers"][0]["entries"][0].pop("source"), 'invalid consumer entry fields'),
    (lambda d: d["consumers"][0]["entries"][0].update(source=""), 'consumer entry fields must be nonempty strings'),
    (lambda d: d["consumers"][0]["entries"][0].update(destination=1), 'consumer entry fields must be nonempty strings'),
])
def test_validate_consumers_rejects(mutate, message):
    doc = _consumers()
    out = mutate(doc)
    with pytest.raises(ValueError, match="^" + re.escape(message) + "$"):
        cch.validate_consumers(out if isinstance(out, list) else doc)


def test_validate_consumers_accepts_locked_and_legacy_without_lock():
    doc = _consumers()
    doc["consumers"].append({"repository": "o/other", "state": "legacy", "lock": None,
                             "entries": [{"repository": "o/a", "source": "s", "destination": "d"}]})
    assert cch.validate_consumers(doc) is doc


@pytest.mark.parametrize(("path", "skip", "want"), [
    ("a", ["a"], True), ("a", ["a/"], True), ("a/b", ["a/"], True), ("a/b", ["a"], False),
    ("ab", ["a/"], False), ("b", ["a", "b/"], True), ("c", [], False), ("a_", ["a_"], True), ("aX", ["aX"], True),
])
def test_skipped(path, skip, want):
    assert cch._skipped(path, skip) is want


def test_tree_uses_nul_records_and_keeps_mode(tmp_path):
    repo = tmp_path / "r"
    _commit(repo, {"tab\tname": "t", "new\nline": "n", "run.sh": ("echo\n", "x"), "日本.txt": "j"})
    tree = cch._tree(repo, "HEAD")
    assert set(tree) == {"tab\tname", "new\nline", "run.sh", "日本.txt"}
    assert tree["run.sh"][0] == "100755" and tree["tab\tname"][0] == "100644"
    assert len(tree["run.sh"][1]) == 40


def test_tree_non_utf8_path_is_surrogate_escaped(tmp_path):
    repo = tmp_path / "r"
    _commit(repo, {"a": "a"})
    (repo / os.fsdecode(b"\xff.txt")).write_text("x", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c")
    assert "\udcff.txt" in cch._tree(repo, "HEAD")


def test_git_error_is_truncated_and_tolerates_bad_bytes(monkeypatch):
    monkeypatch.setattr(cch.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1, b"", b" " + b"\xff" * 500 + b" "))
    with pytest.raises(RuntimeError) as info:
        cch._git_bytes("a", "b", "c")
    assert str(info.value) == "git a b failed: " + "\ufffd" * 400


def test_git_error_message(tmp_path):
    with pytest.raises(RuntimeError, match="git rev-parse nope failed"):
        cch._git("rev-parse", "nope", cwd=tmp_path)


# --- mirrors（Aoi 内のコピーと原本）------------------------------------------------------------

def test_mirrors_states():
    whole = {"p.py": ("100644", "1"), "sub/p.py": ("100644", "1"), "sub/q.py": ("100644", "2"),
             "q.py": ("100644", "3"), "x.py": ("100755", "4"), "sub/x.py": ("100644", "4"), "m.py": ("100644", "5")}
    got = cch._mirrors(whole, "sub", {"p.py": "p.py", "q.py": "q.py", "x.py": "x.py", "m.py": "m.py",
                                      "n.py": "gone.py"})
    assert got == {"m.py": "copy_missing", "n.py": "original_missing", "p.py": "identical",
                   "q.py": "different", "x.py": "different"}


def test_mirror_drift_fails_offline_and_identical_passes(tmp_path):
    root = _parent(tmp_path, {"p.py": "one", "sub/p.py": "one"})
    heads = _heads(SHA, mirrored_from_parent={"p.py": "p.py"})
    report = _run(tmp_path, root, heads, network=False)
    assert report["children"][0]["mirrors"] == {"p.py": "identical"}
    assert not cch.failed(report, fail_on_drift=True, fail_on_diff=True)
    _commit(root, {"p.py": "two"})
    report = _run(tmp_path, root, heads, network=False)
    assert report["children"][0]["mirrors"] == {"p.py": "different"}
    assert cch.failed(report, fail_on_drift=False, fail_on_diff=False)


# --- drift / diff ------------------------------------------------------------------------

def test_identical_child_with_exclusions_preamble_and_mirror(tmp_path):
    sha = _child(tmp_path, {"a.py": "a", "README.md": "child only\n---\nbody\n", "p.py": "p",
                            "pyproject.toml": "c", ".github/x.yml": "w", "run.sh": ("x", "x")})
    root = _parent(tmp_path, {"p.py": "p", "sub/a.py": "a", "sub/README.md": "body\n", "sub/p.py": "p",
                              "sub/run.sh": ("x", "x")})
    heads = _heads(sha, not_in_parent=["pyproject.toml", ".github/"], child_preamble=["README.md"],
                   mirrored_from_parent={"p.py": "p.py"})
    row = _run(tmp_path, root, heads)["children"][0]
    assert row["live_sha"] == sha and row["drift"] is False and row["identical"] is True
    assert row["vendor"] is None and "error" not in row
    assert row["diff"] == {"only_in_parent": [], "only_in_child": [], "different": [], "excluded_in_parent": []}


def test_diff_categories_mode_preamble_and_excluded(tmp_path):
    sha = _child(tmp_path, {"same": "s", "blob": "child", "mode": ("m", "x"), "README.md": "pre\nwrong\n",
                            "child_only": "c", "uv.lock": "l"})
    _commit(tmp_path / "work" / NAME, {"later": "l"})
    _git(tmp_path / "work" / NAME, "push", "-q", str(tmp_path / "remotes" / f"{NAME}.git"), "HEAD:main")
    root = _parent(tmp_path, {"sub/same": "s", "sub/blob": "parent", "sub/mode": "m", "sub/README.md": "body\n",
                              "sub/parent_only": "p", "sub/uv.lock": "l"})
    heads = _heads(sha, not_in_parent=["uv.lock"], child_preamble=["README.md"])
    report = _run(tmp_path, root, heads)
    row = report["children"][0]
    assert row["drift"] is True and row["live_sha"] != sha
    assert row["diff"] == {"only_in_parent": ["parent_only"], "only_in_child": ["child_only"],
                           "different": ["README.md", "blob", "mode"], "excluded_in_parent": ["uv.lock"]}
    assert row["identical"] is False
    assert {k: row[k] for k in ("repository", "recorded_sha", "prefix")} == {"repository": NAME, "recorded_sha": sha,
                                                                            "prefix": "sub"}
    assert not cch.failed(report, fail_on_drift=False, fail_on_diff=False)
    assert cch.failed(report, fail_on_drift=True, fail_on_diff=False)
    assert cch.failed(report, fail_on_drift=False, fail_on_diff=True)


def test_suffix_match_only_for_preamble_files(tmp_path):
    sha = _child(tmp_path, {"README.md": "pre\nbody", "other.md": "pre\nbody"})
    root = _parent(tmp_path, {"sub/README.md": "body", "sub/other.md": "body"})
    row = _run(tmp_path, root, _heads(sha, child_preamble=["README.md"]))["children"][0]
    assert row["diff"]["different"] == ["other.md"]


def test_excluded_in_parent_alone_fails_on_diff(tmp_path):
    root = _parent(tmp_path, {"sub/a": "a", "sub/conftest.py": "x"})
    report = _run(tmp_path, root, _heads(SHA, not_in_parent=["conftest.py"]), network=False)
    assert report["children"][0]["excluded_in_parent"] == ["conftest.py"]
    assert "identical" not in report["children"][0]
    assert cch.failed(report, fail_on_drift=False, fail_on_diff=True)
    assert not cch.failed(report, fail_on_drift=True, fail_on_diff=False)


def test_missing_ref_is_drift_with_null_live_sha(tmp_path):
    sha = _child(tmp_path, {"a": "a"})
    root = _parent(tmp_path, {"sub/a": "a"})
    heads = _heads(sha)
    heads["ref"] = "gone"
    row = _run(tmp_path, root, heads)["children"][0]
    assert row["live_sha"] is None and row["drift"] is True and row["identical"] is True


def test_prefix_not_found_and_missing_repository_continue_per_child(tmp_path):
    sha = _child(tmp_path, {"a": "a"}, name="o/good")
    root = _parent(tmp_path, {"sub/a": "a", "other/a": "a"})
    heads = _heads(sha)
    heads["heads"]["o/good"] = heads["heads"].pop(NAME)
    heads["heads"]["o/missing"] = {"sha": SHA, "repository_id": 8, "optional": {"subtree_prefix": "other"}}
    heads["heads"]["o/noprefix"] = {"sha": SHA, "repository_id": 9, "optional": {"subtree_prefix": "nope"}}
    report = _run(tmp_path, root, heads)
    rows = {r["repository"]: r for r in report["children"]}
    assert list(rows) == ["o/good", "o/missing", "o/noprefix"]
    assert rows["o/good"]["identical"] is True and "error" not in rows["o/good"]
    assert rows["o/missing"]["error"].startswith("fetch_failed: git ls-remote")
    assert rows["o/noprefix"]["error"].startswith("fetch_failed")
    assert cch.failed(report, fail_on_drift=False, fail_on_diff=False)
    offline = _run(tmp_path, root, heads, network=False)
    assert {r["repository"]: r.get("error") for r in offline["children"]} == {
        "o/good": None, "o/missing": None, "o/noprefix": "prefix_not_found"}


def test_timeout_is_per_child_error(tmp_path, monkeypatch):
    root = _parent(tmp_path, {"sub/a": "a"})
    real = cch._git_bytes

    def fake(*args, **kwargs):
        if args[0] == "ls-remote":
            raise subprocess.TimeoutExpired(["git"], kwargs["timeout"])
        return real(*args, **kwargs)

    monkeypatch.setattr(cch, "_git_bytes", fake)
    row = _run(tmp_path, root, _heads(SHA))["children"][0]
    assert row["error"].startswith("fetch_failed: Command '['git']' timed out after 120")


def test_fetch_timeout_value_is_passed(monkeypatch):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen.update(kwargs)
        return subprocess.CompletedProcess(cmd, 0, b"ok", b"")

    monkeypatch.setattr(cch.subprocess, "run", fake_run)
    assert cch._git("status") == "ok"
    assert seen["timeout"] == 300 and seen["capture_output"] is True and seen["cwd"] is None
    seen.clear()
    assert cch._git_bytes("status") == b"ok"
    assert seen["timeout"] == 300


def test_default_url_is_github():
    assert cch.URL_TEMPLATE.format(repository="o/c") == "https://github.com/o/c.git"
    assert set(cch.VENDOR_FAILURES) == {"topology_mismatch", "lock_missing_at_recorded_sha", "lock_invalid"}


# --- vendor ------------------------------------------------------------------------------

def _fake_tools(tmp_path, *, matches=True, compare_raises=False):
    tools = tmp_path / "tools"
    tools.mkdir(exist_ok=True)
    (tools / "vendor_sync.py").write_text(
        "CALLS = []\ndef validate_child_heads(doc):\n    CALLS.append('heads')\n    return doc\n", encoding="utf-8")
    body = "    raise ValueError('bad lock')\n" if compare_raises else f"    return {{'matches': {matches}}}\n"
    (tools / "vendor_consumers.py").write_text(
        "import vendor_sync\nCALLS = vendor_sync.CALLS\n"
        "def validate(reg):\n    CALLS.append('consumers')\n    return reg\n"
        "def compare(reg, lock, name):\n    CALLS.append(('compare', lock['schema'], name))\n" + body,
        encoding="utf-8")
    return tools


def _vendor_case(tmp_path, lock, consumers, tools=None):
    files = {"a": "a"}
    if lock is not None:
        files["vendor.lock.json"] = lock if isinstance(lock, str) else json.dumps(lock)
    sha = _child(tmp_path, files)
    root = _parent(tmp_path, {"sub/a": "a"})
    report = _run(tmp_path, root, _heads(sha, not_in_parent=["vendor.lock.json"]), consumers, tools=tools)
    return report


@pytest.mark.parametrize(("lock", "consumers", "want"), [
    (LOCK, _consumers(), "topology_match"),
    ({"schema": "vendor-lock/1", "files": [{"repository": "o/aoi", "source": "s.py", "destination": "e.py"}]},
     _consumers(), "topology_mismatch"),
    (None, _consumers(), "lock_missing_at_recorded_sha"),
    ("{not json", _consumers(), "lock_invalid"),
    ({"schema": "vendor-lock/1"}, _consumers(), "lock_invalid"),
    ({"schema": "vendor-lock/1", "files": [1]}, _consumers(), "lock_invalid"),
    (b"\xff\xfe".decode("latin-1"), _consumers(), "lock_invalid"),
    (LOCK, _consumers(lock="other.json"), "lock_missing_at_recorded_sha"),
    (None, _consumers(state="legacy", lock=None), "legacy"),
    (LOCK, _consumers(repository="o/someone"), None),
    (LOCK, None, None),
])
def test_vendor_without_tools(tmp_path, lock, consumers, want):
    report = _vendor_case(tmp_path, lock, consumers)
    assert report["children"][0]["vendor"] == want
    failing = {"topology_mismatch", "lock_missing_at_recorded_sha", "lock_invalid"}
    assert cch.failed(report, fail_on_drift=False, fail_on_diff=False) is (want in failing)


def test_vendor_lock_not_utf8_is_invalid(tmp_path):
    sha = _child(tmp_path, {"a": "a", "vendor.lock.json": b"\xff\xfe\x00"})
    root = _parent(tmp_path, {"sub/a": "a"})
    report = _run(tmp_path, root, _heads(sha, not_in_parent=["vendor.lock.json"]), _consumers())
    assert report["children"][0]["vendor"] == "lock_invalid"


def test_vendor_casefold_repository_match(tmp_path):
    report = _vendor_case(tmp_path, LOCK, _consumers(repository="O/CHILD"))
    assert report["children"][0]["vendor"] == "topology_match"


@pytest.mark.parametrize(("matches", "raises", "want"), [
    (True, False, "topology_match"), (False, False, "topology_mismatch"), (True, True, "lock_invalid")])
def test_vendor_with_tools(tmp_path, matches, raises, want):
    tools = _fake_tools(tmp_path, matches=matches, compare_raises=raises)
    report = _vendor_case(tmp_path, LOCK, _consumers(), tools=tools)
    assert report["children"][0]["vendor"] == want
    calls = sys.modules["vendor_sync"].CALLS
    assert calls == ["heads", "consumers", ("compare", "vendor-lock/1", NAME)]
    assert str(tools) not in sys.path


def test_tools_take_precedence_over_sys_path(tmp_path, monkeypatch):
    decoy = tmp_path / "decoy"
    decoy.mkdir()
    (decoy / "vendor_sync.py").write_text("raise ImportError('decoy')\n", encoding="utf-8")
    (decoy / "vendor_consumers.py").write_text("raise ImportError('decoy')\n", encoding="utf-8")
    monkeypatch.setattr(sys, "path", [str(decoy), *sys.path])
    tools = _fake_tools(tmp_path)
    root = _parent(tmp_path, {"sub/a": "a"})
    _run(tmp_path, root, _heads(SHA), None, tools=tools, network=False)
    assert sys.modules["vendor_sync"].CALLS == ["heads"]


def test_tools_reloaded_each_run_and_consumers_optional(tmp_path):
    tools = _fake_tools(tmp_path)
    root = _parent(tmp_path, {"sub/a": "a"})
    _run(tmp_path, root, _heads(SHA), None, tools=tools, network=False)
    first = sys.modules["vendor_sync"]
    assert first.CALLS == ["heads"]
    _run(tmp_path, root, _heads(SHA), None, tools=tools, network=False)
    assert sys.modules["vendor_sync"] is not first and sys.modules["vendor_sync"].CALLS == ["heads"]


# --- CLI ---------------------------------------------------------------------------------

def _write_root(tmp_path, heads, consumers=None, files=None):
    root = tmp_path / "cli"
    payload = {"child-heads.json": json.dumps(heads)}
    if consumers is not None:
        payload["vendor-consumers.json"] = json.dumps(consumers)
    payload.update(files or {"sub/a": "a"})
    _commit(root, payload)
    return root


def _main(capsys, *argv):
    rc = cch.main([str(a) for a in argv])
    out = capsys.readouterr()
    return rc, out.out, out.err


def test_main_ok_and_flags(tmp_path, capsys):
    sha = _child(tmp_path, {"a": "a"})
    root = _write_root(tmp_path, _heads(sha))
    rc, out, err = _main(capsys, "--root", root, "--url-template", _url(tmp_path), "--fail-on-drift", "--fail-on-diff")
    assert rc == 0 and err == ""
    report = json.loads(out)
    assert report["parent"] == _git(root, "rev-parse", "HEAD")
    assert report["children"][0]["identical"] is True


def test_main_output_is_indented_utf8(tmp_path, capsys):
    sha = _child(tmp_path, {"a": "a", "日本.md": "x"})
    root = _write_root(tmp_path, _heads(sha))
    rc, out, _ = _main(capsys, "--root", root, "--url-template", _url(tmp_path))
    assert rc == 0 and out.startswith('{\n  "schema": ') and '"日本.md"' in out


def test_main_returns_1_on_diff_only_with_flag(tmp_path, capsys):
    sha = _child(tmp_path, {"a": "b"})
    root = _write_root(tmp_path, _heads(sha))
    assert _main(capsys, "--root", root, "--url-template", _url(tmp_path))[0] == 0
    assert _main(capsys, "--root", root, "--url-template", _url(tmp_path), "--fail-on-diff")[0] == 1
    assert _main(capsys, "--root", root, "--url-template", _url(tmp_path), "--fail-on-drift")[0] == 0


def test_main_registry_used_when_present(tmp_path, capsys):
    sha = _child(tmp_path, {"a": "a"})
    root = _write_root(tmp_path, _heads(sha), _consumers())
    rc, out, _ = _main(capsys, "--root", root, "--url-template", _url(tmp_path))
    assert rc == 1 and json.loads(out)["children"][0]["vendor"] == "lock_missing_at_recorded_sha"


def test_main_custom_file_names(tmp_path, capsys):
    root = tmp_path / "cli"
    _commit(root, {"h.json": json.dumps(_heads(SHA)), "r.json": "{}", "sub/a": "a"})
    rc, _, err = _main(capsys, "--root", root, "--heads", "h.json", "--registry", "r.json", "--offline")
    assert rc == 2 and "vendor-consumers/1" in err
    rc, out, _ = _main(capsys, "--root", root, "--heads", "h.json", "--offline")
    assert rc == 0 and json.loads(out)["children"][0]["mirrors"] == {}


@pytest.mark.parametrize("case", ["missing", "badjson", "shape", "tools", "norepo"])
def test_main_errors_return_2(tmp_path, capsys, case):
    if case == "norepo":
        root = tmp_path / "plain"
        root.mkdir()
        (root / "child-heads.json").write_text(json.dumps(_heads(SHA)), encoding="utf-8")
    else:
        root = _write_root(tmp_path, _heads(SHA))
    if case == "missing":
        (root / "child-heads.json").unlink()
    if case == "badjson":
        (root / "child-heads.json").write_text("{", encoding="utf-8")
    if case == "shape":
        (root / "child-heads.json").write_text("{}", encoding="utf-8")
    extra = ["--vendor-tools", tmp_path / "no-tools"] if case == "tools" else []
    rc, out, err = _main(capsys, "--root", root, "--offline", *extra)
    assert rc == 2 and out == "" and re.fullmatch(r"check-child-heads: [^_].*\n", err, re.S)


def test_script_entry_point(tmp_path, monkeypatch, capsys):
    root = _write_root(tmp_path, _heads(SHA))
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--root", str(root), "--offline"])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    assert exit_info.value.code == 0
    assert json.loads(capsys.readouterr().out)["schema"] == "aoi-child-heads-check/1"


def test_default_root_is_repository():
    out = subprocess.run([sys.executable, "-S", str(SCRIPT), "--help"], capture_output=True, text=True, check=True)
    assert out.stdout.startswith("usage:") and cch.__doc__.splitlines()[0] in out.stdout


def test_check_does_not_mutate_inputs(tmp_path):
    root = _parent(tmp_path, {"sub/a": "a"})
    heads, consumers = _heads(SHA), _consumers()
    before = copy.deepcopy((heads, consumers))
    _run(tmp_path, root, heads, consumers, network=False)
    assert (heads, consumers) == before
