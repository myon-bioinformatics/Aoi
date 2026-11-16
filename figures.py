"""記録された値の Plotly 図 JSON（data / layout）。あてはめ、平滑化、階級への丸めはしない。"""
from __future__ import annotations

import importlib.util, json, math
from functools import lru_cache
from html import escape
from pathlib import Path

A_COLOR = "#1f77b4"
B_COLOR = "#d62728"
LINE_COLOR = "#9aa0a6"
# 図とページで共通。メイリオが無い環境（Mac・iPhone・Linux）では OS 既定の sans-serif になる。
# メイリオは再配布できないので、フォントファイルは同梱しない。
FONT = "Meiryo, メイリオ, sans-serif"

# Plotly の Viridis を ``to_dict()`` したときと同じ段。
_VIRIDIS_SCALE = [
    [0.0, "#440154"],
    [0.1111111111111111, "#482878"],
    [0.2222222222222222, "#3e4989"],
    [0.3333333333333333, "#31688e"],
    [0.4444444444444444, "#26828e"],
    [0.5555555555555556, "#1f9e89"],
    [0.6666666666666666, "#35b779"],
    [0.7777777777777778, "#6ece58"],
    [0.8888888888888888, "#b5de2b"],
    [1.0, "#fde725"],
]


def class_mark(upper) -> tuple[str, str]:
    """upper_half の true/false を A/B と色にする。null は B にしない。"""
    if upper is True:
        return A_COLOR, "A"
    if upper is False:
        return B_COLOR, "B"
    return "#888888", ""


def _base_layout(**extra):
    layout = dict(
        template={},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family=FONT, size=13, color="#1a1a1a"),
        margin=dict(l=60, r=30, t=88, b=50),
    )
    layout.update(extra)
    return layout


def _team_label(league: str, team_name: str, team: str) -> str:
    return f"{league} {team_name} ({team})"


def _subplot_domains(ncols: int, spacing: float = 0.08) -> list[tuple[float, float]]:
    if ncols < 1:
        raise ValueError("ncols")
    width = (1.0 - spacing * (ncols - 1)) / ncols
    return [(index * (width + spacing), index * (width + spacing) + width) for index in range(ncols)]


def _axis_names(col_index: int) -> tuple[str, str]:
    """1-based column index → trace xaxis/yaxis refs and layout axis keys."""
    if col_index == 1:
        return "x", "y"
    suffix = str(col_index)
    return f"x{suffix}", f"y{suffix}"


def _layout_axis_key(axis_ref: str) -> str:
    """trace の軸の名前 → layout のキー: x → xaxis、x2 → xaxis2（plotly.js が読むのはこの形。x2axis は読まれない）。"""
    return f"{axis_ref[0]}axis{axis_ref[1:]}"


