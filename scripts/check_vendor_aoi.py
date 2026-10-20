#!/usr/bin/env python3
"""vendor/aoi の共有ツールを shared-tools.lock.json と、任意で Aoi の原本と照合する。

schema は vendor-lock/1。各エントリは path、sha256、source（myon-bioinformatics/Aoi）。
path はこのリポジトリの vendor/aoi/ 以下。--aoi を渡すと、vendor/aoi/ を外した
同じ相対パスの原本とバイトを比べる。原本の SHA は lock に書かない。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_NAME = "shared-tools.lock.json"
PREFIX = "vendor/aoi/"
SOURCE = "myon-bioinformatics/Aoi"
ENTRY_KEYS = {"path", "sha256", "source"}
HEX64 = re.compile(r"[0-9a-f]{64}")


def load_lock(root: Path) -> dict:
    return json.loads((root / LOCK_NAME).read_text(encoding="utf-8"))


def _relative(path: str) -> str | None:
    parts = path.split("/")
    if not path or path.startswith("/") or ".." in parts or "" in parts:
        return None
    if not path.startswith(PREFIX) or path == PREFIX:
        return None
    return path[len(PREFIX):]


def problems(root: Path, lock: dict | None = None, aoi: Path | None = None) -> list[str]:
    """lock と vendor/aoi、および任意の Aoi checkout の不一致。空なら一致。"""
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
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            found.append(f"{where} のキーは path, sha256, source")
            continue
        path = entry["path"]
        if not isinstance(path, str) or _relative(path) is None:
            found.append(f"{where} の path は {PREFIX} 以下の相対パス")
            continue
        paths.append(path)
        if entry["source"] != SOURCE:
            found.append(f"{path}: source は {SOURCE}")
        sha = entry["sha256"]
        if not isinstance(sha, str) or HEX64.fullmatch(sha) is None:
            found.append(f"{path}: sha256 は 64 桁の hex")
            continue
        file = root / path
        if not file.is_file():
            found.append(f"{path}: ファイルがない")
            continue
        raw = file.read_bytes()
        got = hashlib.sha256(raw).hexdigest()
        if got != sha:
            found.append(f"{path}: sha256 が違う {got} != {sha}")
        if aoi is None:
            continue
        upstream = aoi / _relative(path)
        if not upstream.is_file():
            found.append(f"{path}: Aoi に {_relative(path)} がない")
            continue
        if upstream.read_bytes() != raw:
            found.append(f"{path}: Aoi の {_relative(path)} とバイトが違う")
    if paths != sorted(paths):
        found.append("files は path の昇順")
    if len(paths) != len(set(paths)):
        found.append("path が重複している")
    vendor = root / "vendor" / "aoi"
    if vendor.is_dir():
        present = sorted(
            item.relative_to(root).as_posix()
            for item in vendor.rglob("*")
            if item.is_file()
            and "__pycache__" not in item.relative_to(vendor).parts
            and item.suffix != ".pyc"
        )
        if present != sorted(set(paths)):
            found.append("vendor/aoi のファイルと lock の path が違う")
    else:
        found.append("vendor/aoi がない")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--aoi", type=Path, help="照合する Aoi の checkout")
    parser.add_argument("--warn", action="store_true", help="不一致を警告にして終了コード 0")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    aoi = args.aoi.resolve() if args.aoi is not None else None
    found = problems(root, aoi=aoi)
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
