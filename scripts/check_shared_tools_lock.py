#!/usr/bin/env python3
"""shared-tools.lock.json の sha256 を、Aoi に置いた共有ツールのバイトと照合する。

schema は vendor-lock/1。各エントリは path、sha256、source（Aoi）、実際に使っている子（consumers、空も可）。
子の main の SHA は lock に書かない。--resolve-consumers のときだけ git ls-remote で
取り、child-heads.json の repository_id と GitHub の id を照合して、SHA を出す。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_NAME = "shared-tools.lock.json"
SOURCE = "myon-bioinformatics/Aoi"
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
ENTRY_KEYS = {"path", "sha256", "source", "consumers"}


def _git_env() -> dict:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    return env


def load_lock(root: Path) -> dict:
    return json.loads((root / LOCK_NAME).read_text(encoding="utf-8"))


def problems(root: Path, lock: dict | None = None) -> list[str]:
    """lock とファイルの不一致。空なら一致。"""
    found: list[str] = []
    if lock is None:
        try:
            lock = load_lock(root)
        except (OSError, json.JSONDecodeError) as exc:
            return [f"{LOCK_NAME} を読めない: {exc}"]
    if not isinstance(lock, dict) or lock.get("schema") != "vendor-lock/1" or set(lock) != {"schema", "files"}:
        return [f"{LOCK_NAME} は vendor-lock/1 の schema と files だけ"]
    files = lock["files"]
    if not isinstance(files, list) or not files:
        return [f"{LOCK_NAME} の files が空"]
    heads_path = root / "child-heads.json"
    try:
        heads = json.loads(heads_path.read_text(encoding="utf-8"))["heads"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        return [f"child-heads.json を読めない: {exc}"]
    paths = []
    for index, entry in enumerate(files):
        where = f"files[{index}]"
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            found.append(f"{where} のキーは path, sha256, source, consumers")
            continue
        path = entry["path"]
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in path.split("/"):
            found.append(f"{where} の path が相対パスでない")
            continue
        paths.append(path)
        if entry["source"] != SOURCE:
            found.append(f"{path}: source は {SOURCE}")
        consumers = entry["consumers"]
        if (not isinstance(consumers, list) or len(set(consumers)) != len(consumers)
                or not set(consumers) <= set(heads) or consumers != sorted(consumers)):
            found.append(f"{path}: consumers は child-heads.json の子から重複なしで昇順")
        sha = entry["sha256"]
        if not isinstance(sha, str) or not HEX64.fullmatch(sha):
            found.append(f"{path}: sha256 は 64 桁の hex")
            continue
        file = root / path
        if not file.is_file():
            found.append(f"{path}: ファイルがない")
            continue
        got = hashlib.sha256(file.read_bytes()).hexdigest()
        if got != sha:
            found.append(f"{path}: sha256 が違う {got} != {sha}")
    if paths != sorted(paths):
        found.append("files は path の昇順")
    if len(paths) != len(set(paths)):
        found.append("path が重複している")
    return found


def _ls_remote(repository: str) -> str:
    url = f"https://github.com/{repository}.git"
    out = subprocess.run(
        ["git", "ls-remote", url, "refs/heads/main"],
        capture_output=True, text=True, timeout=120, env=_git_env(), stdin=subprocess.DEVNULL,
    )
    if out.returncode:
        raise RuntimeError(f"git ls-remote {repository} failed: {out.stderr.strip()[:200]}")
    for line in out.stdout.splitlines():
        sha, ref = line.split()
        if ref == "refs/heads/main" and HEX40.fullmatch(sha):
            return sha
    raise RuntimeError(f"git ls-remote {repository} に refs/heads/main がない")


def _repository_id(repository: str) -> tuple[int, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "aoi-shared-tools"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(f"https://api.github.com/repos/{repository}", headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    return int(data["id"]), str(data.get("full_name", ""))


def resolve_consumers(root: Path) -> str:
    """子の最新 main を解決し、repository id を照合して Markdown を返す。"""
    lock = load_lock(root)
    heads = json.loads((root / "child-heads.json").read_text(encoding="utf-8"))["heads"]
    consumers = sorted({name for entry in lock["files"] for name in entry["consumers"]})
    checkout = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, env=_git_env(),
    ).stdout.strip()
    lines = ["## Shared tool consumers", "", f"Aoi checkout `{checkout}`", ""]
    for name in consumers:
        expected = heads[name]["repository_id"]
        live_id, full_name = _repository_id(name)
        if live_id != expected or full_name.lower() != name.lower():
            raise SystemExit(f"repository id mismatch: {name} live={live_id} {full_name} expected={expected}")
        sha = _ls_remote(name)
        lines.append(f"- `{name}` `{sha}` (repository id `{expected}`)")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--warn", action="store_true", help="不一致を警告にして終了コード 0")
    parser.add_argument("--resolve-consumers", action="store_true", help="子の main を ls-remote で解決する")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.resolve_consumers:
        print(resolve_consumers(root))
        return 0
    found = problems(root)
    if not found:
        print(f"{LOCK_NAME} ok")
        return 0
    stream = sys.stderr
    for item in found:
        if args.warn:
            print(f"::warning::{item}", file=stream)
        else:
            print(item, file=stream)
    if args.warn:
        print(f"{LOCK_NAME} の不一致は pull request では警告", file=stream)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
