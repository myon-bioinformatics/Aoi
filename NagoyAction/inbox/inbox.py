"""Public command inbox; trusted code, immutable requests, separate state branch.

Run intake / worker from the default branch. No comment text is shell code.
GitHub is the only remote used by this service. Optional LLM is loopback-only.
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
import time
from datetime import datetime, timezone
import urllib.error
import urllib.request
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "QueRyu/ask"), str(ROOT / "PythDRagoras/logic"), str(ROOT / "DRAgoWing"), str(ROOT / "DRAgoWing/reports"), str(ROOT / "SakAnalytics/baseball"), str(ROOT / "BlueProbe/reports")]
from feedback import prepare_feedback, observe_report
from bank import lookup, prepare
from autonomous import next_request
from ask import answer, load, parse, render, schema, validate_query
from exploration import Explorer, atomic_json, digest, plan, snapshot, summary, save_state, read_state

BRANCH_PREFIX = "aoi-research-state"
SELF = "github-actions[bot]"
MARKER = "<!-- aoi-inbox:"


def command(comment: dict):
    body = comment.get("body", "").strip()
    if len(body) > 4000:
        return None
    match = re.fullmatch(r"/(ask|explore|status|stop)(?:\s+([\s\S]*))?", body)
    return (match[1], (match[2] or "").strip()) if match else None


def allowed_actor(comment, repository):
    """All commands share the same gate, also during scheduled polling."""
    author = comment.get("user", {}).get("login", "").casefold()
    if not author:
        return False
    raw = json.loads(os.environ.get("AOI_INBOX_ALLOWED_ACTORS", "") or "[]")
    if not isinstance(raw, list) or any(not isinstance(value, str) or not value for value in raw):
        raise ValueError("AOI_INBOX_ALLOWED_ACTORS はGitHubログイン名のJSON配列にしてください")
    allowed = {repository.split("/")[0].casefold(), SELF, *(value.casefold() for value in raw)}
    return comment.get("author_association") in ("OWNER", "MEMBER", "COLLABORATOR") or author in allowed


class GitHub:
    def __init__(self, repository: str, issue: int):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or issue < 1:
            raise ValueError("repository / issue が不正")
        self.repository, self.issue = repository, issue
        self.base = f"https://api.github.com/repos/{repository}"

    def call(self, path, body=None, method=None):
        req = urllib.request.Request(self.base + path, data=None if body is None else json.dumps(body).encode(),
                                     method=method, headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                                     "Accept": "application/vnd.github+json", "Content-Type": "application/json",
                                     "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Aoi-inbox"})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def comments(self):
        rows, page = [], 1
        while True:
            batch = self.call(f"/issues/{self.issue}/comments?per_page=100&page={page}")
            rows.extend(batch)
            if len(batch) < 100:
                return rows
            page += 1

    def reply(self, key, body, comments):
        marker = f"{MARKER}{key} -->"
        if any(c.get("user", {}).get("login") == SELF and marker in c.get("body", "") for c in comments):
            return
        # No echoed user mentions; body is data and never interpolated into shell.
        safe = body[:50000].replace("@", "＠")
        comment = self.call(f"/issues/{self.issue}/comments", {"body": marker + "\n" + safe})
        comments.append(comment)


def git(cwd: Path, *args, check=True, input=None):
    return subprocess.run(["git", "-C", str(cwd), *args], text=True, input=input,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check, timeout=60)


class State:
    """Only intake creates requests/stops; only the worker updates jobs.

    Rebase remote writes before each push so intake remains independent while a
    long worker runs. Failed pushes never discard the local checkpoint.
    """
    def __init__(self, root: Path, path: Path, create=False):
        self.root, self.path = root, path
        self.branch = os.environ.get("AOI_STATE_BRANCH") or BRANCH_PREFIX
        if not re.fullmatch(r"[A-Za-z0-9._/-]+", self.branch) or ".." in self.branch:
            raise ValueError("AOI_STATE_BRANCH が不正")
        remote = git(root, "ls-remote", "--exit-code", "origin", f"refs/heads/{self.branch}", check=False)
        if remote.returncode not in (0, 2):
            raise RuntimeError("状態ブランチを確認できません: " + remote.stderr)
        if remote.returncode == 2 and not create:
            raise FileNotFoundError("受付はまだ起動していません")
        git(root, "config", "user.name", SELF)
        git(root, "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
        if remote.returncode == 0:
            git(root, "fetch", "origin", f"refs/heads/{self.branch}")
            commit = git(root, "rev-parse", "FETCH_HEAD").stdout.strip()
        else:
            tree = git(root, "hash-object", "-w", "-t", "tree", "--stdin", input="").stdout.strip()
            commit = git(root, "commit-tree", tree, "-m", "Initialize Aoi research state").stdout.strip()
        git(root, "worktree", "add", "--detach", str(path), commit)
        if remote.returncode == 2:
            git(path, "push", "origin", f"HEAD:refs/heads/{self.branch}")

    def sync(self):
        git(self.path, "fetch", "origin", f"refs/heads/{self.branch}")
        git(self.path, "rebase", "FETCH_HEAD")

    def save(self):
        git(self.path, "add", "--all")
        if git(self.path, "diff", "--cached", "--quiet", check=False).returncode == 0:
            return
        git(self.path, "commit", "-m", "Record inquiry / exploration checkpoint")
        for _ in range(3):
            self.sync()
            result = git(self.path, "push", "origin", f"HEAD:refs/heads/{self.branch}", check=False)
            if result.returncode == 0:
                return
        raise RuntimeError("状態保存に失敗。ローカルチェックポイントを artifact から回収してください")


class BufferedState:
    """Keep local shards current; push/sync at most every five minutes."""
    def __init__(self, state):
        self.state, self.path = state, state.path
        self.updated = time.monotonic()
        self.dirty = False
        self.started = False

    def flush(self):
        if self.dirty:
            self.state.save()
            self.dirty = False
        self.updated = time.monotonic()

    def save(self):
        self.dirty = True
        if time.monotonic() - self.updated >= 300:
            self.flush()

    def sync(self):
        if not self.started or time.monotonic() - self.updated >= 300:
            self.flush()
            self.state.sync()
            self.started = True


def safe_observe(path):
    try:
        observe_report(path)
    except (ValueError, TypeError, KeyError, OSError) as e:
        atomic_json(path / "feedback/report-error.json", {"error": f"{type(e).__name__}: {e}"})
        print("HTML観測を保留。探索は継続します。", file=sys.stderr)
    else:
        (path / "feedback/report-error.json").unlink(missing_ok=True)


def pending_requests(path):
    pending = []
    for p in (path / "requests").glob("*.json"):
        request = json.loads(p.read_text())
        saved = path / "jobs" / request["job"] / "state.json"
        if (path / "stops" / f"{request['comment_id']}.json").exists():
            continue
        if saved.exists() and json.loads(saved.read_text())["status"] in ("completed", "bounded", "blocked", "error"):
            continue
        pending.append(request)
    return pending


def local_query(text: str):
    """Optional llama.cpp endpoint. A schema restricts syntax, not truth."""
    envelope = {"type": "object", "additionalProperties": False, "required": ["query", "unread"],
                "properties": {"query": schema(), "unread": {"type": "array", "items": {"type": "string"}}}}
    prompt = ("日本語の質問をQueryへ変換。答えを推測しない。Queryで表現できない条件は必ずunreadへ。"
              "年だけの絞り込み、天候、因果関係は未対応。球団コード: g,s,db,d,t,c,h,f,b,e,l,m。"
              "excludeは反例一覧から除く単位。成立率の再計算ではない。Query定義: " + json.dumps(schema(), ensure_ascii=False))
    req = urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions",
        data=json.dumps({"messages": [{"role": "system", "content": prompt}, {"role": "user", "content": text}],
                         "temperature": 0, "max_tokens": 600,
                         "response_format": {"type": "json_schema", "json_schema": {"name": "query", "schema": envelope}}}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as response:
        output = json.load(response)
    raw = json.loads(output["choices"][0]["message"]["content"])
    if set(raw) != {"query", "unread"} or not isinstance(raw["unread"], list) or any(not isinstance(s, str) for s in raw["unread"]):
        raise ValueError("LLMの応答の型が不正")
    return validate_query(raw["query"]), raw["unread"]


def ask_question(text: str, results: Path, use_llm=False, cache: Path | None = None):
    reader = "json" if text.startswith("{") else "rules"
    if text.startswith("{"):
        q, unread = validate_query(json.loads(text)), []
    else:
        q, unread = parse(text)
        if unread and use_llm:
            q, unread = local_query(text)
            reader = "llama.cpp"
    hashes = {name: hashlib.sha256((results / name).read_bytes()).hexdigest() if (results / name).exists() else None
              for name in ("sets.jsonl", "propositions.jsonl")}
    key = digest({"query": asdict(q), "results": hashes,
                  "answer_code": hashlib.sha256((ROOT / "QueRyu/ask/ask.py").read_bytes()).hexdigest()})
    cached = cache / f"{key}.json" if cache else None
    prepared = lookup(q, results, cache.parent / "known") if cache and not unread else None
    if unread:
        res = {"answer": "判定不能", "error": "解釈を確認してください: " + "; ".join(unread), "rows": []}
    elif prepared is not None:
        res = prepared
    elif cached and cached.exists():
        res = json.loads(cached.read_text(encoding="utf-8"))
    else:
        res = answer(q, load(results))
        if cached:
            atomic_json(cached, res)
    identity = ROOT / ".models/identity.json"
    model = json.loads(identity.read_text()) if reader == "llama.cpp" and identity.exists() else None
    return {"question": text, "query": asdict(q), "unread": unread, "result": res, "reader": reader,
            "model": model}, render(text, q, unread, res)



def reply_saved(api, state, key, body, comments):
    """Try once; retain failures for the next poll with a fresh marker list."""
    pending = state.path / "pending-replies" / f"{key}.json"
    try:
        api.reply(key, body, comments)
    except (urllib.error.URLError, OSError, http.client.HTTPException, json.JSONDecodeError) as e:
        atomic_json(pending, {"key": key, "error": f"{type(e).__name__}: {e}"})
        state.save()
        print(f"返信を次回へ保留: {key}: {type(e).__name__}", file=sys.stderr)
        return False
    if pending.exists():
        pending.unlink()
        state.save()
    return True


def status_report(path):
    counts = {"待機": 0, "進行・再開待ち": 0, "完了": 0, "上限到達": 0,
              "停止": 0, "入力変更で保留": 0, "エラー": 0, "状態不明": 0}
    labels = {"queued": "待機", "running": "進行・再開待ち", "completed": "完了", "bounded": "上限到達",
              "blocked": "入力変更で保留", "error": "エラー"}
    requests = list((path / "requests").glob("*.json"))
    for p in requests:
        request = json.loads(p.read_text(encoding="utf-8"))
        if (path / "stops" / f"{request['comment_id']}.json").exists():
            counts["停止"] += 1
            continue
        saved = path / "jobs" / request["job"] / "state.json"
        label = labels.get(json.loads(saved.read_text())["status"], "状態不明") if saved.exists() else "待機"
        counts[label] += 1
    paths = sorted((path / "jobs").glob("*/state.json"), key=lambda p: (json.loads(p.read_text()).get("updated_at", ""), p.parent.name))
    body = f"探索依頼の累積受付: {len(requests)}件（コメント単位。自動探索は含まない）\n"
    body += " / ".join(f"{name}: {n}件" for name, n in counts.items())
    body += f"\n保存済み探索job: {len(paths)}件（同一依頼の統合・自動探索を含む）"
    body += f"\n返信再送待ち: {len(list((path / 'pending-replies').glob('*.json')))}件"
    body += f"\nコマンド累積受付: {len(list((path / 'receipts').glob('*.json')))}件（この /status 自身は保存前）"
    if (path / "feedback/report-error.json").exists():
        body += "\nHTML観測: エラーで保留（前回観測を維持）"
    stopped_jobs = {json.loads(p.read_text())["job"] for p in requests if (path / "stops" / f"{p.stem}.json").exists()}
    active_jobs = {r["job"] for r in pending_requests(path)}
    def shown(p):
        note = "停止（自動探索も停止）\n" if p.parent.name in stopped_jobs - active_jobs else ""
        return note + summary(json.loads(p.read_text(encoding="utf-8")))
    body += "\n\n" + ("\n\n".join(f"`{p.parent.name}`\n" + shown(p) for p in reversed(paths[-10:])) or "探索の実行結果はまだありません。")
    return body

def intake(api, state, cycle: Path, code_sha: str, use_llm=False, cycle_name="", result_sha=""):
    comments = api.comments()
    inputs = snapshot(ROOT, cycle)
    for c in list(comments):
        parsed = command(c)
        if parsed is None or not allowed_actor(c, api.repository):
            continue
        cid = str(int(c["id"]))
        receipt = state.path / "receipts" / f"{cid}.json"
        if receipt.exists():
            previous = json.loads(receipt.read_text(encoding="utf-8"))
            if previous.get("reply_body"):
                reply_saved(api, state, "reply-" + cid, previous["reply_body"], comments)
            continue
        kind, text = parsed
        record = {"comment_id": int(cid), "author": c["user"]["login"], "body": c["body"],
                  "created_at": c["created_at"], "author_association": c.get("author_association", "NONE"), "code_sha": code_sha, "cycle": cycle_name, "result_sha": result_sha, "inputs": inputs, "kind": kind}
        try:
            if kind == "ask":
                response, body = ask_question(text, cycle / "outputs", use_llm, state.path / "answers")
                record["response"] = response
                record["result_files"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in (cycle / "outputs").glob("*.jsonl") if p.name in ("sets.jsonl", "propositions.jsonl")}
            elif kind == "explore":
                if os.environ.get("AOI_RESEARCH_ENABLED") != "1":
                    body = "探索は未稼働です。AOI_RESEARCH_ENABLED=1 と worker の導入後に利用できます。"
                else:
                        request_path = state.path / "requests" / f"{cid}.json"
                    if request_path.exists():
                        request = json.loads(request_path.read_text(encoding="utf-8"))
                        spec, job = request["plan"], request["job"]
                    else:
                        pending = pending_requests(state.path)
                        if len(pending) >= 20 or sum(r["author"] == record["author"] for r in pending) >= 5:
                            raise ValueError("未完了の探索依頼は1人5件・全体20件までです。完了または停止後に新しいコメントで依頼してください")
                        spec = plan(text, cycle)
                        job = digest({"plan": spec, "inputs": inputs})[:24]
                        request = {**record, "plan": spec, "job": job}
                        atomic_json(request_path, request)
                    # Persist the plan before acknowledging or doing any evaluation.
                    state.save()
                    body = f"探索を受け付けました。依頼 `{cid}` / job `{job}`\n計画: `{json.dumps(spec, ensure_ascii=False)}`\n同じ計画・入力は同じjobとして処理します。進捗は /status。停止は /stop {cid}。"
                elif kind == "status":
                body = status_report(state.path)
            else:
                if not re.fullmatch(r"\d+", text):
                    raise ValueError("/stop には依頼のコメントIDを指定してください")
                path = state.path / "requests" / f"{text}.json"
                if not path.exists():
                    raise ValueError("その探索依頼はありません")
                request = json.loads(path.read_text(encoding="utf-8"))
                if request["author"] != record["author"] and c.get("author_association") not in ("OWNER", "MEMBER", "COLLABORATOR"):
                    raise ValueError("停止できるのは依頼者かリポジトリ管理側です")
                saved_path = state.path / "jobs" / request["job"] / "state.json"
                terminal = saved_path.exists() and json.loads(saved_path.read_text())["status"] in ("completed", "bounded", "blocked", "error")
                if terminal:
                    body = f"依頼 `{text}` はすでに終了しています。新しい停止記録は作りません。"
                else:
                    atomic_json(state.path / "stops" / f"{text}.json", record)
                    state.save()
                    body = f"依頼 `{text}` を停止しました。同じjobの自動探索も停止します。別の未停止依頼があれば、その依頼分は続きます。"
        except Exception as e:
            body = "判定不能 / 入力を確認してください: " + str(e)
            record["error"] = str(e)
            record["error_type"] = type(e).__name__
        body += f"\n\n対象サイクル: `{cycle_name}` / 結果SHA: `{result_sha}` / 対象コード: `{code_sha}` / 元コメント: {cid}"
        record["reply_body"] = body
        atomic_json(receipt, record)
        state.save()
        reply_saved(api, state, "reply-" + cid, body, comments)


def worker(api, state, cycle: Path, seconds=18000, autonomous=False):
    buffered = BufferedState(state)
    try:
        return run_worker(api, buffered, cycle, seconds, autonomous)
    finally:
        buffered.flush()


def run_worker(api, state, cycle: Path, seconds=18000, autonomous=False):
    deadline = time.monotonic() + seconds
    last_report = time.monotonic()
    current_inputs = snapshot(ROOT, cycle)
    if autonomous:
        prepare(cycle / "outputs", state.path / "known")
        prepare_feedback(ROOT, cycle, state.path)
        safe_observe(state.path)
        state.save()
    while time.monotonic() < deadline:
        state.sync()
        requests = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((state.path / "requests").glob("*.json"))]
        active = [r for r in requests if not (state.path / "stops" / f"{r['comment_id']}.json").exists()]
        by_job = {r["job"]: r for r in active}
        automatic = next_request(cycle, current_inputs, state.path) if autonomous else None
        if automatic:
            by_job.setdefault(automatic["job"], automatic)
        progressed = False
        for job, request in by_job.items():
            if time.monotonic() >= deadline:
                break
            path = state.path / "jobs" / job / "state.json"
            saved = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            if saved and saved["status"] in ("completed", "bounded", "blocked", "error"):
                continue
            if saved:
                saved = read_state(path)
            if request["inputs"] != current_inputs:
                saved = saved or {"cursor": 0, "candidates": [], "results": [], "bounded": False}
                saved.update(status="blocked", error="入力・判定コードが更新されました。同じデータとして継続せず、新しい依頼で再開してください。")
            else:
                try:
                    explorer = Explorer(cycle, request["plan"])
                    saved = saved or explorer.initial(current_inputs)
                    if not path.exists():
                        save_state(path, saved)
                        state.save()
                    explorer.advance(saved, seconds=min(30, max(0, deadline - time.monotonic())), max_steps=100)
                except Exception as e:
                    saved = saved or {"cursor": 0, "candidates": [], "results": [], "bounded": False}
                    saved.update(status="error", error=f"{type(e).__name__}: {e}")
            saved["updated_at"] = datetime.now(timezone.utc).isoformat()
            saved["origin"] = request.get("origin", "comment")
            save_state(path, saved)
            report = path.with_name("report.md")
            report.write_text(summary(saved) + "\n", encoding="utf-8")
            if autonomous and (time.monotonic() - last_report >= 300 or saved["status"] in ("completed", "bounded", "blocked", "error")):
                safe_observe(state.path)
                last_report = time.monotonic()
            state.save()
            progressed = True
        if not progressed:
            break
    if api:
        notify_run(api, state)


def notify_run(api, state):
    """One durable completion bundle per run; resume prior bundles verbatim."""
    bundles = [json.loads(p.read_text()) for p in sorted((state.path / "notifications").glob("*.json"))]
    assigned = {cid for bundle in bundles for cid in bundle["comments"]}
    finished = []
    for p in sorted((state.path / "requests").glob("*.json")):
        request = json.loads(p.read_text())
        if request["comment_id"] in assigned or (state.path / "stops" / f"{request['comment_id']}.json").exists():
            continue
        path = state.path / "jobs" / request["job"] / "state.json"
        if path.exists():
            saved = json.loads(path.read_text())
            if saved["status"] in ("completed", "bounded", "blocked", "error"):
                finished.append((request, saved))
    finished = finished[:20]  # Bound comment size; the next run collects remaining results.
    if finished:
        ids = [r["comment_id"] for r, _ in finished]
        key = "run-results-" + digest(ids)[:24]
        run_id = os.environ.get("GITHUB_RUN_ID", "local")
        body = f"探索結果まとめ / run `{run_id}` / {len(finished)}依頼\n"
        repo = os.environ.get("GITHUB_REPOSITORY")
        if repo and run_id.isdigit():
            body += f"詳細とartifact: https://github.com/{repo}/actions/runs/{run_id}\n"
        for request, saved in finished:
            body += f"\n依頼 `{request['comment_id']}` / 結果ID: result-{request['comment_id']}\n" + summary(saved)[:1800] + "\n"
        bundle = {"key": key, "comments": ids, "body": body, "run_id": run_id, "sent": False}
        atomic_json(state.path / "notifications" / f"{key}.json", bundle)
        state.save()
        bundles.append(bundle)
    pending = [bundle for bundle in bundles if not bundle["sent"]]
    if not pending:
        return
    state.flush()  # Bundle and results must be durable before any POST.
    try:
        comments = api.comments()  # One shared listing, including retry markers.
    except (urllib.error.URLError, OSError, http.client.HTTPException, json.JSONDecodeError) as e:
        atomic_json(state.path / "pending-replies/worker-comments.json", {"error": f"{type(e).__name__}: {e}"})
        state.save()
        return
    (state.path / "pending-replies/worker-comments.json").unlink(missing_ok=True)
    state.save()
    for bundle in pending:
        if reply_saved(api, state, bundle["key"], bundle["body"], comments):
            bundle["sent"] = True
            atomic_json(state.path / "notifications" / f"{bundle['key']}.json", bundle)
            state.save()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("intake", "worker"))
    ap.add_argument("--autonomous", action="store_true", default=os.environ.get("AOI_RESEARCH_ENABLED") == "1", help="登録済みの式から依頼なしで探索する")
    ap.add_argument("--issue", type=int, default=os.environ.get("AOI_INBOX_ISSUE"))
    ap.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--seconds", type=int, default=18000)
    ap.add_argument("--state-dir", type=Path, default=ROOT / ".research-state")
    args = ap.parse_args(argv)
    if not args.repository or (not args.issue and args.mode == "intake"):
        ap.error("--issue / AOI_INBOX_ISSUE と --repository / GITHUB_REPOSITORY が必要")
    if not 0 < args.seconds <= 18000:
        ap.error("seconds は1〜18000")
    api = GitHub(args.repository, args.issue) if args.issue else None
    cycle_name = os.environ.get("AOI_RESEARCH_CYCLE")
    result_ref = os.environ.get("AOI_RESULTS_REF")
    if not cycle_name or not result_ref:
        ap.error("AOI_RESEARCH_CYCLE / AOI_RESULTS_REF が必要")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", cycle_name) or not re.fullmatch(r"[A-Za-z0-9._/-]+", result_ref) or ".." in result_ref:
        ap.error("AOI_RESEARCH_CYCLE / AOI_RESULTS_REF が不正")
    cycle = ROOT / ".aoi-results" / cycle_name
    result_sha = os.environ.get("AOI_RESULTS_SHA", "")
    try:
        state = State(ROOT, args.state_dir.resolve(), create=args.mode == "intake" or args.autonomous)
    except FileNotFoundError:
        print("受付未起動。処理する依頼はありません。")
        return 0
    if args.mode == "intake":
        intake(api, state, cycle, git(ROOT, "rev-parse", "HEAD").stdout.strip(), os.environ.get("AOI_USE_LOCAL_LLM") == "1", cycle_name, result_sha)
    else:
        worker(api, state, cycle, args.seconds, autonomous=args.autonomous)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
