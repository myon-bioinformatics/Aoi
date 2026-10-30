import json
import os
import subprocess
import sys
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import linkcheck as lc

HERE = Path(__file__).resolve().parents[1]
LINKCHECK = HERE / "linkcheck.py"


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


def run_linkcheck(args, *, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, "-S", str(LINKCHECK), *args],
        cwd=cwd, env=env, capture_output=True, text=True,
    )


def init_repo(path: Path, files: dict[str, str]) -> Path:
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    for name, text in files.items():
        dest = path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", *files], cwd=path, check=True)
    return path


def test_help_documents_every_flag_and_the_unverified_exit():
    proc = run_linkcheck(["--help"])
    assert proc.returncode == 0, proc.stderr
    text = proc.stdout
    assert "--root" in text and "git ls-files" in text
    assert "--remote" in text and "gh api" in text
    assert "--ref" in text and "git ref" in text
    assert "--external" in text and "404" in text and "410" in text
    assert "--json" in text and "nagoyaction-linkcheck/1" in text and "nagoyaction-error/1" in text
    assert "--strict" in text and "終了コード 3" in text
    assert "終了コード:" in text
    assert "Aoi" in text and "Links" in text and "--strict なし" in text


def test_cli_broken_link_exits_1_with_structured_json(tmp_path):
    root = init_repo(tmp_path, {"README.md": "[x](missing.md)\n"})
    proc = run_linkcheck(["--root", str(root), "--json"], cwd=Path("/"))
    assert proc.returncode == 1, proc.stderr
    doc = json.loads(proc.stdout)
    err = json.loads(proc.stderr)
    assert doc["schema"] == "nagoyaction-linkcheck/1"
    assert doc["ok"] is False and doc["exit"] == 1 and doc["strict"] is False
    assert doc["counts"]["broken"] == 1 and doc["counts"]["remote_unverified"] == 0
    assert doc["results"][0]["status"] == "broken"
    assert err == {
        "schema": "nagoyaction-error/1",
        "tool": "linkcheck",
        "ok": False,
        "exit": 1,
        "error": {"code": "broken", "message": "broken が 1 件"},
    }
    assert "[broken]" not in proc.stdout


def test_cli_usage_and_git_errors_are_structured_only_with_json(tmp_path):
    usage = run_linkcheck(["--json", "--remote", "o/r"])
    assert usage.returncode == 2 and usage.stdout == ""
    err = json.loads(usage.stderr)
    assert err["schema"] == "nagoyaction-error/1"
    assert err["tool"] == "linkcheck" and err["exit"] == 2
    assert err["error"]["code"] == "usage" and "--ref" in err["error"]["message"]

    text = run_linkcheck(["--remote", "o/r"])
    assert text.returncode == 2
    assert "nagoyaction-error" not in text.stderr
    assert "--ref" in text.stderr

    git = run_linkcheck(["--json", "--root", str(tmp_path)])
    assert git.returncode == 2 and git.stdout == ""
    assert json.loads(git.stderr)["error"]["code"] == "git"


def _http_server():
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            code = 404 if self.path == "/missing" else 403
            self.send_response(code)
            self.end_headers()

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def test_cli_unverified_is_exit_3_only_when_strict(tmp_path):
    server = _http_server()
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"
    try:
        denied = init_repo(tmp_path / "denied", {"README.md": f"[d]({base}/denied)\n"})
        loose = run_linkcheck(["--root", str(denied), "--external", "--json"])
        assert loose.returncode == 0, loose.stderr
        body = json.loads(loose.stdout)
        assert body["exit"] == 0 and body["ok"] is True and body["counts"]["unverified"] == 1
        assert loose.stderr == ""

        hint = run_linkcheck(["--root", str(denied), "--external"])
        assert hint.returncode == 0
        assert "[unverified]" in hint.stdout and "remote_unverified=0" in hint.stdout
        assert "--strict" in hint.stdout and "終了コード 3" in hint.stdout

        strict = run_linkcheck(["--root", str(denied), "--external", "--strict", "--json"])
        assert strict.returncode == 3, strict.stderr
        err = json.loads(strict.stderr)
        assert err["error"]["code"] == "unverified" and err["exit"] == 3
        assert json.loads(strict.stdout)["strict"] is True and json.loads(strict.stdout)["exit"] == 3

        mixed = init_repo(tmp_path / "mixed", {"README.md": f"[d]({base}/denied) [m]({base}/missing)\n"})
        both = run_linkcheck(["--root", str(mixed), "--external", "--strict"])
        assert both.returncode == 1
        assert "[broken]" in both.stdout
        assert "nagoyaction-error" not in both.stderr
    finally:
        server.shutdown()
        server.server_close()


def _fake_gh(directory: Path, script: str) -> dict[str, str]:
    bindir = directory / "bin"
    bindir.mkdir()
    gh = bindir / "gh"
    gh.write_text(script, encoding="utf-8")
    gh.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
    return env


def test_cli_remote_unverified_is_exit_3_only_with_strict(tmp_path):
    root = init_repo(tmp_path / "repo", {"README.md": "[a](a.md)\n", "a.md": ""})
    env = _fake_gh(tmp_path, "#!/bin/sh\necho HTTP 401 >&2\nexit 1\n")
    loose = run_linkcheck(
        ["--root", str(root), "--remote", "o/r", "--ref", "main", "--json"], env=env,
    )
    assert loose.returncode == 0, loose.stderr
    doc = json.loads(loose.stdout)
    assert doc["counts"]["remote_unverified"] == 1
    assert doc["results"][0]["status"] == "ok" and doc["results"][0]["remote"] == "unverified"
    assert loose.stderr == ""

    strict = run_linkcheck(
        ["--root", str(root), "--remote", "o/r", "--ref", "main", "--strict"], env=env,
    )
    assert strict.returncode == 3, strict.stdout
    assert "[unverified]" in strict.stdout
    assert "終了コード 3" in strict.stderr


def test_cli_remote_404_stays_broken_under_strict(tmp_path):
    root = init_repo(tmp_path / "repo", {"README.md": "[a](a.md)\n", "a.md": ""})
    env = _fake_gh(tmp_path, "#!/bin/sh\necho 'gh: Not Found (HTTP 404)' >&2\nexit 1\n")
    proc = run_linkcheck(
        ["--root", str(root), "--remote", "o/r", "--ref", "main", "--strict", "--json"], env=env,
    )
    assert proc.returncode == 1, proc.stdout
    doc = json.loads(proc.stdout)
    err = json.loads(proc.stderr)
    assert doc["results"][0]["status"] == "broken"
    assert err["error"]["code"] == "broken" and err["exit"] == 1