def trajectory_figure(rows: list[dict]) -> dict:
    """C3. 得点順位 × 失点順位。点の色は upper_half。線は記録の順をつなぐだけ。"""
    for key in ("league", "team", "team_name", "season", "rank_rf", "rank_ra", "upper_half"):
        if rows and key not in rows[0]:
            raise ValueError(f"列がない: {key}")
    grouped: dict[tuple, list] = {}
    for index, row in enumerate(rows):
        if row.get("rank_rf") is None or row.get("rank_ra") is None:
            continue
        grouped.setdefault((row["league"], row["team"]), []).append((row["season"], index, row))
    leagues = sorted({league for league, _ in grouped})
    if not leagues:
        raise ValueError("軌跡にする行がない")
    domains = _subplot_domains(len(leagues))
    traces: list[dict] = []
    points = []
    layout = _base_layout(
        title=dict(
            text="得点順位 rank_rf × 失点順位 rank_ra<br>点の色: A は upper_half==true、B は upper_half==false<br>線は同じ league・team の記録を season の昇順につないだもの"
        ),
        height=640,
        width=1040,
        legend=dict(font=dict(size=11)),
        meta={"kind": "trajectory", "source": "season.jsonl", "points": points},
    )
    annotations = []
    for col, league in enumerate(leagues, start=1):
        x_ref, y_ref = _axis_names(col)
        x_key = _layout_axis_key(x_ref)
        y_key = _layout_axis_key(y_ref)
        lo, hi = domains[col - 1]
        layout[x_key] = dict(
            anchor=y_ref,
            domain=[lo, hi],
            title=dict(text="得点順位 rank_rf"),
            dtick=1,
        )
        layout[y_key] = dict(
            anchor=x_ref,
            domain=[0.0, 1.0],
            title=dict(text="失点順位 rank_ra"),
            dtick=1,
            scaleanchor=x_ref,
            scaleratio=1,
        )
        annotations.append(
            dict(
                font=dict(size=16),
                showarrow=False,
                text=f"league={league}",
                x=(lo + hi) / 2,
                xanchor="center",
                xref="paper",
                y=1.0,
                yanchor="bottom",
                yref="paper",
            )
        )
        teams = sorted(team for lg, team in grouped if lg == league)
        for team in teams:
            series = sorted(grouped[(league, team)], key=lambda item: (item[0], item[1]))
            team_name = series[0][2]["team_name"]
            custom, colors, xs, ys = [], [], [], []
            for season, _index, row in series:
                color, klass = class_mark(row.get("upper_half"))
                xs.append(row["rank_rf"])
                ys.append(row["rank_ra"])
                colors.append(color)
                custom.append(
                    {
                        "season": row["season"],
                        "league": row["league"],
                        "team": row["team"],
                        "team_name": row["team_name"],
                        "rank_rf": row["rank_rf"],
                        "rank_ra": row["rank_ra"],
                        "upper_half": row["upper_half"],
                        "class": klass,
                    }
                )
                points.append(custom[-1])
            trace = dict(
                type="scatter",
                x=xs,
                y=ys,
                mode="lines+markers",
                name=_team_label(league, team_name, team),
                line=dict(color=LINE_COLOR, width=1, shape="linear"),
                marker=dict(color=colors, size=10, line=dict(width=0)),
                customdata=custom,
                connectgaps=False,
                hovertemplate=(
                    "season=%{customdata.season}<br>"
                    "league=%{customdata.league} %{customdata.team_name} (%{customdata.team})<br>"
                    "rank_rf=%{customdata.rank_rf}<br>"
                    "rank_ra=%{customdata.rank_ra}<br>"
                    "upper_half=%{customdata.upper_half}<br>"
                    "class=%{customdata.class}<extra></extra>"
                ),
                meta={"role": "trajectory", "league": league, "team": team, "team_name": team_name},
            )
            trace["xaxis"] = x_ref
            trace["yaxis"] = y_ref
            traces.append(trace)
    layout["annotations"] = annotations
    traces.extend(
        [
            dict(
                type="scatter",
                x=[],
                y=[],
                mode="markers",
                marker=dict(color=A_COLOR, size=10),
                name="A (upper_half==true)",
                meta={"role": "legend"},
            ),
            dict(
                type="scatter",
                x=[],
                y=[],
                mode="markers",
                marker=dict(color=B_COLOR, size=10),
                name="B (upper_half==false)",
                meta={"role": "legend"},
            ),
        ]
    )
    return {"data": traces, "layout": layout}


def _numeric_column(rows: list[dict], column: str) -> None:
    if not rows or column not in rows[0]:
        raise ValueError(f"列がない: {column}")
    for row in rows:
        value = row.get(column)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"列 {column} は数値ではない")


def _exact_text(value) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def _heatmap_order(teams: list[tuple], team_order=()) -> list[tuple]:
    """``team_order`` の記号を上から順に。載っていない球団はその下に記号順で並べる。"""
    rank = {code: index for index, code in enumerate(team_order)}

    def key(item):
        code = item[1]
        if code in rank:
            return (0, rank[code], item[0])
        return (1, code, item[0])

    return sorted(teams, key=key)


