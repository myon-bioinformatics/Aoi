#!/usr/bin/env python3
"""vendor.lock.json の sha256 を、vendor/aoi の写しと照合する。

schema は vendor-lock/1。古いエントリは path、sha256、source（myon-bioinformatics/Aoi）。
driver のエントリは repository、ref、commit、source、destination、blob_sha、sha256。
source は Aoi の中の相対パスで、写しは vendor/aoi/<source> に置く。
--aoi を渡したときは、その checkout の同じ path のバイトとも比べる。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_NAME = "vendor.lock.json"
SOURCE = "myon-bioinformatics/Aoi"
VENDOR_DIR = Path("vendor") / "aoi"
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")
ENTRY_KEYS = {"path", "sha256", "source"}
DRIVER_KEYS = {"repository", "ref", "commit", "source", "destination", "blob_sha", "sha256"}


def load_lock(root: Path) -> dict:
    return json.loads((root / LOCK_NAME).read_text(encoding="utf-8"))


def _rel_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value or value.startswith(("/", "\\")):
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _compare_bytes(root: Path, rel: Path, path: str, sha: str, aoi_root: Path | None) -> list[str]:
    found: list[str] = []
    vendored = root / VENDOR_DIR / rel
    if not vendored.is_file():
        return [f"{path}: vendor/aoi にファイルがない"]
    got = hashlib.sha256(vendored.read_bytes()).hexdigest()
    if got != sha:
        found.append(f"{path}: sha256 が違う {got} != {sha}")
    if aoi_root is None:
        return found
    upstream = aoi_root / rel
    if not upstream.is_file():
        found.append(f"{path}: Aoi にファイルがない")
        return found
    upstream_sha = hashlib.sha256(upstream.read_bytes()).hexdigest()
    if upstream_sha != sha:
        found.append(f"{path}: Aoi の sha256 が違う {upstream_sha} != {sha}")
    return found


def problems(root: Path, aoi_root: Path | None = None, lock: dict | None = None) -> list[str]:
    """lock と写し（と、渡した Aoi）の不一致。空なら一致。"""
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
    paths: list[str] = []
    for index, entry in enumerate(files):
        where = f"files[{index}]"
        if not isinstance(entry, dict) or set(entry) not in (ENTRY_KEYS, DRIVER_KEYS):
            found.append(
                f"{where} のキーは path, sha256, source"
                " か repository, ref, commit, source, destination, blob_sha, sha256"
            )
            continue
        if set(entry) == ENTRY_KEYS:
            rel = _rel_path(entry["path"])
            if rel is None:
                found.append(f"{where} の path が相対パスでない")
                continue
            path = rel.as_posix()
            paths.append(path)
            if entry["source"] != SOURCE:
                found.append(f"{path}: source は {SOURCE}")
            sha = entry["sha256"]
            if not isinstance(sha, str) or not HEX64.fullmatch(sha):
                found.append(f"{path}: sha256 は 64 桁の hex")
                continue
            found.extend(_compare_bytes(root, rel, path, sha, aoi_root))
            continue
        rel = _rel_path(entry["source"])
        if rel is None:
            found.append(f"{where} の source が相対パスでない")
            continue
        path = rel.as_posix()
        paths.append(path)
        if entry["repository"] != SOURCE:
            found.append(f"{path}: repository は {SOURCE}")
        destination = entry["destination"]
        expected = (VENDOR_DIR / rel).as_posix()
        if destination != expected:
            found.append(f"{path}: destination は {expected}")
        ref = entry["ref"]
        commit = entry["commit"]
        if not isinstance(ref, str) or not HEX40.fullmatch(ref):
            found.append(f"{path}: ref は 40 桁の hex")
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            found.append(f"{path}: commit は 40 桁の hex")
        elif isinstance(ref, str) and ref != commit:
            found.append(f"{path}: ref と commit が違う")
        blob = entry["blob_sha"]
        if not isinstance(blob, str) or not HEX40.fullmatch(blob):
            found.append(f"{path}: blob_sha は 40 桁の hex")
            blob = None
        sha = entry["sha256"]
        if not isinstance(sha, str) or not HEX64.fullmatch(sha):
            found.append(f"{path}: sha256 は 64 桁の hex")
            continue
        vendored = root / VENDOR_DIR / rel
        if not vendored.is_file():
            found.append(f"{path}: vendor/aoi にファイルがない")
            continue
        data = vendored.read_bytes()
        got = hashlib.sha256(data).hexdigest()
        if got != sha:
            found.append(f"{path}: sha256 が違う {got} != {sha}")
        if blob is not None and git_blob_sha(data) != blob:
            found.append(f"{path}: blob_sha が違う {git_blob_sha(data)} != {blob}")
        if aoi_root is None:
            continue
        upstream = aoi_root / rel
        if not upstream.is_file():
            found.append(f"{path}: Aoi にファイルがない")
            continue
        upstream_sha = hashlib.sha256(upstream.read_bytes()).hexdigest()
        if upstream_sha != sha:
            found.append(f"{path}: Aoi の sha256 が違う {upstream_sha} != {sha}")
    if paths != sorted(paths):
        found.append("files は path の昇順")
    if len(paths) != len(set(paths)):
        found.append("path が重複している")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--aoi", type=Path, default=None, help="照合する Aoi の checkout")
    parser.add_argument("--warn", action="store_true", help="不一致を警告にして終了コード 0")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    aoi_root = args.aoi.resolve() if args.aoi is not None else None
    found = problems(root, aoi_root)
    if not found:
        print(f"{LOCK_NAME} ok")
        return 0
    for item in found:
        if args.warn:
            print(f"::warning::{item}", file=sys.stderr)
        else:
            print(item, file=sys.stderr)
    if args.warn:
        print(f"{LOCK_NAME} の不一致は pull request では警告", file=sys.stderr)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
