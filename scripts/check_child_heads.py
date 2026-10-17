"""Aoi の子リポジトリ（subtree で切り出したもの）の登録と差分を確かめる（stdlib のみ、書き込みなし）。

- child-heads.json（child-heads/1）と vendor-consumers.json（vendor-consumers/1）の形を確かめる。
  --vendor-tools に親 myon-bioinformatics の checkout（vendor_sync.py / vendor_consumers.py）を渡すと、
  親と同じ validator で確かめ、子の vendor.lock.json と登録の topology も比べる。
- 子の main の今の SHA と、登録した SHA のずれ（drift）を出す。
- 登録した SHA の子の tree と、Aoi の subtree_prefix の tree の差分を出す（not_in_parent は除く）。

既定では drift と差分は報告のみ。--fail-on-drift / --fail-on-diff で終了コード 1 にする。
Git の取得は一時的な bare リポジトリに行い、この checkout には書かない。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def _git(*args, cwd=None, timeout=300) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if out.returncode:
        raise RuntimeError(f"git {' '.join(args[:2])} failed: {out.stderr.strip()[:400]}")
    return out.stdout


def validate_heads(doc: dict) -> dict:
    if not isinstance(doc, dict) or set(doc) != {"schema", "ref", "heads"} or doc["schema"] != "child-heads/1":
        raise ValueError("expected child-heads/1")
    if not isinstance(doc["heads"], dict) or not doc["heads"]:
        raise ValueError("child heads must be a nonempty object")
    for name, entry in doc["heads"].items():
        if not REPO.fullmatch(name):
            raise ValueError(f"expected owner/repository: {name}")
        if not isinstance(entry, dict) or not HEX40.fullmatch(str(entry.get("sha"))):
            raise ValueError(f"{name}: sha must be 40 hex")
        if type(entry.get("repository_id")) is not int or entry["repository_id"] < 1:
            raise ValueError(f"{name}: repository_id must be a positive int")
        optional = entry.get("optional") or {}
        prefix = optional.get("subtree_prefix")
        if not isinstance(prefix, str) or not prefix or prefix.startswith("/") or ".." in prefix.split("/"):
            raise ValueError(f"{name}: optional.subtree_prefix is required")
        skip = optional.get("not_in_parent", [])
        if not isinstance(skip, list) or not all(isinstance(s, str) and s for s in skip):
            raise ValueError(f"{name}: optional.not_in_parent must be a list of paths")
    return doc


def validate_consumers(doc: dict) -> dict:
    if not isinstance(doc, dict) or set(doc) != {"schema", "consumers"} or doc["schema"] != "vendor-consumers/1":
        raise ValueError("expected vendor-consumers/1")
    for consumer in doc["consumers"]:
        if consumer.get("state") not in ("locked", "legacy"):
            raise ValueError("consumer state must be locked or legacy")
        for entry in consumer.get("entries", []):
            if set(entry) != {"repository", "source", "destination"}:
                raise ValueError("invalid consumer entry fields")
    return doc


def _skipped(path: str, skip: list[str]) -> bool:
    return any(path == s.rstrip("/") or (s.endswith("/") and path.startswith(s)) for s in skip)


def _tree(repo: Path, rev: str) -> dict[str, str]:
    rows = {}
    for line in _git("ls-tree", "-r", rev, cwd=repo).splitlines():
        meta, path = line.split("\t", 1)
        rows[path] = meta.split()[2]
    return rows


def check(root: Path, heads: dict, consumers: dict, *, network: bool, tools: Path | None) -> dict:
    report = {"schema": "aoi-child-heads-check/1", "parent": _git("rev-parse", "HEAD", cwd=root).strip(), "children": []}
    vc = vs = None
    if tools is not None:
        sys.path.insert(0, str(tools))
        import vendor_consumers as vc  # noqa: F811
        import vendor_sync as vs  # noqa: F811
        vs.validate_child_heads(heads)
        vc.validate(consumers)
    for name, entry in sorted(heads["heads"].items()):
        optional = entry.get("optional") or {}
        prefix, skip = optional["subtree_prefix"], optional.get("not_in_parent", [])
        row = {"repository": name, "recorded_sha": entry["sha"], "prefix": prefix}
        parent_tree = {p[len(prefix) + 1:]: b for p, b in _tree(root, "HEAD").items() if p.startswith(prefix + "/")}
        if not parent_tree:
            row["error"] = "prefix_not_found"
        if network:
            url = f"https://github.com/{name}.git"
            live = _git("ls-remote", url, f"refs/heads/{heads['ref']}", timeout=120).split()
            row["live_sha"] = live[0] if live else None
            row["drift"] = row["live_sha"] != entry["sha"]
            with tempfile.TemporaryDirectory() as tmp:
                bare = Path(tmp)
                _git("init", "-q", "--bare", str(bare))
                _git("fetch", "-q", "--depth=1", url, entry["sha"], cwd=bare)
                child_tree = _tree(bare, entry["sha"])
                lock_blob = child_tree.get("vendor.lock.json")
                lock = json.loads(_git("cat-file", "blob", lock_blob, cwd=bare)) if lock_blob else None
            child_cmp = {p: b for p, b in child_tree.items() if not _skipped(p, skip)}
            row["diff"] = {
                "only_in_parent": sorted(parent_tree.keys() - child_cmp.keys()),
                "only_in_child": sorted(child_cmp.keys() - parent_tree.keys()),
                "different": sorted(p for p in parent_tree.keys() & child_cmp.keys() if parent_tree[p] != child_cmp[p]),
            }
            row["identical"] = not any(row["diff"].values())
            registered = [c for c in consumers["consumers"] if c["repository"].casefold() == name.casefold()]
            if registered and lock is None:
                row["vendor"] = "lock_missing_at_recorded_sha"
            elif registered and vc is not None:
                row["vendor"] = "topology_match" if vc.compare(consumers, lock, name)["matches"] else "topology_mismatch"
            elif registered:
                want = {(e["repository"].casefold(), e["source"], e["destination"]) for e in registered[0]["entries"]}
                got = {(e["repository"].casefold(), e["source"], e["destination"]) for e in lock["files"]}
                row["vendor"] = "topology_match" if want == got else "topology_mismatch"
        report["children"].append(row)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--heads", default="child-heads.json")
    ap.add_argument("--registry", default="vendor-consumers.json")
    ap.add_argument("--vendor-tools", type=Path, help="親 myon-bioinformatics の checkout（vendor_sync.py と vendor_consumers.py）")
    ap.add_argument("--offline", action="store_true", help="形だけ確かめる（GitHub に取りに行かない）")
    ap.add_argument("--fail-on-drift", action="store_true")
    ap.add_argument("--fail-on-diff", action="store_true")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    try:
        heads = validate_heads(json.loads((root / args.heads).read_text(encoding="utf-8")))
        consumers = validate_consumers(json.loads((root / args.registry).read_text(encoding="utf-8")))
        report = check(root, heads, consumers, network=not args.offline, tools=args.vendor_tools)
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.SubprocessError) as error:
        print("check-child-heads: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    failed = any("error" in c or c.get("vendor") == "topology_mismatch" for c in report["children"])
    failed |= args.fail_on_drift and any(c.get("drift") for c in report["children"])
    failed |= args.fail_on_diff and any(c.get("identical") is False for c in report["children"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
