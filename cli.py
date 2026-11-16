"""python -m dragowing RESULTS

HTML を --out（省略時は新しい一時ディレクトリ）に書き、書いたものをリンクで1行ずつ表示する。
重なりは既定で標準ライブラリの経路を使う。--overlap-backend native で従来の経路を選べる。SVG は --svg で、親の plotly_min が描く（Chrome なし）。
"""
from __future__ import annotations

import argparse, sys, tempfile
from pathlib import Path

from .figures import figure_svg
from .forms import load_items
from .htmlout import index_body, propositions_body, standalone
from .overlap import finalize_conditions, load_overlap, parse_cond
from .records import read_jsonl, select_items


def write_svg(spec: dict, path: Path) -> None:
    """🖼️ 図の JSON を SVG に。描くのは親の plotly_min（標準ライブラリ、Chrome なし）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(figure_svg(spec))


def team_order(text: str) -> tuple[str, ...]:
    codes = tuple(code.strip() for code in text.split(",") if code.strip())
    if len(codes) != len(set(codes)):
        raise ValueError("--team-order に同じ記号が2回ある")
    return codes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="記録された結果を HTML にする。判定はやり直さない。")
    parser.add_argument("results", type=Path, nargs="?", help="season.jsonl と propositions.jsonl があるディレクトリ")
    parser.add_argument("--results", dest="legacy_results", type=Path, help="RESULTS の旧形式（互換用）")
    parser.add_argument("--overlap-backend", choices=("stdlib", "native"), default=None,
                        help="既定は RESULTS なら stdlib、旧 --results なら native（NumPy/Polars が必要）")
    parser.add_argument("--out", type=Path, help="HTML の出力ディレクトリ。省略時は新しい一時ディレクトリ（表示するリンクで開く）")
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
        help="重なりの条件。col,op,値（JSON）。例: rd,>,0 。繰り返せる（B クラスを含めて 2〜8 個）。省略すると if の先頭2件と B クラス",
    )
    parser.add_argument(
        "--breakdown",
        default="team",
        help="重なりの内訳を分ける列。team、team_name、league、season、upper_half のどれか。既定は team",
    )
    parser.add_argument(
        "--breakdown-keep",
        action="append",
        default=[],
        help="内訳で「その他」にまとめず別の色で残す値。繰り返せる。例: d（件数にかかわらず残す）",
    )
    parser.add_argument("--svg", action="store_true", help="🖼️ SVG も書く（親の plotly_min、Chrome なし）。既定では HTML だけ")
    parser.add_argument(
        "--embed",
        action="store_true",
        help="index.html に Plotly.js を埋め込む。既定は CDN。propositions.html は Plotly を使わない",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.results is not None and args.legacy_results is not None:
        parser.error("RESULTS と --results は同時に指定できません")
    if args.overlap_backend is None:
        args.overlap_backend = "native" if args.legacy_results is not None else "stdlib"
    args.results = args.results if args.results is not None else args.legacy_results
    if args.results is None:
        parser.error("RESULTS または --results が必要です")
    try:
        items, present = load_items(args.results)
        season_path = Path(args.results) / "season.jsonl"
        rows = read_jsonl(season_path)
        chosen = select_items(items, present, args.ids)
        conds = finalize_conditions([parse_cond(text) for text in args.conds] if args.conds else None, items, rows)
        overlap = load_overlap(season_path, conds, backend=args.overlap_backend)
        index_html, index_figures = index_body(
            rows, overlap, args.column, team_order(args.team_order), args.breakdown, tuple(args.breakdown_keep)
        )
        prop_html = propositions_body(chosen)
    except (FileNotFoundError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out = args.out or Path(tempfile.mkdtemp(prefix="dragowing-"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        standalone("DRAgoWing", index_html, plotly=True, embed=args.embed), encoding="utf-8"
    )
    (out / "propositions.html").write_text(standalone("命題の一覧", prop_html), encoding="utf-8")
    markdown = sys.modules.get("markdown")
    print(f"📦 markdown {getattr(markdown, '__version__', '?')}")
    for name, note in (("index.html", f"📊 {', '.join(index_figures)}"), ("propositions.html", f"🧾 {len(chosen)}")):
        print(f"📄 {(out / name).resolve().as_uri()} {(out / name).stat().st_size} B · {note}")
    if args.svg:
        for name, fig in index_figures.items():
            write_svg(fig, out / "svg" / f"{name}.svg")
        print(f"🖼️ {(out / 'svg').resolve().as_uri()} {len(index_figures)} svg")
    return 0
