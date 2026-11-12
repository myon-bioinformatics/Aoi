"""サイクル3の命題を PythDRagoras で判定する（元の命題・対偶・逆・裏、判例、終了コード）。

    python cycles/c003-outlets/outlet_judge.py [--report-only]

入力は units.jsonl（outlet_units.py make が書く）と propositions.toml と propositions_r2〜r7.toml（事前登録）。結果は outputs/ に書く。
終了コードは docs/propositions.md の表どおり（最初に 0 でなかった命題のコード）。--report-only は異議（1〜6）で失敗にしない。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pythdragoras"))
sys.path.insert(0, str(HERE))

import polars as pl  # noqa: E402

import outlet_units  # noqa: E402
import propositions as pr  # noqa: E402

OUT = HERE / "outputs"
DROP = ("shares", "kind", "split", "method", "first_left", "base", "stages")  # 列にしない（リスト）か、真偽の列に直してあるもの


def table(units: list[dict]) -> pl.DataFrame:
    rows = [{k: v for k, v in u.items() if k not in DROP} for u in units]
    return pl.DataFrame(rows, infer_schema_length=None)


def code_version() -> str | None:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or None


PROPS = (HERE / "propositions.toml", HERE / "propositions_r2.toml", HERE / "propositions_r3.toml",
         HERE / "propositions_r4.toml", HERE / "propositions_r5.toml",
         HERE / "propositions_r6.toml", HERE / "propositions_r7.toml", HERE / "propositions_r8.toml", HERE / "propositions_r9.toml")  # 事前登録の順。後の弾は前の id を parent に持てる


def load_props(paths=PROPS) -> tuple[list[dict], str]:
    """事前登録のファイルを順につないで 1 つとして読む（同じ問いの重なりと parent は全体で確かめる）。"""
    text = "\n".join(Path(p).read_text(encoding="utf-8") for p in paths)
    with tempfile.TemporaryDirectory() as tmp:
        joined = Path(tmp) / "propositions.toml"
        joined.write_text(text, encoding="utf-8")
        return pr.load(joined)


def evaluate_all(units_path: Path = outlet_units.UNITS, props_paths=PROPS, outdir: Path | None = OUT) -> list[dict]:
    """判定して結果を返す。outdir があれば propositions.jsonl・objections.md・index.md・ledger.jsonl を書く。"""
    props, sha = load_props(props_paths)
    st = table(outlet_units.read_units(units_path))
    meta = {"sha256": sha, "code_version": code_version(),
            "file": " + ".join(str(Path(p).relative_to(ROOT)) for p in props_paths)}
    results = [{**pr.evaluate(p, st), "meta": meta} for p in props]
    if outdir is None:
        return results
    outdir.mkdir(parents=True, exist_ok=True)
    data_sha = hashlib.sha256(units_path.read_bytes()).hexdigest()
    ledger = pr.update_ledger(outdir / "ledger.jsonl", results, data_sha, meta["code_version"])
    for r in results:
        r["judgement"] = pr.judge(r, pr.ledger_summary(ledger, r["id"])["definitions"])
    (outdir / "propositions.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in results), encoding="utf-8")
    (outdir / "objections.md").write_text(pr.render(results, meta, ledger=ledger), encoding="utf-8")
    (outdir / "index.md").write_text(pr.render_index(results, meta), encoding="utf-8")
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    ap.add_argument("--report-only", action="store_true", help="判定を表示するだけで、異議（1〜6）では失敗にしない")
    ap.add_argument("--lang", choices=["ja", "en"], default="ja")
    args = ap.parse_args(argv)
    if not outlet_units.UNITS.exists():
        print(f"[66] {pr.label(66, args.lang)}: {outlet_units.UNITS}", file=sys.stderr)
        return 66
    try:
        results = evaluate_all(outdir=OUT)
    except pr.DataError as e:
        print(f"[65] {e}", file=sys.stderr)
        return 65
    except pr.PropositionError as e:
        print(f"[64] {e}", file=sys.stderr)
        return 64
    except AssertionError as e:
        print(f"[70] {e}", file=sys.stderr)
        return 70
    code = pr.run_judge(results, None, None, True, args.lang)
    return code if (code >= 64 or not args.report_only) else 0


if __name__ == "__main__":
    raise SystemExit(main())
