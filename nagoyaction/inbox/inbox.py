"""Issue-comment question inbox for Aoi main.

Trusted code is always taken from main. Research results are copied from the
configured results ref and treated as data only. Exploration and local-LLM
orchestration are intentionally deferred from this initial main rollout.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "queryu/ask")]

from ask import answer, load, parse, render, validate_query
from bank import lookup

BRANCH_PREFIX = "aoi-research-state"
SELF = "github-actions[bot]"
MARKER = "<!-- aoi-inbox:"


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temp.replace(path)


def snapshot(root: Path, cycle: Path) -> dict:
    """Fingerprint only code that exists on main and result files actually read."""
    files = [
        root / "queryu/ask/ask.py",
        root / "queryu/ask/bank.py",
        root / "nagoyaction/inbox/inbox.py",
    ]
    results = [
        cycle / "outputs" / name
        for name in ("sets.jsonl", "propositions.jsonl")
        if (cycle / "outputs" / name).is_file()
    ]
    if not results:
        raise FileNotFoundError(
            "結果が読めません: outputs/sets.jsonl または outputs/propositions.jsonl が必要です"
        )
    files.extend(results)

    def label(path: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            try:
                return "results/" + str(path.relative_to(cycle))
            except ValueError:
                return path.name

    return {label(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}


def command(comment: dict):
    body = comment.get("body", "").strip()
    if len(body) > 4000:
        return None
    match = re.fullmatch(r"/(ask|explore|status|stop)(?:\s+([\s\S]*))?", body)
    return (match[1], (match[2] or "").strip()) if match else None


def allowed_actor(comment, repository):
    author = comment.get("user", {}).get("login", "").casefold()
    if not author:
        return False
    raw = json.loads(os.environ.get("AOI_INBOX_ALLOWED_ACTORS", "") or "[]")
    if not isinstance(raw, list) or any(
        not isinstance(value, str) or not value for value in raw
    ):
        raise ValueError(
            "AOI_INBOX_ALLOWED_ACTORS はGitHubログイン名のJSON配列にしてください"
        )
    allowed = {
        repository.split("/")[0].casefold(),
        SELF,
        *(value.casefold() for value in raw),
    }
    return (
        comment.get("author_association") in ("OWNER", "MEMBER", "COLLABORATOR")
        or author in allowed
    )


class GitHub:
    def __init__(self, repository: str, issue: int):
        if (
            not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or issue < 1
        ):
            raise ValueError("repository / issue が不正")
        self.repository, self.issue = repository, issue
        self.base = f"https://api.github.com/repos/{repository}"

    def call(self, path, body=None, method=None):
        req = urllib.request.Request(
            self.base + path,
            data=None if body is None else json.dumps(body).encode(),
            method=method,
            headers={
                "Authorization": "Bearer " + os.environ["GH_TOKEN"],
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "Aoi-inbox",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def comments(self):
        rows, page = [], 1
        while True:
            batch = self.call(
                f"/issues/{self.issue}/comments?per_page=100&page={page}"
            )
            rows.extend(batch)
            if len(batch) < 100:
                return rows
            page += 1

    def reply(self, key, body, comments):
        marker = f"{MARKER}{key} -->"
        if any(
            c.get("user", {}).get("login") == SELF
            and marker in c.get("body", "")
            for c in comments
        ):
            return
        safe = body[:50000].replace("@", "＠")
        comment = self.call(
            f"/issues/{self.issue}/comments", {"body": marker + "\n" + safe}
        )
        comments.append(comment)


def git(cwd: Path, *args, check=True, input=None):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        input=input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
        timeout=60,
    )


class State:
    """Durable receipts live on one state branch per research cycle."""

    def __init__(self, root: Path, path: Path, create=False):
        self.root, self.path = root, path
        self.branch = os.environ.get("AOI_STATE_BRANCH") or BRANCH_PREFIX
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", self.branch) or ".." in self.branch:
            raise ValueError("AOI_STATE_BRANCH が不正")
        remote = git(
            root,
            "ls-remote",
            "--exit-code",
            "origin",
            f"refs/heads/{self.branch}",
            check=False,
        )
        if remote.returncode not in (0, 2):
            raise RuntimeError("状態ブランチを確認できません: " + remote.stderr)
        if remote.returncode == 2 and not create:
            raise FileNotFoundError("受付はまだ起動していません")
        git(root, "config", "user.name", SELF)
        git(
            root,
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com",
        )
        if remote.returncode == 0:
            git(root, "fetch", "origin", f"refs/heads/{self.branch}")
            commit = git(root, "rev-parse", "FETCH_HEAD").stdout.strip()
        else:
            tree = git(
                root, "hash-object", "-w", "-t", "tree", "--stdin", input=""
            ).stdout.strip()
            commit = git(
                root, "commit-tree", tree, "-m", "Initialize Aoi inbox state"
            ).stdout.strip()
        git(root, "worktree", "add", "--detach", str(path), commit)
        if remote.returncode == 2:
            git(path, "push", "origin", f"HEAD:refs/heads/{self.branch}")

    def sync(self):
        git(self.path, "fetch", "origin", f"refs/heads/{self.branch}")
        git(self.path, "rebase", "FETCH_HEAD")

    def save(self):
        git(self.path, "add", "--all")
        if git(
            self.path, "diff", "--cached", "--quiet", check=False
        ).returncode == 0:
            return
        git(self.path, "commit", "-m", "Record Aoi inbox receipt")
        for _ in range(3):
            self.sync()
            result = git(
                self.path,
                "push",
                "origin",
                f"HEAD:refs/heads/{self.branch}",
                check=False,
            )
            if result.returncode == 0:
                return
        raise RuntimeError(
            "状態保存に失敗。ローカルチェックポイントを artifact から回収してください"
        )


def ask_question(text: str, results: Path, cache: Path | None = None):
    reader = "json" if text.startswith("{") else "rules"
    if text.startswith("{"):
        q, unread = validate_query(json.loads(text)), []
    else:
        q, unread = parse(text)

    hashes = {
        name: hashlib.sha256((results / name).read_bytes()).hexdigest()
        if (results / name).exists()
        else None
        for name in ("sets.jsonl", "propositions.jsonl")
    }
    key = digest(
        {
            "query": asdict(q),
            "results": hashes,
            "answer_code": hashlib.sha256(
                (ROOT / "queryu/ask/ask.py").read_bytes()
            ).hexdigest(),
        }
    )
    cached = cache / f"{key}.json" if cache else None
    prepared = lookup(q, results, cache.parent / "known") if cache and not unread else None
    if unread:
        result = {
            "answer": "判定不能",
            "error": "解釈を確認してください: " + "; ".join(unread),
            "rows": [],
        }
    elif prepared is not None:
        result = prepared
    elif cached and cached.exists():
        result = json.loads(cached.read_text(encoding="utf-8"))
    else:
        result = answer(q, load(results))
        if cached:
            atomic_json(cached, result)
    return {
        "question": text,
        "query": asdict(q),
        "unread": unread,
        "result": result,
        "reader": reader,
    }, render(text, q, unread, result)


def reply_saved(api, state, key, body, comments):
    pending = state.path / "pending-replies" / f"{key}.json"
    try:
        api.reply(key, body, comments)
    except (
        urllib.error.URLError,
        OSError,
        http.client.HTTPException,
        json.JSONDecodeError,
    ) as exc:
        atomic_json(
            pending, {"key": key, "error": f"{type(exc).__name__}: {exc}"}
        )
        state.save()
        print(f"返信を次回へ保留: {key}: {type(exc).__name__}", file=sys.stderr)
        return False
    if pending.exists():
        pending.unlink()
        state.save()
    return True


def status_report(path: Path):
    receipts = len(list((path / "receipts").glob("*.json")))
    pending = len(list((path / "pending-replies").glob("*.json")))
    answers = len(list((path / "answers").glob("*.json")))
    return (
        f"コマンド累積受付: {receipts}件（この /status 自身は保存前）\n"
        f"回答キャッシュ: {answers}件\n"
        f"返信再送待ち: {pending}件\n"
        "探索ワーカー: 未導入（#10 は質問受付のみ）"
    )


def intake(
    api,
    state,
    cycle: Path,
    code_sha: str,
    cycle_name="",
    result_sha="",
):
    comments = api.comments()
    inputs = snapshot(ROOT, cycle)
    for comment_row in list(comments):
        parsed = command(comment_row)
        if parsed is None or not allowed_actor(comment_row, api.repository):
            continue
        cid = str(int(comment_row["id"]))
        receipt = state.path / "receipts" / f"{cid}.json"
        if receipt.exists():
            previous = json.loads(receipt.read_text(encoding="utf-8"))
            if previous.get("reply_body"):
                reply_saved(
                    api,
                    state,
                    "reply-" + cid,
                    previous["reply_body"],
                    comments,
                )
            continue

        kind, text = parsed
        record = {
            "comment_id": int(cid),
            "author": comment_row["user"]["login"],
            "body": comment_row["body"],
            "created_at": comment_row["created_at"],
            "author_association": comment_row.get("author_association", "NONE"),
            "code_sha": code_sha,
            "cycle": cycle_name,
            "result_sha": result_sha,
            "inputs": inputs,
            "kind": kind,
        }
        try:
            if kind == "ask":
                response, body = ask_question(
                    text, cycle / "outputs", state.path / "answers"
                )
                record["response"] = response
                record["result_files"] = {
                    path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (cycle / "outputs").glob("*.jsonl")
                    if path.name in ("sets.jsonl", "propositions.jsonl")
                }
            elif kind == "status":
                body = status_report(state.path)
            elif kind == "explore":
                body = (
                    "探索は #10 では未導入です。まず質問受付を本番確認し、"
                    "探索は main 構成に合わせた別PRで導入します。"
                )
            else:
                body = "探索は #10 では未導入のため、停止対象はありません。"
        except Exception as exc:
            body = "判定不能 / 入力を確認してください: " + str(exc)
            record["error"] = str(exc)
            record["error_type"] = type(exc).__name__

        body += (
            f"\n\n対象サイクル: `{cycle_name}`"
            f" / 結果SHA: `{result_sha}`"
            f" / 対象コード: `{code_sha}`"
            f" / 元コメント: {cid}"
        )
        record["reply_body"] = body
        atomic_json(receipt, record)
        state.save()
        reply_saved(api, state, "reply-" + cid, body, comments)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("intake",))
    parser.add_argument("--issue", type=int, default=os.environ.get("AOI_INBOX_ISSUE"))
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument(
        "--state-dir", type=Path, default=ROOT / ".research-state"
    )
    args = parser.parse_args(argv)
    if not args.repository or not args.issue:
        parser.error(
            "--issue / AOI_INBOX_ISSUE と --repository / GITHUB_REPOSITORY が必要"
        )

    cycle_name = os.environ.get("AOI_RESEARCH_CYCLE")
    result_ref = os.environ.get("AOI_RESULTS_REF")
    if not cycle_name or not result_ref:
        parser.error("AOI_RESEARCH_CYCLE / AOI_RESULTS_REF が必要")
    if (
        not re.fullmatch(r"[A-Za-z0-9._-]+", cycle_name)
        or not re.fullmatch(r"[A-Za-z0-9._/-]+", result_ref)
        or ".." in result_ref
    ):
        parser.error("AOI_RESEARCH_CYCLE / AOI_RESULTS_REF が不正")

    api = GitHub(args.repository, args.issue)
    cycle = ROOT / ".aoi-results" / cycle_name
    state = State(ROOT, args.state_dir.resolve(), create=True)
    intake(
        api,
        state,
        cycle,
        git(ROOT, "rev-parse", "HEAD").stdout.strip(),
        cycle_name,
        os.environ.get("AOI_RESULTS_SHA", ""),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
