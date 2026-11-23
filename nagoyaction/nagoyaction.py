"""NagoyAction — 研究を、続けられる仕組みに。

パイプラインを TOML に一度だけ書き、ローカルでも GitHub Actions でも同じコマンドで動かす。
GitHub Actions のワークフローは `python nagoyaction/nagoyaction.py run <pipeline>` を呼ぶだけにする。
データを外に出せない案件では、同じ定義をローカルで実行すればよい。

  doctor <pipeline>  実行前の確認。Python の版、必要なツール（git, uv, gh など）、
                     オフライン実行に必要な成果物の有無。足りないものがあれば終了コード 1
  show <pipeline>    パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示する
  run <pipeline>     doctor のあと、手順を順に実行する。各手順の結果を受領記録(JSONL)に残す
    --offline        network = true の手順は実行しない（成果物が既にあれば飛ばす。なければ止まる）
    --only / --from / --until  一部の手順だけ実行する
    -v KEY=VALUE     変数をコマンドラインから設定・上書きする
    --dry-run        何を実行するかだけ表示する
    --json           成功は stdout の JSON。失敗は stderr の nagoyaction-error/1

終了コード（--help にも書く）:
  0      成功。doctor の warn は成功。run は選んだ手順がすべて成功
  1      doctor が fail を出した。run は実行しない
  2      使い方、TOML、パイプライン定義、ファイル読み込みの誤り
  その他  run が、失敗した手順自身の終了コードを返す。手順が 2 で終わったときと
          定義の誤り（2）は、stderr の error.code（step か pipeline / usage / toml / io）で区別する

標準ライブラリだけで書く（Python 3.11+、tomllib）。1ファイルをコピーすれば他のリポジトリでも使える。

パイプライン定義:
  name = "..."
  root = "../.."                       # 手順を実行するディレクトリ（定義ファイルからの相対）
  [requires]
  python = "3.11"
  tools = ["git", "uv"]                # 必須
  optional = ["gh"]                    # なくても実行できる（警告のみ）
  [vars]
  years = "2012-2025"                  # 手順の中で {years} として使える
  [[step]]
  name = "fetch"
  run = ["uv", "run", "python", "queryu/queryu.py", "--years", "{years}"]
  network = true                       # 外部にアクセスする手順
  outputs = ["data/observations/x.jsonl"]
"""

from __future__ import annotations

import argparse, base64, contextlib, datetime as dt, hashlib, importlib.util, io, json, os, posixpath, random, re, secrets
import shutil, signal, subprocess, sys, tarfile, tempfile, time, tomllib, urllib.error, urllib.request, zipfile
from dataclasses import dataclass
from types import SimpleNamespace
from pathlib import Path


class PipelineError(ValueError):
    pass


def load(path: Path) -> dict:
    with Path(path).open("rb") as f:
        p = tomllib.load(f)
    steps = p.get("step", [])
    if not steps:
        raise PipelineError("step が1つもない")
    names = [s.get("name") for s in steps]
    if len(set(names)) != len(names) or not all(names):
        raise PipelineError(f"step の name は必須で一意: {names}")
    for s in steps:
        if not isinstance(s.get("run"), list) or not all(isinstance(a, str) for a in s["run"]):
            raise PipelineError(f"{s['name']}: run は文字列の配列（シェルは使わない）")
    p["_path"] = Path(path).resolve()
    p["_root"] = (p["_path"].parent / p.get("root", ".")).resolve()
    return p


def _version(tool: str) -> str:
    try:
        out = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError):
        return "?"
    return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr).strip() else "?"


def doctor(p: dict, *, offline: bool = False, which=shutil.which) -> list[dict]:
    """確認結果の一覧。level は ok / warn / fail。"""
    req = p.get("requires", {})
    checks = []
    need = tuple(int(x) for x in str(req.get("python", "3.11")).split("."))
    have = sys.version_info[: len(need)]
    checks.append({"check": "python", "level": "ok" if have >= need else "fail",
                   "detail": f"{sys.version.split()[0]} (requires >= {'.'.join(map(str, need))})"})
    for tool in req.get("tools", []):
        path = which(tool)
        checks.append({"check": tool, "level": "ok" if path else "fail",
                       "detail": _version(tool) if path else "見つからない（インストールが必要）"})
    for tool in req.get("optional", []):
        path = which(tool)
        checks.append({"check": tool, "level": "ok" if path else "warn",
                       "detail": _version(tool) if path else "見つからない（なくても実行できる）"})
    if offline:
        for s in p["step"]:
            if s.get("network"):
                missing = [o for o in s.get("outputs", []) if not (p["_root"] / o).exists()]
                checks.append({"check": f"offline:{s['name']}", "level": "fail" if missing else "ok",
                               "detail": f"成果物がない: {missing}" if missing else "成果物あり（取得を飛ばす）"})
    return checks


def _expand(argv: list[str], vars_: dict) -> list[str]:
    try:
        return [a.format(**vars_) for a in argv]
    except KeyError as e:
        raise PipelineError(f"未定義の変数: {e}") from None


def _parse_override_vars(var_list: list[str] | None) -> dict[str, str]:
    res = {}
    if not var_list:
        return res
    for item in var_list:
        if "=" not in item:
            raise PipelineError(f"変数指定の形式が不正: {item} (KEY=VALUE の形式で指定)")
        k, v = item.split("=", 1)
        k = k.strip()
        if not k:
            raise PipelineError(f"変数名が空: {item}")
        res[k] = v
    return res


def _select(steps, only=None, start=None, until=None):
    names = [s["name"] for s in steps]
    for n in [*(only or []), *([start] if start else []), *([until] if until else [])]:
        if n not in names:
            raise PipelineError(f"そんな step はない: {n}（{names}）")
    if only:
        return [s for s in steps if s["name"] in only]
    s_idx = names.index(start) if start else 0
    e_idx = names.index(until) + 1 if until else len(steps)
    if s_idx >= e_idx:
        raise PipelineError(f"--from ({start}) は --until ({until}) より前でなければならない")
    return steps[s_idx:e_idx]


def run(p: dict, *, offline=False, only=None, start=None, until=None, var_overrides=None,
        dry_run=False, receipt: Path | None = None, runner=subprocess.run,
        quiet: bool = False, records: list | None = None) -> int:
    vars_ = {k: str(v) for k, v in p.get("vars", {}).items()}
    if var_overrides:
        vars_.update(var_overrides)
    for s in _select(p["step"], only, start, until):
        argv = _expand(s["run"], vars_)
        entry = {"pipeline": p.get("name"), "step": s["name"], "argv": argv,
                 "started": dt.datetime.now(dt.UTC).isoformat(timespec="seconds")}
        if offline and s.get("network"):
            entry.update(skipped=True, reason="offline: network step")
            if not quiet:
                print(f"[skip] {s['name']}（オフライン。取得済みの成果物を使う）")
        elif dry_run:
            entry.update(skipped=True, reason="dry-run")
            if not quiet:
                print(f"[dry-run] {s['name']}: {' '.join(argv)}")
        else:
            if not quiet:
                print(f"[run] {s['name']}: {' '.join(argv)}", flush=True)
            rc = runner(argv, cwd=p["_root"], check=False).returncode
            entry.update(returncode=rc, ended=dt.datetime.now(dt.UTC).isoformat(timespec="seconds"))
            if records is not None:
                records.append(entry)
            if receipt:
                _append(receipt, entry)
            if rc != 0:
                if not quiet:
                    print(f"[fail] {s['name']} (exit {rc})", file=sys.stderr)
                return rc
            continue
        if records is not None:
            records.append(entry)
        if receipt:
            _append(receipt, entry)
    return 0


def _append(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def show(p: dict, *, var_overrides=None, json_output: bool = False) -> str:
    """パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示形式で返す。"""
    vars_ = {k: str(v) for k, v in p.get("vars", {}).items()}
    if var_overrides:
        vars_.update(var_overrides)
    req = p.get("requires", {})
    steps_data = []
    for s in p.get("step", []):
        expanded = _expand(s["run"], vars_)
        steps_data.append({
            "name": s["name"],
            "network": bool(s.get("network")),
            "run": s["run"],
            "expanded_run": expanded,
            "outputs": s.get("outputs", []),
        })

    data = {
        "schema": "nagoyaction-pipeline/1",
        "name": p.get("name", ""),
        "root": str(p["_root"]),
        "requires": {
            "python": req.get("python", "3.11"),
            "tools": req.get("tools", []),
            "optional": req.get("optional", []),
        },
        "vars": vars_,
        "steps": steps_data,
    }

    if json_output:
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines = [
        f"Pipeline: {data['name']}",
        f"Root: {data['root']}",
        "Requires:",
        f"  Python: >= {data['requires']['python']}",
        f"  Tools: {', '.join(data['requires']['tools']) or 'なし'}",
        f"  Optional: {', '.join(data['requires']['optional']) or 'なし'}",
    ]

    if vars_:
        lines.append("Vars:")
        for k, v in vars_.items():
            lines.append(f"  {k} = {v}")
    else:
        lines.append("Vars: なし")

    lines.append(f"Steps ({len(steps_data)}):")
    for idx, s in enumerate(steps_data, 1):
        net_tag = " (network)" if s["network"] else ""
        cmd_str = " ".join(s["expanded_run"])
        lines.append(f"  {idx}. [{s['name']}]" + net_tag)
        lines.append(f"     command: {cmd_str}")
        if s["outputs"]:
            lines.append(f"     outputs: {', '.join(s['outputs'])}")

    return "\n".join(lines)


def _print_checks(checks: list[dict]) -> None:
    mark = {"ok": "✓", "warn": "!", "fail": "✗"}
    for c in checks:
        print(f"[{mark[c['level']]}] {c['check']}: {c['detail']}")


EXIT_EPILOG = """
終了コード:
  0      成功。doctor の warn は成功。run は選んだ手順がすべて成功
  1      doctor が fail を出した。run は実行しない
  2      使い方、TOML、パイプライン定義、ファイル読み込みの誤り
  その他  run が、失敗した手順自身の終了コードを返す。手順が 2 で終わったときと
          定義の誤りは、--json の stderr にある error.code で区別する
          （step か、pipeline / usage / toml / io）
""".strip("\n")

JSON_PARENT_HELP = (
    "doctor、show、run の出力を JSON にする。サブコマンドの前でも後ろでも同じ。"
    " 失敗は stderr の schema nagoyaction-error/1（tool, ok, exit, error.code, error.message）。"
)


class JsonArgumentParser(argparse.ArgumentParser):
    """--json のとき、使い方の誤りを nagoyaction-error/1 で stderr に書く。"""

    json_mode = False
    tool = "nagoyaction"

    def error(self, message: str) -> None:
        if self.json_mode:
            emit_error(self.tool, 2, "usage", message)
            self.exit(2)
        super().error(message)


def emit_error(tool: str, exit_code: int, code: str, message: str) -> None:
    """エージェントが stderr だけを読んで失敗を区別するための1オブジェクト。"""
    payload = {
        "schema": "nagoyaction-error/1",
        "tool": tool,
        "ok": False,
        "exit": exit_code,
        "error": {"code": code, "message": message},
    }
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)


def _arm_json(parser: JsonArgumentParser, enabled: bool) -> None:
    parser.json_mode = enabled
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                _arm_json(sub, enabled)


def _add_json_flag(parser: argparse.ArgumentParser, help_text: str) -> None:
    # 親とサブコマンドの両方に置く。サブコマンド側は未指定のとき親の値を上書きしない。
    parser.add_argument("--json", dest="json_output", action="store_true",
                        default=argparse.SUPPRESS, help=help_text)


def _parser() -> JsonArgumentParser:
    ap = JsonArgumentParser(
        description="パイプラインの事前確認と実行（ローカル / GitHub Actions 共通）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_EPILOG,
    )
    ap.add_argument("--json", dest="json_output", action="store_true", help=JSON_PARENT_HELP)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser(
        "doctor",
        help="実行前の確認。fail があれば終了コード 1 で、run はしない",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_EPILOG,
    )
    d.add_argument("pipeline", type=Path, help="パイプライン TOML のパス")
    d.add_argument("--offline", action="store_true",
                   help="network の手順は実行せず、outputs のファイルが root にあるかだけを見る。無ければ fail")
    _add_json_flag(d, "チェック結果を stdout の schema nagoyaction-doctor/1 で書く。"
                      " fail のときは終了コード 1 で、stderr に nagoyaction-error/1（error.code=doctor）。")
    s = sub.add_parser(
        "show",
        help="パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_EPILOG,
    )
    s.add_argument("pipeline", type=Path, help="パイプライン TOML のパス")
    s.add_argument("-v", "--var", action="append", metavar="KEY=VALUE",
                   help="変数の上書き。繰り返せる。定義の [vars] よりこちらが優先され、展開後のコマンドを見る")
    _add_json_flag(s, "パイプライン構造を stdout の schema nagoyaction-pipeline/1 で書く。"
                      " エラーは stderr の nagoyaction-error/1。")
    r = sub.add_parser(
        "run",
        help="doctor のあと手順を順に実行する。失敗した手順の終了コードを返す",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXIT_EPILOG,
    )
    r.add_argument("pipeline", type=Path, help="パイプライン TOML のパス")
    r.add_argument("--offline", action="store_true",
                   help="network = true の手順は実行しない。成果物が無ければ doctor が終了コード 1 で止める")
    r.add_argument("--only", nargs="+", metavar="STEP",
                   help="この名前の手順だけを、定義の順に実行する")
    r.add_argument("--from", dest="start", metavar="STEP",
                   help="この手順から最後（または --until）まで実行する")
    r.add_argument("--until", "--to", dest="until", metavar="STEP",
                   help="この手順まで実行する（この手順を含む）。--to は同じ意味")
    r.add_argument("-v", "--var", action="append", metavar="KEY=VALUE",
                   help="変数の上書き。繰り返せる。KEY=VALUE。定義の [vars] より優先する")
    r.add_argument("--dry-run", action="store_true",
                   help="展開したコマンドを表示するだけで、手順は実行しない")
    r.add_argument("--receipt", type=Path,
                   help="受領記録（JSONL）の追記先。親ディレクトリは作る。1行が1手順")
    _add_json_flag(r, "人間向けの行を出さず、stdout に schema nagoyaction-run/1 を書く。"
                      " doctor が止めたときは、その代わりに nagoyaction-doctor/1 を1つだけ書く。"
                      " 手順が失敗したときは、その終了コードと stderr の nagoyaction-error/1（error.code=step）。")
    for name, help_text in DELEGATES_HELP.items():  # main() hands these to their module before this parser runs
        sub.add_parser(name, help=help_text, add_help=False).add_argument("rest", nargs=argparse.REMAINDER, help="そのまま各節へ渡す引数")
    for each in (ap, *sub.choices.values()):
        each.suggest_on_error = True  # 🤔 argparse 3.14+: "maybe you meant" for subcommands; older Pythons ignore it
    return ap


def _json_mode(args, argv: list[str]) -> bool:
    return bool(getattr(args, "json_output", False)) or "--json" in argv


def _report(json_mode: bool, exit_code: int, code: str, message: str, *, human: str) -> None:
    if json_mode:
        emit_error("nagoyaction", exit_code, code, message)
    else:
        print(human, file=sys.stderr)


# ──── linkcheck ───────────────────────────────────────────────────────────────────────────────────────────
# Markdown のリンクと画像の参照先を確かめる。
#
#   python nagoyaction/linkcheck.py                          # ローカル: git に登録済みのファイルと照合（ネットワークなし）
#   python nagoyaction/linkcheck.py --remote OWNER/REPO --ref BRANCH
#                                                            # push 後: GitHub 上のそのブランチに実在するか（gh api）
#   python nagoyaction/linkcheck.py --external               # http(s) のリンクも確かめる（404/410 だけを失敗とする）
#   python nagoyaction/linkcheck.py --strict                 # unverified も失敗（終了コード 3）。既定では付けない
#   python nagoyaction/linkcheck.py --json                   # stdout は nagoyaction-linkcheck/1。失敗は stderr の nagoyaction-error/1
#
# ローカルの照合は「git に登録済み」かつ「大文字小文字まで一致」で判定する。
# GitHub は大文字小文字を区別するため、macOS などで開けても GitHub では 404 になる（例: genesis.md と GENESIS.md）。
# git add を忘れたファイルも、手元にはあるが GitHub にはないので失敗にする。
#
# コードブロック・インラインコードの中は対象外。ページ内アンカー（#...）と mailto: は確かめない。
# 外部リンクは、到達できなかっただけ（タイムアウト・403 など）なら失敗にせず unverified として報告する。
# gh api が 404 以外で失敗したときも remote=unverified で、リンク自体は broken にしない。
#
# 終了コード:
#   0  broken がない。unverified は既定では失敗にしない
#   1  broken が1つ以上（--strict でも broken が優先）
#   2  使い方、または git ls-files の失敗
#   3  --strict のときだけ。broken は無く、unverified（status または remote）がある
#
# 既定を 0 のままにするのは、Aoi の Links ワークフローが --strict なしでローカルと
# --remote を実行するため。到達できない外部リンクや gh の一時失敗で、そのジョブを落とさない。
# 標準ライブラリだけで動く。

_LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_LINK_FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
_LINK_INLINE = re.compile(r"`[^`\n]*`")


def links_in(text: str) -> list[str]:
    text = _LINK_INLINE.sub("", _LINK_FENCE.sub("", text))
    return _LINK.findall(text)


def _link_classify(target: str) -> str:
    if target.startswith(("http://", "https://")):
        return "external"
    if target.startswith(("#", "mailto:")) or ":" in target.split("/")[0]:
        return "skip"
    return "relative"


def _link_resolve(md_path: str, target: str) -> str | None:
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
    dirs |= {d for f in files for d in _link_parents(f)}
    results = []
    case_index = None
    for md in sorted(f for f in files if f.lower().endswith(".md")):
        for target in links_in((root / md).read_text(encoding="utf-8")):
            kind = _link_classify(target)
            r = {"file": md, "target": target, "kind": kind}
            if kind == "relative":
                path = _link_resolve(md, target)
                if path is None:
                    r.update(status="broken", reason="リポジトリの外を指している")
                elif path == "" or path in tracked or path in dirs:
                    r.update(status="ok", path=path)
                else:
                    if case_index is None:
                        case_index = {}
                        for candidate in tracked | dirs:
                            case_index.setdefault(candidate.lower(), candidate)
                    near = case_index.get(path.lower())
                    reason = f"大文字小文字が違う（実際は {near}）" if near is not None else "git に登録されたファイルがない"
                    r.update(status="broken", path=path, reason=reason)
            else:
                r["status"] = "not-checked"
            results.append(r)
    return results


def _link_parents(f: str):
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


_LINKCHECK_EPILOG = """
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


def _link_summarize(results: list[dict]) -> dict:
    counts = {s: sum(r["status"] == s for r in results) for s in ("ok", "broken", "unverified", "not-checked")}
    counts["remote_unverified"] = sum(r.get("remote") == "unverified" for r in results)
    return counts


def _link_unverified_count(results: list[dict]) -> int:
    return sum(1 for r in results if r["status"] == "unverified" or r.get("remote") == "unverified")


def _link_exit_code(results: list[dict], *, strict: bool) -> int:
    """broken は 1。--strict で unverified だけが残るときは 3。それ以外は 0。"""
    if any(r["status"] == "broken" for r in results):
        return 1
    if strict and _link_unverified_count(results):
        return 3
    return 0


def _link_problem_label(result: dict) -> str | None:
    if result["status"] in ("broken", "unverified"):
        return result["status"]
    if result.get("remote") == "unverified":
        return "unverified"
    return None


def _linkcheck_parser() -> JsonArgumentParser:
    ap = JsonArgumentParser(
        prog="nagoyaction linkcheck",
        description="🔗 Markdown のリンクと画像の参照先を確かめる",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=_LINKCHECK_EPILOG,
    )
    ap.tool = "linkcheck"  # nagoyaction-error/1 の tool
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


def _linkcheck_main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    ap = _linkcheck_parser()
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
            emit_error("linkcheck", 2, exc.code, str(exc))
        else:
            print(f"linkcheck: {exc}", file=sys.stderr)
        return 2

    code = _link_exit_code(results, strict=args.strict)
    counts = _link_summarize(results)
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
            emit_error("linkcheck", 1, "broken", f"broken が {counts['broken']} 件")
        elif code == 3:
            emit_error("linkcheck", 3, "unverified", f"unverified が {_link_unverified_count(results)} 件（--strict）")
    else:
        for r in results:
            label = _link_problem_label(r)
            if label:
                print(f"[{label}] {r['file']}: {r['target']} — {r.get('reason', '')}")
        print("links: " + " ".join(f"{k}={v}" for k, v in counts.items()))
        if code == 0 and _link_unverified_count(results):
            print("unverified は既定では失敗にしない。--strict で終了コード 3。")
        elif code == 3:
            print("linkcheck: unverified がある（--strict のため終了コード 3）", file=sys.stderr)
    return code



# ====================================================================================================
# 🏠 hub: ローカル Gitea / Forgejo（nagoyaction hub …）（旧 local_forge.py）
# Local Gitea/Forgejo control, extracted from OneLaunchNumerousModules.
# ====================================================================================================

PY = Path(__file__).resolve()
OLNM_HOME = Path(os.environ.get("OLNM_HOME", Path.home() / ".olnm"))
DIAL_FILE = Path(os.environ.get("DIAL_FILE", OLNM_HOME / "dial"))
DIALS = {0: "🔌 offline", 1: "🏠 local", 2: "🔁 mirror", 3: "☁️ github"}
DIAL_NAMES = {"offline": 0, "local": 1, "mirror": 2, "github": 3}  # the file keeps the digit; names are for people


def dial_level(value: int | str) -> int:
    """offline|local|mirror|github (or 0-3) → 0-3. Raises ValueError for anything else."""
    if isinstance(value, int) and not isinstance(value, bool) and value in DIALS:
        return value
    text = str(value).strip().lower()
    if text in DIAL_NAMES:
        return DIAL_NAMES[text]
    if text.isdigit() and int(text) in DIALS:
        return int(text)
    raise ValueError(f"dial must be one of {', '.join(DIAL_NAMES)} (or 0-3), not {value!r}")


def dial_label(level: int) -> str:
    """'🔁 mirror (2)': the name first, the stored digit after it."""
    return f"{DIALS[level]} ({level})"

def read_dial(default: int = 3) -> int:
    """Current dial (0..3); unset = 3 (plain online box)."""
    try:
        return int(DIAL_FILE.read_text().strip())
    except (OSError, ValueError):
        return default


def _write_dial(level: int) -> None:
    DIAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    DIAL_FILE.write_text(f"{level}\n")


def dial(level: int | str | None = None) -> int:
    """Show or set the dial (offline|local|mirror|github or 0-3). When the local forge exists, also start/stop it and re-point every repo's origin."""
    if level is None:
        lv = read_dial()
        print(f"🎛️  {dial_label(lv)}  ({DIAL_FILE})")
        return lv
    try:
        level = dial_level(level)
    except ValueError as error:
        raise SystemExit(f"❌ {error}") from None
    try:
        if FSTATE.exists():
            _hub_apply(level)
        _write_dial(level)
    except (Exception, SystemExit):
        print("❌ dial change did not complete; inspect forge and repository remotes before retrying. "
              "Earlier side effects are not automatically rolled back.", file=sys.stderr)
        raise
    print(f"🎛️  → {dial_label(level)}" + ("  🌍 one-liners stubbed" if level <= 1 else ""))
    return level


# ───────────────────────── 🏠 hub: local GitHub-like forge (Gitea / Forgejo) ─────────────────────────
FORGE = OLNM_HOME / "forge"
BIN, DATA, BARE, LOG = FORGE / "bin" / "forge", FORGE / "data", FORGE / "bare", FORGE / "log"
INI, PID, FSTATE = FORGE / "app.ini", FORGE / "forge.pid", FORGE / "state.json"
# 🧬 flavors: Gitea (default: since 2016, MIT, released on GitHub) or Forgejo (its 2022 fork, GPLv3+, released on Codeberg). Same CLI + API.
FLAVORS = {
    "forgejo": {"urls": ("https://codeberg.org/forgejo/forgejo/releases/download/v{v}/forgejo-{v}-linux-{arch}", "https://code.forgejo.org/forgejo/forgejo/releases/download/v{v}/forgejo-{v}-linux-{arch}"),
                "latest": ("https://codeberg.org/api/v1/repos/forgejo/forgejo/releases/latest", "https://code.forgejo.org/api/v1/repos/forgejo/forgejo/releases/latest")},
    "gitea": {"urls": ("https://github.com/go-gitea/gitea/releases/download/v{v}/gitea-{v}-linux-{arch}", "https://dl.gitea.com/gitea/{v}/gitea-{v}-linux-{arch}"),
              "latest": ("https://api.github.com/repos/go-gitea/gitea/releases/latest", "https://github.com/go-gitea/gitea/releases/latest")},
}
VERIFIED = {"gitea": "1.27.3"}  # ✅ end-to-end checked with olnm; used when the "latest" lookup is blocked but downloads are not
GH_LABELS = {"bug": "d73a4a", "enhancement": "a2eeef", "documentation": "0075ca", "question": "d876e3", "help wanted": "008672", "good first issue": "7057ff", "wontfix": "ffffff", "duplicate": "cfd3d7"}
APP_INI = """\
APP_NAME = olnm hub
RUN_MODE = prod
WORK_PATH = {home}
[server]
PROTOCOL = http
HTTP_ADDR = 127.0.0.1
HTTP_PORT = {port}
ROOT_URL = http://localhost:{port}/
PUBLIC_URL_DETECTION = legacy
DISABLE_SSH = true
OFFLINE_MODE = true
[database]
DB_TYPE = sqlite3
PATH = {data}/forge.db
[repository]
ROOT = {data}/repos
DEFAULT_BRANCH = main
[security]
INSTALL_LOCK = true
SECRET_KEY = {secret}
[service]
DISABLE_REGISTRATION = true
REQUIRE_SIGNIN_VIEW = false
[mailer]
ENABLED = false
[log]
MODE = file
ROOT_PATH = {log}
[actions]
ENABLED = true
[mirror]
ENABLED = true
DEFAULT_INTERVAL = 1h
"""
_NOPROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _sh(*cmd: str, cwd: Path | None = None, check: bool = True) -> str:
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and r.returncode:
        raise SystemExit(f"❌ {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def _open(req: urllib.request.Request | str, timeout: int):
    url = req.full_url if isinstance(req, urllib.request.Request) else req
    opener = _NOPROXY if url.startswith(("http://127.0.0.1", "http://localhost")) else urllib.request.build_opener()
    return opener.open(req, timeout=timeout)


def _fetch(url: str, dest: Path | None = None, timeout: int = 120) -> bytes:
    with _open(urllib.request.Request(url, headers={"User-Agent": "olnm"}), timeout) as r:
        data = r.read()
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return data


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fstate() -> dict:
    return json.loads(FSTATE.read_text()) if FSTATE.exists() else {"port": 3000, "user": "admin", "repos": {}}


def _fsave(st: dict) -> None:
    FORGE.mkdir(parents=True, exist_ok=True)
    FSTATE.write_text(json.dumps(st, indent=2, ensure_ascii=False) + "\n")
    FSTATE.chmod(0o600)


def _forge(*args: str, check: bool = True) -> str:
    if not BIN.exists():
        raise SystemExit("❌ forge binary missing → hubdial install")
    return _sh(str(BIN), "--config", str(INI), *args, check=check)


def _running() -> int:
    if PID.exists():
        try:
            pid = int(PID.read_text() or 0)
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            PID.unlink(missing_ok=True)
    return 0


def hub_port() -> int:
    """Port of the local forge."""
    return _fstate()["port"]


def _latest_version(flavor: str = "gitea") -> str:
    for url in FLAVORS[flavor]["latest"]:
        try:
            if url.startswith("https://github.com/"):  # release page redirects to /tag/vX.Y.Z
                with _open(urllib.request.Request(url, headers={"User-Agent": "olnm"}), 20) as r:
                    return r.geturl().rsplit("/v", 1)[1]
            return json.loads(_fetch(url, timeout=20))["tag_name"].lstrip("v")
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError, TimeoutError):
            continue
    if v := VERIFIED.get(flavor):
        print(f"↪️  latest {flavor} unknown (lookup blocked) → verified {v}")
        return v
    other = "gitea" if flavor == "forgejo" else "forgejo"
    raise SystemExit(f"❌ cannot reach {flavor} releases → try --flavor {other}, or install --from FILE")


def hub_bundle(dest: str = "carry", version: str = "latest", arch: str = "amd64", flavor: str = "gitea") -> Path:
    """🌍 Download the forge binary + .sha256 into DEST and copy nagoyaction.py beside it — carry DEST into a closed network."""
    if flavor not in FLAVORS:
        raise SystemExit(f"❌ flavor must be one of {', '.join(FLAVORS)}")
    v = _latest_version(flavor) if version == "latest" else version
    out = Path(dest)
    name = f"{flavor}-{v}-linux-{arch}"
    for tmpl in FLAVORS[flavor]["urls"]:
        url = tmpl.format(v=v, arch=arch)
        try:
            print(f"⬇️  {url}")
            binary = _fetch(url, out / name, timeout=900)
            want = _fetch(url + ".sha256", out / f"{name}.sha256", timeout=60).split()[0].decode()
            break
        except urllib.error.URLError as e:
            print(f"⚠️  {url.split('/')[2]}: {e}")
    else:
        raise SystemExit(f"❌ download failed on all hosts → try --flavor {'gitea' if flavor == 'forgejo' else 'forgejo'}")
    if hashlib.sha256(binary).hexdigest() != want:
        raise SystemExit("❌ sha256 mismatch")
    shutil.copy2(PY, out / PY.name)
    print(f"✅ sha256 ok → 🎒 {out}/  (offline: python3 nagoyaction.py hub install --from {out}/{name})")
    return out / name


def hub_install(version: str = "latest", src: str | None = None, sha: str | None = None, flavor: str = "gitea") -> Path:
    """Place the forge binary at ~/.olnm/forge/bin/forge. Online: download+verify. Offline: --from carried file (checked against sha or sidecar .sha256)."""
    if src:
        path = Path(src)
        if not path.is_file():
            raise SystemExit(f"❌ no such file: {src}")
        side = path.with_name(path.name + ".sha256")
        want = sha or (side.read_text().split()[0] if side.exists() else None)
        if want and _sha256(path) != want:
            raise SystemExit("❌ sha256 mismatch for carried binary")
    else:
        path = hub_bundle(str(FORGE / "bundle"), version, flavor=flavor)
    BIN.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, BIN)
    BIN.chmod(0o755)
    print(f"📦 {BIN} ← {path.name}")
    try:
        print(f"🔖 {_forge('--version', check=False) or 'installed'}")
    except OSError as e:
        print(f"⚠️  binary not runnable here: {e}")
    return BIN


def hub_init(port: int = 3000, user: str = "admin", password: str | None = None, email: str = "admin@localhost") -> dict:
    """Write app.ini (sqlite, 127.0.0.1 only, no SSH/mail/sign-up), migrate, create admin + API token, set git auth."""
    for d in (DATA, BARE, LOG):
        d.mkdir(parents=True, exist_ok=True)
    st = _fstate()
    if not INI.exists():
        INI.write_text(APP_INI.format(home=FORGE, port=port, data=DATA, log=LOG, secret=secrets.token_urlsafe(48)))
        INI.chmod(0o600)
    _forge("migrate")
    pw = password or secrets.token_urlsafe(16)
    out = _forge("admin", "user", "create", "--admin", "--username", user, "--password", pw, "--email", email, "--must-change-password=false", check=False)
    created = "already exists" not in out.lower()
    tok = _forge("admin", "user", "generate-access-token", "--username", user, "--token-name", f"olnm-{int(time.time())}", "--scopes", "all", "--raw")
    st.update(port=port, user=user, token=tok.strip().splitlines()[-1])
    if created:
        st["password"] = pw
    _fsave(st)
    if not DIAL_FILE.exists():
        _write_dial(1)
    basic = base64.b64encode(f"{user}:{st['token']}".encode()).decode()
    _sh("git", "config", "--global", "--replace-all", f"http.http://localhost:{port}/.extraHeader", f"Authorization: Basic {basic}")
    print(f"🏗️  http://localhost:{port}  user={user}" + (f"  password={pw}" if created else "  (user existed)"))
    print(f"🔑 token → {FSTATE}   🔐 git auth → ~/.gitconfig")
    return st


