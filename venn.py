"""条件の重なり（load_overlap の結果）の図。マスの格子と、領域ごとの内訳の積み上げ棒。

n 個の集合の 2^n 領域を 1 つずつ置く。空の領域も 0 のまま格子に置く。円は描かない。面積は件数と無関係。
返すのは Plotly の JSON 仕様（data / layout）だけ。plotly パッケージも numpy も使わない。
"""
from __future__ import annotations

from collections import Counter
from math import ceil

from .figures import FONT, _base_layout, _exact_text

GAP = 8  # 枠どうし・マスどうしの間隔（px）。px の値は 8 の倍数にしている
LABEL = 24  # 集合の番号ラベルの高さ（px）
BAR_ROW = 24  # 内訳の棒 1 本の高さ（px）
MAX_SERIES = 7  # 内訳で色を付ける値の数。残りは「その他」にまとめる
BY_KEYS = ("team", "team_name", "league", "season", "upper_half")  # 内訳に使える列（unit の項目）
# 集合の枠と内訳の値の色。先頭から固定の順（値の昇順・集合の番号順）で割り当てる。
SERIES_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
OTHER_COLOR = "#898781"
# 件数は一つの色相（青）の薄い→濃い。
COUNT_SCALE = [[0.0, "#cde2fb"], [0.25, "#86b6ef"], [0.5, "#3987e5"], [0.75, "#1c5cab"], [1.0, "#0d366b"]]
INK = "#1a1a1a"
TITLE_LEFT = dict(x=0, xref="container", xanchor="left", font=dict(size=14))  # 図が題より狭くても左が切れない


