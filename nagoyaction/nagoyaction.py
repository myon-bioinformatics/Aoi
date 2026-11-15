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

import argparse, datetime as dt, json, posixpath, re, shutil, subprocess, sys, tomllib, urllib.error, urllib.request
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
        sub.add_parser(name, help=help_text, add_help=False).add_argument("rest", nargs=argparse.REMAINDER)
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



def actionlint(*argv: str) -> int:
    """actionlint + `uses:` pin checks of .github/workflows; --all = the whole localci run (SHA resolution, pytest in Aoi).
    Same as `nagoyaction actionlint ...`: actionlint("--strict"), actionlint("--all", "--repeat", "10")."""
    import localci  # only when asked, so pipeline commands never load it
    rest = list(argv)
    if "--all" in rest:
        rest.remove("--all")
        return localci.main(["run", *rest], prog="nagoyaction actionlint")
    return localci.main(["lint", *rest], prog="nagoyaction actionlint")


def hub(*argv: str) -> int:
    """Local forge (Gitea / Forgejo): hub("status"), hub("dial", "mirror"). Same as `nagoyaction hub ...` and `olnm hub ...`."""
    import local_forge  # only when asked, so pipeline commands never load it
    return local_forge.main(list(argv), prog="nagoyaction hub")


linkcheck = SimpleNamespace(links_in=links_in, classify=_link_classify, resolve=_link_resolve, tracked_files=tracked_files, check_local=check_local, check_remote=check_remote, check_external=check_external, summarize=_link_summarize, unverified_count=_link_unverified_count, exit_code=_link_exit_code, LinkcheckError=LinkcheckError, main=_linkcheck_main)  # Python: nagoyaction.linkcheck.check_local(...)
DELEGATES = {"actionlint": actionlint, "hub": hub, "linkcheck": lambda *argv: _linkcheck_main(list(argv))}
DELEGATES_HELP = {
    "actionlint": "🔍 actionlint と uses: のピン検査（--strict / --all で localci run 全体）。残りの引数を localci に渡す",
    "hub": "🏠 ローカル GitHub（Gitea / Forgejo）の操作。残りの引数を local_forge に渡す（例: hub status / hub dial mirror）",
    "linkcheck": "🔗 Markdown のリンク・画像の参照先を確かめる（このファイルの中。--remote / --external / --json）",
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
