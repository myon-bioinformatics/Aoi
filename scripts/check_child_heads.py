"""Aoi の子リポジトリ（subtree で切り出したもの）の登録と差分を確かめる（stdlib のみ、書き込みなし）。

- child-heads.json（child-heads/1）の形を確かめる。sha は書かない（履歴から導く）。
- 子の main の第一親をたどり、Aoi の subtree_prefix と同じ tree を持つ最新のコミットを「同期済みの sha」（synced_sha）にする。
- 子の main の今の SHA（live_sha）と synced_sha のずれ（drift）を出す。
- 同じ tree の状態が子の履歴になければ、子の main の tree との差分を、blob と mode で出す。
  子は prefix の純粋な subtree（除外するファイルはない）。not_in_parent / child_preamble は受け付けない。
- mirrored_from_parent（prefix の下のパス → Aoi の原本のパス）は、Aoi の中で blob と mode が原本と
  同じかを確かめ、違えば失敗にする（共有するルートのファイルを子に通常のファイルとして置くとき）。
- Aoi と subtree 子の間では vendor-consumers.json を置かない。置かれていたら失敗する。共有ツールの shared-tools.lock.json はこの検査の対象外。
- 子ごとの取得の失敗（リポジトリがない、タイムアウトなど）は、その子の error にして次の子へ進む。

既定では drift と差分は報告のみ。--fail-on-drift / --fail-on-diff で終了コード 1 にする。
Git の取得は一時的な bare リポジトリに行い、この checkout には書かない。
"""
from __future__ import annotations

import argparse
import json
import re
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
URL_TEMPLATE = "https://github.com/{repository}.git"
UNSUPPORTED = ("not_in_parent", "child_preamble")
LEGACY_VENDOR_CONSUMERS = "vendor-consumers.json"


# fetch-guard: ls-remote/fetch of child repositories never wait for a prompt.
def _git_env() -> dict:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"}
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    return env


def _git_bytes(*args, cwd=None, timeout=300) -> bytes:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, timeout=timeout, env=_git_env(),
                         stdin=subprocess.DEVNULL)
    if out.returncode:
        stderr = out.stderr.decode("utf-8", "replace").strip()[:400]
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {stderr}")
    return out.stdout


def _git(*args, cwd=None, timeout=300) -> str:
    return _git_bytes(*args, cwd=cwd, timeout=timeout).decode("utf-8")


def validate_heads(doc: dict) -> dict:
    if not isinstance(doc, dict) or set(doc) != {"schema", "ref", "heads"} or doc["schema"] != "child-heads/1":
        raise ValueError("expected child-heads/1")
    if not isinstance(doc["ref"], str) or not doc["ref"]:
        raise ValueError("child-heads ref must be a nonempty string")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in doc["ref"]):
        raise ValueError("child-heads ref must not contain control characters")
    if not isinstance(doc["heads"], dict) or not doc["heads"]:
        raise ValueError("child heads must be a nonempty object")
    for name, entry in doc["heads"].items():
        if not REPO.fullmatch(name):
            raise ValueError(f"expected owner/repository: {name}")
        if not isinstance(entry, dict):
            raise ValueError(f"{name}: entry must be an object")
        if "sha" in entry:
            raise ValueError(f"{name}: sha is derived from the child history; remove it")
        if type(entry.get("repository_id")) is not int or entry["repository_id"] < 1:
            raise ValueError(f"{name}: repository_id must be a positive int")
        optional = entry.get("optional")
        if not isinstance(optional, dict):
            raise ValueError(f"{name}: optional must be an object")
        prefix = optional.get("subtree_prefix")
        if not isinstance(prefix, str) or not prefix or prefix.startswith("/") or ".." in prefix.split("/"):
            raise ValueError(f"{name}: optional.subtree_prefix is required")
        for key in UNSUPPORTED:
            if key in optional:
                raise ValueError(f"{name}: optional.{key} is not supported (the child is a pure subtree)")
        mirrors = optional.get("mirrored_from_parent", {})
        if not isinstance(mirrors, dict) or not all(isinstance(k, str) and k and isinstance(v, str) and v
                                                    for k, v in mirrors.items()):
            raise ValueError(f"{name}: optional.mirrored_from_parent must map paths to paths")
    return doc


def _reject_legacy_vendor_consumers(root: Path) -> None:
    if (root / LEGACY_VENDOR_CONSUMERS).exists():
        raise ValueError(
            f"{LEGACY_VENDOR_CONSUMERS} is not used between Aoi and subtree children; remove the file"
        )


def _tree(repo: Path, rev: str) -> dict[str, tuple[str, str]]:
    """path -> (mode, object)。-z で NUL 区切り（改行やタブを含むパスもそのまま）。"""
    rows = {}
    for record in _git_bytes("ls-tree", "-r", "-z", rev, cwd=repo).split(b"\0"):
        if record:
            meta, path = record.split(b"\t", 1)
            mode, _kind, obj = meta.decode("ascii").split(" ")
            rows[path.decode("utf-8", "surrogateescape")] = (mode, obj)
    return rows


def _mirrors(whole: dict, prefix: str, mirrors: dict) -> dict[str, str]:
    result = {}
    for path, original in sorted(mirrors.items()):
        copy, source = whole.get(f"{prefix}/{path}"), whole.get(original)
        if source is None:
            result[path] = "original_missing"
        elif copy is None:
            result[path] = "copy_missing"
        else:
            result[path] = "identical" if copy == source else "different"
    return result


