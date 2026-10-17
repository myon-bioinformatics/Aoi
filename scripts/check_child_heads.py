"""Aoi の子リポジトリ（subtree で切り出したもの）の登録と差分を確かめる（stdlib のみ、書き込みなし）。

- child-heads.json（child-heads/1）と vendor-consumers.json（vendor-consumers/1）の形を確かめる。
  --vendor-tools に親 myon-bioinformatics の checkout（vendor_sync.py / vendor_consumers.py）を渡すと、
  親と同じ validator で確かめ、子の vendor lock と登録の topology も比べる。
- 子の main の今の SHA と、登録した SHA のずれ（drift）を出す。
- 登録した SHA の子の tree と、Aoi の subtree_prefix の tree の差分を、blob と mode で出す。
  子は prefix の純粋な subtree（除外するファイルはない）。not_in_parent / child_preamble は受け付けない。
- mirrored_from_parent（prefix の下のパス → Aoi の原本のパス）は、Aoi の中で blob と mode が原本と
  同じかを確かめ、違えば失敗にする（共有するルートのファイルを子に通常のファイルとして置くとき）。
- vendor-consumers.json はなくてもよい（vendor する子がいなければ置かない）。
- 登録した vendor consumer（state=locked）の lock が登録した SHA にない・読めないときは失敗にする。
- 子ごとの取得の失敗（リポジトリがない、タイムアウトなど）は、その子の error にして次の子へ進む。

既定では drift と差分は報告のみ。--fail-on-drift / --fail-on-diff で終了コード 1 にする。
Git の取得は一時的な bare リポジトリに行い、この checkout には書かない。
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
URL_TEMPLATE = "https://github.com/{repository}.git"
UNSUPPORTED = ("not_in_parent", "child_preamble")
VENDOR_FAILURES = ("topology_mismatch", "lock_missing_at_recorded_sha", "lock_invalid")


def _git_bytes(*args, cwd=None, timeout=300) -> bytes:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, timeout=timeout)
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
    if not isinstance(doc["heads"], dict) or not doc["heads"]:
        raise ValueError("child heads must be a nonempty object")
    for name, entry in doc["heads"].items():
        if not REPO.fullmatch(name):
            raise ValueError(f"expected owner/repository: {name}")
        if not isinstance(entry, dict) or not isinstance(entry.get("sha"), str) or not HEX40.fullmatch(entry["sha"]):
            raise ValueError(f"{name}: sha must be 40 hex")
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


def validate_consumers(doc: dict) -> dict:
    if not isinstance(doc, dict) or set(doc) != {"schema", "consumers"} or doc["schema"] != "vendor-consumers/1":
        raise ValueError("expected vendor-consumers/1")
    if not isinstance(doc["consumers"], list) or not doc["consumers"]:
        raise ValueError("consumers must be a nonempty list")
    for consumer in doc["consumers"]:
        if not isinstance(consumer, dict) or not isinstance(consumer.get("repository"), str) \
                or not REPO.fullmatch(consumer["repository"]):
            raise ValueError("consumer repository must be owner/repository")
        if consumer.get("state") not in ("locked", "legacy"):
            raise ValueError("consumer state must be locked or legacy")
        if consumer["state"] == "locked" and (not isinstance(consumer.get("lock"), str) or not consumer["lock"]):
            raise ValueError("locked consumer requires lock path")
        entries = consumer.get("entries")
        if not isinstance(entries, list) or not entries:
            raise ValueError("consumer entries must be a nonempty list")
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"repository", "source", "destination"}:
                raise ValueError("invalid consumer entry fields")
            if not all(isinstance(entry[k], str) and entry[k] for k in entry):
                raise ValueError("consumer entry fields must be nonempty strings")
    return doc


def _tree(repo: Path, rev: str) -> dict[str, tuple[str, str]]:
    """path -> (mode, object)。-z で NUL 区切り（改行やタブを含むパスもそのまま）。"""
    rows = {}
    for record in _git_bytes("ls-tree", "-r", "-z", rev, cwd=repo).split(b"\0"):
        if record:
            meta, path = record.split(b"\t", 1)
            mode, _kind, obj = meta.decode("ascii").split(" ")
            rows[path.decode("utf-8", "surrogateescape")] = (mode, obj)
    return rows


def _load_tools(tools: Path):
    sys.path.insert(0, str(tools))
    try:
        for name in ("vendor_consumers", "vendor_sync"):
            sys.modules.pop(name, None)
        return importlib.import_module("vendor_consumers"), importlib.import_module("vendor_sync")
    finally:
        sys.path.remove(str(tools))


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


def _vendor(consumers: dict | None, name: str, child_tree: dict, bare: Path, vc) -> str | None:
    registered = [c for c in (consumers or {"consumers": []})["consumers"] if c["repository"].casefold() == name.casefold()]
    if not registered:
        return None
    consumer = registered[0]
    if consumer["state"] != "locked":
        return "legacy"
    lock_row = child_tree.get(consumer["lock"])
    if lock_row is None:
        return "lock_missing_at_recorded_sha"
    try:
        lock = json.loads(_git("cat-file", "blob", lock_row[1], cwd=bare))
        if vc is not None:
            return "topology_match" if vc.compare(consumers, lock, name)["matches"] else "topology_mismatch"
        want = {(e["repository"].casefold(), e["source"], e["destination"].casefold()) for e in consumer["entries"]}
        got = {(e["repository"].casefold(), e["source"], e["destination"].casefold()) for e in lock["files"]}
    except (ValueError, KeyError, TypeError):
        return "lock_invalid"
    return "topology_match" if want == got else "topology_mismatch"


def _child(name: str, entry: dict, parent_tree: dict, consumers: dict | None, vc, *, ref: str,
           url_template: str, row: dict) -> None:
    url = url_template.format(repository=name)
    live = _git("ls-remote", url, f"refs/heads/{ref}", timeout=120).split()
    row["live_sha"] = live[0] if live else None
    row["drift"] = row["live_sha"] != entry["sha"]
    with tempfile.TemporaryDirectory() as tmp:
        bare = Path(tmp)
        _git("init", "-q", "--bare", str(bare))
        _git("fetch", "-q", "--depth=1", url, entry["sha"], cwd=bare)
        child_tree = _tree(bare, entry["sha"])
        row["vendor"] = _vendor(consumers, name, child_tree, bare, vc)
    row["diff"] = {
        "only_in_parent": sorted(parent_tree.keys() - child_tree.keys()),
        "only_in_child": sorted(child_tree.keys() - parent_tree.keys()),
        "different": sorted(p for p in parent_tree.keys() & child_tree.keys() if parent_tree[p] != child_tree[p]),
    }
    row["identical"] = not any(row["diff"].values())


def check(root: Path, heads: dict, consumers: dict | None, *, network: bool, tools: Path | None,
          url_template: str = URL_TEMPLATE) -> dict:
    report = {"schema": "aoi-child-heads-check/1", "parent": _git("rev-parse", "HEAD", cwd=root).strip(), "children": []}
    vc = None
    if tools is not None:
        vc, vs = _load_tools(tools)
        vs.validate_child_heads(heads)
        if consumers is not None:
            vc.validate(consumers)
    whole = _tree(root, "HEAD")
    for name, entry in sorted(heads["heads"].items()):
        optional = entry["optional"]
        prefix = optional["subtree_prefix"]
        row = {"repository": name, "recorded_sha": entry["sha"], "prefix": prefix}
        parent_tree = {p[len(prefix) + 1:]: b for p, b in whole.items() if p.startswith(prefix + "/")}
        row["mirrors"] = _mirrors(whole, prefix, optional.get("mirrored_from_parent", {}))
        if not parent_tree:
            row["error"] = "prefix_not_found"
        if network:
            try:
                _child(name, entry, parent_tree, consumers, vc, ref=heads["ref"],
                       url_template=url_template, row=row)
            except (RuntimeError, subprocess.SubprocessError, OSError) as error:
                row["error"] = "fetch_failed: " + str(error)
        report["children"].append(row)
    return report


def failed(report: dict, *, fail_on_drift: bool, fail_on_diff: bool) -> bool:
    rows = report["children"]
    bad = any("error" in c or c.get("vendor") in VENDOR_FAILURES for c in rows)
    bad |= any(state != "identical" for c in rows for state in c["mirrors"].values())
    bad |= fail_on_drift and any(c.get("drift") for c in rows)
    bad |= fail_on_diff and any(c.get("identical") is False for c in rows)
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--heads", default="child-heads.json")
    ap.add_argument("--registry", default="vendor-consumers.json")
    ap.add_argument("--vendor-tools", type=Path, help="親 myon-bioinformatics の checkout（vendor_sync.py と vendor_consumers.py）")
    ap.add_argument("--offline", action="store_true", help="形と Aoi 側だけ確かめる（GitHub に取りに行かない）")
    ap.add_argument("--url-template", default=URL_TEMPLATE, help="子の URL。{repository} を owner/repository にする")
    ap.add_argument("--fail-on-drift", action="store_true")
    ap.add_argument("--fail-on-diff", action="store_true")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    try:
        heads = validate_heads(json.loads((root / args.heads).read_text(encoding="utf-8")))
        registry = root / args.registry
        consumers = validate_consumers(json.loads(registry.read_text(encoding="utf-8"))) if registry.exists() else None
        report = check(root, heads, consumers, network=not args.offline, tools=args.vendor_tools,
                       url_template=args.url_template)
    except (OSError, ValueError, RuntimeError, ImportError, subprocess.SubprocessError) as error:
        print("check-child-heads: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failed(report, fail_on_drift=args.fail_on_drift, fail_on_diff=args.fail_on_diff) else 0


if __name__ == "__main__":
    raise SystemExit(main())