def heatmap_figure(rows: list[dict], column: str = "wins_vs_pythag", team_order=()) -> dict:
    """C4. 球団 × 年。色は列の値。マスの文字は A/B だけ。数はホバー。

    ``team_order`` は上から並べる球団の記号（呼び出し側の設定。省略すると記号順）。
    """
    _numeric_column(rows, column)
    teams = _heatmap_order(list({(row["league"], row["team"], row["team_name"]) for row in rows}), team_order)
    seasons = sorted({row["season"] for row in rows})
    index = {(row["league"], row["team"], row["season"]): row for row in rows}
    codes = [team for _league, team, _name in teams]
    clash = len(codes) != len(set(codes))
    labels = [f"{league}:{team}" if clash else team for league, team, _name in teams]
    z, text, marks, records, custom = [], [], [], [], []
    for (league, team, name), label in zip(teams, labels):
        z_row, text_row, mark_row, custom_row = [], [], [], []
        for season in seasons:
            row = index.get((league, team, season))
            if row is None:
                value, upper, rank = None, None, None
            else:
                value, upper = row.get(column), row.get("upper_half")
                rank = row.get("rank") if "rank" in row else None
            _color, klass = class_mark(upper)
            z_row.append(value)
            text_row.append(klass)
            mark_row.append(klass)
            custom_row.append(
                {
                    "league": league,
                    "team": team,
                    "team_name": name,
                    "season": season,
                    "class": klass,
                    "rank": rank,
                    "rank_text": _exact_text(rank),
                    "value": value,
                    "value_text": _exact_text(value),
                }
            )
            records.append(custom_row[-1] | {"column": column, "upper_half": upper, "mark": klass})
        z.append(z_row)
        text.append(text_row)
        marks.append(mark_row)
        custom.append(custom_row)
    finite = [value for row in z for value in row if isinstance(value, (int, float))]
    zmin = min(finite) if finite else None
    zmax = max(finite) if finite else None
    layout = _base_layout(
        title=dict(text="球団 × 年"),
        height=640,
        width=980,
        meta={
            "kind": "heatmap",
            "source": "season.jsonl",
            "column": column,
            "x": seasons,
            "y": labels,
            "z": z,
            "marks": marks,
            "records": records,
        },
        xaxis=dict(type="category", title=dict(text="season"), automargin=True),
        yaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=list(reversed(labels)),
            title=dict(text="team"),
            automargin=True,
        ),
    )
    trace = dict(
        type="heatmap",
        x=seasons,
        y=labels,
        z=z,
        text=text,
        texttemplate="%{text}",
        textfont=dict(family=FONT, size=14, color="#1a1a1a"),
        customdata=custom,
        colorscale=_VIRIDIS_SCALE,
        zmin=zmin,
        zmax=zmax,
        zsmooth=False,
        hoverongaps=False,
        showlegend=False,
        colorbar=dict(title=dict(text=column)),
        hovertemplate=(
            "team=%{customdata.team} %{customdata.team_name}<br>"
            "season=%{customdata.season}<br>"
            "class=%{customdata.class}<br>"
            "rank=%{customdata.rank_text}<br>"
            f"{column}=%{{customdata.value_text}}<extra></extra>"
        ),
    )
    return {"data": [trace], "layout": layout}


# FFSS experiment records: values are plotted without re-running the experiments.
# (F<NN> identifier, the FFSS (experiment, run) rows it reads). The order is the F number.
FFSS_FIGURES = (("energy-coal", (("E31", "energy:coal"),)), ("energy-gtcc", (("E31", "energy:lng"),)),
                ("losses", (("E31", "energy:coal"), ("E31", "energy:lng"))), ("pinch-tq", (("E31", "tq"),)),
                ("balance-point", (("E32", "balance"),)), ("startup", (("E31", "startup"),)),
                ("sensitivity", (("E31", "sensitivity"),)), ("rate-window", (("E31", "rate-window"),)),
                ("blood-flow", (("E30", "blood"),)))
_COLORS = {"heat": "#FFA15A", "water": "#19d3f3", "power": "#00cc96", "loss": "#9aa0a6", "heart": "#EF553B",
           "organ": "#FF6692", "vein": "#636efa", "lung": "#ab63fa"}