def _esc(text) -> str:
    """Plotly の文字は HTML の一部を解釈する。条件式の < > & をそのまま見せる。"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _bits_text(bits) -> str:
    return "".join("1" if bit else "0" for bit in bits)


def _gray(width: int) -> list[int]:
    """0 .. 2^width-1 をグレイ符号の順に。先頭の集合（最上位ビット）が 1 の側から始める。"""
    return [k ^ (k >> 1) for k in range(1 << width)][::-1]


def _pattern(value: int, width: int) -> tuple:
    return tuple(bool(value >> (width - 1 - j) & 1) for j in range(width))


def karnaugh(n: int) -> tuple[list[tuple], list[tuple]]:
    """行と列の並び。行は前半 n//2 個の集合、列は残りの集合の入る/入らないの組。

    隣り合う行どうし・列どうしは 1 つの集合だけが違う。マス (r, c) の領域は rows[r] + cols[c]。
    """
    if n < 2:
        raise ValueError("格子にする集合は 2 個以上")
    rows = n // 2
    return (
        [_pattern(v, rows) for v in _gray(rows)],
        [_pattern(v, n - rows) for v in _gray(n - rows)],
    )


def _runs(flags: list[bool]) -> list[tuple[int, int]]:
    """True が続く区間（開始, 終了）。"""
    runs, start = [], None
    for index, flag in enumerate([*flags, False]):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            runs.append((start, index - 1))
            start = None
    return runs


def _set_label(index: int, cond: dict) -> str:
    return f"S{index + 1}: {_esc(cond['label'])}"


def grid_figure(overlap: dict) -> dict:
    """2^n 領域を、カルノー図の並びの格子に置く。マスの数は件数、色は件数（濃いほど多い）。

    集合は枠で示す（行の集合は横長、列の集合は縦長の長方形）。
    """
    conds = overlap["conditions"]
    n = len(conds)
    rows, cols = karnaugh(n)
    row_sets = len(rows[0])
    region = {tuple(r["bits"]): r for r in overlap["regions"]}
    cell = 64 if len(cols) <= 8 else 40
    gap = GAP / cell
    z = [[region[rp + cp]["count"] for cp in cols] for rp in rows]
    custom = [
        [
            {"name": _esc(region[rp + cp]["name"]), "bits": _bits_text(rp + cp), "count": region[rp + cp]["count"]}
            for cp in cols
        ]
        for rp in rows
    ]
    # 枠は格子の外へはみ出す。軸の座標だとはみ出しが切られるので、paper 座標（格子 = 0..1）にする。
    px = lambda x: (x + 0.5) / len(cols)  # noqa: E731
    py = lambda y: 1 - (y + 0.5) / len(rows)  # noqa: E731
    shapes, notes, legend = [], [], []
    for i in range(n):
        by_row = i < row_sets
        axis, k = (rows, i) if by_row else (cols, i - row_sets)
        color = SERIES_COLORS[i % len(SERIES_COLORS)]
        out = (k + 1) * gap  # 同じ側の集合どうしで枠が重ならないよう、外へ GAP ずつずらす
        for a, b in _runs([p[k] for p in axis]):
            if by_row:
                x0, x1, y0, y1 = -0.5 - out, len(cols) - 0.5 + out, a - 0.5 + gap, b + 0.5 - gap
            else:
                x0, x1, y0, y1 = a - 0.5 + gap, b + 0.5 - gap, -0.5 - out, len(rows) - 0.5 + out
            shapes.append(
                dict(type="rect", name=f"S{i + 1}", xref="paper", yref="paper",
                     x0=px(x0), x1=px(x1), y0=py(y0), y1=py(y1),
                     line=dict(color=color, width=2), fillcolor="rgba(0,0,0,0)", layer="above")
            )
            at = dict(showarrow=False, text=f"<b>S{i + 1}</b>", font=dict(size=12, color=INK),
                      bgcolor="#ffffff", bordercolor=color, borderwidth=2, borderpad=2, xref="paper", yref="paper")
            # 入れ子の枠は中心が同じになりやすい。ラベルは集合ごとに LABEL px ずつずらして重ならないようにする
            # （枠の区間からは出さない）。
            spread = (k - (len(axis[0]) - 1) / 2) * LABEL
            room = max(0, (b - a + 1) * cell / 2 - LABEL / 2)
            spread = max(-room, min(room, spread))
            if by_row:  # 右の外側
                at.update(x=px(x1), y=py((y0 + y1) / 2), xanchor="left", yanchor="middle", xshift=4, yshift=-spread)
            else:  # 下の外側
                at.update(x=px((x0 + x1) / 2), y=py(y1), xanchor="center", yanchor="top", yshift=-4, xshift=spread)
            notes.append(at)
        # 空の配列だと Plotly はトレースを非表示にして凡例にも出さない。[None] なら線の見本だけ出る。
        legend.append(
            dict(type="scatter", x=[None], y=[None], mode="lines", name=_set_label(i, conds[i]),
                 line=dict(color=color, width=2), meta={"role": "legend", "set": i + 1})
        )
    col_sets = n - row_sets
    plot_w, plot_h = len(cols) * cell, len(rows) * cell
    longest = max(len(_set_label(i, c)) for i, c in enumerate(conds))
    legend_w = 8 * ceil((longest * 8 + 48) / 8)
    side = row_sets * GAP + 48  # 行の集合の枠とラベルが外へ出る分
    margin = dict(l=48 + 16 * row_sets, r=side + legend_w, t=136 + 16 * col_sets, b=48 + 16 * col_sets)
    heat = dict(
        type="heatmap", x=list(range(len(cols))), y=list(range(len(rows))), z=z,
        texttemplate="%{z}", textfont=dict(family=FONT, size=16 if cell == 64 else 12),
        customdata=custom, colorscale=COUNT_SCALE, zmin=0, zsmooth=False, xgap=2, ygap=2,
        showscale=False, showlegend=False,
        hovertemplate="領域 %{customdata.name}<br>桁 %{customdata.bits}<br>件数 %{customdata.count}<extra></extra>",
    )
    hidden = dict(ticks="outside", tickcolor="rgba(0,0,0,0)", showgrid=False, zeroline=False, tickfont=dict(size=12))
    span = lambda a, b: f"S{a}" if a == b else f"S{a}–S{b}"  # noqa: E731
    layout = _base_layout(
        title=dict(
            text=(f"条件の重なり: {n} 集合・{2 ** n} 領域<br>"
                  f"行は {span(1, row_sets)}、列は {span(row_sets + 1, n)} に入る(1)・入らない(0)<br>"
                  "隣のマスは 1 つの集合だけ違う。空の領域も 0 で置く"),
            **TITLE_LEFT,
        ),
        width=max(640, margin["l"] + plot_w + margin["r"]),  # 題が切れない最小幅
        height=margin["t"] + plot_h + margin["b"],
        margin=margin,
        xaxis=dict(tickvals=list(range(len(cols))), ticktext=[_bits_text(c) for c in cols], side="top",
                   range=[-0.5, len(cols) - 0.5], ticklen=col_sets * GAP + 8, **hidden),
        yaxis=dict(tickvals=list(range(len(rows))), ticktext=[_bits_text(r) for r in rows],
                   range=[len(rows) - 0.5, -0.5], ticklen=row_sets * GAP + 8, **hidden),
        shapes=shapes,
        annotations=notes,
        legend=dict(x=1 + side / plot_w, xanchor="left", y=1, yanchor="top", font=dict(size=12)),
        meta={
            "kind": "overlap_grid",
            "source": "season.jsonl",
            "sets": [{"index": i + 1, "label": c["label"]} for i, c in enumerate(conds)],
            "rows": [_bits_text(r) for r in rows],
            "cols": [_bits_text(c) for c in cols],
            "z": z,
        },
    )
    return {"data": [heat, *legend], "layout": layout}


def _label(value) -> str:
    return value if isinstance(value, str) else _exact_text(value)


def breakdown_figure(overlap: dict, by: str = "team", keep: tuple = ()) -> dict:
    """領域ごとの件数を、`by` の値で分けた積み上げ棒。長さが件数、色が値。

    色は値の昇順で割り当てる。MAX_SERIES を超える値は「その他」にまとめ、中身はホバーに出す。
    `keep` の値（文字列で書く）は件数にかかわらず別の色で残す。件数 0 の領域は棒にせず、数を題に書く
    （格子とページの表には出ている）。
    """
    if by not in BY_KEYS:
        raise ValueError(f"内訳の列は {', '.join(BY_KEYS)} のどれか: {by}")
    units = overlap["units"]
    if not units:
        raise ValueError("内訳にする行がない")
    totals = Counter(unit[by] for unit in units)
    order = sorted(totals, key=lambda v: (v is None, v))
    forced = [v for v in order if _label(v) in keep]
    if len(forced) > MAX_SERIES:
        raise ValueError(f"breakdown-keep で別の色に残せる値は {MAX_SERIES} 個まで")
    rest = sorted((v for v in order if v not in forced), key=lambda v: -totals[v])
    shown = set(forced + rest[: max(0, MAX_SERIES - len(forced))])
    kept = [v for v in order if v in shown]
    folded = [v for v in order if v not in shown]

    regions = sorted((r for r in overlap["regions"] if r["count"]), key=lambda r: -r["count"])
    empty = len(overlap["regions"]) - len(regions)
    labels = [f"{_bits_text(r['bits'])}  ({r['count']})" for r in regions]
    members = [Counter(units[i][by] for i in r["unit_index"]) for r in regions]
    traces = []
    for slot, value in enumerate(kept):
        traces.append(
            dict(type="bar", orientation="h", name=_esc(_label(value)), y=labels,
                 x=[m[value] for m in members],
                 marker=dict(color=SERIES_COLORS[slot % len(SERIES_COLORS)], line=dict(color="#ffffff", width=2)),
                 hovertemplate="領域 %{y}<br>" + _esc(_label(value)) + " %{x}<extra></extra>",
                 meta={"role": "series", "value": value})
        )
    if folded:
        inside = [", ".join(f"{_esc(_label(v))} {m[v]}" for v in folded if m[v]) for m in members]
        traces.append(
            dict(type="bar", orientation="h", name="その他", y=labels,
                 x=[sum(m[v] for v in folded) for m in members],
                 marker=dict(color=OTHER_COLOR, line=dict(color="#ffffff", width=2)),
                 customdata=inside,
                 hovertemplate="領域 %{y}<br>その他 %{x}<br>%{customdata}<extra></extra>",
                 meta={"role": "other", "values": folded})
        )
    biggest = max(r["count"] for r in regions) if regions else 0
    count_axis = dict(title=dict(text="件数"), rangemode="tozero", tickformat="d")
    if biggest <= 10:
        count_axis["dtick"] = 1  # 少ないときに 2.5 件の目盛りが出ない
    plot_h = max(len(regions), 1) * BAR_ROW
    longest = max([len(t["name"]) for t in traces] + [3])
    layout = _base_layout(
        title=dict(
            text=(f"領域ごとの内訳（{by}）<br>棒の長さは件数、左の括弧の数は領域の件数。"
                  f"空の領域 {empty} 個は棒にしない"
                  + (f"。{len(folded)} 個の値は「その他」" if folded else "")),
            **TITLE_LEFT,
        ),
        width=1040,
        height=plot_h + 160,
        margin=dict(l=168, r=8 * ceil((longest * 8 + 56) / 8), t=96, b=64),
        barmode="stack",
        bargap=0.2,
        xaxis=count_axis,
        yaxis=dict(type="category", categoryorder="array", categoryarray=labels, autorange="reversed", automargin=True),
        legend=dict(x=1.02, xanchor="left", y=1, yanchor="top", font=dict(size=12), traceorder="normal"),
        meta={
            "kind": "overlap_breakdown",
            "source": "season.jsonl",
            "by": by,
            "empty_regions": empty,
            "folded": folded,
            "regions": [
                {"bits": _bits_text(r["bits"]), "count": r["count"], "by": {_label(v): c for v, c in m.items()}}
                for r, m in zip(regions, members)
            ],
        },
    )
    return {"data": traces, "layout": layout}


def venn_figures(overlap: dict, by: str = "team", keep: tuple = ()) -> dict[str, dict]:
    """Python から呼ぶ入口。load_overlap の結果から二つの図の仕様を返す。"""
    return {"overlap_grid": grid_figure(overlap), "overlap_breakdown": breakdown_figure(overlap, by, keep)}
