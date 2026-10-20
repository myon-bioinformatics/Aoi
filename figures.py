"""記録された値の Plotly 図 JSON（data / layout）。あてはめ、平滑化、階級への丸めはしない。"""
from __future__ import annotations

import json

A_COLOR = "#1f77b4"
B_COLOR = "#d62728"
LINE_COLOR = "#9aa0a6"
FONT = "Noto Sans JP, Yu Gothic, Meiryo, sans-serif"

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
    return "xaxis" if axis_ref == "x" else f"{axis_ref}axis"


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
