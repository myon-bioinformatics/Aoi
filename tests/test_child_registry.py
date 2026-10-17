"""子リポジトリの登録（child-heads.json）と scripts/check_child_heads.py。

ネットワークは使わない。子はローカルの bare リポジトリ（file://）。
"""
import ast
import copy
import json
import os
import re
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_child_heads.py"
sys.path.insert(0, str(ROOT / "scripts"))


def _import_check_child_heads(path: Path | None = None):
    import importlib.util

    if path is None:
        import check_child_heads as mod

        return mod
    spec = importlib.util.spec_from_file_location("check_child_heads", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_mutated = os.environ.get("CHECK_CHILD_HEADS_MUTATED")
cch = _import_check_child_heads(Path(_mutated) if _mutated else None)

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
    assert not set(cch.UNSUPPORTED) & entry["optional"].keys()
    for path in (".github/workflows/ci.yml", "pyproject.toml", "uv.lock", "conftest.py", ".gitignore"):
        assert (ROOT / "pythdragoras" / path).is_file(), path  # 純粋な subtree：子のルートのファイルも Aoi に置く


def test_queryu_registered_with_exact_ids():
    entry = _load("child-heads.json")["heads"]["myon-bioinformatics/QueRyu"]
    assert entry["repository_id"] == 1423051557
    assert entry["optional"]["subtree_prefix"] == "queryu"
    # queryu/aoi_paths.py は subtree add のあとにできる。それまでは mirrored_from_parent に書かない
    # （書くと copy_missing で失敗する）。subtree add の直後に {"aoi_paths.py": "aoi_paths.py"} を書く
    assert "mirrored_from_parent" not in entry["optional"]


def test_registered_mirrors_are_blob_identical_to_aoi_originals():
    report = cch.check(ROOT, cch.validate_heads(_load("child-heads.json")), network=False)
    for row in report["children"]:
        assert set(row["mirrors"].values()) <= {"identical"}, row


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


def _parent(tmp_path, files):
    root = tmp_path / "parent"
    _commit(root, files)
    return root


def _run(tmp_path, root, heads, *, network=True):
    return cch.check(root, cch.validate_heads(heads), network=network, url_template=_url(tmp_path))


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
    (lambda d: d["heads"][NAME]["optional"].update(not_in_parent=[]), 'o/child: optional.not_in_parent is not supported (the child is a pure subtree)'),
    (lambda d: d["heads"][NAME]["optional"].update(child_preamble=["README.md"]), 'o/child: optional.child_preamble is not supported (the child is a pure subtree)'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent=[]), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent={"a": ""}), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent={"": "a"}), 'o/child: optional.mirrored_from_parent must map paths to paths'),
    (lambda d: d["heads"][NAME]["optional"].update(mirrored_from_parent={"a": 1}), 'o/child: optional.mirrored_from_parent must map paths to paths'),
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
    doc = _heads(SHA, mirrored_from_parent={"p.py": "p.py"}, other="free")
    assert cch.validate_heads(doc) is doc


def test_reject_legacy_vendor_consumers(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / cch.LEGACY_VENDOR_CONSUMERS).write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="not used between Aoi and subtree children"):
        cch._reject_legacy_vendor_consumers(root)


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

def test_identical_pure_subtree_with_mirror(tmp_path):
    sha = _child(tmp_path, {"a.py": "a", "README.md": "r", "p.py": "p", "pyproject.toml": "c",
                            ".github/x.yml": "w", "run.sh": ("x", "x")})
    root = _parent(tmp_path, {"p.py": "p", "sub/a.py": "a", "sub/README.md": "r", "sub/p.py": "p",
                              "sub/pyproject.toml": "c", "sub/.github/x.yml": "w", "sub/run.sh": ("x", "x")})
    heads = _heads(sha, mirrored_from_parent={"p.py": "p.py"})
    row = _run(tmp_path, root, heads)["children"][0]
    assert row["live_sha"] == sha and row["drift"] is False and row["identical"] is True
    assert "error" not in row
    assert row["diff"] == {"only_in_parent": [], "only_in_child": [], "different": []}


