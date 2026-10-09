"""BlueProbe — 観測する。解釈はあとで。

取得元（source）に依存しない部分だけを置く。
  - normalize(): 表記揺れの吸収。何をしたかは記録単位で残す
  - Report: 1ページを読んだ結果の契約。採用したもの以外も必ず数える
  - inspect(): 取得済みのページを再解析して集計する。ネットワークには出ない

取得元ごとの読み方は別モジュール（例: npb_calendar.py）に置き、次の2つを持たせる:
  pages(scope)        -> [(key, url, group)]   取得すべきページの一覧
  parse(html, url)    -> Report               1ページの観測結果

Aoi の原則との対応:
  Observe Before Explaining  … 原文(raw)と読み取った値(derived)を同じ記録に並べる
  Never Hide Unknowns        … unknown は件数と原文を残す
  Separate Facts From Explanations … ここでは勝敗も点差も計算しない
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
import unicodedata
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

NORMALIZATION = "nul->U+FFFD, NFKC, collapse-whitespace"


def normalize(text: str) -> str:
    """NUL は U+FFFD に置き換え（黙って消さない）、NFKC、連続空白を1つに。"""
    text = unicodedata.normalize("NFKC", text.replace("\x00", "�"))
    return " ".join(text.split())


def new_report() -> dict:
    """1ページ（または複数ページの合計）の観測結果。

    records : 採用した観測。key で一意
    counts  : 採用しなかったものの区分ごとの件数（例: cancelled, non_regular）
    unknown : どの区分にも当たらなかったもの。原文を残す
    """
    return {"records": [], "counts": Counter(), "unknown": []}


def merge(total: dict, part: dict, key: str = "key") -> dict:
    """結果を足し合わせる。同じ key の記録は最初のものを残す。"""
    seen = {r[key] for r in total["records"]}
    total["records"] += [r for r in part["records"] if r[key] not in seen]
    total["counts"].update(part["counts"])
    total["unknown"] += part["unknown"]
    return total


def load_source(name: str):
    """取得元モジュールを名前で読み込む（blueprobe/ 直下の <name>.py）。"""
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise ValueError(f"invalid source name: {name!r}")
    return importlib.import_module(name)


def mask_digits(text: str) -> str:
    """docs に未知表記の「形」だけ残すため、数字を # に伏せる。"""
    return re.sub(r"[0-9０-９]", "#", text)


def inspect(source, pages: Iterable[tuple[str, str, str, str]], records_out: list | None = None) -> list[dict]:
    """取得済みページ (key, url, group, html) を再解析し、group ごとに集計する。

    ネットワークには出ない。解析ルールを直したら、これだけを何度でも回す。
    """
    return _inspect(source.parse, pages, records_out)


def inspect_cache(source, cache, entries=None, records_out=None) -> list[dict]:
    """Replay latest or explicitly selected historical cache entries, offline.

    Snapshot-aware sources receive the verified envelope; existing semantic
    parsers receive the unchanged decoded HTML. Cache integrity errors stop the
    replay before parser invocation and never trigger a replacement fetch.
    """
    snapshot_parser = getattr(source, 'parse_snapshot', None)
    if entries is None:
        entries = [entry for _, entry in sorted(cache.latest().items())]

    def pages():
        for entry in entries:
            if snapshot_parser is not None:
                snapshot = cache.snapshot(entry)
                payload = snapshot if snapshot['html'] else ''
            else:
                payload = cache.body(entry)
            yield entry['key'], entry['url'], entry['group'], payload

    parser = (lambda snapshot, url: snapshot_parser(snapshot)) if snapshot_parser is not None else source.parse
    return _inspect(parser, pages(), records_out)


def _inspect(parser, pages, records_out):
    groups: dict[str, dict] = {}
    for key, url, group, html in pages:
        g = groups.setdefault(group, {"pages": 0, "empty": 0, "report": new_report()})
        if not html:
            g["empty"] += 1
            continue
        g["pages"] += 1
        merge(g["report"], parser(html, url))
    rows = []
    for group, g in sorted(groups.items()):
        r = g["report"]
        if records_out is not None:
            records_out += r["records"]
        rows.append({
            "group": group, "pages": g["pages"], "empty_pages": g["empty"],
            "records": len(r["records"]), **{f"n_{k}": v for k, v in sorted(r["counts"].items())},
            "unknown": len(r["unknown"]),
            "unknown_shapes": sorted({mask_digits(u["raw"]) for u in r["unknown"]})[:5],
        })
    return rows


def to_markdown(rows: list[dict], title: str, checks: list[dict] | None = None) -> str:
    """checks は source.check() の返り値（{"group", "ok", "text"} の並び）。"""
    cols = sorted({k for r in rows for k in r if k != "unknown_shapes"}, key=lambda k: (k != "group", k))
    lines = [f"# {title}", "", "取得済みページの再解析結果（自動生成）。ネットワークには出ていない。", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(r.get(c, 0)) for c in cols) + " |" for r in rows]
    if checks:
        lines += ["", "## 取りこぼしの確認（既知値との照合）", "", *[f"- {c['text']}" for c in checks]]
    shapes = [(r["group"], r["unknown_shapes"]) for r in rows if r["unknown_shapes"]]
    if shapes:
        lines += ["", "## 未知の表記（数字は # に伏せた形）", ""]
        lines += [f"- {g}: " + ", ".join(f"`{s!r}`" for s in ss) for g, ss in shapes]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="取得済みページをオフラインで再解析する")
    ap.add_argument("--source", required=True)
    ap.add_argument("--cache", type=Path, required=True, help="QueRyu のキャッシュディレクトリ")
    ap.add_argument("--out", type=Path, help="Markdown の出力先")
    ap.add_argument("--strict", action="store_true", help="未知の表記、または既知値と合わない group があれば終了コード1")
    args = ap.parse_args(argv)

    source = load_source(args.source)
    manifest = args.cache / "manifest.jsonl"
    if not manifest.exists():
        print(f"no cache manifest: {manifest}", file=sys.stderr)
        return 1
    from queryu import Cache
    records: list = []
    rows = inspect_cache(source, Cache(args.cache), records_out=records)
    checks = source.check(records) if hasattr(source, "check") else None
    md = to_markdown(rows, f"{args.source}: 観測された構造", checks)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding="utf-8")
    print(md)
    n_unknown = sum(r["unknown"] for r in rows)
    if n_unknown:
        print(f"unknown: {n_unknown} 件。表記の変化を疑う（上の表を参照）", file=sys.stderr)
    failed = [c["group"] for c in checks or [] if not c["ok"]]
    if failed:
        print(f"既知値と合わない group: {', '.join(failed)}（取りこぼし・混入を疑う）", file=sys.stderr)
    return 1 if (args.strict and (n_unknown or failed)) else 0


if __name__ == "__main__":
    sys.path[:0] = [str(Path(__file__).resolve().parent),
                    str(Path(__file__).resolve().parents[1] / "queryu")]
    raise SystemExit(main())