def hub_up() -> int:
    """Start the forge in the background."""
    if pid := _running():
        print(f"🏠 already up pid={pid}")
        return pid
    if os.geteuid() == 0:
        print("⚠️  running as root: Gitea / Forgejo refuse to serve as root → run olnm as a normal user")
    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / "web.out").open("a") as output:
        p = subprocess.Popen([str(BIN), "--config", str(INI), "web"], stdout=output,
                             stderr=subprocess.STDOUT, start_new_session=True)
    try:
        PID.write_text(str(p.pid))
        port = hub_port()
        for _ in range(60):
            if p.poll() is not None:
                raise SystemExit(f"❌ forge exited before becoming healthy → {LOG / 'web.out'}")
            try:
                _fetch(f"http://127.0.0.1:{port}/api/healthz", timeout=2)
                if p.poll() is not None:
                    raise SystemExit(f"❌ forge exited during startup → {LOG / 'web.out'}")
                print(f"🏠 up pid={p.pid} → http://localhost:{port}")
                return p.pid
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                time.sleep(0.5)
        raise SystemExit(f"❌ forge health check timed out → {LOG / 'web.out'}")
    except BaseException:
        # Only stop the child created by this call, never a PID read from shared state.
        stopped = p.poll() is not None
        try:
            if not stopped:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=5)
                stopped = True
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"⚠️  failed to stop startup child {p.pid}: {exc}; inspect {LOG / 'web.out'}",
                  file=sys.stderr)
        # A different manager may have replaced the PID file during startup.
        if stopped and PID.exists() and PID.read_text().strip() == str(p.pid):
            PID.unlink()
        raise


def hub_down() -> None:
    """Stop the forge."""
    if pid := _running():
        os.kill(pid, signal.SIGTERM)
        PID.unlink(missing_ok=True)
        print(f"🛑 stopped pid={pid}")


def hub_status() -> dict:
    """Dial, forge state, repo count."""
    st, pid, lv = _fstate(), _running(), read_dial()
    print(f"🎛️  {dial_label(lv)} | {'🟢 pid=' + str(pid) if pid else '⚪ down'} | 📚 {len(st['repos'])} | http://localhost:{st['port']}")
    return {"dial": lv, "pid": pid, "repos": st["repos"]}


def hub_logs(n: int = 40) -> str:
    """Tail the forge web log."""
    f = LOG / "web.out"
    out = "\n".join(f.read_text(errors="replace").splitlines()[-n:]) if f.exists() else "(no log yet)"
    print(out)
    return out


def hub_api(method: str, path: str, data: dict | None = None, token: str | None = None, base: str | None = None):
    """Gitea / Forgejo REST v1 (GitHub-shaped): hub_api('GET', '/user/repos')."""
    st = _fstate()
    url = (base or f"http://127.0.0.1:{st['port']}/api/v1") + path
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method.upper(), headers={"Authorization": f"token {token or st.get('token', '')}", "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with _open(req, 30) as r:
            raw = r.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"❌ {method} {path} → {e.code} {e.read().decode(errors='replace')[:300]}")


def _github_token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not tok and shutil.which("gh"):
        tok = _sh("gh", "auth", "token", check=False)
    if not tok:
        raise SystemExit("❌ dial 2 mirroring needs GITHUB_TOKEN or `gh auth login`")
    return tok


def _ensure_forge_repo(name: str, private: bool = True) -> None:
    if name not in {r["name"] for r in (hub_api("GET", "/user/repos?limit=200") or [])}:
        hub_api("POST", "/user/repos", {"name": name, "private": private, "default_branch": "main", "auto_init": False})
        print(f"  🆕 forge repo {name}")


def _point_origin(p: Path, level: int, st: dict) -> str:
    r = st["repos"][str(p)]
    target = "bare" if level == 0 else ("github" if level == 3 and r.get("github") else "local")
    url = _sh("git", "remote", "get-url", target, cwd=p, check=False) or _sh("git", "remote", "get-url", "bare", cwd=p)
    _sh("git", "remote", "remove", "origin", cwd=p, check=False)
    _sh("git", "remote", "add", "origin", url, cwd=p)
    print(f"  🎯 {r['name']}: origin → {target}")
    return target


def _ensure_push_mirror(r: dict, st: dict) -> None:
    if not r.get("github"):
        return
    orp, gh_url = f"{st['user']}/{r['name']}", f"https://github.com/{r['github']}.git"
    if any(m.get("remote_address", "").rstrip("/") == gh_url for m in hub_api("GET", f"/repos/{orp}/push_mirrors") or []):
        return
    hub_api("POST", f"/repos/{orp}/push_mirrors", {"remote_address": gh_url, "remote_username": r["github"].split("/")[0], "remote_password": _github_token(), "interval": "1h", "sync_on_commit": True})
    print(f"  🔁 push-mirror → {r['github']}")


def _hub_apply(level: int) -> None:
    st = _fstate()
    if level == 0:
        hub_down()
    elif BIN.exists() and INI.exists():
        hub_up()
    for path, r in st["repos"].items():
        p = Path(path)
        if not p.exists():
            continue
        _point_origin(p, level, st)
        if level >= 1 and _running():
            _ensure_forge_repo(r["name"], r.get("private", True))
            if level == 2:
                _ensure_push_mirror(r, st)


def hub_repo_add(path: str = ".", github: str | None = None, private: bool = True) -> dict:
    """Register a working tree: forge repo + bare backup, remotes `local` `bare` (`github`), origin by dial."""
    p = Path(path).resolve()
    if not (p / ".git").exists():
        _sh("git", "init", "-q", "-b", "main", cwd=p)
    st, name = _fstate(), p.name
    bare = BARE / f"{name}.git"
    if not bare.exists():
        bare.parent.mkdir(parents=True, exist_ok=True)
        _sh("git", "init", "-q", "--bare", "-b", "main", str(bare))
    if _running():
        _ensure_forge_repo(name, private)
    else:
        print("⚠️  forge down; repo is created on next `olnm_dial 1` / `hubdial up`")
    remotes = {"local": f"http://localhost:{st['port']}/{st['user']}/{name}.git", "bare": str(bare)}
    if github:
        remotes["github"] = f"https://github.com/{github}.git"
    for rname, url in remotes.items():
        _sh("git", "remote", "remove", rname, cwd=p, check=False)
        _sh("git", "remote", "add", rname, url, cwd=p)
    st["repos"][str(p)] = {"name": name, "github": github, "private": private}
    _fsave(st)
    print(f"📚 {name}  " + "  ".join(f"{k}={v}" for k, v in remotes.items()))
    _point_origin(p, read_dial(), st)
    return st["repos"][str(p)]


def hub_repo_ls() -> dict:
    """Registered repos."""
    repos = _fstate()["repos"]
    for path, r in repos.items():
        print(f"📚 {r['name']:24} {path}  {('☁️ ' + r['github']) if r.get('github') else ''}")
    return repos


def hub_repo_rm(path: str = ".") -> None:
    """Unregister a working tree (nothing deleted)."""
    st = _fstate()
    st["repos"].pop(str(Path(path).resolve()), None)
    _fsave(st)
    print("🗑️  unregistered")


def hub_sync() -> dict:
    """Push every registered repo to bare / local / github (github only at dial ≥2)."""
    st, lv, res = _fstate(), read_dial(), {}
    for path, r in st["repos"].items():
        p = Path(path)
        if not p.exists():
            continue
        for rem in ("bare", "local", "github"):
            if (rem == "local" and not _running()) or (rem == "github" and lv < 2):
                continue
            if _sh("git", "remote", "get-url", rem, cwd=p, check=False):
                ok = subprocess.run(["git", "push", "-q", "--all", rem], cwd=p, capture_output=True).returncode == 0
                res[f"{r['name']}:{rem}"] = ok
                print(f"  {'✅' if ok else '⚠️ '} {r['name']} → {rem}")
    return res


def _owner_repo(path: str = ".") -> str:
    st = _fstate()
    r = st["repos"].get(str(Path(path).resolve()))
    if not r:
        raise SystemExit("❌ not a registered repo → hubadd")
    return f"{st['user']}/{r['name']}"


def hub_issue_ls(path: str = ".", state: str = "open") -> list:
    """Issues of the current repo."""
    items = hub_api("GET", f"/repos/{_owner_repo(path)}/issues?state={state}&type=issues") or []
    for i in items:
        print(f"🐛 #{i['number']:<4} {i['title']}  {' '.join('🏷️' + l['name'] for l in i.get('labels', []))}")
    return items


def hub_issue_new(title: str, body: str = "", labels: list[str] | None = None, path: str = ".") -> dict:
    """New issue; labels by name (unknown names are skipped)."""
    orp = _owner_repo(path)
    have = {l["name"]: l["id"] for l in hub_api("GET", f"/repos/{orp}/labels") or []} if labels else {}
    it = hub_api("POST", f"/repos/{orp}/issues", {"title": title, "body": body, "labels": [have[n] for n in labels or [] if n in have]})
    print(f"🐛 #{it['number']} {it['html_url']}")
    return it


def hub_pr_ls(path: str = ".") -> list:
    """Open pull requests."""
    items = hub_api("GET", f"/repos/{_owner_repo(path)}/pulls?state=open") or []
    for p in items:
        print(f"🔀 #{p['number']:<4} {p['head']['ref']} → {p['base']['ref']}  {p['title']}")
    return items


def hub_pr_new(title: str, head: str | None = None, base: str = "main", body: str = "", path: str = ".") -> dict:
    """PR from the current branch (pushed to `local` first)."""
    p = Path(path).resolve()
    head = head or _sh("git", "branch", "--show-current", cwd=p)
    _sh("git", "push", "-q", "-u", "local", head, cwd=p)
    orp = _owner_repo(path)
    for _ in range(30):  # the forge indexes pushed branches asynchronously
        with contextlib.suppress(SystemExit):
            hub_api("GET", f"/repos/{orp}/branches/{head}")
            break
        time.sleep(0.5)
    pr = hub_api("POST", f"/repos/{orp}/pulls", {"title": title, "head": head, "base": base, "body": body})
    print(f"🔀 #{pr['number']} {pr['html_url']}")
    return pr


def hub_labels(path: str = ".") -> None:
    """GitHub's default labels (bug, enhancement, …) in the current repo."""
    orp = _owner_repo(path)
    have = {l["name"] for l in hub_api("GET", f"/repos/{orp}/labels") or []}
    for name, color in GH_LABELS.items():
        if name not in have:
            hub_api("POST", f"/repos/{orp}/labels", {"name": name, "color": "#" + color})
    print(f"🏷️  labels ready in {orp}")


def hub_doctor() -> dict:
    """Binary, config, token, forge, git, gh, GitHub reachability."""
    st = _fstate()
    checks = {"binary": BIN.exists(), "app.ini": INI.exists(), "token": bool(st.get("token")), "forge up": bool(_running()), "git": bool(shutil.which("git")), "gh": bool(shutil.which("gh"))}
    try:
        _fetch("https://api.github.com", timeout=5)
        checks["github 🌍"] = True
    except Exception:
        checks["github 🌍"] = False
    print(" ".join(("✅ " if v else "❌ ") + k for k, v in checks.items()))
    return checks



def build_parser(prog: str = "nagoyaction hub"):
    ap = argparse.ArgumentParser(prog=prog)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("hub", prog=prog, help="🏠 local GitHub-like forge"); h = s.add_subparsers(dest="sub", required=True)  # main() adds "hub"; keep it out of usage
    x = h.add_parser("install", help="📦 🌍 download or --from carried binary"); x.add_argument("--version", default="latest", help="🏷️ release number such as 1.27.3 (default: latest)"); x.add_argument("--from", dest="src", help="📁 carried binary to place instead of downloading"); x.add_argument("--sha256", dest="sha", help="🔐 expected sha256 of --from (default: its .sha256 sidecar)"); x.add_argument("--flavor", choices=sorted(FLAVORS), default="gitea", help="🍵 forge to fetch")
    x = h.add_parser("bundle", help="🎒 🌍 binary + .sha256 + nagoyaction.py into DIR"); x.add_argument("dir", help="📁 directory to fill and carry"); x.add_argument("--version", default="latest", help="🏷️ release number such as 1.27.3 (default: latest)"); x.add_argument("--flavor", choices=sorted(FLAVORS), default="gitea", help="🍵 forge to fetch")
    x = h.add_parser("init", help="🏗️ config, db, admin, token"); x.add_argument("--port", type=int, default=3000, help="🔌 HTTP port on 127.0.0.1"); x.add_argument("--user", default="admin", help="👤 admin user name"); x.add_argument("--password", help="🔑 admin password (default: a random one)")
    for name, hp in (("up", "🟢 start"), ("down", "🛑 stop"), ("status", "📊 status"), ("doctor", "🩺 checks"), ("sync", "🔄 push to all remotes"), ("labels", "🏷️ GitHub default labels")):
        h.add_parser(name, help=hp)
    x = h.add_parser("logs", help="📜 tail log"); x.add_argument("-n", type=int, default=40, help="🔢 lines to show")
    x = h.add_parser("dial", help="🎛️ show / set: offline · local · mirror · github (0-3 also work)"); x.add_argument("level", nargs="?", choices=[*DIAL_NAMES, *map(str, DIALS)], metavar="level", help="offline | local | mirror | github (0-3 also work); omit to show")
    x = h.add_parser("repo", help="📚 register working trees"); r = x.add_subparsers(dest="repo_cmd", required=True)
    y = r.add_parser("add", help="➕ register a working tree"); y.add_argument("path", nargs="?", default=".", help="📁 working tree (default: .)"); y.add_argument("--github", help="owner/name"); y.add_argument("--public", action="store_true", help="🌐 public forge repo (default: private)")
    r.add_parser("ls", help="📋 registered trees"); y = r.add_parser("rm", help="➖ unregister a working tree"); y.add_argument("path", nargs="?", default=".", help="📁 working tree (default: .)")
    x = h.add_parser("api", help="🌐 raw REST"); x.add_argument("method", choices=["GET", "POST", "PATCH", "PUT", "DELETE"], help="🔤 HTTP method"); x.add_argument("path", help="🧭 path under /api/v1, e.g. /user/repos"); x.add_argument("--data", help="JSON body")
    x = h.add_parser("issue", help="🐛 issues"); i = x.add_subparsers(dest="issue_cmd", required=True)
    y = i.add_parser("ls", help="📋 list"); y.add_argument("--state", default="open", choices=["open", "closed", "all"], help="🔍 which issues")
    y = i.add_parser("new", help="➕ open"); y.add_argument("title", help="🏷️ title"); y.add_argument("--body", default="", help="📝 body"); y.add_argument("--label", action="append", default=[], help="🏷️ label name, repeatable (unknown names are skipped)")
    x = h.add_parser("pr", help="🔀 pull requests"); p = x.add_subparsers(dest="pr_cmd", required=True)
    p.add_parser("ls", help="📋 open ones"); y = p.add_parser("new", help="➕ open from a branch (pushed to `local` first)"); y.add_argument("title", help="🏷️ title"); y.add_argument("--head", help="🌿 source branch (default: current)"); y.add_argument("--base", default="main", help="🎯 target branch"); y.add_argument("--body", default="", help="📝 body")
    _suggest(ap)
    return ap


def _suggest(parser: argparse.ArgumentParser) -> None:
    # 🤔 argparse 3.14+: "maybe you meant 'mirror'?" for choices and subcommands at every level; older Pythons ignore it
    parser.suggest_on_error = True
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for child in action.choices.values():
                _suggest(child)

def _hub_main(a: argparse.Namespace) -> None:
    match a.sub:
        case "install": hub_install(a.version, a.src, a.sha, a.flavor)
        case "bundle": hub_bundle(a.dir, a.version, flavor=a.flavor)
        case "init": hub_init(a.port, a.user, a.password)
        case "up": hub_up()
        case "down": hub_down()
        case "status": hub_status()
        case "doctor": hub_doctor()
        case "sync": hub_sync()
        case "labels": hub_labels()
        case "logs": hub_logs(a.n)
        case "dial": dial(a.level)
        case "repo": {"add": lambda: hub_repo_add(a.path, a.github, not a.public), "ls": hub_repo_ls, "rm": lambda: hub_repo_rm(a.path)}[a.repo_cmd]()
        case "api": print(json.dumps(hub_api(a.method, a.path, json.loads(a.data) if a.data else None), indent=2, ensure_ascii=False))
        case "issue": hub_issue_ls(state=a.state) if a.issue_cmd == "ls" else hub_issue_new(a.title, a.body, a.label)
        case "pr": hub_pr_ls() if a.pr_cmd == "ls" else hub_pr_new(a.title, a.head, a.base, a.body)



def local_forge_main(argv=None, prog: str = "nagoyaction hub"):
    args = build_parser(prog).parse_args(["hub", *(sys.argv[1:] if argv is None else argv)])
    _hub_main(args)
    return 0