def _synced_sha(url: str, ref: str, tree_id: str | None) -> str | None:
    # 子の ref の第一親をたどり、tree が tree_id と同じ最新のコミットを返す（なければ None）。
    # コミットだけ取る（--filter=tree:0）。%T はコミットに書いてあるので tree は要らない。
    with tempfile.TemporaryDirectory() as tmp:
        bare = Path(tmp)
        _git("init", "-q", "--bare", str(bare))
        _git("fetch", "-q", "--no-tags", "--filter=tree:0", url, f"refs/heads/{ref}", cwd=bare)
        rows = (line.split() for line in _git("log", "--first-parent", "--format=%H %T", "FETCH_HEAD", cwd=bare).splitlines())
        return next((commit for commit, tree in rows if tree == tree_id), None)


def _child(name: str, parent_tree: dict, tree_id: str | None, *, ref: str, url_template: str, row: dict) -> None:
    url = url_template.format(repository=name)
    live = _git("ls-remote", url, f"refs/heads/{ref}", timeout=120).split()
    row["live_sha"] = live[0] if live else None
    if not live:
        raise RuntimeError(f"ref {ref} not found")
    row["synced_sha"] = _synced_sha(url, ref, tree_id)
    row["drift"] = row["synced_sha"] not in (None, row["live_sha"])  # 追いついていない状態があるときだけ drift
    if row["synced_sha"]:
        row["diff"] = {"only_in_parent": [], "only_in_child": [], "different": []}
    else:  # 同じ tree の状態が子の履歴にない: 子の main との差分を出す
        with tempfile.TemporaryDirectory() as tmp:
            bare = Path(tmp)
            _git("init", "-q", "--bare", str(bare))
            _git("fetch", "-q", "--depth=1", url, row["live_sha"], cwd=bare)
            child_tree = _tree(bare, row["live_sha"])
        row["diff"] = {
            "only_in_parent": sorted(parent_tree.keys() - child_tree.keys()),
            "only_in_child": sorted(child_tree.keys() - parent_tree.keys()),
            "different": sorted(p for p in parent_tree.keys() & child_tree.keys() if parent_tree[p] != child_tree[p]),
        }
    row["identical"] = not any(row["diff"].values())


def check(root: Path, heads: dict, *, network: bool, url_template: str = URL_TEMPLATE) -> dict:
    report = {"schema": "aoi-child-heads-check/1", "parent": _git("rev-parse", "HEAD", cwd=root).strip(), "children": []}
    whole = _tree(root, "HEAD")
    for name, entry in sorted(heads["heads"].items()):
        optional = entry["optional"]
        prefix = optional["subtree_prefix"]
        row = {"repository": name, "prefix": prefix}
        parent_tree = {p[len(prefix) + 1:]: b for p, b in whole.items() if p.startswith(prefix + "/")}
        tree_id = _git("rev-parse", f"HEAD:{prefix}", cwd=root).strip() if parent_tree else None
        row["mirrors"] = _mirrors(whole, prefix, optional.get("mirrored_from_parent", {}))
        if not parent_tree:
            row["error"] = "prefix_not_found"
        if network:
            try:
                _child(name, parent_tree, tree_id, ref=heads["ref"], url_template=url_template, row=row)
            except (RuntimeError, subprocess.SubprocessError, OSError) as error:
                row["error"] = "fetch_failed: " + str(error)
        report["children"].append(row)
    return report


def failed(report: dict, *, fail_on_drift: bool, fail_on_diff: bool) -> bool:
    rows = report["children"]
    bad = any("error" in c for c in rows)
    bad |= any(state != "identical" for c in rows for state in c["mirrors"].values())
    bad |= fail_on_drift and any(c.get("drift") for c in rows)
    bad |= fail_on_diff and any(c.get("identical") is False for c in rows)
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--heads", default="child-heads.json")
    ap.add_argument("--offline", action="store_true", help="形と Aoi 側だけ確かめる（GitHub に取りに行かない）")
    ap.add_argument("--url-template", default=URL_TEMPLATE, help="子の URL。{repository} を owner/repository にする")
    ap.add_argument("--fail-on-drift", action="store_true")
    ap.add_argument("--fail-on-diff", action="store_true")
    ap.add_argument("--print-synced", metavar="OWNER/REPO",
                    help="その子の synced_sha（Aoi の prefix と同じ tree の最新コミット）だけを出す")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    try:
        _reject_legacy_vendor_consumers(root)
        heads = validate_heads(json.loads((root / args.heads).read_text(encoding="utf-8")))
        report = check(root, heads, network=not args.offline, url_template=args.url_template)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print("check-child-heads: " + str(error), file=sys.stderr)
        return 2
    if args.print_synced:
        row = next((c for c in report["children"] if c["repository"] == args.print_synced), {})
        if not row.get("synced_sha"):
            print(f"check-child-heads: no synced sha for {args.print_synced}: {row.get('error', 'no matching tree')}",
                  file=sys.stderr)
            return 1
        print(row["synced_sha"])
        return 0
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failed(report, fail_on_drift=args.fail_on_drift, fail_on_diff=args.fail_on_diff) else 0


if __name__ == "__main__":
    raise SystemExit(main())
