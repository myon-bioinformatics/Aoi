"""NagoyAction — 研究を、続けられる仕組みに。

パイプラインを TOML に一度だけ書き、ローカルでも GitHub Actions でも同じコマンドで動かす。
GitHub Actions のワークフローは `python nagoyaction/nagoyaction.py run <pipeline>` を呼ぶだけにする。
データを外に出せない案件では、同じ定義をローカルで実行すればよい。

  doctor <pipeline>  実行前の確認。Python の版、必要なツール（git, uv, gh など）、
                     オフライン実行に必要な成果物の有無（-v/--verbose で詳細診断）。足りないものがあれば終了コード1
  show <pipeline>    パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示する
  run <pipeline>     doctor のあと、手順を順に実行する。各手順の結果を受領記録(JSONL)に残す
    --offline        network = true の手順は実行しない（成果物が既にあれば飛ばす。なければ止まる）
    --only / --from  一部の手順だけ実行する
    --dry-run        何を実行するかだけ表示する

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

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tomllib
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
    """確認結果の一覧。level は ok / warn / fail。info に詳細診断情報、hint に改善策を含む。"""
    req = p.get("requires", {})
    checks = []
    need_str = str(req.get("python", "3.11"))
    need = tuple(int(x) for x in need_str.split("."))
    have = sys.version_info[: len(need)]
    py_ok = have >= need
    py_check = {
        "check": "python",
        "level": "ok" if py_ok else "fail",
        "detail": f"{sys.version.split()[0]} (requires >= {'.'.join(map(str, need))})",
        "info": {
            "executable": sys.executable,
            "platform": sys.platform,
            "version": sys.version.replace("\n", " "),
        },
    }
    if not py_ok:
        py_check["hint"] = f"Python {need_str} 以上をインストールしてください"
    checks.append(py_check)

    for tool in req.get("tools", []):
        path = which(tool)
        ver = _version(tool) if path else None
        t_check = {
            "check": tool,
            "level": "ok" if path else "fail",
            "detail": ver if path else "見つからない（インストールが必要）",
            "info": {
                "executable": path or "not found",
                "status": "installed" if path else "missing (required)",
            },
        }
        if not path:
            t_check["hint"] = f"ツール '{tool}' をインストールして PATH に追加してください"
        checks.append(t_check)

    for tool in req.get("optional", []):
        path = which(tool)
        ver = _version(tool) if path else None
        opt_check = {
            "check": tool,
            "level": "ok" if path else "warn",
            "detail": ver if path else "見つからない（なくても実行できる）",
            "info": {
                "executable": path or "not found",
                "status": "installed" if path else "missing (optional)",
            },
        }
        if not path:
            opt_check["hint"] = f"ツール '{tool}' をインストールすると追加機能が有効になります"
        checks.append(opt_check)

    if offline:
        for s in p["step"]:
            if s.get("network"):
                outputs_info = []
                missing = []
                for o in s.get("outputs", []):
                    target = p["_root"] / o
                    if target.exists():
                        size = target.stat().st_size
                        outputs_info.append(f"{o} (exists, {size} bytes)")
                    else:
                        outputs_info.append(f"{o} (missing)")
                        missing.append(o)
                off_check = {
                    "check": f"offline:{s['name']}",
                    "level": "fail" if missing else "ok",
                    "detail": f"成果物がない: {missing}" if missing else "成果物あり（取得を飛ばす）",
                    "info": {
                        "outputs": ", ".join(outputs_info) if outputs_info else "none declared",
                    },
                }
                if missing:
                    off_check["hint"] = f"オンライン環境で '{s['name']}' ステップを実行して成果物を取得してください"
                checks.append(off_check)
    return checks


def _expand(argv: list[str], vars_: dict) -> list[str]:
    try:
        return [a.format(**vars_) for a in argv]
    except KeyError as e:
        raise PipelineError(f"未定義の変数: {e}") from None


def _select(steps, only, start):
    names = [s["name"] for s in steps]
    for n in [*(only or []), *([start] if start else [])]:
        if n not in names:
            raise PipelineError(f"そんな step はない: {n}（{names}）")
    if only:
        return [s for s in steps if s["name"] in only]
    if start:
        return steps[names.index(start):]
    return steps


def run(p: dict, *, offline=False, only=None, start=None, dry_run=False, receipt: Path | None = None,
        runner=subprocess.run) -> int:
    vars_ = {k: str(v) for k, v in p.get("vars", {}).items()}
    for s in _select(p["step"], only, start):
        argv = _expand(s["run"], vars_)
        entry = {"pipeline": p.get("name"), "step": s["name"], "argv": argv,
                 "started": dt.datetime.now(dt.UTC).isoformat(timespec="seconds")}
        if offline and s.get("network"):
            entry.update(skipped=True, reason="offline: network step")
            print(f"[skip] {s['name']}（オフライン。取得済みの成果物を使う）")
        elif dry_run:
            entry.update(skipped=True, reason="dry-run")
            print(f"[dry-run] {s['name']}: {' '.join(argv)}")
        else:
            print(f"[run] {s['name']}: {' '.join(argv)}", flush=True)
            rc = runner(argv, cwd=p["_root"], check=False).returncode
            entry.update(returncode=rc, ended=dt.datetime.now(dt.UTC).isoformat(timespec="seconds"))
            if receipt:
                _append(receipt, entry)
            if rc != 0:
                print(f"[fail] {s['name']} (exit {rc})", file=sys.stderr)
                print(f"[hint] トラブルシューティング: `python nagoyaction.py troubleshoot --step {s['name']} --exit-code {rc}`", file=sys.stderr)
                return rc
            continue
        if receipt:
            _append(receipt, entry)
    return 0


def _append(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def show(p: dict, *, json_output: bool = False) -> str:
    """パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示形式で返す。"""
    vars_ = {k: str(v) for k, v in p.get("vars", {}).items()}
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


TROUBLESHOOT_PATTERNS = [
    {
        "id": "cuda_gpu_error",
        "keywords": ["cuda", "nvcc", "nvidia", "cublas", "gpu", "out of memory", "device-side assert"],
        "category": "CUDA / GPU Driver Issue",
        "remediation": "NVIDIA ドライバと CUDA Toolkit / GPU ライブラリのバージョン整合性を確認してください。`nvidia-smi` で GPU 状態を確認し、`CUDA_VISIBLE_DEVICES` を見直してください。",
        "resources": [
            "NVIDIA CUDA Docs: https://docs.nvidia.com/cuda/",
            "PyTorch CUDA Troubleshooting: https://pytorch.org/docs/stable/notes/cuda.html",
            "Qiita (CUDA トラブルシューティング): https://qiita.com/tags/cuda",
            "Stack Overflow [cuda]: https://stackoverflow.com/questions/tagged/cuda",
        ],
    },
    {
        "id": "missing_module",
        "keywords": ["modulenotfounderror", "no module named", "import error", "cannot import name"],
        "category": "Missing Python Module / Dependency",
        "remediation": "環境に依存関係が不足しています。`uv sync` または `uv pip install` でライブラリをセットアップしてください。",
        "resources": [
            "uv Documentation: https://docs.astral.sh/uv/",
            "PyPI (Python Package Index): https://pypi.org/",
            "Stack Overflow [python-import]: https://stackoverflow.com/questions/tagged/python-import",
        ],
    },
    {
        "id": "command_not_found",
        "keywords": ["command not found", "見つかりません", "not recognized as an internal or external command", "executable not found"],
        "category": "Missing Executable / PATH Issue",
        "remediation": "実行コマンドが見つかりません。ツールがインストールされているか、PATH 環境変数に含まれているか確認してください。",
        "resources": [
            "NagoyAction Doctor: `python nagoyaction.py doctor <pipeline.toml> -v`",
            "Qiita (PATH 設定): https://qiita.com/tags/path",
        ],
    },
    {
        "id": "offline_miss",
        "keywords": ["offlinemiss", "成果物がない", "offline: network step"],
        "category": "Offline Mode Missing Artifact",
        "remediation": "オフライン実行に必要なキャッシュ/成果物が存在しません。オンライン環境でネットワークステップを実行してください。",
        "resources": [
            "QueRyu Cache Docs: https://github.com/myon-bioinformatics/QueRyu",
        ],
    },
    {
        "id": "test_failure",
        "keywords": ["assertionerror", "pytest", "junit", "failed", "failure"],
        "category": "Test / Verification Failure",
        "remediation": "テストまたは検証ステップで失敗が発生しました。該当のテストスイートを個別実行して詳細ログを確認してください。",
        "resources": [
            "pytest Documentation: https://docs.pytest.org/",
            "Stack Overflow [pytest]: https://stackoverflow.com/questions/tagged/pytest",
        ],
    },
]


def troubleshoot(error_text: str = "", exit_code: int | None = None, receipt_path: Path | None = None,
                 step: str | None = None, json_output: bool = False) -> str:
    """エラーメッセージや受領記録から失敗原因を解析し、改善策とコミライブラリ/参照先を提案する。"""
    logs = [error_text] if error_text else []
    failed_step = step

    if receipt_path and Path(receipt_path).exists():
        lines = Path(receipt_path).read_text(encoding="utf-8").splitlines()
        for line in reversed(lines):
            try:
                rec = json.loads(line)
                if rec.get("returncode", 0) != 0:
                    if not failed_step:
                        failed_step = rec.get("step")
                    if not exit_code:
                        exit_code = rec.get("returncode")
                    logs.append(json.dumps(rec, ensure_ascii=False))
                    break
            except ValueError:
                continue

    combined = " ".join(logs).lower()
    matches = []
    for pat in TROUBLESHOOT_PATTERNS:
        if any(kw in combined for kw in pat["keywords"]):
            matches.append(pat)

    if not matches:
        matches.append({
            "id": "general_execution_failure",
            "category": "General Execution Failure",
            "remediation": f"ステップ '{failed_step or '不明'}' (exit {exit_code or '非ゼロ'}) が失敗しました。`python nagoyaction.py doctor <pipeline.toml> -v` で環境と依存を確認してください。",
            "resources": [
                "NagoyAction Docs: https://github.com/myon-bioinformatics/NagoyAction",
                "Stack Overflow: https://stackoverflow.com/",
                "Qiita: https://qiita.com/",
            ],
        })

    data = {
        "step": failed_step,
        "exit_code": exit_code,
        "matched_categories": [m["category"] for m in matches],
        "diagnostics": matches,
    }

    if json_output:
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines = [
        "Troubleshooting Analysis Report:",
        f"  Failed Step: {failed_step or 'Not specified'}",
        f"  Exit Code: {exit_code if exit_code is not None else 'Not specified'}",
        "  Identified Issues:",
    ]
    for idx, match in enumerate(matches, 1):
        lines.append(f"  {idx}. [{match['category']}]")
        lines.append(f"     ↳ 対策: {match['remediation']}")
        lines.append("     ↳ 参照コミュニティ / ナレッジ情報:")
        for res in match["resources"]:
            lines.append(f"       • {res}")

    return "\n".join(lines)


def _print_checks(checks: list[dict], *, verbose: bool = False, json_output: bool = False) -> None:
    counts = {"ok": sum(c["level"] == "ok" for c in checks),
              "warn": sum(c["level"] == "warn" for c in checks),
              "fail": sum(c["level"] == "fail" for c in checks)}

    if json_output:
        report = {
            "summary": {
                "status": "fail" if counts["fail"] > 0 else "ok",
                "total": len(checks),
                "ok": counts["ok"],
                "warn": counts["warn"],
                "fail": counts["fail"],
            },
            "checks": checks,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    mark = {"ok": "✓", "warn": "!", "fail": "✗"}
    for c in checks:
        print(f"[{mark[c['level']]}] {c['check']}: {c['detail']}")
        if verbose and c.get("info"):
            for k, v in c["info"].items():
                print(f"    • {k}: {v}")
        if c.get("hint"):
            print(f"    ↳ 助言: {c['hint']}")

    if counts["fail"] == 0 and counts["warn"] == 0:
        print("\n[✓] Doctor found no issues!")
    else:
        print(f"\n[!] Doctor found issues: {counts['fail']} failed, {counts['warn']} warning(s).")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="パイプラインの事前確認と実行（ローカル / GitHub Actions 共通）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("doctor")
    d.add_argument("pipeline", type=Path)
    d.add_argument("--offline", action="store_true")
    d.add_argument("-v", "--verbose", action="store_true", help="詳細な診断情報を表示")
    d.add_argument("--json", dest="json_output", action="store_true", help="診断結果を JSON 形式で出力")
    s = sub.add_parser("show", help="パイプラインの構造（変数・ステップ・コマンド・出力・ネットワーク要求）を表示する")
    s.add_argument("pipeline", type=Path)
    s.add_argument("--json", dest="json_output", action="store_true", help="JSON 形式で出力")
    t = sub.add_parser("troubleshoot", help="エラーメッセージや受領記録から失敗原因を解析し、解決策・コミュニティ参照先を提示する")
    t.add_argument("--error", default="", help="エラーメッセージまたはログテキスト")
    t.add_argument("--exit-code", type=int, default=None, help="プロセス終了コード")
    t.add_argument("--receipt", type=Path, default=None, help="受領記録 (JSONL)")
    t.add_argument("--step", default=None, help="失敗したステップ名")
    t.add_argument("--json", dest="json_output", action="store_true", help="JSON 形式で出力")
    r = sub.add_parser("run")
    r.add_argument("pipeline", type=Path)
    r.add_argument("--offline", action="store_true")
    r.add_argument("--only", nargs="+")
    r.add_argument("--from", dest="start")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--receipt", type=Path, help="受領記録(JSONL)の追記先")
    args = ap.parse_args(argv)

    if args.cmd == "troubleshoot":
        print(troubleshoot(error_text=args.error, exit_code=args.exit_code, receipt_path=args.receipt,
                           step=args.step, json_output=args.json_output))
        return 0

    try:
        p = load(args.pipeline)
        if args.cmd == "show":
            print(show(p, json_output=args.json_output))
            return 0
        checks = doctor(p, offline=args.offline)
        _print_checks(checks, verbose=getattr(args, "verbose", False), json_output=getattr(args, "json_output", False))
        if any(c["level"] == "fail" for c in checks):
            print("doctor: 足りないものがある。実行しない", file=sys.stderr)
            return 1
        if args.cmd == "doctor":
            return 0
        return run(p, offline=args.offline, only=args.only, start=args.start, dry_run=args.dry_run,
                   receipt=args.receipt)
    except PipelineError as e:
        print(f"pipeline error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
