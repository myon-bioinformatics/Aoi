"""記録された値の Plotly 図。あてはめ、平滑化、階級への丸めはしない。"""
from __future__ import annotations

import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import forms
from ask import registration_status
from .forms import FORM_LABEL, _counts, _form_cell, _forms, contingency

A_COLOR = "#1f77b4"
B_COLOR = "#d62728"
LINE_COLOR = "#9aa0a6"
FONT = "Noto Sans JP, Yu Gothic, Meiryo, sans-serif"


def class_mark(upper) -> tuple[str, str]:
    """upper_half の true/false を A/B と色にする。null は B にしない。"""
    if upper is True:
        return A_COLOR, "A"
    if upper is False:
        return B_COLOR, "B"
    return "#888888", ""


def _base_layout(**extra):
    layout = dict(
        template=None,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family=FONT, size=13, color="#1a1a1a"),
        margin=dict(l=60, r=30, t=88, b=50),
    )
    layout.update(extra)
    return layout


def _rate_suffix(form: dict | None) -> str:
    if not form or _counts(form) is None:
        return ""
    rate = form.get("rate")
    if isinstance(rate, bool) or not isinstance(rate, (int, float)):
        return ""
    return "\nrate=" + json.dumps(rate, ensure_ascii=False)


def form_meta(form: dict | None) -> dict:
    counts = _counts(form) if form else None
    rate = None
    if form and counts is not None:
        raw = form.get("rate")
        if not isinstance(raw, bool) and isinstance(raw, (int, float)):
            rate = raw
    return {
        "form": form.get("form") if form else None,
        "n": counts[0] if counts else None,
        "hold": counts[1] if counts else None,
        "counterexample_count": (counts[0] - counts[1]) if counts else None,
        "rate": rate,
    }


def four_forms_figure(item: dict) -> go.Figure:
    """C1. 2×2 と四つの形。印は registration_status。"""
    label = registration_status(item)
    cells = contingency(item)
    forms_by_name = _forms(item)
    order = ("original", "converse", "inverse", "contrapositive")
    metas = []
    texts = {}
    for name in order:
        form = forms_by_name.get(name)
        metas.append(form_meta(form))
        texts[name] = f"{FORM_LABEL[name]}: {_form_cell(form)}{_rate_suffix(form)}"
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "table"}], [{"type": "table"}]],
        vertical_spacing=0.08,
        row_heights=[0.42, 0.58],
    )
    fig.add_trace(
        go.Table(
            header=dict(values=["", "Q", "¬Q"], fill_color="#f4f4f4", align="center", font=dict(family=FONT, size=14)),
            cells=dict(
                values=[
                    ["P", "¬P"],
                    [forms._cell(cells["P∧Q"]), forms._cell(cells["¬P∧Q"])],
                    [forms._cell(cells["P∧¬Q"]), forms._cell(cells["¬P∧¬Q"])],
                ],
                align="center",
                font=dict(family=FONT, size=16),
                height=32,
            ),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Table(
            header=dict(values=["", ""], fill_color="#f4f4f4", align="center"),
            cells=dict(
                values=[
                    [texts["original"], texts["inverse"]],
                    [texts["converse"], texts["contrapositive"]],
                ],
                align="left",
                font=dict(family=FONT, size=13),
                height=36,
            ),
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"［{label}］ {item.get('id', '')}"),
            height=560,
            margin=dict(l=16, r=16, t=64, b=16),
            meta={
                "kind": "four_forms",
                "id": item.get("id"),
                "registration": label,
                "cells": cells,
                "forms": metas,
            },
        )
    )
    return fig


def _team_label(league: str, team_name: str, team: str) -> str:
    return f"{league} {team_name} ({team})"


def trajectory_figure(rows: list[dict]) -> go.Figure:
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
    fig = make_subplots(
        rows=1,
        cols=len(leagues),
        subplot_titles=[f"league={league}" for league in leagues],
        horizontal_spacing=0.08,
    )
    points = []
    for col, league in enumerate(leagues, start=1):
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
            fig.add_trace(
                go.Scatter(
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
                ),
                row=1,
                col=col,
            )
        axis = "x" if col == 1 else f"x{col}"
        fig.update_xaxes(title_text="得点順位 rank_rf", dtick=1, row=1, col=col)
        fig.update_yaxes(
            title_text="失点順位 rank_ra",
            dtick=1,
            scaleanchor=axis,
            scaleratio=1,
            row=1,
            col=col,
        )
    fig.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="markers",
            marker=dict(color=A_COLOR, size=10),
            name="A (upper_half==true)",
            meta={"role": "legend"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="markers",
            marker=dict(color=B_COLOR, size=10),
            name="B (upper_half==false)",
            meta={"role": "legend"},
        )
    )
    fig.update_layout(
        **_base_layout(
            title=dict(
                text="得点順位 rank_rf × 失点順位 rank_ra<br>点の色: A は upper_half==true、B は upper_half==false<br>線は同じ league・team の記録を season の昇順につないだもの"
            ),
            height=640,
            width=1040,
            legend=dict(font=dict(size=11)),
            meta={"kind": "trajectory", "source": "season.jsonl", "points": points},
        )
    )
    return fig


def _numeric_column(rows: list[dict], column: str) -> None:
    if not rows or column not in rows[0]:
        raise ValueError(f"列がない: {column}")
    for row in rows:
        value = row.get(column)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"列 {column} は数値ではない")


