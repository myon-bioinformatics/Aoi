"""Markdown のリンクと画像の参照先を確かめる。

  python nagoyaction/linkcheck.py                          # ローカル: git に登録済みのファイルと照合（ネットワークなし）
  python nagoyaction/linkcheck.py --remote OWNER/REPO --ref BRANCH
                                                           # push 後: GitHub 上のそのブランチに実在するか（gh api）
  python nagoyaction/linkcheck.py --external               # http(s) のリンクも確かめる（404/410 だけを失敗とする）
  python nagoyaction/linkcheck.py --strict                 # unverified も失敗（終了コード 3）。既定では付けない
  python nagoyaction/linkcheck.py --json                   # stdout は nagoyaction-linkcheck/1。失敗は stderr の nagoyaction-error/1

ローカルの照合は「git に登録済み」かつ「大文字小文字まで一致」で判定する。
GitHub は大文字小文字を区別するため、macOS などで開けても GitHub では 404 になる（例: genesis.md と GENESIS.md）。
git add を忘れたファイルも、手元にはあるが GitHub にはないので失敗にする。

コードブロック・インラインコードの中は対象外。ページ内アンカー（#...）と mailto: は確かめない。
外部リンクは、到達できなかっただけ（タイムアウト・403 など）なら失敗にせず unverified として報告する。
gh api が 404 以外で失敗したときも remote=unverified で、リンク自体は broken にしない。

終了コード:
  0  broken がない。unverified は既定では失敗にしない
  1  broken が1つ以上（--strict でも broken が優先）
  2  使い方、または git ls-files の失敗
  3  --strict のときだけ。broken は無く、unverified（status または remote）がある

既定を 0 のままにするのは、Aoi の Links ワークフローが --strict なしでローカルと
--remote を実行するため。到達できない外部リンクや gh の一時失敗で、そのジョブを落とさない。
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


class LinkcheckError(RuntimeError):
    def __init__(self, message: str, code: str = "git"):
        super().__init__(message)
        self.code = code


def tracked_files(root: Path, runner=subprocess.run) -> list[str]:
    try:
        out = runner(["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        raise LinkcheckError(f"git ls-files を実行できない: {exc}") from None
    if getattr(out, "returncode", 1) != 0:
        detail = (getattr(out, "stderr", "") or getattr(out, "stdout", "") or "").strip()
        raise LinkcheckError(detail or f"git ls-files が終了コード {out.returncode}")
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
        elif status == "unverified":
            r["reason"] = reason


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


EXIT_EPILOG = """
終了コード:
  0  broken がない。unverified は既定では失敗にしない
  1  broken が1つ以上（相対パスの欠落、大文字小文字の不一致、HTTP 404/410、リモートの 404）
  2  使い方の誤り、または git ls-files の失敗
  3  --strict のときだけ。broken は無く、unverified がある（status または remote）

unverified を既定で失敗にしない。Aoi の Links ワークフローは --strict なしで
ローカルと --remote を実行する。gh api の 404 以外（認証、制限、一時失敗）や、
到達できない外部リンクを失敗にすると、そのジョブが壊れる。
--strict を付けたときだけ、broken が無い unverified を終了コード 3 にする。
broken がある場合は --strict でも 1。
""".strip("\n")


class JsonArgumentParser(argparse.ArgumentParser):
    json_mode = False

    def error(self, message: str) -> None:
        if self.json_mode:
            emit_error(2, "usage", message)
            self.exit(2)
        super().error(message)


def emit_error(exit_code: int, code: str, message: str) -> None:
    payload = {
        "schema": "nagoyaction-error/1",
        "tool": "linkcheck",
        "ok": False,
        "exit": exit_code,
        "error": {"code": code, "message": message},
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)


def summarize(results: list[dict]) -> dict:
    counts = {s: sum(r["status"] == s for r in results) for s in ("ok", "broken", "unverified", "not-checked")}
    counts["remote_unverified"] = sum(r.get("remote") == "unverified" for r in results)
    return counts


def unverified_count(results: list[dict]) -> int:
    return sum(1 for r in results if r["status"] == "unverified" or r.get("remote") == "unverified")


def exit_code(results: list[dict], *, strict: bool) -> int:
    """broken は 1。--strict で unverified だけが残るときは 3。それ以外は 0。"""
    if any(r["status"] == "broken" for r in results):
        return 1
    if strict and unverified_count(results):
        return 3
    return 0


def _problem_label(result: dict) -> str | None:
    if result["status"] in ("broken", "unverified"):
        return result["status"]
    if result.get("remote") == "unverified":
        return "unverified"
    return None


def _parser() -> JsonArgumentParser:
    ap = JsonArgumentParser(
        description="Markdown のリンクと画像の参照先を確かめる",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_EPILOG,
    )
    ap.add_argument("--root", type=Path, default=Path("."),
                    help="リポジトリのルート。git ls-files と Markdown の読み込みの基準。既定はカレントディレクトリ。")
    ap.add_argument("--remote", metavar="OWNER/REPO",
                    help="push 後に gh api で repos/OWNER/REPO の contents を見る。--ref が必須。"
                         " 404 は broken。それ以外の失敗は remote=unverified で、既定では終了コードを変えない。")
    ap.add_argument("--ref",
                    help="--remote で確かめる git ref（ブランチ、タグ、またはコミット）。--remote と組で必須。")
    ap.add_argument("--external", action="store_true",
                    help="http と https を HEAD で確かめる。404 と 410 だけ broken。"
                         " タイムアウト、接続失敗、それ以外の HTTP は unverified で、既定の終了コードは 0。")
    ap.add_argument("--json", action="store_true",
                    help="走査できたときは stdout に schema nagoyaction-linkcheck/1"
                         "（ok, exit, strict, counts, results）。"
                         " 終了コードが 0 でないとき、および走査前の失敗は stderr の nagoyaction-error/1。")
    ap.add_argument("--strict", action="store_true",
                    help="broken が無く unverified（status または remote）があるとき終了コード 3。"
                         " 既定では unverified だけでは 0。Aoi の Links ワークフローはこれを付けない。")
    return ap


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    ap = _parser()
    ap.json_mode = "--json" in argv
    args = ap.parse_args(argv)
    if args.remote and not args.ref:
        ap.error("--remote には --ref が必要")

    try:
        results = check_local(args.root, tracked_files(args.root))
        if args.remote:
            check_remote(results, args.remote, args.ref)
        if args.external:
            check_external(results)
    except LinkcheckError as exc:
        if args.json:
            emit_error(2, exc.code, str(exc))
        else:
            print(f"linkcheck: {exc}", file=sys.stderr)
        return 2

    code = exit_code(results, strict=args.strict)
    counts = summarize(results)
    if args.json:
        print(json.dumps({
            "schema": "nagoyaction-linkcheck/1",
            "ok": code == 0,
            "exit": code,
            "strict": bool(args.strict),
            "counts": counts,
            "results": results,
        }, ensure_ascii=False, indent=2))
        if code == 1:
            emit_error(1, "broken", f"broken が {counts['broken']} 件")
        elif code == 3:
            emit_error(3, "unverified", f"unverified が {unverified_count(results)} 件（--strict）")
    else:
        for r in results:
            label = _problem_label(r)
            if label:
                print(f"[{label}] {r['file']}: {r['target']} — {r.get('reason', '')}")
        print("links: " + " ".join(f"{k}={v}" for k, v in counts.items()))
        if code == 0 and unverified_count(results):
            print("unverified は既定では失敗にしない。--strict で終了コード 3。")
        elif code == 3:
            print("linkcheck: unverified がある（--strict のため終了コード 3）", file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
