"""Markdown のリンクと画像の参照先を確かめる。

  python nagoyaction/linkcheck.py                          # ローカル: git に登録済みのファイルと照合（ネットワークなし）
  python nagoyaction/linkcheck.py --remote OWNER/REPO --ref BRANCH
                                                           # push 後: GitHub 上のそのブランチに実在するか（gh api）
  python nagoyaction/linkcheck.py --external               # http(s) のリンクも確かめる（404/410 だけを失敗とする）

ローカルの照合は「git に登録済み」かつ「大文字小文字まで一致」で判定する。
GitHub は大文字小文字を区別するため、macOS などで開けても GitHub では 404 になる（例: genesis.md と GENESIS.md）。
git add を忘れたファイルも、手元にはあるが GitHub にはないので失敗にする。

コードブロック・インラインコードの中は対象外。ページ内アンカー（#...）と mailto: は確かめない。
外部リンクは、到達できなかっただけ（タイムアウト・403 など）なら失敗にせず「未確認」として報告する。
標準ライブラリだけで動く。
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
INLINE = re.compile(r"`[^`\n]*`")


def links_in(text: str) -> list[str]:
    text = INLINE.sub("", FENCE.sub("", text))
    return LINK.findall(text)


def classify(target: str) -> str:
    if target.startswith(("http://", "https://")):
        return "external"
    if target.startswith(("#", "mailto:")) or ":" in target.split("/")[0]:
        return "skip"
    return "relative"


def resolve(md_path: str, target: str) -> str | None:
    """リポジトリのルートからの POSIX パス。ルートの外を指すなら None。"""
    path = target.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return ""
    base = "" if path.startswith("/") else posixpath.dirname(md_path)
    joined = posixpath.normpath(posixpath.join(base, path.lstrip("/")))
    return None if joined.startswith("..") else joined


def tracked_files(root: Path, runner=subprocess.run) -> list[str]:
    out = runner(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True, check=True)
    return [f for f in out.stdout.split("\0") if f]


def check_local(root: Path, files: list[str]) -> list[dict]:
    tracked = set(files)
    dirs = {posixpath.dirname(f) for f in files}
    dirs |= {d for f in files for d in _parents(f)}
    results = []
    for md in sorted(f for f in files if f.lower().endswith(".md")):
        for target in links_in((root / md).read_text(encoding="utf-8")):
            kind = classify(target)
            r = {"file": md, "target": target, "kind": kind}
            if kind == "relative":
                path = resolve(md, target)
                if path is None:
                    r.update(status="broken", reason="リポジトリの外を指している")
                elif path == "" or path in tracked or path in dirs:
                    r.update(status="ok", path=path)
                else:
                    near = [f for f in tracked | dirs if f.lower() == path.lower()]
                    reason = f"大文字小文字が違う（実際は {near[0]}）" if near else "git に登録されたファイルがない"
                    r.update(status="broken", path=path, reason=reason)
            else:
                r["status"] = "not-checked"
            results.append(r)
    return results


def _parents(f: str):
    p = posixpath.dirname(f)
    while p:
        yield p
        p = posixpath.dirname(p)


def check_remote(results: list[dict], repo: str, ref: str, runner=subprocess.run) -> None:
    """push 後のブランチに、相対リンクの参照先が実在するかを gh api で確かめる。"""
    cache: dict[str, tuple[str, str]] = {}
    for r in results:
        if r["kind"] != "relative" or r.get("status") == "broken" or not r.get("path"):
            continue
        path = r["path"]
        if path not in cache:
            out = runner(["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}", "--silent"],
                         capture_output=True, text=True, check=False)
            if out.returncode == 0:
                cache[path] = ("ok", "")
            elif "404" in (out.stderr or ""):
                cache[path] = ("broken", f"GitHub の {ref} に存在しない（404）")
            else:
                cache[path] = ("unverified", "gh api で確認できなかった")
        status, reason = cache[path]
        r["remote"] = status
        if status == "broken":
            r.update(status="broken", reason=reason)


def check_external(results: list[dict], opener=urllib.request.urlopen, timeout: float = 10) -> None:
    for r in results:
        if r["kind"] != "external":
            continue
        req = urllib.request.Request(r["target"], method="HEAD", headers={"User-Agent": "Aoi-linkcheck"})
        try:
            opener(req, timeout=timeout)
            r["status"] = "ok"
        except urllib.error.HTTPError as e:
            r["status"], r["reason"] = ("broken", f"HTTP {e.code}") if e.code in (404, 410) else ("unverified", f"HTTP {e.code}")
        except (urllib.error.URLError, OSError) as e:
            r["status"], r["reason"] = "unverified", type(e).__name__


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Markdown のリンクと画像の参照先を確かめる")
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--remote", metavar="OWNER/REPO")
    ap.add_argument("--ref", help="--remote で確かめるブランチ")
    ap.add_argument("--external", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if args.remote and not args.ref:
        ap.error("--remote には --ref が必要")

    results = check_local(args.root, tracked_files(args.root))
    if args.remote:
        check_remote(results, args.remote, args.ref)
    if args.external:
        check_external(results)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if r["status"] in ("broken", "unverified"):
                print(f"[{r['status']}] {r['file']}: {r['target']} — {r.get('reason', '')}")
        counts = {s: sum(r["status"] == s for r in results) for s in ("ok", "broken", "unverified", "not-checked")}
        print("links: " + " ".join(f"{k}={v}" for k, v in counts.items()))
    return 1 if any(r["status"] == "broken" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