# ====================================================================================================
# 🧪 localci: ワークフローとテストを手元で検査する（nagoyaction localci … / actionlint）（旧 localci.py）
# ローカル CI。GitHub Actions を待たずに、ワークフローとテストを手元で検査する。
#
#   python nagoyaction.py localci run --repeat 10
#   python nagoyaction.py localci run --repeat 10 --seed 7 --keep-going
#   python nagoyaction.py localci run --self-tests
#   python nagoyaction.py localci run --strict
#   python nagoyaction.py localci resolve --github-output
#
# `--repeat N` は同じ検査を N 回なぞらない。検査の一覧を seed でシャッフルし、
# ほぼ等しい N 個のシャードに分け、1 ラウンドに 1 シャードだけ実行する。
# 全ラウンドが終わると各検査はちょうど一度だけ走る。失敗したラウンドで止まり、
# ラウンド番号・シャードの中身・seed を出す。`--keep-going` で最後まで続ける。
#
# 既定の pytest は Aoi の `tests/` 全体。実行時に解決した SHA を `.localci/aoi`
# に checkout し、HEAD がその SHA であることを確かめてから、このリポジトリの
# tree を `nagoyaction/` に重ねる。`--self-tests` は Aoi を取らず
# `tests/test_localci.py` だけを実行する。
#
# 特定の固定値で通る検査は `substitute` で、そのラウンドの seed から別の値に差し替える。
# pytest では `-p nagoyaction` が同じ差し替えを monkeypatch する。
#
# 参照先（Aoi、myon-bioinformatics/myon-bioinformatics、vendor）の main SHA は
# `git ls-remote` と GitHub API の repository id 照合で実行時に解決する。
# SHA はソースに固定しない。`uses:` のピンが各アクションの最新リリースタグの
# コミットと一致するかは、既定では報告だけする。`--strict` で古い SHA ピンと、
# setup アクションの SHA でないピンを失敗にする。setup 以外の actions/* の
# メジャータグ `vN`（checkout、upload-artifact、download-artifact、cache など）は許す。
#
# actionlint の版もソースに固定しない。実行のたびに最新リリースを解決し、
# タグ・資産名・検証した sha256 を記録する。GitHub Actions では取得か検証に
# 失敗したら停止する。手元では、解決済みのタグだけ `go run ...@<tag>` に戻る。
# `.localci/refs.env` は追記しない。キーごとに1行へ原子的に書き換え、同じキーは
# 後の値を残し、並びはファイルに最初に出た順を保つ。
#
# 標準ライブラリだけ（Python 3.11+）。
# ====================================================================================================

class LocalCIError(Exception):
    pass


class Unreachable(LocalCIError):
    """GitHub が応答しない（経路なし・DNS・タイムアウト）。閉域網はここに来る。"""


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
MAJOR_TAG_RE = re.compile(r"^v[0-9]+$")
# 親は setup をリリースの 40 桁 SHA にする。actions/setup-* と setup-uv。
_SETUP_ACTIONS = frozenset({
    "actions/setup-python",
    "actions/setup-node",
    "astral-sh/setup-uv",
})
_USES = re.compile(r"^[ \t]*(?:-[ \t]*)?uses:[ \t]*(?P<value>.+?)[ \t]*$", re.M)

# repository id はコミット SHA ではなく、取り違えを防ぐための公開の数値 ID。
@dataclass(frozen=True)
class Source:
    key: str
    env: str
    repo: str
    repository_id: int | None


SOURCES = (
    Source("aoi", "AOI_SHA", "myon-bioinformatics/Aoi", 1402862784),
    Source("myon_bioinformatics", "MYON_BIOINFORMATICS_SHA", "myon-bioinformatics/myon-bioinformatics", 638801160),
    Source("markdown", "MARKDOWN_SHA", "myon-bioinformatics/markdown", 1374546518),
    Source("web_ui", "WEB_UI_SHA", "myon-bioinformatics/PySaiyanWeBoo", 1382466695),
)

_OS = {"Linux": "linux", "Darwin": "darwin", "Windows": "windows"}
_ARCH = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64", "i386": "386", "i686": "386"}
_active_rng: random.Random | None = None
_substitutions: list[dict] = []


@dataclass(frozen=True)
class Check:
    id: str
    kind: str
    target: str
    file: str = ""
    ref: str = ""
    repo: str = ""


@dataclass
class Outcome:
    status: str
    detail: str
    inputs: list[dict]

    @property
    def ok(self) -> bool:
        return self.status == "pass"


@dataclass
class Resolved:
    source: Source
    sha: str
    how: str
    repository_id: int


@dataclass(frozen=True)
class ActionlintRecord:
    tag: str
    asset: str
    sha256: str
    binary: Path | None
    via: str  # release | go | path、best effort では cache | none も
    note: str = ""  # best effort: 最新版を使えなかった理由


@dataclass
class RoundReport:
    number: int
    seed: int
    shard: list[str]
    passed: bool
    failed_check: str | None
    lines: list[str]
    skipped: int = 0
    not_run: int = 0
    pytest_skipped: int = 0
    batch_error: str = ""

    @property
    def confirmed_pass(self) -> bool:
        return self.passed and bool(self.shard) and not (self.skipped or self.not_run)


@dataclass
class PlanReport:
    master_seed: int
    rounds: list[RoundReport]
    stopped: bool

    @property
    def passed_rounds(self) -> int:
        return sum(1 for r in self.rounds if r.confirmed_pass)


def substitute(name: str, value, draw):
    """固定値を返す。ラウンドの seed が有効なときは draw(rng) に差し替える。"""
    rng = _active_rng
    if rng is None:
        return value
    drawn = draw(rng)
    _substitutions.append({"name": name, "fixed": value, "value": drawn})
    return drawn


def take_substitutions() -> list[dict]:
    found = list(_substitutions)
    _substitutions.clear()
    return found


class use_seed:
    def __init__(self, seed: int):
        self.seed = seed
        self.previous = None

    def __enter__(self) -> random.Random:
        global _active_rng
        self.previous = _active_rng
        _substitutions.clear()
        _active_rng = random.Random(self.seed)
        return _active_rng

    def __exit__(self, *exc) -> None:
        global _active_rng
        _active_rng = self.previous


def mix_seed(master: int, *parts: object) -> int:
    material = ":".join([str(master), *map(str, parts)]).encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def split_shards(items: list, repeat: int, seed: int) -> list[list]:
    """seed でシャッフルし、各要素がちょうど一つのシャードに入るよう N 等分する。"""
    if repeat < 1:
        raise ValueError("repeat must be >= 1")
    ordered = list(items)
    random.Random(seed).shuffle(ordered)
    total = len(ordered)
    base, extra = divmod(total, repeat)
    shards: list[list] = []
    start = 0
    for i in range(repeat):
        size = base + (1 if i < extra else 0)
        shards.append(ordered[start:start + size])
        start += size
    return shards


def shard_for_round(items: list, repeat: int, round_no: int, seed: int) -> list:
    if not 1 <= round_no <= repeat:
        raise ValueError(f"round {round_no} is outside 1..{repeat}")
    return split_shards(items, repeat, seed)[round_no - 1]


def confidence_line(passed: int, total: int, completed: int, stopped: bool) -> str:
    text = f"confidence: {passed}/{total} rounds passed, {completed}/{total} completed"
    if stopped:
        return text + "; stopped"
    return text


def _strip_yaml_comment(text: str) -> str:
    if text[:1] in {"'", '"'}:
        quote = text[0]
        end = text.find(quote, 1)
        if end != -1:
            return text[1:end]
    mark = text.find(" #")
    if mark != -1:
        return text[:mark]
    return text


def parse_action_ref(value: str) -> dict | None:
    value = value.strip()
    if not value or value.startswith(("./", "docker://")) or "${{" in value:
        return None
    if "@" in value:
        left, ref = value.rsplit("@", 1)
    else:
        left, ref = value, ""
    parts = [p for p in left.split("/") if p]
    if len(parts) < 2:
        return None
    return {"repo": f"{parts[0]}/{parts[1]}", "path": "/".join(parts[2:]), "ref": ref.strip(), "raw": value}


def parse_uses(text: str) -> list[dict]:
    found = []
    for match in _USES.finditer(text):
        raw = _strip_yaml_comment(match.group("value").strip()).strip()
        parsed = parse_action_ref(raw)
        if parsed is None:
            continue
        parsed["line"] = text.count("\n", 0, match.start()) + 1
        found.append(parsed)
    return found


def is_setup_action(repo: str) -> bool:
    """親が 40 桁 SHA と `# vX.Y.Z` で書く setup アクション。"""
    return repo in _SETUP_ACTIONS or repo.startswith("actions/setup-")


def allows_major_tag(repo: str) -> bool:
    """setup 以外の actions/* は動くメジャータグ vN でよい。"""
    return repo.startswith("actions/") and not is_setup_action(repo)


def classify_pin(ref: str, latest: tuple[str, str] | None, repo: str = "") -> str:
    """latest は (tag, commit SHA)。リリースが無ければ None。

    setup 以外の actions/* のメジャータグ vN は major。
    それ以外で SHA でないピンは unpinned。
    SHA でリリースが無ければ no-release。一致すれば match、違えば outdated。
    """
    if MAJOR_TAG_RE.fullmatch(ref) and allows_major_tag(repo):
        return "major"
    if not SHA_RE.fullmatch(ref.lower()):
        return "unpinned"
    if latest is None:
        return "no-release"
    _tag, sha = latest
    if ref.lower() == sha.lower():
        return "match"
    return "outdated"


def pin_fails(status: str, strict: bool) -> bool:
    """major は setup 以外の actions/* の動くメジャータグ。`--strict` でも失敗にしない。"""
    return strict and status in {"outdated", "unpinned"}


def github_token(env: dict | None = None) -> str:
    env = os.environ if env is None else env
    return env.get("GITHUB_TOKEN") or env.get("GH_TOKEN") or ""


