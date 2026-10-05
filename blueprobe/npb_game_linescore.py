"""取得元: npb.jp の試合ごとのページの得点表（R H E）。チームの記録（個人の記録は読まない）。

URL : 日程（npb_calendar）の観測に入っている試合のリンク（https://npb.jp/bis/{year}/games/s{試合ID}.html）
1ページ = 1試合。得点表の2行（ビジター・ホーム）から、チームごとの得点（R）・安打（H）・失策（E）を読む。
回ごとの得点の列は原文のまま残すが、ここでは解釈しない。回ごとの失策はページにない。

形（WebFetch で 2024年の1試合を確認、2026-10-05）:
  「読 売 0 0 0 3 0 0 0 0 0 0 0 - 3 11 0」「中 日 0 0 0 0 0 1 2 0 0 0 1X - 4 9 0」
  チーム名は2文字を1文字空けて書き、巨人は「読売」と書く。最後の3つのセルが R・H・E。
知らないチーム名・形の合わない行は unknown に入れる（黙って捨てない・黙って採用しない）。
取得量が大きい（1年 約860ページ）ので、パイプラインでは年を絞って取得する（R63、ユーザーと決めた: まず 2025年）。

記録（1チーム1試合）:
  observed : raw（行のセルの原文）, source_url
  derived  : key（試合ID-チーム）, game_id, season, date, team, r, h, e
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from selectolax.lexbor import LexborHTMLParser

from blueprobe import new_report, normalize
from npb_calendar import GAME_PATH, LEAGUE, TEAM_NAME

NAME = "npb_game_linescore"
GAMES = Path("data/observations/npb_calendar/games.jsonl")   # 日程の観測（パイプラインの root から）
TEAM_BY_NAME = {v: k for k, v in TEAM_NAME.items()} | {"読売": "g"}
INT = re.compile(r"[0-9]{1,3}")


def pages(years, games: Path = GAMES) -> list[tuple[str, str, str]]:
    """日程の観測から、指定した年の試合ページを並べる（日付順）。"""
    if not games.exists():
        return []
    want = {int(y) for y in years}
    out = []
    for line in games.read_text(encoding="utf-8").splitlines():
        g = json.loads(line)
        m = GAME_PATH.fullmatch(urlsplit(g.get("href", "")).path)
        if m and int(m["y"]) in want:
            out.append((m["id"], f"https://npb.jp{m.group(0)}", m["y"]))
    return sorted(set(out))


def _cells(tr) -> list[str]:
    return [normalize(c.text(deep=True)) for c in tr.iter() if c.tag in ("td", "th")]


def parse(html: str, url: str = "") -> dict:
    out = new_report()
    m = GAME_PATH.fullmatch(urlsplit(url).path) if url else None
    gid = m["id"] if m else None
    season = int(m["y"]) if m else None
    date = f'{m["y"]}-{m["md"][:2]}-{m["md"][2:]}' if m else None
    teams = []
    for tr in LexborHTMLParser(html).css("tr"):
        cells = _cells(tr)
        if len(cells) < 5:
            continue
        name = re.sub(r"\s", "", cells[0])
        tail = cells[-3:]
        if not all(INT.fullmatch(c) for c in tail):
            continue
        team = TEAM_BY_NAME.get(name)
        if team is None:
            if any(re.fullmatch(r"[0-9xX]{1,3}", c) for c in cells[1:-3]):   # 得点表の行の形なのに知らない名前
                out["unknown"].append({"key": f"{gid}:{name}", "raw": " | ".join(cells)})
            continue
        r, h, e = (int(c) for c in tail)
        teams.append(team)
        out["records"].append({"key": f"{gid}-{team}", "game_id": gid, "season": season, "date": date, "team": team,
                               "league": LEAGUE[team], "r": r, "h": h, "e": e,
                               "raw": " | ".join(cells), "source_url": url})
    if len(teams) not in (0, 2) or len(set(teams)) != len(teams):
        out["unknown"].append({"key": f"{gid}:rows", "raw": f"得点表の行が2つでない: {teams}"})
        out["records"] = []
    return out


def check(records: list[dict]) -> list[dict]:
    """年ごとに、1試合2行そろっているか。得点が日程の観測と一致するかは SakAnalytics で照合する。"""
    from collections import Counter

    out = []
    by_year: dict[int, Counter] = {}
    for r in records:
        by_year.setdefault(r["season"], Counter())[r["game_id"]] += 1
    for y in sorted(by_year):
        c = by_year[y]
        bad = [g for g, n in c.items() if n != 2]
        out.append({"group": str(y), "ok": not bad, "text": f"{y}: games={len(c)} rows_not_2={len(bad)} " + ("OK" if not bad else "要確認")})
    return out


def group(record: dict) -> str:
    return str(record["season"])