def heatmap_figure(rows: list[dict], column: str = "wins_vs_pythag") -> go.Figure:
    """C4. 球団 × 年。値は列の記録。B は upper_half==false のマスだけに付ける。"""
    _numeric_column(rows, column)
    teams = sorted({(row["league"], row["team"], row["team_name"]) for row in rows})
    seasons = sorted({row["season"] for row in rows})
    index = {(row["league"], row["team"], row["season"]): row for row in rows}
    labels = [_team_label(league, name, team) for league, team, name in teams]
    z, text, marks, records = [], [], [], []
    for league, team, name in teams:
        z_row, text_row, mark_row = [], [], []
        for season in seasons:
            row = index.get((league, team, season))
            if row is None:
                value, upper = None, None
            else:
                value, upper = row.get(column), row.get("upper_half")
            _color, klass = class_mark(upper)
            mark = "B" if upper is False else ""
            shown = "null" if value is None else json.dumps(value, ensure_ascii=False)
            if mark:
                shown = f"{shown} {mark}"
            z_row.append(value)
            text_row.append(shown)
            mark_row.append(mark)
            records.append(
                {
                    "league": league,
                    "team": team,
                    "team_name": name,
                    "season": season,
                    "column": column,
                    "value": value,
                    "upper_half": upper,
                    "mark": mark,
                    "class": klass,
                }
            )
        z.append(z_row)
        text.append(text_row)
        marks.append(mark_row)
    custom = []
    cursor = 0
    for _team in teams:
        custom.append(records[cursor : cursor + len(seasons)])
        cursor += len(seasons)
    fig = go.Figure(
        data=[
            go.Heatmap(
                x=seasons,
                y=labels,
                z=z,
                text=text,
                texttemplate="%{text}",
                customdata=custom,
                colorscale="Viridis",
                zsmooth=False,
                hoverongaps=False,
                colorbar=dict(title=dict(text=column)),
                hovertemplate=(
                    "league=%{customdata.league} %{customdata.team_name} (%{customdata.team})<br>"
                    "season=%{customdata.season}<br>"
                    f"{column}=%{{customdata.value}}<br>"
                    "upper_half=%{customdata.upper_half}<br>"
                    "mark=%{customdata.mark}<extra></extra>"
                ),
            )
        ]
    )
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"{column}<br>B は upper_half==false のマス"),
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
        )
    )
    fig.update_xaxes(type="category", title_text="season")
    fig.update_yaxes(type="category", categoryorder="array", categoryarray=list(reversed(labels)), title_text="team")
    return fig


_CIRCLES = {
    2: [(-0.55, 0.1, 0.95), (0.55, 0.1, 0.95)],
    3: [(-0.58, 0.42, 1.05), (0.58, 0.42, 1.05), (0.0, -0.38, 1.05)],
}
_SPOTS = {
    2: {
        (False, False): (-1.7, -1.25),
        (True, False): (-1.05, 0.2),
        (False, True): (1.05, 0.2),
        (True, True): (0.0, 0.2),
    },
    3: {
        (False, False, False): (-1.95, -1.5),
        (True, False, False): (-1.25, 0.9),
        (False, True, False): (1.25, 0.9),
        (False, False, True): (0.0, -1.2),
        (True, True, False): (0.0, 1.0),
        (True, False, True): (-0.62, -0.12),
        (False, True, True): (0.62, -0.12),
        (True, True, True): (0.0, 0.32),
    },
}
_FILL = ("rgba(31,119,180,0.28)", "rgba(255,127,14,0.28)", "rgba(44,160,44,0.28)")
_SOLID = ("#1f77b4", "#ff7f0e", "#2ca02c")


def overlap_figure(overlap: dict) -> go.Figure:
    """C5. 円の面積は件数ではない。件数は整数ラベル。"""
    conds = overlap["conditions"]
    n_sets = len(conds)
    if n_sets not in (2, 3):
        raise ValueError("条件集合は 2 個か 3 個にする（B クラスを含む）")
    shapes = []
    for (cx, cy, radius), fill in zip(_CIRCLES[n_sets], _FILL):
        shapes.append(
            dict(
                type="circle",
                x0=cx - radius,
                y0=cy - radius,
                x1=cx + radius,
                y1=cy + radius,
                line=dict(color="#333333", width=1),
                fillcolor=fill,
                layer="below",
            )
        )
    fig = go.Figure()
    annotations = []
    for region in overlap["regions"]:
        spot = _SPOTS[n_sets][tuple(region["bits"])]
        text = f"外 {region['count']}" if not any(region["bits"]) else str(region["count"])
        annotations.append(dict(x=spot[0], y=spot[1], text=text, showarrow=False, font=dict(size=16, color="#111111")))
    for index, cond in enumerate(conds):
        fig.add_trace(
            go.Scatter(
                x=[],
                y=[],
                mode="markers",
                marker=dict(size=12, color=_SOLID[index]),
                name=cond["label"],
                meta={"role": "legend"},
            )
        )
    names = " · ".join(cond["label"] for cond in conds)
    fig.update_layout(
        **_base_layout(
            title=dict(text=f"条件集合の重なり<br>{names}<br>円の面積は件数ではない。件数はラベルの整数"),
            height=700,
            width=820,
            shapes=shapes,
            annotations=annotations,
            xaxis=dict(visible=False, range=[-2.6, 2.6]),
            yaxis=dict(visible=False, range=[-2.15, 2.35], scaleanchor="x", scaleratio=1),
            meta={
                "kind": "overlap",
                "source": "season.jsonl",
                "conditions": overlap["conditions"],
                "regions": overlap["regions"],
                "units": overlap["units"],
                "matrix": overlap["matrix"],
            },
        )
    )
    return fig