def test_diff_categories_and_mode(tmp_path):
    sha = _child(tmp_path, {"same": "s", "blob": "child", "mode": ("m", "x"), "child_only": "c"})
    _commit(tmp_path / "work" / NAME, {"later": "l"})
    _git(tmp_path / "work" / NAME, "push", "-q", str(tmp_path / "remotes" / f"{NAME}.git"), "HEAD:main")
    root = _parent(tmp_path, {"sub/same": "s", "sub/blob": "parent", "sub/mode": "m", "sub/parent_only": "p"})
    report = _run(tmp_path, root, _heads(sha))
    row = report["children"][0]
    assert row["drift"] is True and row["live_sha"] != sha
    assert row["diff"] == {"only_in_parent": ["parent_only"], "only_in_child": ["child_only"],
                           "different": ["blob", "mode"]}
    assert row["identical"] is False
    assert {k: row[k] for k in ("repository", "recorded_sha", "prefix")} == {"repository": NAME, "recorded_sha": sha,
                                                                            "prefix": "sub"}
    assert not cch.failed(report, fail_on_drift=False, fail_on_diff=False)
    assert cch.failed(report, fail_on_drift=True, fail_on_diff=False)
    assert cch.failed(report, fail_on_drift=False, fail_on_diff=True)


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


# --- CLI ---------------------------------------------------------------------------------

def _write_root(tmp_path, heads, files=None, *, legacy_vendor=False):
    root = tmp_path / "cli"
    payload = {"child-heads.json": json.dumps(heads)}
    if legacy_vendor:
        payload[cch.LEGACY_VENDOR_CONSUMERS] = '{"schema":"vendor-consumers/1","consumers":[]}'
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


def test_main_rejects_legacy_vendor_consumers(tmp_path, capsys):
    sha = _child(tmp_path, {"a": "a"})
    root = _write_root(tmp_path, _heads(sha), legacy_vendor=True)
    rc, out, err = _main(capsys, "--root", root, "--url-template", _url(tmp_path))
    assert rc == 2 and out == "" and "vendor-consumers.json" in err


def test_main_custom_heads_file(tmp_path, capsys):
    root = tmp_path / "cli"
    _commit(root, {"h.json": json.dumps(_heads(SHA)), "sub/a": "a"})
    rc, out, _ = _main(capsys, "--root", root, "--heads", "h.json", "--offline")
    assert rc == 0 and json.loads(out)["children"][0]["mirrors"] == {}


@pytest.mark.parametrize("case", ["missing", "badjson", "shape", "legacy", "norepo"])
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
    if case == "legacy":
        (root / cch.LEGACY_VENDOR_CONSUMERS).write_text("{}", encoding="utf-8")
    rc, out, err = _main(capsys, "--root", root, "--offline")
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
    heads = _heads(SHA)
    before = copy.deepcopy(heads)
    _run(tmp_path, root, heads, network=False)
    assert heads == before


# --- coverage / mutation (stdlib only; targets scripts/check_child_heads.py) ---------------

_COMPARE_FLIPS = {
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
}


def _mutation_eligible(node: ast.AST) -> bool:
    if isinstance(node, ast.Compare):
        if len(node.ops) != 1 or type(node.ops[0]) not in _COMPARE_FLIPS:
            return False
        for part in ast.walk(node):
            if isinstance(part, ast.Constant) and part.value == "__main__":
                return False
        return True
    return isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not)


