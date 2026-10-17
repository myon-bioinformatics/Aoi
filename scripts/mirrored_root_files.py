"""子の prefix の下に置いた「Aoi 直下のファイルのコピー」が、原本と同じ git blob かを確かめる（stdlib のみ、書き込みなし）。

例: ``queryu/aoi_paths.py`` と ``pythdragoras/aoi_paths.py`` は、Aoi 直下の ``aoi_paths.py`` と同じ blob であること。
子を Aoi に subtree add する前はコピーがまだないので、その組は ``absent`` として飛ばす（失敗にしない）。

組は child-heads.json の子ごとに、``optional.mirrored_from_parent``（prefix の下のパス → Aoi の原本のパス）と、
既定の ``aoi_paths.py`` → ``aoi_paths.py`` を合わせたもの。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

DEFAULT_MIRRORS = {"aoi_paths.py": "aoi_paths.py"}


def git_blob(path: Path) -> str:
    """作業ツリーのファイルの git blob SHA-1（``git hash-object`` と同じ。フィルタなし）。"""
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _executable(path: Path) -> bool:
    return bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def compare(root: Path, copy: str, original: str) -> dict:
    """``root/copy`` と ``root/original`` を比べる。state は identical / different / absent / original_missing。"""
    copy_path, original_path = root / copy, root / original
    row = {"copy": copy, "original": original}
    if not original_path.is_file():
        row["state"] = "original_missing"
        return row
    row["original_blob"] = git_blob(original_path)
    if not copy_path.is_file():
        row["state"] = "absent"
        return row
    row["copy_blob"] = git_blob(copy_path)
    same = row["copy_blob"] == row["original_blob"]
    if os.name != "nt":  # Windows の作業ツリーは実行ビットを持たない
        same = same and _executable(copy_path) == _executable(original_path)
    row["state"] = "identical" if same else "different"
    return row


def mirror_pairs(heads: dict) -> list[tuple[str, str, str]]:
    """child-heads/1 から (子, prefix の下のコピーのパス, Aoi の原本のパス) の一覧を作る。"""
    pairs = []
    for name, entry in sorted(heads["heads"].items()):
        optional = entry.get("optional") or {}
        prefix = optional["subtree_prefix"].strip("/")
        mirrors = {**DEFAULT_MIRRORS, **(optional.get("mirrored_from_parent") or {})}
        for path, original in sorted(mirrors.items()):
            pairs.append((name, f"{prefix}/{path}", original))
    return pairs


def check(root: Path, heads: dict) -> list[dict]:
    return [{"repository": name, **compare(root, copy, original)} for name, copy, original in mirror_pairs(heads)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--heads", default="child-heads.json")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    rows = check(root, json.loads((root / args.heads).read_text(encoding="utf-8")))
    print(json.dumps({"schema": "aoi-mirrored-root-files/1", "files": rows}, ensure_ascii=False, indent=2))
    return 1 if any(r["state"] in ("different", "original_missing") for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
