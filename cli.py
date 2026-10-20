"""python -m dragowing --results DIR --out DIR

HTML を書く。PNG / SVG は --png / --svg と Chrome があるときだけ。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .chrome_pipe import find_chrome
from .export import PLOTLY, export_draw, plotly_figure_content
from .render import RenderSession
from .forms import load_items
from .htmlout import index_body, propositions_body, standalone
from .overlap import finalize_conditions, load_overlap, parse_cond
from .records import read_jsonl, select_items


class ExportUnavailable(RuntimeError):
    """Chrome が無い。HTML は書けている。"""


class PngUnavailable(ExportUnavailable):
    """Chrome が無い。後方互換のための例外クラス。"""


def write_image(
    spec: dict, path: Path, fmt: str = "png", *, chrome: str | None = None, session: RenderSession | None = None
) -> None:
    """session を渡すと、その Chrome を使い回す（--png と --svg で起動は 1 回）。"""
    if session is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        export_draw(PLOTLY, plotly_figure_content(spec), path, fmt, session=session)
        return
    try:
        executable = find_chrome(chrome)
    except RuntimeError as exc:
        raise ExportUnavailable(
            f"{fmt.upper()} には Chrome/Chromium が必要です。--chrome または CHROME 環境変数で実行ファイルを指定してください。"
        ) from exc
    path.parent.mkdir(parents=True, exist_ok=True)
    export_draw(PLOTLY, plotly_figure_content(spec), path, fmt, chrome=executable)


def write_png(spec: dict, path: Path, *, chrome: str | None = None) -> None:
    try:
        write_image(spec, path, "png", chrome=chrome)
    except ExportUnavailable as exc:
        raise PngUnavailable(str(exc)) from exc


def write_svg(spec: dict, path: Path, *, chrome: str | None = None) -> None:
    write_image(spec, path, "svg", chrome=chrome)


def team_order(text: str) -> tuple[str, ...]:
    codes = tuple(code.strip() for code in text.split(",") if code.strip())
    if len(codes) != len(set(codes)):
        raise ValueError("--team-order に同じ記号が2回ある")
    return codes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="記録された結果を HTML にする。判定はやり直さない。")
    parser.add_argument("--results", type=Path, required=True, help="season.jsonl と propositions.jsonl があるディレクトリ")
    parser.add_argument("--out", type=Path, required=True, help="HTML の出力ディレクトリ")
    parser.add_argument("--id", action="append", dest="ids", help="この命題だけ。繰り返せる。省略すると全部")
    parser.add_argument("--column", default="wins_vs_pythag", help="球団×年に置く数値列。既定は wins_vs_pythag")
    parser.add_argument(
        "--team-order",
        default="",
        help="球団×年で上から並べる球団の記号（カンマ区切り）。例: d,g,s 。省略すると記号順",
    )
    parser.add_argument(
        "--cond",
        action="append",
        dest="conds",
        help="重なりの条件。col,op,値（JSON）。例: rd,>,0 。省略すると if の先頭2件と B クラス",
    )
    parser.add_argument(
        "--chrome",
        default=None,
        help="Chrome/Chromium の実行ファイル。省略時は CHROME / CHROMIUM 環境変数、なければ PATH",
    )
    parser.add_argument(
        "--overlap-backend", choices=("native", "stdlib"), default="native",
        help="重なり計算。stdlib は限定したスカラー列のみ（numpy/polars 不要）。既定は native",
    )
    parser.add_argument("--png", action="store_true", help="PNG も書く。Chrome が要る。既定では HTML だけ")
    parser.add_argument("--svg", action="store_true", help="SVG も書く。Chrome が要る。既定では HTML だけ")
    parser.add_argument(
        "--embed",
        action="store_true",
        help="index.html に Plotly.js を埋め込む。既定は CDN。propositions.html は Plotly を使わない",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        items, present = load_items(args.results)
        season_path = Path(args.results) / "season.jsonl"
        rows = read_jsonl(season_path)
        chosen = select_items(items, present, args.ids)
        conds = finalize_conditions([parse_cond(text) for text in args.conds] if args.conds else None, items, rows)
        overlap = load_overlap(season_path, conds, backend=args.overlap_backend)
        index_html, index_figures = index_body(rows, overlap, args.column, team_order(args.team_order))
        prop_html = propositions_body(chosen)
    except (FileNotFoundError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        standalone("DRAgoWing", index_html, plotly=True, embed=args.embed), encoding="utf-8"
    )
    (out / "propositions.html").write_text(standalone("命題の一覧", prop_html), encoding="utf-8")
    if args.png or args.svg:
        formats = [fmt for fmt, wanted in (("png", args.png), ("svg", args.svg)) if wanted]
        try:
            try:
                executable = find_chrome(args.chrome)
            except RuntimeError as exc:
                raise ExportUnavailable(
                    f"{'/'.join(f.upper() for f in formats)} には Chrome/Chromium が必要です。"
                    "--chrome または CHROME 環境変数で実行ファイルを指定してください。"
                ) from exc
            # 図と形式が何件あっても Chrome の起動は 1 回だけ。
            with RenderSession(chrome=executable) as session:
                for name, fig in index_figures.items():
                    for fmt in formats:
                        write_image(fig, out / fmt / f"{name}.{fmt}", fmt, session=session)
        except ExportUnavailable as exc:
            print(str(exc), file=sys.stderr)
            return 2
        except (OSError, ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1
    return 0