def github_json(url: str, token: str, opener=urllib.request.urlopen, timeout: float = 60):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nagoyaction-localci"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener(req, timeout=timeout) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        raise LocalCIError(f"GitHub API {exc.code} for {url}") from exc
    except json.JSONDecodeError as exc:
        raise LocalCIError(f"GitHub API failed for {url}: {exc}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise Unreachable(f"GitHub API failed for {url}: {exc}") from exc


def fetch_bytes(url: str, token: str, opener=urllib.request.urlopen, timeout: float = 60) -> bytes:
    headers = {"User-Agent": "nagoyaction-localci"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise LocalCIError(f"download {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LocalCIError(f"download failed for {url}: {exc}") from exc


def git_env(base: dict | None = None) -> dict:
    env = dict(os.environ if base is None else base)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
    return env


def parse_ls_remote(listing: str, ref: str) -> str | None:
    want = ref
    for line in listing.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == want and SHA_RE.fullmatch(parts[0].lower()):
            return parts[0].lower()
    return None


def ls_remote(repo: str, ref: str, runner=subprocess.run) -> str:
    url = f"https://github.com/{repo}"
    try:
        out = runner(
            ["git", "ls-remote", url, ref],
            capture_output=True, text=True, check=False, timeout=60, env=git_env(),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise LocalCIError(f"git ls-remote failed for {repo} {ref}: {exc}") from exc
    if out.returncode != 0:
        detail = (out.stderr or out.stdout or "").strip()
        raise LocalCIError(f"git ls-remote failed for {repo} {ref}: {detail}")
    peeled = parse_ls_remote(out.stdout or "", ref + "^{}")
    direct = parse_ls_remote(out.stdout or "", ref)
    sha = peeled or direct
    if sha is None:
        raise LocalCIError(f"could not resolve {repo} {ref}")
    return sha


def verify_repository(repo: str, expected_id: int | None, data: dict) -> int:
    full = str(data.get("full_name", "")).lower()
    if full != repo.lower():
        raise LocalCIError(f"{repo}: repository id mismatch")
    got = data.get("id")
    if expected_id is not None and got != expected_id:
        raise LocalCIError(f"{repo}: repository id mismatch")
    if data.get("visibility") not in (None, "public") or data.get("private") is True:
        raise LocalCIError(f"{repo}: repository is not public")
    if type(got) is not int:
        raise LocalCIError(f"{repo}: repository id missing")
    return got


def resolve_ref(repo: str, ref_input: str, runner=subprocess.run) -> tuple[str, str]:
    """ref を SHA にする。40 桁の SHA はそのまま使う。戻り値は (sha, how)。"""
    text = ref_input.strip()
    if re.fullmatch(r"[0-9a-fA-F]{40}", text):
        return text.lower(), "workflow_dispatch input"
    if re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", text):
        return ls_remote(repo, text, runner), text
    if re.fullmatch(r"[A-Za-z0-9._/-]+", text):
        ref = "refs/heads/" + text
        return ls_remote(repo, ref, runner), ref
    raise LocalCIError("invalid aoi_ref")


def sources_for(root: Path) -> list[Source]:
    found = list(SOURCES)
    seen = {s.repo.lower() for s in found}
    lock = root / "vendor.lock.json"
    if not lock.is_file():
        return found
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LocalCIError(f"vendor.lock.json: {exc}") from exc
    repos: list[str] = []
    files = data.get("files", [])
    if isinstance(files, list):
        repos = [str(item.get("repository", "")) for item in files if isinstance(item, dict)]
    elif isinstance(files, dict):
        repos = [str(item.get("source_repo", "")) for item in files.values() if isinstance(item, dict)]
    for repo in repos:
        if repo and repo.lower() not in seen:
            key = re.sub(r"[^A-Za-z0-9]+", "_", repo).strip("_").upper()
            found.append(Source(key.lower(), key + "_SHA", repo, None))
            seen.add(repo.lower())
    return found


def resolve_source(source: Source, ref_input: str = "", *, token: str = "",
                   runner=subprocess.run, opener=urllib.request.urlopen) -> Resolved:
    data = github_json(f"https://api.github.com/repos/{source.repo}", token, opener)
    repository_id = verify_repository(source.repo, source.repository_id, data)
    if ref_input.strip():
        sha, how = resolve_ref(source.repo, ref_input, runner)
    else:
        how = "refs/heads/main"
        sha = ls_remote(source.repo, how, runner)
    return Resolved(source, sha, how, repository_id)


def resolve_sources(root: Path, aoi_ref: str = "", *, token: str = "",
                    runner=subprocess.run, opener=urllib.request.urlopen) -> list[Resolved]:
    resolved = []
    for source in sources_for(root):
        override = aoi_ref if source.key == "aoi" else ""
        resolved.append(resolve_source(source, override, token=token, runner=runner, opener=opener))
    return resolved


def provenance_mode(event_name: str, github_ref: str) -> str:
    if event_name == "schedule":
        return "strict"
    if event_name == "push" and github_ref == "refs/heads/main":
        return "strict"
    return "report-only"


_ENV_HEADER = "# localci resolved refs. source: git ls-remote + repository id check"
_ENV_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def env_pairs(resolved: list[Resolved]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in resolved:
        pairs.append((item.source.env, item.sha))
        pairs.append((f"{item.source.env.removesuffix('_SHA')}_REPOSITORY_ID", str(item.repository_id)))
    return pairs


def actionlint_pairs(record: ActionlintRecord) -> list[tuple[str, str]]:
    pairs = [("ACTIONLINT_TAG", record.tag), ("ACTIONLINT_ASSET", record.asset)]
    if record.sha256:
        pairs.append(("ACTIONLINT_SHA256", record.sha256))
    return pairs


def merge_env_lines(existing: str, updates: list[tuple[str, str]], *,
                    header: str | None = None, drop: tuple[str, ...] = ()) -> str:
    """同じキーは後の値を残す。並びは最初に出た順で、新しいキーは末尾に足す。"""
    order: list[str] = []
    values: dict[str, str] = {}
    kept = header
    for raw in existing.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if kept is None:
                kept = line
            continue
        key, sep, value = line.partition("=")
        if sep == "" or _ENV_KEY.fullmatch(key) is None:
            continue
        if key not in values:
            order.append(key)
        values[key] = value
    for key, value in updates:
        if key not in values:
            order.append(key)
        values[key] = value
    for key in drop:
        if key in values:
            del values[key]
            order.remove(key)
    lines: list[str] = []
    if kept:
        lines.append(kept)
    lines.extend(f"{key}={values[key]}" for key in order)
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def atomic_write_text(path: Path, text: str) -> None:
    """同じディレクトリへ書いてから replace する。失敗しても宛先の中身は残る。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def rewrite_env_file(path: Path, updates: list[tuple[str, str]], *,
                     header: str | None = None, drop: tuple[str, ...] = ()) -> None:
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    atomic_write_text(path, merge_env_lines(existing, updates, header=header, drop=drop))


def format_env(resolved: list[Resolved]) -> str:
    return merge_env_lines("", env_pairs(resolved), header=_ENV_HEADER)


def write_env_file(path: Path, resolved: list[Resolved]) -> None:
    rewrite_env_file(path, env_pairs(resolved), header=_ENV_HEADER)


def write_actionlint_env(path: Path, record: ActionlintRecord) -> None:
    drop = () if record.sha256 else ("ACTIONLINT_SHA256",)
    rewrite_env_file(path, actionlint_pairs(record), drop=drop)


def format_github_output(resolved: list[Resolved]) -> str:
    lines = []
    for item in resolved:
        lines.append(f"{item.source.key}_sha={item.sha}")
        if item.source.key == "aoi":
            lines.append(f"sha={item.sha}")
    return "\n".join(lines) + ("\n" if lines else "")


def running_in_github_actions() -> bool:
    return os.environ.get("GITHUB_ACTIONS") == "true"


def format_actionlint_line(record: ActionlintRecord) -> str:
    sha = record.sha256 if record.sha256 else "unverified"
    via = f"go@{record.tag}" if record.via == "go" and record.tag else record.via
    return f"actionlint tag={record.tag} asset={record.asset} sha256={sha} via={via}"


def format_actionlint_env(record: ActionlintRecord) -> str:
    return merge_env_lines("", actionlint_pairs(record))


def format_run_summary(resolved: list[Resolved], actionlint: ActionlintRecord | None) -> str:
    """解決した参照先 SHA と、その隣に actionlint の解決結果を書く。"""
    lines = ["## Resolved repositories"]
    if not resolved:
        lines.append("No repository SHA was resolved.")
    for item in resolved:
        lines.append(f"- `{item.source.repo}` `{item.sha}` ({item.how}), repository id `{item.repository_id}`")
    lines.append("")
    lines.append("## actionlint")
    if actionlint is None or not actionlint.tag:
        lines.append("actionlint was not resolved.")
    else:
        lines.append(f"- Tag: `{actionlint.tag}`")
        lines.append(f"- Asset: `{actionlint.asset}`")
        if actionlint.sha256:
            lines.append(f"- sha256: `{actionlint.sha256}`")
        else:
            lines.append("- sha256: not verified")
        via = f"go@{actionlint.tag}" if actionlint.via == "go" else actionlint.via
        lines.append(f"- via: `{via}`")
    return "\n".join(lines) + "\n"


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text)


def format_step_summary(resolved: list[Resolved], mode: str) -> str:
    aoi = next((item for item in resolved if item.source.key == "aoi"), None)
    lines = ["## Aoi source"]
    if aoi is None:
        lines.append("Aoi was not resolved.")
    else:
        lines.append(f"Resolved `{aoi.sha}` from `{aoi.how}`.")
        lines.append(f"Repository id `{aoi.repository_id}`.")
        lines.append(f"Source-hash provenance: {mode}.")
    lines.append("")
    lines.append("## Referenced repositories")
    for item in resolved:
        lines.append(f"- `{item.source.repo}` `{item.sha}` ({item.how}), repository id `{item.repository_id}`")
    return "\n".join(lines) + "\n"


def latest_release(repo: str, *, token: str = "", opener=urllib.request.urlopen,
                   runner=subprocess.run) -> tuple[str, str] | None:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nagoyaction-localci"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener(req, timeout=60) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise LocalCIError(f"GitHub API {exc.code} for {url}") from exc
    except json.JSONDecodeError as exc:
        raise LocalCIError(f"GitHub API failed for {url}: {exc}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise Unreachable(f"GitHub API failed for {url}: {exc}") from exc
    tag = str(data.get("tag_name", ""))
    if not tag:
        return None
    sha = ls_remote(repo, "refs/tags/" + tag, runner)
    return tag, sha


def workflow_files(root: Path) -> list[Path]:
    directory = root / ".github" / "workflows"
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml"))


def workflow_uses(root: Path) -> list[dict]:
    rows = []
    for path in workflow_files(root):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(root))
        for item in parse_uses(text):
            item = dict(item)
            item["file"] = rel
            rows.append(item)
    return rows


def actionlint_archive(version: str, system: str, machine: str) -> str:
    goos = _OS.get(system)
    goarch = _ARCH.get(machine)
    if not goos or not goarch:
        raise LocalCIError(f"unsupported platform {system}/{machine}")
    ext = "zip" if goos == "windows" else "tar.gz"
    return f"actionlint_{version}_{goos}_{goarch}.{ext}"


def checksum_for(text: str, filename: str) -> str:
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2 or not re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            continue
        name = parts[-1][1:] if parts[-1].startswith("*") else parts[-1]
        if name == filename:
            return parts[0].lower()
    raise LocalCIError(f"no checksum for {filename}")


def verify_bytes(data: bytes, expected: str, label: str) -> None:
    got = hashlib.sha256(data).hexdigest()
    if got != expected.lower():
        raise LocalCIError(f"checksum mismatch for {label}")


def _asset_digest(asset: dict) -> str | None:
    digest = str(asset.get("digest", ""))
    if digest.startswith("sha256:"):
        return digest.split(":", 1)[1].lower()
    return None


def extract_actionlint(archive: bytes, filename: str) -> bytes:
    name = "actionlint.exe" if filename.endswith(".zip") else "actionlint"
    if filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(archive)) as zf:
            member = next((info for info in zf.infolist() if Path(info.filename).name == name), None)
            if member is None or member.is_dir():
                raise LocalCIError("actionlint binary missing from archive")
            return zf.read(member)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        member = next((info for info in tar.getmembers() if Path(info.name).name == "actionlint" and info.isfile()), None)
        if member is None or member.issym() or member.islnk():
            raise LocalCIError("actionlint binary missing from archive")
        extracted = tar.extractfile(member)
        if extracted is None:
            raise LocalCIError("actionlint binary missing from archive")
        return extracted.read()


_ACTIONLINT_RECORD = "actionlint.record.json"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _read_actionlint_record(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    sha = str(data.get("sha256", "")).lower()
    if not _HEX64.fullmatch(sha):
        return None
    return {"tag": str(data.get("tag", "")), "asset": str(data.get("asset", "")), "sha256": sha}


def _install_actionlint(cache: Path, release: dict, tag: str, version: str, filename: str, *,
                        token: str, opener) -> ActionlintRecord:
    dest = cache / "actionlint" / version / ("actionlint.exe" if filename.endswith(".zip") else "actionlint")
    record_path = dest.parent / _ACTIONLINT_RECORD
    saved = _read_actionlint_record(record_path)
    if dest.is_file() and os.access(dest, os.X_OK) and saved and saved["tag"] == tag and saved["asset"] == filename:
        return ActionlintRecord(tag, filename, saved["sha256"], dest, "release")
    assets = {item.get("name"): item for item in release.get("assets", [])}
    archive_asset = assets.get(filename)
    checksum_name = f"actionlint_{version}_checksums.txt"
    checksum_asset = assets.get(checksum_name)
    if not archive_asset or not checksum_asset:
        raise LocalCIError(f"actionlint release is missing {filename}")
    archive = fetch_bytes(archive_asset["browser_download_url"], token, opener)
    checksum_bytes = fetch_bytes(checksum_asset["browser_download_url"], token, opener)
    archive_digest = _asset_digest(archive_asset)
    checksum_digest = _asset_digest(checksum_asset)
    if archive_digest:
        verify_bytes(archive, archive_digest, filename)
    if checksum_digest:
        verify_bytes(checksum_bytes, checksum_digest, checksum_name)
    expected = checksum_for(checksum_bytes.decode("utf-8", "replace"), filename).lower()
    verify_bytes(archive, expected, filename)
    payload = extract_actionlint(archive, filename)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(payload)
    dest.chmod(0o755)
    record_path.write_text(
        json.dumps({"tag": tag, "asset": filename, "sha256": expected}) + "\n",
        encoding="utf-8",
    )
    return ActionlintRecord(tag, filename, expected, dest, "release")


def ensure_actionlint(cache: Path, *, token: str = "", opener=urllib.request.urlopen,
                      system: str | None = None, machine: str | None = None) -> ActionlintRecord:
    """最新リリースを解決する。版はソースに固定しない。

    取得と checksum/digest の検証に成功した sha256 だけを記録する。
    GitHub Actions では失敗したらそこで止まる。手元では、タグを解決できたときだけ
    Go のそのタグへ戻す（`@latest` には戻さない）。
    """
    system = system or sys.platform
    if system == "linux":
        system = "Linux"
    elif system == "darwin":
        system = "Darwin"
    elif system in {"win32", "windows"}:
        system = "Windows"
    if machine is None:
        if system == "Windows":
            machine = os.environ.get("PROCESSOR_ARCHITECTURE", "amd64")
        else:
            machine = os.uname().machine
    release = github_json("https://api.github.com/repos/rhysd/actionlint/releases/latest", token, opener)
    tag = str(release.get("tag_name", ""))
    version = tag[1:] if tag.startswith("v") else tag
    if not version:
        raise LocalCIError("actionlint release has no tag")
    try:
        filename = actionlint_archive(version, system, machine)
        return _install_actionlint(cache, release, tag, version, filename, token=token, opener=opener)
    except (LocalCIError, OSError) as exc:
        if running_in_github_actions():
            raise LocalCIError(f"actionlint {tag}: {exc}") from exc
        asset = ""
        try:
            asset = actionlint_archive(version, system, machine)
        except LocalCIError:
            asset = ""
        return ActionlintRecord(tag, asset, "", None, "go")


def cached_actionlint(cache: Path) -> ActionlintRecord | None:
    """以前の実行が取得して検証した中で、いちばん新しい版。"""
    found = []
    for record_path in (cache / "actionlint").glob(f"*/{_ACTIONLINT_RECORD}"):
        saved = _read_actionlint_record(record_path)
        binary = next((path for name in ("actionlint", "actionlint.exe")
                       if (path := record_path.parent / name).is_file() and os.access(path, os.X_OK)), None)
        if saved and binary:
            version = tuple(int(part) for part in re.findall(r"\d+", record_path.parent.name))
            found.append((version, ActionlintRecord(saved["tag"], saved["asset"], saved["sha256"], binary, "cache")))
    return max(found, key=lambda item: item[0])[1] if found else None


def local_actionlint(cache: Path, note: str, which=None) -> ActionlintRecord:
    """best effort: 最新版を使えないとき、取得済みの検証済み版 → PATH の actionlint → 無し（検査は skip）。"""
    if record := cached_actionlint(cache):
        return ActionlintRecord(record.tag, record.asset, record.sha256, record.binary, "cache", note)
    if found := (which or shutil.which)("actionlint"):
        return ActionlintRecord("", "", "", Path(found), "path", note)
    return ActionlintRecord("", "", "", None, "none", note)


def format_best_effort_line(record: ActionlintRecord) -> str:
    use = {"cache": f"取得済みの {record.tag} を使う", "path": f"PATH の {record.binary} を使う"}.get(record.via, "使えるものが無いので検査しない。actionlint を PATH に置けば使う")
    return f"actionlint: 最新版を使えない（{record.note}）→ {use}"


def actionlint_argv(binary: Path | None, files: list[str], shellcheck: str | None,
                    go_ref: str | None = None) -> list[str]:
    if binary is not None:
        cmd = [str(binary)]
    elif go_ref and go_ref not in {"latest", "@latest"}:
        ref = go_ref[1:] if go_ref.startswith("@") else go_ref
        cmd = ["go", "run", f"github.com/rhysd/actionlint/cmd/actionlint@{ref}"]
    else:
        raise LocalCIError("actionlint tag was not resolved")
    if shellcheck:
        cmd.extend(["-shellcheck", shellcheck])
    else:
        cmd.append("-shellcheck=")
    cmd.extend(files)
    return cmd


def shellcheck_path(which=shutil.which) -> str | None:
    return which("shellcheck")


def parse_collect_only(stdout: str) -> list[str]:
    """`--collect-only -q` の各行を node id として読む。空白や括弧を含む id も切らない。"""
    nodeids = []
    for line in stdout.splitlines():
        text = line.strip()
        if "::" not in text or text.startswith(("=", "-", "ERROR", "collected", "warning", "!", "<")):
            continue
        if " collected in " in text or text.endswith(" collected"):
            continue
        nodeids.append(text)
    return nodeids


def collect_pytest(paths: list[str], root: Path, runner=subprocess.run) -> tuple[list[str], list[str]]:
    if importlib_pytest() is None:
        return [], ["pytest が見つからない"]
    try:
        out = runner(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", "--continue-on-collection-errors", *paths],
            cwd=root, capture_output=True, text=True, check=False, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [], [f"pytest collection failed: {exc}"]
    nodeids = parse_collect_only(out.stdout or "")
    limits = []
    for line in ((out.stdout or "") + "\n" + (out.stderr or "")).splitlines():
        if "ERROR collecting" in line or line.startswith("ERROR "):
            limits.append(line.strip())
    if out.returncode != 0 and not nodeids and not limits:
        limits.append("pytest collection failed")
    return nodeids, limits


def importlib_pytest():
    import importlib.util
    return importlib.util.find_spec("pytest")


def _read_input_log(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        found.append({"name": parts[0], "fixed": parts[1], "value": parts[2]})
    return found


AOI_PYTEST_PREFIX = ["uv", "run", "--locked", "--python", "3.11", "pytest", "-c", "pyproject.toml"]


def _git(runner, argv: list[str], *, cwd: Path, timeout: int, text: bool = True):
    try:
        out = runner(argv, cwd=cwd, capture_output=True, text=text, check=False, timeout=timeout, env=git_env())
    except (OSError, subprocess.SubprocessError) as exc:
        raise LocalCIError(f"{' '.join(argv)} failed: {exc}") from exc
    if out.returncode != 0:
        err = out.stderr or out.stdout or ""
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        raise LocalCIError(f"{' '.join(argv)} failed: {str(err).strip()}")
    return out


def checkout_aoi(root: Path, resolved: Resolved, *, runner=subprocess.run, remote: str | None = None) -> Path:
    """解決済み SHA を `.localci/aoi` に checkout し、HEAD が一致しなければ失敗する。"""
    if not SHA_RE.fullmatch(resolved.sha):
        raise LocalCIError(f"resolved Aoi SHA is not 40 hex digits: {resolved.sha}")
    dest = root / ".localci" / "aoi"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        if dest.exists():
            shutil.rmtree(dest)
        url = remote or f"https://github.com/{resolved.source.repo}"
        _git(runner, ["git", "clone", "--no-checkout", url, str(dest)], cwd=root, timeout=600)
    fetch = resolved.how if resolved.how.startswith("refs/") else resolved.sha
    _git(runner, ["git", "fetch", "--no-tags", "origin", fetch], cwd=dest, timeout=600)
    _git(runner, ["git", "checkout", "-f", "--detach", resolved.sha], cwd=dest, timeout=180)
    head = _git(runner, ["git", "rev-parse", "HEAD"], cwd=dest, timeout=60).stdout.strip().lower()
    if head != resolved.sha:
        raise LocalCIError(f"Aoi checkout {head} does not match resolved {resolved.sha}")
    return dest


def overlay_nagoyaction(aoi: Path, root: Path, *, runner=subprocess.run) -> None:
    """このリポジトリの commit 済み tree を Aoi の nagoyaction/ に重ね、tree が一致することを確かめる。"""
    dest = aoi / "nagoyaction"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    out = _git(runner, ["git", "archive", "HEAD"], cwd=root, timeout=120, text=False)
    blob = out.stdout if isinstance(out.stdout, bytes) else (out.stdout or "").encode()
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as tar:
            try:
                tar.extractall(dest, filter="data")
            except TypeError:
                tar.extractall(dest)
    except (tarfile.TarError, OSError) as exc:
        raise LocalCIError(f"git archive extract failed: {exc}") from exc
    _git(runner, ["git", "add", "-A", "nagoyaction"], cwd=aoi, timeout=120)
    tree = _git(runner, ["git", "write-tree", "--prefix=nagoyaction/"], cwd=aoi, timeout=60).stdout.strip()
    expected = _git(runner, ["git", "rev-parse", "HEAD^{tree}"], cwd=root, timeout=60).stdout.strip()
    if tree != expected:
        raise LocalCIError(f"nagoyaction overlay {tree} does not match HEAD^{{tree}} {expected}")


def child_pytest_env(cwd: Path) -> dict:
    env = git_env()
    plugin_root = cwd if (cwd / "nagoyaction.py").is_file() else cwd / "nagoyaction"
    env["PYTHONPATH"] = str(plugin_root) + os.pathsep + env.get("PYTHONPATH", "")
    return env


class PytestBatch(dict[str, Outcome]):
    """Keep session errors separate from observed node outcomes."""
    batch_error: str = ""

    @classmethod
    def unobserved(cls, checks, error):
        batch = cls((check.id, Outcome("not_run", "not run", [])) for check in checks)
        batch.batch_error = error
        return batch


def _batch_outcomes(checks, returncode, detail, inputs, receipt, *, timed_out=False):
    by_node = {}
    receipt_error = ""
    try:
        for lineno, line in enumerate(receipt.read_text(encoding="utf-8").splitlines(), 1):
            node, phase, status, reason = json.loads(line)
            if not isinstance(node, str) or not isinstance(reason, str):
                raise ValueError("invalid pytest evidence")
            phases = by_node.setdefault(node, {})
            if phase == "subtest" and status in ("failed", "skipped"):
                # Multiple subtests share one parent node; only the strongest
                # non-pass outcome is relevant to the parent receipt.
                if phases.get(phase, ("", ""))[0] != "failed":
                    phases[phase] = (status, reason)
                continue
            if phase in phases:
                raise ValueError(f"duplicate pytest phase at receipt line {lineno}")
            if phase not in ("setup", "call", "teardown") or status not in ("passed", "failed", "skipped"):
                raise ValueError(f"invalid pytest phase at receipt line {lineno}")
            phases[phase] = (status, reason)
    except FileNotFoundError:
        receipt_error = "receipt not created"
    except OSError:
        receipt_error = "receipt unreadable"
    except (TypeError, ValueError) as exc:
        receipt_error = f"malformed receipt ({exc})"
        by_node.clear()

    results = PytestBatch()
    for check in checks:
        phases = by_node.get(check.target, {})
        setup, call, teardown = (phases.get(key, ("", ""))[0] for key in ("setup", "call", "teardown"))
        subtest, subreason = phases.get("subtest", ("", ""))
        if "failed" in (setup, call, teardown, subtest):
            outcome = Outcome("fail", f"failed {check.target}", [])
        elif (setup, call, teardown) == ("passed", "passed", "passed"):
            # Pytest treats non-strict XPASS as successful, strict XPASS as failed.
            outcome = (Outcome("skip", f"pytest subtest skipped {check.target}" +
                               (f": {subreason}" if subreason else ""), [])
                       if subtest == "skipped" else Outcome("pass", "", []))
        elif teardown in ("passed", "skipped") and (
            (setup == "skipped" and not call) or
            (setup == "passed" and call in ("passed", "skipped") and "skipped" in (call, teardown))
        ):
            reason = next(phases[key][1] for key in ("setup", "call", "teardown") if phases.get(key, ("", ""))[0] == "skipped")
            outcome = Outcome("skip", f"pytest skipped {check.target}" + (f": {reason}" if reason else ""), [])
        else:
            outcome = Outcome("not_run", "not run", [])
        results[check.id] = outcome
    failed = next((key for key, out in results.items() if out.status == "fail"), None)
    missing = next((key for key, out in results.items() if out.status == "not_run"), None)
    if timed_out and checks:
        interrupted = next((check.id for check in checks
                            if results[check.id].status == "not_run" and check.target in by_node), None)
        if interrupted:
            failed = interrupted
            results[failed] = Outcome("fail", "pytest batch timed out", [])
        else:
            results.batch_error = "pytest batch timed out"
    if checks and not failed and not results.batch_error:
        if missing:
            results.batch_error = "pytest batch failed or has missing per-test evidence"
            if receipt_error:
                results.batch_error += f": {receipt_error}"
        elif returncode:
            results.batch_error = f"pytest session exited {returncode}"
    if results.batch_error and detail:
        results.batch_error += "\n" + detail
    if failed:
        results[failed].detail += "\n" + detail if detail else ""
        results[failed].inputs.extend(inputs)
    elif checks:
        results[checks[0].id].inputs.extend(inputs)
    return results


def run_pytest_batch(checks: list[Check], round_seed: int, *, cwd: Path, prefix: list[str],
                     keep_going: bool, runner=subprocess.run) -> dict[str, Outcome]:
    """Run one shard in a single pytest process and observe each node."""
    handle = tempfile.NamedTemporaryFile(prefix="localci-inputs-", suffix=".log", delete=False)
    log = Path(handle.name)
    handle.close()
    cmd = [*prefix, "-q", "--tb=line", "-p", "nagoyaction", "--localci-round-seed", str(round_seed)]
    if not keep_going:
        cmd.append("-x")
    try:
        with tempfile.TemporaryDirectory(prefix="localci-pytest-") as temp:
            receipt = Path(temp) / "outcomes.jsonl"
            # Pass the destination only to this pytest invocation; a nested
            # pytest must never write to the enclosing session's receipt.
            cmd.extend(["--localci-receipt", str(receipt), *(check.target for check in checks)])
            env = child_pytest_env(cwd)
            try:
                out = runner(cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=900, env=env)
            except subprocess.TimeoutExpired as exc:
                return _batch_outcomes(checks, 1, str(exc), _read_input_log(log), receipt, timed_out=True)
            detail = "\n".join(x for x in (out.stdout, out.stderr) if x).strip()
            return _batch_outcomes(checks, out.returncode, detail, _read_input_log(log), receipt)
    except (OSError, subprocess.SubprocessError) as exc:
        return PytestBatch.unobserved(checks, f"pytest launch failed: {exc}")
    finally:
        log.unlink(missing_ok=True)


def collect_aoi_tests(aoi: Path, runner=subprocess.run) -> list[str]:
    if shutil.which("uv") is None:
        raise LocalCIError(
            "uv が PATH に無いので Aoi の tests/ を実行できない。"
            "--self-tests で tests/test_localci.py だけ実行できる"
        )
    cmd = [*AOI_PYTEST_PREFIX, "--collect-only", "-q", "nagoyaction/tests"]
    try:
        out = runner(cmd, cwd=aoi, capture_output=True, text=True, check=False, timeout=300, env=child_pytest_env(aoi))
    except (OSError, subprocess.SubprocessError) as exc:
        raise LocalCIError(f"Aoi のテスト収集に失敗した: {exc}") from exc
    detail = "\n".join(part for part in ((out.stdout or ""), (out.stderr or "")) if part).strip()
    if out.returncode != 0:
        raise LocalCIError(f"Aoi のテスト収集に失敗した: {detail}")
    nodeids = parse_collect_only(out.stdout or "")
    if not nodeids:
        raise LocalCIError(f"Aoi のテスト収集が空だった: {detail}")
    return nodeids


def workflow_checks(root: Path) -> tuple[list[Check], list[str]]:
    limits: list[str] = []
    checks: list[Check] = []
    for source in sources_for(root):
        checks.append(Check(f"resolve:{source.repo}", "resolve", source.repo, repo=source.repo))
    files = workflow_files(root)
    if not files:
        limits.append("workflow ファイルがない")
    for path in files:
        rel = str(path.relative_to(root))
        checks.append(Check(f"actionlint:{rel}", "actionlint", rel, file=rel))
    for item in workflow_uses(root):
        ident = f"pin:{item['file']}:{item['line']}:{item['raw']}"
        checks.append(Check(ident, "pin", item["raw"], file=item["file"], ref=item["ref"], repo=item["repo"]))
    return checks, limits


def full_suite(pytest_paths: list[str] | None, skip_pytest: bool, self_tests: bool) -> bool:
    return not skip_pytest and not self_tests and not pytest_paths


def prepare_pytest(root: Path, *, pytest_paths: list[str] | None, skip_pytest: bool, self_tests: bool,
                   aoi_ref: str, token: str, runner, opener, emit) -> tuple[list[Check], list[str], Path, list[str], Resolved | None]:
    """検査一覧、pytest の cwd、コマンド前置、checkout 済みの Aoi 解決結果を返す。"""
    if not full_suite(pytest_paths, skip_pytest, self_tests):
        paths = pytest_paths
        if self_tests and not paths:
            paths = ["tests/test_localci.py"]
        checks, limits = build_checks(root, pytest_paths=paths, skip_pytest=skip_pytest, runner=runner)
        return checks, limits, root, [sys.executable, "-m", "pytest"], None
    source = next(item for item in SOURCES if item.key == "aoi")
    ref = aoi_ref or os.environ.get("AOI_REF_INPUT", "")
    resolved = resolve_source(source, ref, token=token, runner=runner, opener=opener)
    emit(f"Aoi {resolved.sha} from {resolved.how} (repository id {resolved.repository_id})")
    aoi = checkout_aoi(root, resolved, runner=runner)
    overlay_nagoyaction(aoi, root, runner=runner)
    emit(f"Aoi checkout {aoi} HEAD {resolved.sha}")
    nodeids = collect_aoi_tests(aoi, runner)
    checks, limits = workflow_checks(root)
    checks.extend(Check(f"pytest:{nodeid}", "pytest", nodeid) for nodeid in nodeids)
    return checks, limits, aoi, list(AOI_PYTEST_PREFIX), resolved


def build_checks(root: Path, *, pytest_paths: list[str] | None, skip_pytest: bool,
                 runner=subprocess.run) -> tuple[list[Check], list[str]]:
    checks, limits = workflow_checks(root)
    if not skip_pytest:
        paths = pytest_paths or ["tests"]
        existing = []
        for path in paths:
            candidate = Path(path)
            if not candidate.is_absolute():
                candidate = root / path
            if candidate.exists():
                existing.append(str(path))
            else:
                limits.append(f"pytest path がない: {path}")
        if existing:
            nodeids, extra = collect_pytest(existing, root, runner)
            limits.extend(extra)
            for nodeid in nodeids:
                checks.append(Check(f"pytest:{nodeid}", "pytest", nodeid))
    return checks, limits


class Session:
    def __init__(self, root: Path, *, token: str = "", strict: bool = False,
                 runner=subprocess.run, opener=urllib.request.urlopen,
                 actionlint: Path | None | str = "auto",
                 aoi_resolved: Resolved | None = None, aoi_ref: str = "", cache: Path | None = None,
                 best_effort: bool = False):
        self.root = root
        # best effort: できない検査は fail でなく skip にする。GitHub Actions では常に無効。
        self.best_effort = best_effort and not running_in_github_actions()
        self.offline = ""  # GitHub が応答しなかった理由。入ったら、以降は問い合わせない
        self.unasked: dict[str, str] = {}  # repo → 最新リリースを聞けなかった理由
        self.cache = cache or root / ".localci"  # actionlint binary + record
        self.token = token
        self.strict = strict
        self.runner = runner
        self.opener = opener
        self.actionlint = actionlint
        self.aoi_resolved = aoi_resolved
        self.aoi_ref = aoi_ref
        self.resolved: dict[str, Resolved] = {}
        self.releases: dict[str, tuple[str, str] | None] = {}
        self.shellcheck = shellcheck_path()
        self.actionlint_record: ActionlintRecord | None = None

    def prepare_actionlint(self) -> ActionlintRecord | None:
        if self.actionlint_record is not None:
            return self.actionlint_record
        if self.actionlint is None:
            return None
        if isinstance(self.actionlint, Path):
            self.actionlint_record = ActionlintRecord("", "", "", self.actionlint, "path")
            return self.actionlint_record
        try:
            record = ensure_actionlint(self.cache, token=self.token, opener=self.opener)
            if record.via == "go":
                if not record.tag:
                    raise LocalCIError("actionlint tag was not resolved")
                if shutil.which("go") is None:
                    raise LocalCIError(f"actionlint {record.tag} の取得に失敗し、go も PATH に無い")
        except LocalCIError as exc:
            if not self.best_effort:
                raise
            if isinstance(exc, Unreachable):
                self.offline = str(exc)
            record = local_actionlint(self.cache, str(exc))
        self.actionlint_record = record
        return record

    def execute(self, check: Check) -> Outcome:
        if check.kind == "resolve":
            return self._resolve(check)
        if check.kind == "pin":
            return self._pin(check)
        if check.kind == "actionlint":
            return self._actionlint(check)
        raise LocalCIError(f"unknown check {check.kind}")

    def _resolve(self, check: Check) -> Outcome:
        source = next(s for s in sources_for(self.root) if s.repo == check.repo)
        if source.key == "aoi" and self.aoi_resolved is not None:
            item = self.aoi_resolved
        else:
            ref = ""
            if source.key == "aoi":
                ref = self.aoi_ref or os.environ.get("AOI_REF_INPUT", "")
            item = resolve_source(source, ref, token=self.token, runner=self.runner, opener=self.opener)
        self.resolved[source.repo] = item
        return Outcome("pass", f"{item.sha} from {item.how} (repository id {item.repository_id})", [])

    def _release(self, repo: str) -> tuple[str, str] | None:
        if repo not in self.releases:
            self.releases[repo] = latest_release(repo, token=self.token, opener=self.opener, runner=self.runner)
        return self.releases[repo]

    def _latest(self, repo: str) -> tuple[tuple[str, str] | None, str]:
        """（最新リリース, 聞けなかった理由）。best effort でなければ、聞けないときは例外のまま。"""
        if not self.best_effort:
            return self._release(repo), ""
        if self.offline:  # 理由は最初の 1 回に出した
            return None, "GitHub に届かない"
        if why := self.unasked.get(repo, ""):
            return None, why
        try:
            return self._release(repo), ""
        except LocalCIError as exc:
            if isinstance(exc, Unreachable):
                self.offline = str(exc)
            self.unasked[repo] = str(exc)
            return None, str(exc)

    def _pin(self, check: Check) -> Outcome:
        latest, why = self._latest(check.repo)
        if why:  # 手元で分かるのは SHA ピンかどうかまで
            kind = {"major": "動くメジャータグ", "unpinned": "SHA ピンではない"}.get(classify_pin(check.ref, None, check.repo), "SHA ピン")
            return Outcome("skip", f"{check.repo}@{check.ref or '(none)'}: {kind}。最新版と比べていない（{why}）", [])
        status = classify_pin(check.ref, latest, check.repo)
        probe = substitute("sha_probe", "0" * 40, lambda rng: f"{rng.getrandbits(160):040x}")
        latest_sha = latest[1] if latest else ""
        if latest_sha and probe == latest_sha:
            probe = substitute("sha_probe_retry", "f" * 40, lambda rng: f"{rng.getrandbits(160):040x}")
        if latest_sha and classify_pin(probe, latest, check.repo) == "match":
            raise LocalCIError("random sha probe matched the latest release")
        if latest is None and status == "major":
            detail = f"{check.repo}@{check.ref} is a moving major tag; no release to compare"
        elif latest is None:
            detail = f"{check.repo}@{check.ref or '(none)'} has no release tag; not compared"
        elif status == "match":
            detail = f"{check.repo}@{check.ref} matches {latest[0]}"
        elif status == "outdated":
            detail = f"{check.repo}@{check.ref} is outdated; latest {latest[0]} is {latest[1]}"
        elif status == "major":
            detail = f"{check.repo}@{check.ref} is a moving major tag; latest {latest[0]} is {latest[1]}"
        else:
            detail = f"{check.repo}@{check.ref or '(none)'} is not a SHA pin; latest {latest[0]} is {latest[1]}"
        failed = pin_fails(status, self.strict)
        return Outcome("fail" if failed else "pass", detail, [])

    def _actionlint(self, check: Check) -> Outcome:
        record = self.prepare_actionlint()
        if record is not None and record.via == "none":
            return Outcome("skip", f"actionlint を使えないので検査していない（{record.note}）", [])
        binary = None if record is None else record.binary
        go_ref = record.tag if record is not None and record.via == "go" else None
        argv = actionlint_argv(binary, [str(self.root / check.target)], self.shellcheck, go_ref=go_ref)
        try:
            out = self.runner(argv, cwd=self.root, capture_output=True, text=True, check=False, timeout=180)
        except (OSError, subprocess.SubprocessError) as exc:
            return Outcome("fail", str(exc), [])
        detail = "\n".join(part for part in ((out.stdout or ""), (out.stderr or "")) if part).strip()
        tool = "shellcheck on" if self.shellcheck else "shellcheck off"
        if out.returncode == 0:
            return Outcome("pass", f"actionlint ok ({tool})", [])
        return Outcome("fail", detail or f"actionlint exit {out.returncode} ({tool})", [])


def iter_work(shard: list[Check], coalesce_pytest: bool):
    """非 pytest は 1 件ずつ。pytest はシャード内を 1 プロセスにまとめる。"""
    if not coalesce_pytest:
        for check in shard:
            yield [check]
        return
    pytest_checks = [check for check in shard if check.kind == "pytest"]
    emitted = False
    for check in shard:
        if check.kind == "pytest":
            if not emitted:
                yield pytest_checks
                emitted = True
            continue
        yield [check]


def run_plan(*, shards: list[list[Check]], master_seed: int, execute, keep_going: bool, emit,
             execute_pytest=None) -> PlanReport:
    reports: list[RoundReport] = []
    stopped = False
    total = len(shards)
    for number, shard in enumerate(shards, 1):
        rseed = mix_seed(master_seed, "round", number)
        ids = [c.id for c in shard]
        emit(f"=== round {number}/{total} seed={rseed} master={master_seed} checks={len(shard)} ===")
        for ident in ids:
            emit(f"  - {ident}")
        if not ids:
            emit("  (empty shard)")
        failed_check = None
        batch_error = ""
        lines: list[str] = []
        skipped = pytest_skipped = 0
        not_run = len(ids)

        def note(check: Check, outcome: Outcome) -> str | None:
            nonlocal skipped, not_run, pytest_skipped
            skipped += outcome.status == "skip"
            pytest_skipped += check.kind == "pytest" and outcome.status == "skip"
            not_run -= outcome.status != "not_run"
            for item in outcome.inputs:
                text = f"    inputs: {item['name']} {item['fixed']} -> {item['value']}"
                lines.append(text)
                emit(text)
            mark = "pass" if outcome.ok else outcome.status
            line = f"    [{mark}] {outcome.detail.splitlines()[0] if outcome.detail else check.kind}"
            lines.append(line)
            emit(line)
            if outcome.ok or outcome.status in ("skip", "not_run"):  # skip: 検査できなかった。失敗ではない
                return None
            if outcome.detail and "\n" in outcome.detail:
                emit(outcome.detail)
            return check.id

        for group in iter_work(shard, execute_pytest is not None):
            if (failed_check is not None or batch_error) and not keep_going:
                break
            if execute_pytest is not None and group and group[0].kind == "pytest":
                for check in group:
                    emit(f"  > {check.id}")
                try:
                    outcomes = execute_pytest(group, rseed, keep_going)
                except (LocalCIError, OSError, urllib.error.URLError, subprocess.SubprocessError) as exc:
                    outcomes = PytestBatch.unobserved(group, f"pytest batch failed: {exc}")
                for check in group:
                    outcome = outcomes.get(check.id) or Outcome("not_run", "not run", [])
                    found = note(check, outcome)
                    if found is not None and failed_check is None:
                        failed_check = found
                error = getattr(outcomes, "batch_error", "")
                if not error and any(check.id not in outcomes for check in group):
                    error = "pytest batch has missing per-test evidence"
                if error:
                    batch_error = error
                    line = f"    [fail] {error.splitlines()[0]}"
                    lines.append(line)
                    emit(line)
                    if "\n" in error:
                        emit(error)
                # -x stops pytest execution; account for every observed result in this batch.
                continue
            check = group[0]
            emit(f"  > {check.id}")
            cseed = mix_seed(rseed, check.id)
            try:
                with use_seed(cseed):
                    outcome = execute(check, cseed)
                    inputs = take_substitutions()
                    inputs.extend(outcome.inputs)
                    outcome = Outcome(outcome.status, outcome.detail, inputs)
            except (LocalCIError, OSError, urllib.error.URLError, subprocess.SubprocessError) as exc:
                outcome = Outcome("fail", str(exc), take_substitutions())
            found = note(check, outcome)
            if found is not None and failed_check is None:
                failed_check = found
        passed = failed_check is None and not batch_error
        reports.append(RoundReport(number, rseed, ids, passed, failed_check, lines, skipped, not_run, pytest_skipped, batch_error))
        if passed:
            label = "empty" if not ids else "skip" if skipped == len(ids) else "partial" if skipped or not_run else "pass"
            emit(f"[{label}] round {number}/{total}" + (f"（{skipped}/{len(ids)} 件は skip）" if skipped else ""))
        else:
            emit(f"[fail] round {number}/{total} seed={rseed}")
            emit("shard:")
            for ident in ids:
                emit(f"  - {ident}")
        completed = len(reports)
        passed_n = sum(1 for r in reports if r.confirmed_pass)
        emit(confidence_line(passed_n, total, completed, stopped=not passed and not keep_going))
        if not passed and not keep_going:
            stopped = True
            break
    return PlanReport(master_seed, reports, stopped)


def _emit_print(text: str) -> None:
    print(text, flush=True)


LINT_KINDS = ("actionlint", "pin")  # `lint`: workflow checks only — no SHA resolution, no pytest, no Aoi checkout


def lint_cache() -> Path:
    """Where `lint` keeps actionlint and its record, so linting another repository writes nothing into it."""
    return Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "nagoyaction" / "localci"


def run_local(root: Path, *, repeat: int, seed: int | None, keep_going: bool, strict: bool,
              pytest_paths: list[str] | None, skip_pytest: bool, env_file: Path | None,
              self_tests: bool = False, aoi_ref: str = "", kinds: tuple[str, ...] | None = None, cache: Path | None = None,
              best_effort: bool = False,
              token: str | None = None, runner=subprocess.run, opener=urllib.request.urlopen,
              emit=_emit_print) -> int:
    master = seed if seed is not None else random.SystemRandom().randrange(1, 2**31)
    token = github_token() if token is None else token
    emit(f"localci seed={master}")
    checks, limits, pytest_cwd, pytest_prefix, aoi_resolved = prepare_pytest(
        root, pytest_paths=pytest_paths, skip_pytest=skip_pytest, self_tests=self_tests,
        aoi_ref=aoi_ref, token=token, runner=runner, opener=opener, emit=emit,
    )
    if kinds is not None:
        checks = [check for check in checks if check.kind in kinds]
    shards = split_shards(checks, repeat, master)
    shellcheck = shellcheck_path()
    emit(f"localci seed={master} checks={len(checks)} rounds={repeat}")
    emit("shellcheck: " + (f"actionlint が {shellcheck} を使う" if shellcheck else "PATH に無いので使わない"))
    if limits:
        emit("limits:")
        for item in limits:
            emit(f"  - {item}")
    session = Session(
        root, token=token, strict=strict, runner=runner, opener=opener,
        aoi_resolved=aoi_resolved, aoi_ref=aoi_ref, cache=cache, best_effort=best_effort,
    )
    actionlint_record = None
    if any(check.kind == "actionlint" for check in checks):
        actionlint_record = session.prepare_actionlint()
        if actionlint_record is not None and actionlint_record.tag:
            emit(format_actionlint_line(actionlint_record))
        if actionlint_record is not None and actionlint_record.note:
            emit(format_best_effort_line(actionlint_record))

    def execute(check: Check, cseed: int) -> Outcome:
        del cseed
        return session.execute(check)

    def execute_pytest(group: list[Check], rseed: int, going: bool) -> dict[str, Outcome]:
        return run_pytest_batch(group, rseed, cwd=pytest_cwd, prefix=pytest_prefix, keep_going=going, runner=runner)

    report = run_plan(
        shards=shards, master_seed=master, execute=execute, keep_going=keep_going, emit=emit,
        execute_pytest=None if skip_pytest else execute_pytest,
    )
    recorded = list(session.resolved.values())
    path = env_file or (root / ".localci" / "refs.env")
    updates: list[tuple[str, str]] = []
    header = None
    drop: tuple[str, ...] = ()
    if recorded:
        updates.extend(env_pairs(recorded))
        header = _ENV_HEADER
        emit(f"refs: {path}")
        emit(format_env(recorded).rstrip())
    if actionlint_record is not None and actionlint_record.tag:
        updates.extend(actionlint_pairs(actionlint_record))
        if not actionlint_record.sha256:
            drop = ("ACTIONLINT_SHA256",)
        emit(format_actionlint_line(actionlint_record))
    if updates:
        rewrite_env_file(path, updates, header=header, drop=drop)
    summary = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary and (recorded or (actionlint_record is not None and actionlint_record.tag)):
        append_text(Path(summary), format_run_summary(recorded, actionlint_record))
    passed = report.passed_rounds
    emit("=== summary ===")
    emit(f"seed: {master}")
    emit(confidence_line(passed, repeat, len(report.rounds), report.stopped))
    pytest_skipped = sum(r.pytest_skipped for r in report.rounds)
    if pytest_skipped:
        emit(f"pytest: {pytest_skipped} 件は [skip]（成功数に含めない）")
    not_run = sum(r.not_run for r in report.rounds) + sum(len(shard) for shard in shards[len(report.rounds):])
    if not_run:
        emit(f"未実行 [not_run]: {not_run}/{len(checks)} 件")
    if skipped := sum(r.skipped for r in report.rounds) - pytest_skipped:
        nothing = skipped == len(checks)
        emit(f"⚠️ best effort: {skipped} 件は検査できず [skip]" + ("。何も確かめていない" if nothing else "") + "。失敗にするなら --strict")
    if report.stopped or any(not r.passed for r in report.rounds):
        return 1
    return 0


def run_resolve(root: Path, *, aoi_ref: str, env_file: Path | None, github_output: bool,
                token: str | None = None, runner=subprocess.run, opener=urllib.request.urlopen,
                emit=_emit_print) -> int:
    token = github_token() if token is None else token
    if not aoi_ref:
        aoi_ref = os.environ.get("AOI_REF_INPUT", "")
    resolved = resolve_sources(root, aoi_ref, token=token, runner=runner, opener=opener)
    path = env_file or (root / ".localci" / "refs.env")
    write_env_file(path, resolved)
    text = format_env(resolved).rstrip()
    emit(text)
    if github_output:
        output = os.environ.get("GITHUB_OUTPUT", "")
        if not output:
            raise LocalCIError("GITHUB_OUTPUT is not set")
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(format_github_output(resolved))
        summary = os.environ.get("GITHUB_STEP_SUMMARY", "")
        if summary:
            mode = provenance_mode(os.environ.get("EVENT_NAME", ""), os.environ.get("GITHUB_REF", ""))
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(format_step_summary(resolved, mode))
    return 0


def _localci_parser(prog: str | None = None) -> argparse.ArgumentParser:
    """prog: `nagoyaction actionlint` shows `lint` as itself and `run` as `… --all`."""
    parser = argparse.ArgumentParser(prog=prog, description="ワークフローとテストを手元で検査する（GitHub Actions と同じ解決）")
    sub = parser.add_subparsers(dest="cmd", required=True)
    lint = sub.add_parser("lint", prog=prog, help="🔍 actionlint と uses: のピン検査だけ（SHA 解決・pytest・Aoi checkout なし）")
    lint.add_argument("--strict", action="store_true",
                      help="古い SHA ピンと、検査できなかったもの（actionlint を取得できない、GitHub に届かない）を失敗にする。setup 以外の actions/* の vN は許す")
    lint.add_argument("--seed", type=int, default=None, help="入力の差し替えを再現する")
    lint.add_argument("--root", type=Path, default=None, help="検査するリポジトリ。既定は今いるディレクトリ")
    lint.add_argument("--env-file", type=Path, default=None, help="actionlint の記録の書き先。既定はユーザーキャッシュ（~/.cache/nagoyaction/localci）")
    run = sub.add_parser("run", prog=f"{prog} --all" if prog else None, help="actionlint、ピン検査、SHA 解決、pytest をシャードして実行する")
    run.add_argument("--repeat", type=_positive, default=1, help="シャード数。各検査は全ラウンドで一度だけ走る")
    run.add_argument("--seed", type=int, default=None, help="シャッフルと入力の差し替えを再現する")
    run.add_argument("--keep-going", action="store_true", help="失敗したあとも残りのラウンドを実行する")
    run.add_argument("--strict", action="store_true", help="古い SHA ピンを失敗にする。setup 以外の actions/* の vN は許す")
    run.add_argument("--root", type=Path, default=None, help="検査するリポジトリ。既定は今いるディレクトリ")
    run.add_argument("--pytest", dest="pytest_paths", action="append", default=None,
                     help="このリポジトリ内の pytest パス。指定すると Aoi は checkout しない")
    run.add_argument("--self-tests", action="store_true",
                     help="Aoi を checkout せず tests/test_localci.py だけ実行する")
    run.add_argument("--skip-pytest", action="store_true", help="pytest を実行しない（Aoi も checkout しない）")
    run.add_argument("--aoi-ref", default="", help="Aoi の ref。空なら AOI_REF_INPUT、それも空なら main")
    run.add_argument("--env-file", type=Path, default=None, help="解決した SHA と actionlint の記録の書き先。既定は <root>/.localci/refs.env")
    resolve = sub.add_parser("resolve", help="参照先リポジトリの main SHA を解決する")
    resolve.add_argument("--root", type=Path, default=None, help="参照を読むリポジトリ。既定は今いるディレクトリ")
    resolve.add_argument("--env-file", type=Path, default=None, help="解決した SHA の書き先。既定は <root>/.localci/refs.env")
    resolve.add_argument("--github-output", action="store_true", help="$GITHUB_OUTPUT にも <key>_sha=… を書く（Aoi は sha=… も）")
    resolve.add_argument("--aoi-ref", default="", help="Aoi の ref。空なら AOI_REF_INPUT、それも空なら main")
    return parser


def _positive(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--repeat は 1 以上の整数") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("--repeat は 1 以上の整数")
    return value


def localci_main(argv: list[str] | None = None, prog: str | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] not in {"run", "lint", "resolve", "-h", "--help"}:
        argv = ["run", *argv]
    args = _localci_parser(prog).parse_args(argv)
    root = (args.root or (Path.cwd() if args.cmd == "lint" else Path(__file__).resolve().parent)).resolve()
    try:
        if args.cmd == "resolve":
            return run_resolve(root, aoi_ref=args.aoi_ref, env_file=args.env_file, github_output=args.github_output)
        if args.cmd == "lint":
            cache = lint_cache()
            return run_local(root, repeat=1, seed=args.seed, keep_going=True, strict=args.strict, pytest_paths=None,
                             skip_pytest=True, env_file=args.env_file or cache / "refs.env", kinds=LINT_KINDS, cache=cache,
                             best_effort=not args.strict)
        return run_local(
            root, repeat=args.repeat, seed=args.seed, keep_going=args.keep_going, strict=args.strict,
            pytest_paths=args.pytest_paths, skip_pytest=args.skip_pytest, env_file=args.env_file,
            self_tests=args.self_tests, aoi_ref=args.aoi_ref,
        )
    except LocalCIError as exc:
        print(f"localci: {exc}", file=sys.stderr)
        return 1


# ====================================================================================================
# 🎲 pytest プラグイン: 1 ラウンドのシャードと seed つきの差し替え（pytest -p nagoyaction）（旧 localci_pytest.py）
# pytest plugin: shard one round, and seeded input substitution.
#
#   pytest -p nagoyaction --localci-repeat 10 --localci-round 3 --localci-seed 7
#
# `--localci-round` を省略すると絞らない。`--localci-seed` があるときは
# `substitute` が固定値ではなく seed からの値を返す。
# `--localci-round-seed` は各テストの直前に `mix_seed(round, "pytest:" + nodeid)`
# で乱数を置き直す。同じシャードの複数ノードを 1 プロセスで実行するときに使う。
# ====================================================================================================

def pytest_addoption(parser):
    parser.addoption("--localci-repeat", type=int, default=None)
    parser.addoption("--localci-round", type=int, default=None)
    parser.addoption("--localci-seed", default=None)
    parser.addoption("--localci-round-seed", default=None)
    parser.addoption("--localci-receipt", default=None, help=argparse.SUPPRESS)
    parser.addoption("--localci-activate", action="store_true")


def pytest_configure(config):
    global _active_rng
    if path := config.getoption("localci_receipt"):
        config.pluginmanager.register(_PytestReceiptWriter(path), name="localci-receipt-writer")
    raw = config.getoption("localci_seed")
    if raw is None or raw == "":
        return
    config._localci_previous_rng = _active_rng  # pytest を import せずに、終わりに元へ戻す
    _active_rng = random.Random(int(raw))


def pytest_unconfigure(config):
    global _active_rng
    if hasattr(config, "_localci_previous_rng"):
        _active_rng = config._localci_previous_rng


def pytest_runtest_setup(item):
    global _active_rng
    raw = item.config.getoption("localci_round_seed")
    if raw is None or raw == "":
        return
    seed = mix_seed(int(raw), "pytest:" + item.nodeid)
    _substitutions.clear()
    _active_rng = random.Random(seed)


def pytest_collection_modifyitems(config, items):
    repeat = config.getoption("localci_repeat")
    round_no = config.getoption("localci_round")
    raw_seed = config.getoption("localci_seed")
    if not repeat or round_no is None or raw_seed is None or raw_seed == "":
        return
    ids = [item.nodeid for item in items]
    chosen = shard_for_round(ids, int(repeat), int(round_no), int(raw_seed))
    order = {node: index for index, node in enumerate(chosen)}
    selected = [item for item in items if item.nodeid in order]
    selected.sort(key=lambda item: order[item.nodeid])
    deselected = [item for item in items if item.nodeid not in order]
    items[:] = selected
    if deselected:
        config.hook.pytest_deselected(items=deselected)


class _PytestReceiptWriter:
    def __init__(self, path):
        self.path = path
        self.pid = os.getpid()

    def pytest_runtest_logreport(self, report):
        if os.getpid() != self.pid:
            return
        # Native and legacy pytest subtest reports have their own type and
        # context, but reuse the parent's nodeid and normal call phase.
        subtest = hasattr(report, "context") and any(
            cls.__name__.lower() == "subtestreport" for cls in type(report).__mro__
        )
        if subtest and report.passed:
            return
        reason = ""
        if report.skipped:
            if xfail := getattr(report, "wasxfail", None):
                reason = f"xfail: {xfail}"
            elif isinstance(report.longrepr, tuple):
                reason = str(report.longrepr[-1])
        with open(self.path, "a", encoding="utf-8") as receipt:
            receipt.write(json.dumps([report.nodeid, "subtest" if subtest else report.when, report.outcome, reason[:240]]) + "\n")


def pytest_runtest_teardown(item, nextitem):
    del item, nextitem
    log = os.environ.get("LOCALCI_INPUT_LOG", "")
    notes = take_substitutions()
    if not log or not notes:
        return
    with open(log, "a", encoding="utf-8") as fh:
        for note in notes:
            fixed = str(note["fixed"]).replace("\t", " ").replace("\n", " ")
            value = str(note["value"]).replace("\t", " ").replace("\n", " ")
            fh.write(f"{note['name']}\t{fixed}\t{value}\n")


# ====================================================================================================
# 🚦 publication-gate: 公開前の証拠の検査と記録（オフライン）（旧 publication_gate.py）
# Offline publication gate and same-execution evidence recorder (stdlib only).
#
# Identity observation belongs to the GHI adapter; research rules belong to the
# caller. A saved gate report is evidence, never a bearer token authorizing writes.
# ====================================================================================================

def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def _constant(value):
    raise ValueError(f"non-finite JSON: {value}")


def loads(text):
    value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    # This also rejects overflow literals such as 1e999, including nested ones.
    json.dumps(value, allow_nan=False)
    return value


def read_json(path):
    return loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def safe_path(root, name):
    root = Path(root).resolve()
    rel = Path(name)
    if rel.is_absolute() or not rel.parts or any(p in {"..", "."} for p in rel.parts):
        raise ValueError(f"unsafe evidence path: {name}")
    path = root
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"symlink evidence: {name}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"escaped evidence: {name}")
    return path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(root, env=None):
    value = read_json(safe_path(root, "execution-identity.json"))
    if not isinstance(value, dict) or value.get("schema") != "nagoyaction-execution/1":
        raise ValueError("missing execution identity schema")
    if value.get("mode") != "github_actions" or value.get("observer") != "gh_identity":
        raise ValueError("unobserved execution identity")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value.get("repository", "")):
        raise ValueError("invalid repository identity")
    for name in ("run_id", "run_attempt", "workflow_id"):
        if type(value.get(name)) is not int or value[name] < 1:
            raise ValueError(f"invalid identity {name}")
    for name in ("head_sha", "harness_sha", "research_sha", "ghi_sha"):
        if not re.fullmatch(r"[a-f0-9]{40}", value.get(name, "")):
            raise ValueError(f"invalid identity {name}")
    if value["head_sha"] != value["harness_sha"]:
        raise ValueError("run head does not match harness checkout")
    if not isinstance(value.get("workflow_path"), str) or not value["workflow_path"]:
        raise ValueError("missing workflow path")
    env = os.environ if env is None else env
    if env.get("GITHUB_ACTIONS") == "true":
        expected = {"repository": env.get("GITHUB_REPOSITORY"),
                    "run_id": int(env.get("GITHUB_RUN_ID", "0")),
                    "run_attempt": int(env.get("GITHUB_RUN_ATTEMPT", "0")),
                    "head_sha": env.get("GITHUB_SHA")}
        if any(value[key] != val for key, val in expected.items()):
            raise ValueError("stale execution identity: repository/run/attempt/SHA")
    return value


def seal(root, stage, names, returncode, env=None):
    """Called by record_command after the child, including on nonzero exit."""
    root = Path(root).resolve()
    identity(root, env)
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", stage) or type(returncode) is not int:
        raise ValueError("invalid stage receipt")
    files = {}
    for name in names:
        path = safe_path(root, name)
        files[name] = digest(path) if path.is_file() else None
    payload = {"schema": "nagoyaction-stage/1", "stage": stage,
               "identity_sha256": digest(root / "execution-identity.json"),
               "returncode": returncode, "files": files}
    dest = safe_path(root, f"stage-evidence/{stage}.json")
    if dest.exists():
        raise ValueError(f"stage evidence already exists: {stage}")
    write_json(dest, payload)
    return payload


def record_command(root, stage, names, command, runner=subprocess.run):
    identity(root)
    if safe_path(root, f"stage-evidence/{stage}.json").exists():
        raise ValueError("cannot overwrite a previous stage receipt")
    try:
        code = runner(command, check=False).returncode
    except OSError:
        seal(root, stage, names, 64)
        raise
    seal(root, stage, names, code)
    return code


def inspect(root, required_files, env=None):
    """Authenticate mandatory stage coverage, bytes and the execution binding."""
    root = Path(root).resolve()
    observed = identity(root, env)
    ident_hash = digest(root / "execution-identity.json")
    hashes, stages = {}, {}
    for stage, names in required_files.items():
        path = safe_path(root, f"stage-evidence/{stage}.json")
        receipt = read_json(path)
        if (not isinstance(receipt, dict) or receipt.get("schema") != "nagoyaction-stage/1" or receipt.get("stage") != stage
                or receipt.get("identity_sha256") != ident_hash):
            raise ValueError(f"stage identity mismatch: {stage}")
        if type(receipt.get("returncode")) is not int:
            raise ValueError(f"invalid return code: {stage}")
        files = receipt.get("files")
        if not isinstance(files, dict) or not set(names) <= files.keys():
            raise ValueError(f"incomplete evidence coverage: {stage}")
        for name, expected in files.items():
            path = safe_path(root, name)
            if not isinstance(expected, str) or not path.is_file() or digest(path) != expected:
                raise ValueError(f"evidence hash mismatch or missing file: {stage}/{name}")
            hashes[name] = expected
        stages[stage] = receipt["returncode"]
    return {"identity": observed, "identity_sha256": ident_hash,
            "stage_returncodes": stages, "evidence_sha256": hashes}


def decide(evidence, checks):
    """Generic fail-closed gate. All named checks must explicitly pass."""
    if not checks or any(type(v) is not bool for v in checks.values()):
        raise ValueError("gate checks must be explicit nonempty booleans")
    failed = [key for key, ok in checks.items() if not ok]
    return {"schema": "nagoyaction-publication-gate/1", "allowed": not failed,
            "status": "allowed" if not failed else "blocked",
            "failed_checks": failed, "checks": checks, **evidence}


def publication_gate_main(argv=None):
    parser = argparse.ArgumentParser(prog="nagoyaction publication-gate", description="Offline publication gate and same-execution evidence recorder (stdlib only).")
    parser.add_argument("command", choices=["record"], help="record: run the child command after -- and seal its stage receipt")
    parser.add_argument("--audit", type=Path, required=True, help="audit directory holding execution-identity.json")
    parser.add_argument("--stage", required=True, help="stage name; its receipt cannot be overwritten")
    parser.add_argument("--evidence", nargs="+", required=True, help="files under --audit that this stage produces")
    args, command = parser.parse_known_args(argv)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("child command required after --")
    try:
        return record_command(args.audit, args.stage, args.evidence, command)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(64, f"Invalid stage evidence: {exc}\n")


# ====================================================================================================
# 🪪 ghi-execution: GHI で Actions の実行と checkout を結びつける（読むだけ）（旧 ghi_execution.py）
# Read-only GHI adapter: bind this Actions attempt and both actual checkouts.
#
# GHI is loaded from a pinned separate checkout, not copied or reimplemented.
# This observer runs in setup; replay, evidence checking and publication are offline.
# ====================================================================================================

GHI_COMMIT = "fc2c527257b12eb99c00637bbae74f8988fd6bf4"
GHI_BLOB = "57f96181fecaef0a6f19bf5052b93d9bdcab69c5"


def load_ghi(directory):
    path = Path(directory).resolve() / "gh_identity.py"
    if path.is_symlink():
        raise ValueError("GHI source must be a regular file")
    raw = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != GHI_BLOB:
        raise ValueError("GHI source blob differs from reviewed pin")
    spec = importlib.util.spec_from_file_location("_aoi_pinned_ghi", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.local_identity(cwd=str(path.parent), env={})["sha"] != GHI_COMMIT:
        raise ValueError("GHI checkout differs from reviewed pin")
    return module


def observe(ghi, harness, research, env):
    repository = ghi.repo(env["GITHUB_REPOSITORY"])
    run, attempt = int(env["GITHUB_RUN_ID"]), int(env["GITHUB_RUN_ATTEMPT"])
    if run < 1 or attempt < 1:
        raise ValueError("invalid Actions run/attempt")
    # Do not let GITHUB_SHA mask the separate research checkout's actual SHA.
    h = ghi.local_identity(cwd=str(harness), env={})
    r = ghi.local_identity(cwd=str(research), env={})
    endpoint = f"repos/{repository}/actions/runs/{run}/attempts/{attempt}"
    data = ghi.request("GET", endpoint, transport="auto", timeout=30)
    if (type(data.get("id")) is not int or type(data.get("run_attempt")) is not int
            or data["id"] != run or data["run_attempt"] != attempt
            or data.get("repository", {}).get("full_name") != repository
            or data.get("head_sha") != h["sha"] or h["sha"] != env["GITHUB_SHA"]):
        raise ValueError("GHI observation does not match this run/attempt/checkout")
    return {"schema": "nagoyaction-execution/1", "mode": "github_actions",
            "observer": "gh_identity", "ghi_sha": GHI_COMMIT, "ghi_blob": GHI_BLOB,
            "repository": repository, "run_id": run, "run_attempt": attempt,
            "workflow_id": data.get("workflow_id"), "workflow_path": data.get("path"),
            "event": data.get("event"), "head_sha": data["head_sha"],
            "harness_sha": h["sha"], "research_sha": r["sha"],
            "observation_scope": "identity_only_not_final_workflow_success"}


def ghi_execution_main(argv=None):
    parser = argparse.ArgumentParser(prog="nagoyaction ghi-execution", description="Read-only GHI adapter: bind this Actions attempt and both actual checkouts.")
    parser.add_argument("--ghi", type=Path, required=True, help="checkout holding the pinned gh_identity.py")
    parser.add_argument("--harness", type=Path, default=Path.cwd(), help="harness checkout (default: current directory)")
    parser.add_argument("--research", type=Path, required=True, help="research checkout")
    parser.add_argument("--audit", type=Path, required=True, help="new audit directory to create")
    args = parser.parse_args(argv)
    try:
        if args.audit.exists():
            raise ValueError("audit directory must be new for each execution")
        ghi = load_ghi(args.ghi)
        result = observe(ghi, args.harness.resolve(), args.research.resolve(), os.environ)
        args.audit.mkdir(parents=True)
        write_json(args.audit / "execution-identity.json", result)
        identity(args.audit)
    except Exception as exc:
        parser.exit(64, f"Execution identity unavailable: {exc}\n")
    print("GHI execution identity captured; no research source was fetched")
    return 0

# ====================================================================================================
# 🧭 入口（サブコマンドを各節の *_main に渡す）
# ====================================================================================================


def actionlint(*argv: str) -> int:
    """actionlint + `uses:` pin checks of .github/workflows; --all = the whole localci run (SHA resolution, pytest in Aoi).
    Same as `nagoyaction actionlint ...`: actionlint("--strict"), actionlint("--all", "--repeat", "10")."""
    rest = list(argv)
    if "--all" in rest:
        rest.remove("--all")
        return localci_main(["run", *rest], prog="nagoyaction actionlint")
    return localci_main(["lint", *rest], prog="nagoyaction actionlint")


def hub(*argv: str) -> int:
    """Local forge (Gitea / Forgejo): hub("status"), hub("dial", "mirror"). Same as `nagoyaction hub ...` and `olnm hub ...`."""
    return local_forge_main(list(argv), prog="nagoyaction hub")


linkcheck = SimpleNamespace(links_in=links_in, classify=_link_classify, resolve=_link_resolve, tracked_files=tracked_files, check_local=check_local, check_remote=check_remote, check_external=check_external, summarize=_link_summarize, unverified_count=_link_unverified_count, exit_code=_link_exit_code, LinkcheckError=LinkcheckError, main=_linkcheck_main)  # Python: nagoyaction.linkcheck.check_local(...)
DELEGATES = {"actionlint": actionlint, "hub": hub, "linkcheck": lambda *argv: _linkcheck_main(list(argv)),
             "localci": lambda *argv: localci_main(list(argv), prog="nagoyaction localci"),
             "publication-gate": lambda *argv: publication_gate_main(list(argv)),
             "ghi-execution": lambda *argv: ghi_execution_main(list(argv))}
DELEGATES_HELP = {
    "actionlint": "🔍 actionlint と uses: のピン検査（--strict / --all で localci run 全体）",
    "hub": "🏠 ローカル GitHub（Gitea / Forgejo）の操作（例: hub status / hub dial mirror）",
    "linkcheck": "🔗 Markdown のリンク・画像の参照先を確かめる（このファイルの中。--remote / --external / --json）",
    "localci": "🧪 ワークフローとテストを手元で検査する（lint / run / resolve。CI の resolve・local-ci ジョブも使う）",
    "publication-gate": "🚦 公開前の証拠の検査と記録（record --audit DIR --stage NAME --evidence … -- コマンド）",
    "ghi-execution": "🪪 GHI で Actions の実行と両方の checkout を結びつける（--ghi --research --audit）",
}


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)
    if argv[:1] and argv[0] in DELEGATES:  # hand everything (incl. --help) to the module before this parser sees it
        return DELEGATES[argv[0]](*argv[1:])
    ap = _parser()
    _arm_json(ap, "--json" in argv)
    args = ap.parse_args(argv)
    if args.cmd in DELEGATES:  # e.g. `--json hub status`
        return DELEGATES[args.cmd](*args.rest)
    json_mode = _json_mode(args, argv)

    try:
        p = load(args.pipeline)
        var_overrides = _parse_override_vars(getattr(args, "var", None))
        if args.cmd == "show":
            print(show(p, var_overrides=var_overrides, json_output=json_mode))
            return 0
        checks = doctor(p, offline=args.offline)
        failed = any(c["level"] == "fail" for c in checks)
        doctor_doc = {
            "schema": "nagoyaction-doctor/1",
            "ok": not failed,
            "exit": 1 if failed else 0,
            "pipeline": p.get("name", ""),
            "root": str(p["_root"]),
            "offline": bool(args.offline),
            "checks": checks,
        }
        # run --json は doctor の結果を run の文書に含め、stdout は JSON 1つにする。
        # doctor が止めたときも、その理由は doctor の文書1つだけを出す。
        if json_mode and (args.cmd == "doctor" or failed):
            print(json.dumps(doctor_doc, ensure_ascii=False, indent=2))
        elif not json_mode:
            _print_checks(checks)
        if failed:
            _report(json_mode, 1, "doctor", "足りないものがある。実行しない",
                    human="doctor: 足りないものがある。実行しない")
            return 1
        if args.cmd == "doctor":
            return 0
        records: list = []
        rc = run(p, offline=args.offline, only=args.only, start=args.start, until=args.until,
                 var_overrides=var_overrides, dry_run=args.dry_run, receipt=args.receipt,
                 quiet=json_mode, records=records if json_mode else None)
        if json_mode:
            print(json.dumps({
                "schema": "nagoyaction-run/1",
                "ok": rc == 0,
                "exit": rc,
                "pipeline": p.get("name", ""),
                "offline": bool(args.offline),
                "dry_run": bool(args.dry_run),
                "checks": checks,
                "steps": records,
            }, ensure_ascii=False, indent=2))
            if rc != 0:
                failed_step = next(s for s in reversed(records) if s.get("returncode") not in (None, 0))
                emit_error("nagoyaction", rc, "step",
                           f"手順 {failed_step['step']} が終了コード {rc}")
        return rc
    except PipelineError as e:
        _report(json_mode, 2, "pipeline", str(e), human=f"pipeline error: {e}")
        return 2
    except tomllib.TOMLDecodeError as e:
        _report(json_mode, 2, "toml", str(e), human=f"pipeline error: {e}")
        return 2
    except OSError as e:
        _report(json_mode, 2, "io", str(e), human=f"pipeline error: {e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
