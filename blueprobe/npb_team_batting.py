"""取得元: npb.jp の年度別「チーム打撃成績」。

URL : https://npb.jp/bis/{year}/stats/tmb_{c|p}.html （c = セ・リーグ、p = パ・リーグ。2012〜2025年は同じ列）
1ページ = 1年・1リーグの6球団。

表の見出し行（先頭のセルが「チーム」）で列を決め、同じセル数の行を1球団として読む。
見出しは正規化し、語の中の空白を除いてから既知の名前と全体一致で比べる
（2012〜2024年は「打 率」のように空白が入り、2025年は入らない。「故意四球」と「故意四」は同じ列）。
チーム名は既知の表記と全体一致。2012〜2024年の「中 日」のように1文字ずつ空けた形は、詰めると既知の表記になるときだけ読む。
知らない見出し・知らないチーム名は unknown に入れる（黙って捨てない・黙って採用しない）。

記録（1球団1年）:
  observed : raw（行のセルの原文）, source_url
  derived  : season, team, league, 各列の値（整数、率は小数）
ここで率の計算はしない（SakAnalytics の仕事）。ページの率（avg, slg, obp）は照合のために残す。
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from selectolax.lexbor import LexborHTMLParser

from blueprobe import new_report, normalize
from npb_calendar import LEAGUE, TEAM_NAME

NAME = "npb_team_batting"
URL = "https://npb.jp/bis/{year}/stats/tmb_{lg}.html"
LEAGUES = {"c": "C", "p": "P"}
PATH = re.compile(r"/bis/(?P<y>\d{4})/stats/tmb_(?P<lg>[cp])\.html")

# 見出し（正規化後）→ 列名。別の表記は同じ列に寄せる
COLUMNS = {
    "打率": "avg", "試合": "g", "打席": "pa", "打数": "ab", "得点": "r", "安打": "h", "二塁打": "b2",
    "三塁打": "b3", "本塁打": "hr", "塁打": "tb", "打点": "rbi", "盗塁": "sb", "盗塁刺": "cs", "犠打": "sh",
    "犠飛": "sf", "四球": "bb", "故意四球": "ibb", "故意四": "ibb", "死球": "hbp", "三振": "so",
    "併殺打": "gdp", "長打率": "slg", "出塁率": "obp",
}
RATES = {"avg", "slg", "obp"}
TEAM_BY_NAME = {v: k for k, v in TEAM_NAME.items()}
INT = re.compile(r"[0-9]{1,5}")
RATE = re.compile(r"[01]?\.[0-9]{3}")
SPREAD = re.compile(r"\S \S")  # 2文字のチーム名を1文字空けた書き方（「中 日」）。観測したのは2文字の名前だけ


def pages(years) -> list[tuple[str, str, str]]:
    return [(f"{y}_{lg}", URL.format(year=y, lg=lg), str(y)) for y in years for lg in LEAGUES]


def _cells(tr) -> list[str]:
    return [normalize(c.text(deep=True)) for c in tr.iter() if c.tag in ("td", "th")]


def parse(html: str, url: str = "") -> dict:
    out = new_report()
    m = PATH.fullmatch(urlsplit(url).path) if url else None
    season, league = (int(m["y"]), LEAGUES[m["lg"]]) if m else (None, None)
    header = None
    for tr in LexborHTMLParser(html).css("tr"):
        cells = _cells(tr)
        names = [re.sub(r"\s", "", c) for c in cells]  # 見出しは語の中に空白が入る年がある（2012〜2024年の「打 率」）
        if names and names[0] == "チーム":
            unknown = [c for c in names[1:] if c not in COLUMNS]
            if unknown:
                out["unknown"].append({"key": f"header:{season}:{league}", "raw": " | ".join(unknown)})
                header = None
                continue
            header = [COLUMNS[c] for c in names[1:]]
            continue
        if header is None or len(cells) != len(header) + 1:
            continue
        name, values = cells[0], cells[1:]
        # 2012〜2024年は2文字のチーム名を1文字ずつ空けて書く（「中 日」）。1文字ずつ空いた形だけを詰める
        team = TEAM_BY_NAME.get(name) or (TEAM_BY_NAME.get(name.replace(" ", "")) if SPREAD.fullmatch(name) else None)
        if team is None or (league and LEAGUE[team] != league):
            out["unknown"].append({"key": f"{season}:{name}", "raw": " | ".join(cells)})
            continue
        rec = {"key": f"{season}-{team}", "season": season, "team": team, "league": LEAGUE[team]}
        bad = False
        for col, v in zip(header, values):
            pat = RATE if col in RATES else INT
            if not pat.fullmatch(v):
                bad = True
                break
            rec[col] = float(v) if col in RATES else int(v)
        if bad:
            out["unknown"].append({"key": f"{season}:{team}", "raw": " | ".join(cells)})
            continue
        out["records"].append({**rec, "raw": " | ".join(cells), "source_url": url})
    return out


def check(records: list[dict]) -> list[dict]:
    """年ごとに12球団そろっているか。打数などの整合（出塁率の再計算）は SakAnalytics で照合する。"""
    from collections import Counter

    n = Counter(r["season"] for r in records)
    out = []
    for y in sorted(n):
        teams = {r["team"] for r in records if r["season"] == y}
        ok = teams == set(TEAM_NAME)
        out.append({"group": str(y), "ok": ok, "text": f"{y}: teams={len(teams)} expected=12 " + ("OK" if ok else "要確認")})
    return out


def group(record: dict) -> str:
    return str(record["season"])