_PLANT = {"coal": "🪨", "lng": "🌀"}


def _rgba(color: str, alpha: float) -> str:
    h = color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha:g})"


def _fig(title: str, data: list, **layout) -> dict:
    """720×448 px（8 の倍数）、余白も 8 の倍数。文字は plotly_min の既定（メイリオ）。"""
    layout = {"title": {"text": title}, "width": 720, "height": 448,
              "margin": layout.pop("margin", {"l": 72, "r": 32, "t": 64, "b": 64}), **layout}
    return {"data": data, "layout": layout}


def _sankey(title: str, rows: list[dict]) -> dict:
    """リンクの行（source・target・組・value・unit）からサンキー図。ノードは出てきた順、ラベルは 名前 + 入りと出の大きい方。"""
    names: dict[str, str] = {}
    for r in rows:
        names.setdefault(r["source"], r["source_group"])
        names.setdefault(r["target"], r["target_group"])
    order = list(names)
    size = {n: max(sum(r["value"] for r in rows if r["source"] == n), sum(r["value"] for r in rows if r["target"] == n))
            for n in order}
    return _fig(title, [{"type": "sankey",  # 単位（% ・L/min）は題に書く
                         "node": {"label": [f"{n} {size[n]:.1f}" for n in order],
                                  "color": [_COLORS[names[n]] for n in order], "pad": 16, "thickness": 16},
                         "link": {"source": [order.index(r["source"]) for r in rows],
                                  "target": [order.index(r["target"]) for r in rows],
                                  "value": [r["value"] for r in rows],
                                  "color": [_rgba(_COLORS[r["target_group"]], 0.35) for r in rows]}}],
                margin={"l": 16, "r": 16, "t": 64, "b": 24})


def _losses(coal: list[dict], lng: list[dict]) -> dict:
    data = []
    for icon, rows in (("🪨", coal), ("🌀", lng)):
        loss = [r for r in rows if r["target_group"] == "loss"]
        grid = next(r["value"] for r in rows if r["target"] == "送電端")
        steps = [100.0, *(-r["value"] for r in loss), grid]
        data.append({"type": "waterfall", "name": icon, "x": [f"{icon} {n}" for n in ("燃料", *(r["target"] for r in loss), "送電端")],
                     "y": steps, "measure": ["absolute", *["relative"] * len(loss), "total"],
                     "text": [f"{abs(v):.1f}" for v in steps]})
    return _fig("🪜 燃料 100 から送電端まで（損を順に引く）", data, showlegend=False, yaxis={"title": {"text": "燃料 100 に対する割合"}, "range": [0, 112]},
                xaxis={"tickangle": -30}, margin={"l": 72, "r": 32, "t": 64, "b": 104})


def _pinch(rows: list[dict]) -> dict:
    gas = [r for r in rows if r["stream"] == "gas"]
    water = [r for r in rows if r["stream"] == "water"]
    fig = _fig("🌡️ 🌀 排熱回収ボイラの T–Q 線図（3 圧・再熱）", [
        {"type": "scatter", "mode": "lines", "name": "ガス（GT の排気）", "x": [r["q_mw"] for r in gas],
         "y": [r["t_c"] for r in gas], "line": {"color": "#EF553B", "width": 3}},
        {"type": "scatter", "mode": "lines", "name": "水・蒸気（3 圧の合成）", "x": [r["q_mw"] for r in water],
         "y": [r["t_c"] for r in water], "line": {"color": "#636efa", "width": 3}}],
        xaxis={"title": {"text": "煙突の側から渡した熱 [MW]"}}, yaxis={"title": {"text": "温度 [°C]"}, "range": [0, 650]})
    names = {"lp": "低圧", "ip": "中圧", "hp": "高圧"}
    for r in (r for r in rows if r["stream"] == "pinch"):
        fig["layout"].setdefault("shapes", []).append({"type": "line", "x0": r["q_mw"], "x1": r["q_mw"], "y0": r["t_c"],
                                                       "y1": r["t_gas_c"], "line": {"color": "#444", "width": 1, "dash": "dot"}})
        fig["layout"].setdefault("annotations", []).append({"x": r["q_mw"], "y": r["t_gas_c"] + 28, "showarrow": False,
                                                            "text": f"{names[r['drum']]} ΔT {r['dt_k']:.1f} K"})
    return fig


