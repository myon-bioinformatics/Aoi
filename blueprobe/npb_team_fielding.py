"""取得元: npb.jp の年度別「チーム守備成績」。

URL : https://npb.jp/bis/{year}/stats/tmf_{c|p}.html （c = セ・リーグ、p = パ・リーグ）
1ページ = 1年・1リーグの6球団。チームの記録（個人の記録ではない）。

見出し（2025年・2018年のセ・リーグを WebFetch で確認、2026-10-05）:
  チーム | 守備率 | 試合 | 守備機会 | 刺殺 | 補殺 | 失策 | 併殺（参加・球団の2列にまたがる） | 捕逸
2018年は打撃と同じく見出しの語の中と2文字のチーム名に空白が入る（「失 策」「中 日」）。
表の読み方は打撃と共通（npb_team_batting.parse_team_table）。またがる見出しは下の行と続けた名前（「併殺参加」）で比べる。
知らない見出し・知らないチーム名は unknown に入れる。

記録（1球団1年）:
  observed : raw（行のセルの原文）, source_url
  derived  : season, team, league, 各列の値（整数、守備率は小数）
"""

from __future__ import annotations

import re

from npb_team_batting import check, group, parse_team_table  # noqa: F401  （check・group は同じ）

NAME = "npb_team_fielding"
URL = "https://npb.jp/bis/{year}/stats/tmf_{lg}.html"
LEAGUES = ("c", "p")
PATH = re.compile(r"/bis/(?P<y>\d{4})/stats/tmf_(?P<lg>[cp])\.html")
COLUMNS = {
    "守備率": "fpct", "試合": "g", "守備機会": "tc", "刺殺": "po", "補殺": "a", "失策": "e",
    "併殺参加": "dp_part", "併殺球団": "dp", "捕逸": "pb",
}
RATES = {"fpct"}


def pages(years) -> list[tuple[str, str, str]]:
    return [(f"{y}_{lg}", URL.format(year=y, lg=lg), str(y)) for y in years for lg in LEAGUES]


def parse(html: str, url: str = "") -> dict:
    return parse_team_table(html, url, PATH, COLUMNS, RATES)
