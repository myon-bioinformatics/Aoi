"""記録された値の Plotly 図。あてはめ、平滑化、階級への丸めはしない。"""
from __future__ import annotations

import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots

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


# 上から下。中日 d を最上段にする。括弧内の並びは記録にある記号で、d を先頭に繰り上げたもの。
_TEAM_TOP_DOWN = ("d", "g", "s", "db", "t", "c", "h", "f", "b", "e", "l", "m")


def _exact_text(value) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def _heatmap_order(teams: list[tuple]) -> list[tuple]:
    rank = {code: index for index, code in enumerate(_TEAM_TOP_DOWN)}

    def key(item):
        code = item[1]
        if code in rank:
            return (0, rank[code], item[0])
        return (1, code, item[0])

    return sorted(teams, key=key)


def heatmap_figure(rows: list[dict], column: str = "wins_vs_pythag") -> go.Figure:
    """C4. 球団 × 年。色は列の値。マスの文字は A/B だけ。数はホバー。"""
    _numeric_column(rows, column)
    teams = _heatmap_order(list({(row["league"], row["team"], row["team_name"]) for row in rows}))
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
    fig = go.Figure(
        data=[
            go.Heatmap(
                x=seasons,
                y=labels,
                z=z,
                text=text,
                texttemplate="%{text}",
                textfont=dict(family=FONT, size=14, color="#1a1a1a"),
                customdata=custom,
                colorscale="Viridis",
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
        ]
    )
    fig.update_layout(
        **_base_layout(
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
        )
    )
    fig.update_xaxes(type="category", title_text="season", automargin=True)
    fig.update_yaxes(
        type="category",
        categoryorder="array",
        categoryarray=list(reversed(labels)),
        title_text="team",
        automargin=True,
    )
    return fig