def _balance(rows: list[dict]) -> dict:
    curve = [r for r in rows if r["kind"] == "curve"]
    cat = [r for r in rows if r["kind"] == "catalog"]
    bal = next(r["t_out"] for r in rows if r["kind"] == "balance" and not r["iso"])
    ts = [r["t_out"] for r in curve]
    fig = _fig("✖️ 🏠 最大暖房出力と家の暖房負荷（交点 = バランス点）", [
        {"type": "scatter", "mode": "lines", "name": "最大暖房出力（× 除霜）", "x": ts, "y": [r["max_kw"] for r in curve],
         "line": {"color": "#EF553B", "width": 3}},
        {"type": "scatter", "mode": "lines", "name": "家の負荷（JIS）", "x": ts, "y": [r["load_jis_kw"] for r in curve],
         "line": {"color": "#636efa"}},
        {"type": "scatter", "mode": "lines", "name": "家の負荷（ISO 16358-2）", "x": ts, "y": [r["load_iso_kw"] for r in curve],
         "line": {"color": "#636efa", "dash": "dash"}},
        {"type": "scatter", "mode": "markers", "name": "カタログの低温の最大能力", "x": [r["t_out"] for r in cat],
         "y": [r["max_kw"] for r in cat], "marker": {"color": "#444", "size": 10, "symbol": "diamond"}}],
        xaxis={"title": {"text": "外気 [°C]"}}, yaxis={"title": {"text": "暖房 [kW]"}, "range": [0, 10]})
    fig["layout"]["shapes"] = [{"type": "line", "x0": bal, "x1": bal, "xref": "x", "y0": 0, "y1": 1, "yref": "y domain",
                                "line": {"color": "#444", "width": 1, "dash": "dot"}}]
    fig["layout"]["annotations"] = [{"x": bal, "y": 9.3, "showarrow": False, "xanchor": "left",
                                     "text": f"バランス点 {bal:.1f} °C".replace("-", "−")}]
    return fig


def _startup(rows: list[dict]) -> dict:
    keys = [(p, s) for p in ("lng", "coal") for s in ("cold", "hot")]
    labels = [f"{_PLANT[p]} {s}" for p, s in keys]
    phase = {(r["plant"], r["start"], r["phase"]): r for r in rows}
    names = {"steps": ("手順", _COLORS["loss"]), "warmup": ("🧱 暖機", "#EF553B"), "ramp": ("負荷上げ", _COLORS["power"])}
    data = [{"type": "bar", "orientation": "h", "name": name, "y": labels, "marker": {"color": color},
             "base": [phase[(p, s, k)]["from_min"] for p, s in keys],
             "x": [phase[(p, s, k)]["to_min"] - phase[(p, s, k)]["from_min"] for p, s in keys]}
            for k, (name, color) in names.items()]
    for i, (p, s) in enumerate(keys):
        r = phase[(p, s, "steps")]
        data.append({"type": "scatter", "mode": "markers", "name": "Agora の起動時間（並列まで）", "showlegend": i == 0,
                     "x": [r["agora_lo_min"], r["agora_hi_min"]], "y": [labels[i]] * 2,
                     "marker": {"color": "#444", "size": 10, "symbol": "diamond"}})
    at = rows[0]["at"] if rows else 0.5
    return _fig(f"📅 🌅 起動の手順と時間（出典の範囲の at = {at:g}）", data, barmode="overlay",
                xaxis={"title": {"text": "止めてからの時間 [分]"}})


