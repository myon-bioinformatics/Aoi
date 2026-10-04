import subprocess
import urllib.error

import pytest

import linkcheck as lc


def repo(tmp_path, files: dict[str, str], untracked: dict[str, str] | None = None):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for name, text in {**files, **(untracked or {})}.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", *files], cwd=tmp_path, check=True)
    return lc.check_local(tmp_path, lc.tracked_files(tmp_path))


def status(results):
    return {(r["file"], r["target"]): r["status"] for r in results}


def test_relative_links_images_dirs_and_anchors(tmp_path):
    res = repo(tmp_path, {
        "README.md": "[a](docs/a.md) ![i](docs/img/x.webp) [d](docs) [s](docs/a.md#sec) [h](#top) [m](mailto:x@y)",
        "docs/a.md": "[up](../README.md) [root](/README.md)",
        "docs/img/x.webp": "",
    })
    assert set(status(res).values()) <= {"ok", "not-checked"}
    assert status(res)[("README.md", "#top")] == "not-checked"


def test_case_mismatch_is_reported_with_the_real_name(tmp_path):
    res = repo(tmp_path, {"README.md": "[g](docs/genesis.md)", "docs/GENESIS.md": ""})
    r = res[0]
    assert r["status"] == "broken" and "docs/GENESIS.md" in r["reason"]


def test_untracked_file_counts_as_missing(tmp_path):
    res = repo(tmp_path, {"README.md": "![x](img.webp)"}, untracked={"img.webp": ""})
    assert res[0]["status"] == "broken" and "git" in res[0]["reason"]


def test_outside_repo_is_broken(tmp_path):
    assert repo(tmp_path, {"README.md": "[x](../outside.md)"})[0]["status"] == "broken"


def test_links_in_code_are_ignored():
    text = "```\n[a](missing.md)\n```\n~~~md\n[b](missing.md)\n~~~\n`[c](missing.md)` [d](real.md)"
    assert lc.links_in(text) == ["real.md"]


@pytest.mark.parametrize("text,expected", [
    ('[t](a.md "title")', ["a.md"]), ("[t](<a b.md>)", []), ("[t](<a.md>)", ["a.md"]),
    ("[a \\] b](x.md)", ["x.md"]), ("![](i.png)", ["i.png"]), ("plain docs/a.md", []),
])
def test_link_syntax(text, expected):
    assert lc.links_in(text) == expected


class Out:
    def __init__(self, rc, stderr=""):
        self.returncode, self.stderr = rc, stderr


def test_remote_check_marks_404_on_branch(tmp_path):
    res = repo(tmp_path, {"README.md": "[a](a.md) [b](b.md) [b2](b.md)", "a.md": "", "b.md": ""})
    calls = []

    def runner(argv, **kw):
        calls.append(argv[2])
        return Out(0) if "a.md" in argv[2] else Out(1, "gh: Not Found (HTTP 404)")

    lc.check_remote(res, "o/r", "feature", runner=runner)
    assert status(res) == {("README.md", "a.md"): "ok", ("README.md", "b.md"): "broken"}
    assert calls == ["repos/o/r/contents/a.md?ref=feature", "repos/o/r/contents/b.md?ref=feature"]  # 同じ参照先は1回だけ


def test_remote_check_does_not_fail_on_auth_errors(tmp_path):
    res = repo(tmp_path, {"README.md": "[a](a.md)", "a.md": ""})
    lc.check_remote(res, "o/r", "main", runner=lambda argv, **kw: Out(1, "HTTP 401"))
    assert res[0]["status"] == "ok" and res[0]["remote"] == "unverified"


def test_external_only_404_and_410_fail():
    res = [{"kind": "external", "target": f"https://x/{c}"} for c in (200, 404, 410, 403)] + \
          [{"kind": "external", "target": "https://down"}]

    def opener(req, timeout):
        code = req.full_url.rsplit("/", 1)[1]
        if code == "down":
            raise urllib.error.URLError("timeout")
        if code != "200":
            raise urllib.error.HTTPError(req.full_url, int(code), "x", {}, None)

    lc.check_external(res, opener=opener)
    assert [r["status"] for r in res] == ["ok", "broken", "broken", "unverified", "unverified"]


def test_repository_links_are_all_valid():
    root = __import__("pathlib").Path(__file__).resolve().parents[2]
    broken = [r for r in lc.check_local(root, lc.tracked_files(root)) if r["status"] == "broken"]
    assert broken == []