def _mutant_source_at(source: str, target_index: int) -> str:
    counter = 0

    class _Mutate(ast.NodeTransformer):
        def visit_Compare(self, node: ast.Compare):
            nonlocal counter
            node = self.generic_visit(node)
            if not _mutation_eligible(node):
                return node
            if counter == target_index:
                flip = _COMPARE_FLIPS[type(node.ops[0])]
                return ast.Compare(left=node.left, ops=[flip()], comparators=node.comparators)
            counter += 1
            return node

        def visit_UnaryOp(self, node: ast.UnaryOp):
            nonlocal counter
            node = self.generic_visit(node)
            if not _mutation_eligible(node):
                return node
            if counter == target_index:
                return node.operand
            counter += 1
            return node

    tree = _Mutate().visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + "\n"


def _mutation_site_count(source: str) -> int:
    counter = 0

    class _Count(ast.NodeVisitor):
        def visit_Compare(self, node: ast.Compare):
            nonlocal counter
            if _mutation_eligible(node):
                counter += 1
            self.generic_visit(node)

        def visit_UnaryOp(self, node: ast.UnaryOp):
            nonlocal counter
            if _mutation_eligible(node):
                counter += 1
            self.generic_visit(node)

    _Count().visit(ast.parse(source))
    return counter


def _smoke_battery(mod, tmp_path: Path) -> None:
    """Fast checks that must fail when check_child_heads.py is meaningfully mutated."""
    heads_doc = _heads(SHA)
    mod.validate_heads(heads_doc)
    with pytest.raises(ValueError):
        mod.validate_heads({})
    root = _parent(tmp_path, {"sub/a": "a"})
    mod._reject_legacy_vendor_consumers(root)
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    (legacy / mod.LEGACY_VENDOR_CONSUMERS).write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        mod._reject_legacy_vendor_consumers(legacy)
    whole = {"p.py": ("100644", "1"), "sub/p.py": ("100644", "2")}
    assert mod._mirrors(whole, "sub", {"p.py": "p.py"})["p.py"] == "different"
    report = mod.check(root, heads_doc, network=False)
    assert not mod.failed(report, fail_on_drift=False, fail_on_diff=False)
    sha = _child(tmp_path, {"a": "a"})
    root2 = _parent(tmp_path / "n", {"sub/a": "b"})
    report2 = mod.check(root2, _heads(sha), network=True, url_template=_url(tmp_path))
    assert report2["children"][0]["identical"] is False
    assert mod.failed(report2, fail_on_drift=False, fail_on_diff=True)
    assert mod.main(["--root", str(root), "--offline"]) == 0


def test_check_child_heads_line_and_branch_coverage():
    cov_file = ROOT / ".coverage.check_child_heads"
    cov_file.unlink(missing_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ROOT / "scripts"), "COVERAGE_FILE": str(cov_file)}
    run = subprocess.run(
        [sys.executable, "-m", "coverage", "run", "--branch", "--source=check_child_heads",
         "-m", "pytest", "-q", str(Path(__file__).resolve()),
         "-k", "not test_mutations_all_killed and not test_check_child_heads_line_and_branch_coverage"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    report = subprocess.run(
        [sys.executable, "-m", "coverage", "report", "--include=scripts/check_child_heads.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert report.returncode == 0, report.stdout + report.stderr
    total_line = report.stdout.splitlines()[-1]
    assert "100%" in total_line
    assert " 0 " in total_line


def test_mutations_all_killed(tmp_path):
    source = SCRIPT.read_text(encoding="utf-8")
    sites = _mutation_site_count(source)
    assert sites > 0
    survived = []
    equivalent = []
    for index in range(sites):
        mutant = _mutant_source_at(source, index)
        if mutant == source:
            equivalent.append(index)
            continue
        path = tmp_path / f"mut-{index}.py"
        path.write_text(mutant, encoding="utf-8")
        mod = _import_check_child_heads(path)
        try:
            _smoke_battery(mod, tmp_path / f"smoke-{index}")
        except Exception:
            continue
        survived.append(index)
    assert not survived, f"survived mutant indices: {survived} (equivalent skipped: {equivalent})"
