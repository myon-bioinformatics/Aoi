"""NagoyAction — 研究を、続けられる仕組みに。

パイプラインを TOML に一度だけ書き、ローカルでも GitHub Actions でも同じコマンドで動かす。
GitHub Actions のワークフローは `python NagoyAction/nagoyaction.py run <pipeline>` を呼ぶだけにする。
データを外に出せない案件では、同じ定義をローカルで実行すればよい。

  doctor <pipeline>  実行前の確認。Python の版、必要なツール（git, uv, gh など）、
                     オフライン実行に必要な成果物の有無。足りないものがあれば終了コード1
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
  run = ["uv", "run", "python", "QueRyu/queryu.py", "--years", "{years}"]
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
                return rc
            continue
        if receipt:
            _append(receipt, entry)
    return 0


def _append(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _print_checks(checks: list[dict]) -> None:
    mark = {"ok": "✓", "warn": "!", "fail": "✗"}
    for c in checks:
        print(f"[{mark[c['level']]}] {c['check']}: {c['detail']}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="パイプラインの事前確認と実行（ローカル / GitHub Actions 共通）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("doctor")
    d.add_argument("pipeline", type=Path)
    d.add_argument("--offline", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("pipeline", type=Path)
    r.add_argument("--offline", action="store_true")
    r.add_argument("--only", nargs="+")
    r.add_argument("--from", dest="start")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--receipt", type=Path, help="受領記録(JSONL)の追記先")
    args = ap.parse_args(argv)

    try:
        p = load(args.pipeline)
        checks = doctor(p, offline=args.offline)
        _print_checks(checks)
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