def _assumption(r: dict) -> str:
    icon, name = {"pinch": ("📍", "pinch"), "metal-rate": ("🧱", "温め直し"), "metal-tau": ("🧱", "τ"),
                  "compressor-eta": ("🫧", "圧縮機の効率"), "boiler": ("🪨", "ボイラ")}.get(r["assumption"], ("🎚️", r["assumption"]))
    lo, hi, unit = r["lo"], r["hi"], r["unit"]
    span = f"{lo * 100:g}〜{hi * 100:g} %" if r["assumption"] == "boiler" else f"{lo:g}〜{hi:g}" + (f" {unit}" if unit else "")
    return f"{icon} {name} {span}" + ("" if r["source_range"] else "（幅は仮）")


def _tornado(rows: list[dict]) -> dict:
    spans: dict[str, list[dict]] = {}
    for r in rows:
        spans.setdefault(r["assumption"], []).append(r)
    items = sorted(spans.values(), key=lambda v: max(r["metric"] for r in v) - min(r["metric"] for r in v))
    names = [_assumption(v[0]) for v in items]
    lo = [min(r["metric"] for r in v if not r["use"]) for v in items]
    hi = [max(r["metric"] for r in v if not r["use"]) for v in items]
    use = [next(r["metric"] for r in v if r["use"]) for v in items]
    fig = _fig("🌪️ 🎚️ 仮定を振ったときの 🔮 のずれ（1 を超えると外れる）", [
        {"type": "bar", "orientation": "h", "name": "幅の中", "y": names, "base": lo, "x": [b - a for a, b in zip(lo, hi)],
         "marker": {"color": [_COLORS["power"] if b <= 1.0 else _COLORS["heat"] for b in hi]}},
        {"type": "scatter", "mode": "markers", "name": "使った値", "x": use, "y": names,
         "marker": {"color": "#444", "size": 10, "symbol": "diamond"}}],
        xaxis={"title": {"text": "ずれ ÷ 許容"}}, showlegend=False, margin={"l": 216, "r": 32, "t": 64, "b": 64})
    fig["layout"]["shapes"] = [{"type": "line", "x0": 1.0, "x1": 1.0, "xref": "x", "y0": 0, "y1": 1, "yref": "y domain",
                                "line": {"color": "#EF553B", "width": 2, "dash": "dash"}}]
    return fig


def _window(rows: list[dict], use: tuple[float, float] | None = None) -> dict:
    rates = sorted({r["rate_k_min"] for r in rows})
    taus = sorted({r["tau_h"] for r in rows})
    z = {(r["tau_h"], r["rate_k_min"]): r["metric"] for r in rows}
    if len(z) != len(rows) or len(z) != len(rates) * len(taus):
        raise ValueError("rate-window must be a complete grid without duplicate coordinates")
    return _fig("🧱 cold の起動が Agora の範囲に入る窓（1 以下 = 中）", [
        {"type": "heatmap", "x": rates, "y": taus, "z": [[z[(t, x)] for x in rates] for t in taus], "zmin": 0.0, "zmax": 3.0,
         "colorbar": {"title": {"text": "ずれ ÷ 半幅"}},
         "colorscale": [[0.0, "#2166ac"], [1 / 3, "#f7f7f7"], [1.0, "#b2182b"]]}] + ([
        {"type": "scatter", "mode": "markers", "name": "使った値", "x": [use[0]], "y": [use[1]],
         "marker": {"color": "#444", "size": 12, "symbol": "diamond"}}] if use is not None else []),
        xaxis={"title": {"text": "温め直しの速さ [K/min]"}}, yaxis={"title": {"text": "τ [h]"}}, showlegend=False,
        margin={"l": 72, "r": 96, "t": 64, "b": 64})


