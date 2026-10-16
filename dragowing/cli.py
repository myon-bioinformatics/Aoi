"""python -m dragowing --results DIR --out DIR

HTML を書く。PNG は --png かつ任意依存 png（kaleido）があるときだけ。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .forms import load_items
from .htmlout import index_body, propositions_body, standalone
from .overlap import finalize_conditions, load_overlap, parse_cond
from .records import read_jsonl, select_items


class PngUnavailable(RuntimeError):
    """kaleido が無い。HTML は書けている。"""


def write_png(fig, path: Path) -> None:
    try:
        import kaleido  # noqa: F401
    except ImportError as exc:
        raise PngUnavailable(
            "PNG には任意依存 png（kaleido）が必要です。HTML は kaleido なしで書けます。"
        ) from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_image(path, format="png", engine="kaleido")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="記録された結果を Plotly の HTML にする。判定はやり直さない。")
    parser.add_argument("--results", type=Path, required=True, help="season.jsonl と propositions.jsonl があるディレクトリ")
    parser.add_argument("--out", type=Path, required=True, help="HTML の出力ディレクトリ")
    parser.add_argument("--id", action="append", dest="ids", help="この命題だけ。繰り返せる。省略すると全部")
    parser.add_argument("--column", default="wins_vs_pythag", help="球団×年に置く数値列。既定は wins_vs_pythag")
    parser.add_argument(
        "--cond",
        action="append",
        dest="conds",
        help="重なりの条件。col,op,値（JSON）。例: rd,>,0 。省略すると if の先頭2件と B クラス",
    )
    parser.add_argument("--png", action="store_true", help="PNG も書く。kaleido と Chrome が要る。既定では HTML だけ")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        items, present = load_items(args.results)
        season_path = Path(args.results) / "season.jsonl"
        rows = read_jsonl(season_path)
        chosen = select_items(items, present, args.ids)
        conds = finalize_conditions([parse_cond(text) for text in args.conds] if args.conds else None, items, rows)
        overlap = load_overlap(season_path, conds)
        index_html, index_figures = index_body(rows, overlap, args.column)
        prop_html, prop_figures = propositions_body(chosen)
    except (FileNotFoundError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(standalone("DRAgoWing", index_html), encoding="utf-8")
    (out / "propositions.html").write_text(standalone("命題ごとの四つの形と反例カード", prop_html), encoding="utf-8")
    if args.png:
        try:
            for name, fig in {**index_figures, **prop_figures}.items():
                write_png(fig, out / "png" / f"{name}.png")
        except PngUnavailable as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except (OSError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return 0
