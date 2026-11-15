"""Exercise a real Gitea server in isolated temporary state (CI only)."""
import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORGE = ROOT / "local_forge.py"


def main():
    with tempfile.TemporaryDirectory(prefix="local-forge-ci-") as tmp:
        root = Path(tmp)
        env = dict(os.environ, OLNM_HOME=str(root / "state"), DIAL_FILE=str(root / "dial"),
                   GIT_CONFIG_GLOBAL=str(root / "gitconfig"), GIT_TERMINAL_PROMPT="0")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]

        def run(*args, cwd=None):
            return subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=True, timeout=120)

        def cli(*args, cwd=None):
            return run(sys.executable, str(FORGE), *args, cwd=cwd)

        try:
            cli("install", "--version", "1.27.3", "--flavor", "gitea")
            cli("init", "--port", str(port), "--user", "ciuser", "--password", "Temporary-ci-password-4987")
            cli("up")
            work = root / "sample"
            work.mkdir()
            run("git", "init", "-q", "-b", "main", cwd=work)
            (work / "sample.txt").write_text("initial\n")
            run("git", "add", "sample.txt", cwd=work)
            run("git", "-c", "user.name=CI", "-c", "user.email=ci@example.invalid", "commit", "-qm", "initial", cwd=work)
            cli("repo", "add", str(work))
            run("git", "push", "local", "main", cwd=work)
            cli("issue", "new", "Smoke issue", cwd=work)
            issues = cli("issue", "ls", cwd=work).stdout
            if "Smoke issue" not in issues:
                raise AssertionError("created issue not returned")
            run("git", "switch", "-c", "smoke", cwd=work)
            (work / "sample.txt").write_text("changed\n")
            run("git", "add", "sample.txt", cwd=work)
            run("git", "-c", "user.name=CI", "-c", "user.email=ci@example.invalid", "commit", "-qm", "change", cwd=work)
            cli("pr", "new", "Smoke PR", "--base", "main", cwd=work)
            pulls = cli("pr", "ls", cwd=work).stdout
            if "Smoke PR" not in pulls:
                raise AssertionError("created PR not returned")
            print(json.dumps({"forge": "gitea", "version": "1.27.3", "repo": True, "issue": True, "pull_request": True}))
        except subprocess.CalledProcessError as exc:
            print(f"Real forge command failed: {exc.cmd[:3]} (exit {exc.returncode})", file=sys.stderr)
            print(exc.stderr[-4000:], file=sys.stderr)
            raise
        finally:
            subprocess.run([sys.executable, str(FORGE), "down"], env=env, text=True, capture_output=True, timeout=15)


if __name__ == "__main__":
    main()