def ffss_figures(records: dict[tuple[str, str], list[dict]]) -> dict[str, dict]:
    """F<NN>_<識別子> → plotly の図 JSON（data・layout）。記録の値を並べるだけで、判定はやり直さない。"""
    get = records.get
    # The grid itself does not record a chosen point. Use the sensitivity
    # records when supplied, and omit that marker when they are absent.
    used = {r["assumption"]: r["x"] for r in get(("E31", "sensitivity"), []) if r.get("use")}
    point = (used["metal-rate"], used["metal-tau"]) if {"metal-rate", "metal-tau"} <= used.keys() else None
    build = {"energy-coal": lambda: _sankey("🔀 🪨 石炭火力（USC）: 燃料 100 の行き先（1 段目の割合）", get(("E31", "energy:coal"))),
             "energy-gtcc": lambda: _sankey("🔀 🌀 LNG 複合（GTCC）: 燃料 100 の行き先（1 段目の割合）", get(("E31", "energy:lng"))),
             "losses": lambda: _losses(get(("E31", "energy:coal")), get(("E31", "energy:lng"))),
             "pinch-tq": lambda: _pinch(get(("E31", "tq"))), "balance-point": lambda: _balance(get(("E32", "balance"))),
             "startup": lambda: _startup(get(("E31", "startup"))), "sensitivity": lambda: _tornado(get(("E31", "sensitivity"))),
             "rate-window": lambda: _window(get(("E31", "rate-window")), point),
             "blood-flow": lambda: _sankey("🔀 🫀 心拍出量の行き先（L/min）", get(("E30", "blood")))}
    out = {}
    for n, (name, needs) in enumerate(FFSS_FIGURES, 1):
        if all(records.get(k) for k in needs):  # 記録に無い図は描かない（run E31 だけの記録でもよい）
            try:
                for key in needs:
                    for row in records[key]:
                        if any(isinstance(v, float) and not math.isfinite(v) for v in row.values()):
                            raise ValueError("numeric fields must be finite")
                out[f"F{n:02d}_{name}"] = build[name]()
            except (KeyError, StopIteration, TypeError, ValueError) as exc:
                raise ValueError(f"FFSS F{n:02d}_{name}: incomplete or invalid records ({exc})") from exc
    return out


# --- 🖼️ 図の JSON → SVG（親の plotly_min、Chrome なし） -----------------------------------------------

@lru_cache(maxsize=1)
def plotly_min():
    """vendor/tools/stdlib_min/plotly_min.py（親の stdlib_min を vendor.lock.json で固定）。名前は子どうしでぶつからないように。"""
    path = Path(__file__).resolve().parent / "vendor" / "tools" / "stdlib_min" / "plotly_min.py"
    if not path.is_file():
        raise FileNotFoundError(f"plotly_min が無い: {path}（DRAgoWing のリポジトリから動かす）")
    spec = importlib.util.spec_from_file_location("dragowing_plotly_min", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def figure_svg(spec: dict) -> bytes:
    """🖼️ 図の JSON を SVG に。野球の図（サブプロット・積み上げ・マスの文字）も FFSS の図も同じ道。"""
    return plotly_min().Figure(spec).to_image("svg")


def write_ffss(records_path, out_dir, *, svg: bool = True) -> list[Path]:
    """📊 FFSS の記録から ffss.html（plotly.js）と svg/F<NN>_<識別子>.svg（plotly_min、Chrome なし）を書く。"""
    from .records import read_ffss

    pm = plotly_min()
    figs = ffss_figures(read_ffss(records_path))
    if not figs:
        raise ValueError("FFSS の図にする記録が無い（run E30・E31・E32 か verify の --jsonl）")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    blocks = "".join(f'<section><h2>{escape(name)}</h2>{pm.Figure(spec).to_html(include_plotlyjs=False, full_html=False, div_id=name)}</section>'
                     for name, spec in figs.items())
    page = (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>📊 FFSS の図</title>'
            f'<script src="https://cdn.plot.ly/plotly-{pm.PLOTLY_JS}.min.js" charset="utf-8"></script>'
            f'<style>body{{font-family:{pm.FONT};margin:16px}}h2{{font-size:16px}}</style></head>'
            f'<body><h1>📊 FFSS の図（記録から）</h1>{blocks}</body></html>\n')
    written = [out / "ffss.html"]
    written[0].write_text(page, encoding="utf-8")
    if svg:
        (out / "svg").mkdir(exist_ok=True)
        for name, spec in figs.items():
            path = out / "svg" / f"{name}.svg"
            path.write_bytes(figure_svg(spec))
            written.append(path)
    return written
