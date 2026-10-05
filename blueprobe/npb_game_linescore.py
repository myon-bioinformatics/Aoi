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
TEAM_BY_NAME = {v: k for k, v in TEAM_NAME.items()} | {
    "読売": "g",
    # 得点表で観測した正式名称（2025年、preview_linescore の2回目、2026-10-05）
    "北海道日本ハム": "f", "千葉ロッテ": "m", "埼玉西武": "l", "広島東洋": "c", "東京ヤクルト": "s",
}
INT = re.compile(r"[0-9]{1,3}")
LINE_CELL = re.compile(r"[0-9]{0,2}[xX]?|-")   # 回の得点の列（「1X」「X」「-」、空も）


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
    """得点表の2行を読む。選手の行（投手・打者の成績）は読まない・数えない・unknown にも入れない（個人の記録は扱わない方針）。

    得点表が読めないページは、形の手がかりだけを counts に残す（中身は残さない）:
      no_team_row            : チーム名のセルを持つ行がない
      team_rows_<n>          : チーム名のセルを持つ行が n 個（2 でない）
      team_cell_<i>_len_<k>  : 読めなかったページで、チーム名が行の i 番目のセルにあり、行のセルが k 個
      tail_not_rhe           : チーム名の行はあるが、最後の3つが整数でない
    """
    out = new_report()
    m = GAME_PATH.fullmatch(urlsplit(url).path) if url else None
    gid = m["id"] if m else None
    season = int(m["y"]) if m else None
    date = f'{m["y"]}-{m["md"][:2]}-{m["md"][2:]}' if m else None
    found = []                               # (チーム, セル)
    shapes = []                              # 読めなかったときの手がかり（チーム名の位置, セルの数）
    unknown_names = []                       # 得点表の形の行の、知らない先頭の名前（チーム名の候補）
    for tr in LexborHTMLParser(html).css("tr"):
        cells = _cells(tr)
        names = [re.sub(r"\s", "", c) for c in cells]
        hit = [i for i, n in enumerate(names) if n in TEAM_BY_NAME]
        if not hit:
            # 得点表の形: 先頭が数字を含まない名前、回の得点の列（数字・X・-・空）が9つ以上、最後の3つが整数
            if (names and names[0] and not re.search(r"[0-9]", names[0]) and len(cells) >= 13
                    and all(INT.fullmatch(c) for c in cells[-3:])
                    and all(LINE_CELL.fullmatch(c) for c in cells[1:-3])):
                unknown_names.append(names[0])
            continue
        shapes.append((hit[0], len(cells)))
        if hit[0] != 0 or len(cells) < 5:
            continue
        found.append((TEAM_BY_NAME[names[0]], cells))
    rows = [(t, c) for t, c in found if all(INT.fullmatch(x) for x in c[-3:])]
    if len(rows) == 2 and rows[0][0] != rows[1][0]:
        for team, cells in rows:
            r, h, e = (int(c) for c in cells[-3:])
            out["records"].append({"key": f"{gid}-{team}", "game_id": gid, "season": season, "date": date, "team": team,
                                   "league": LEAGUE[team], "r": r, "h": h, "e": e,
                                   "raw": " | ".join(cells), "source_url": url})
        return out
    out["counts"]["no_linescore_page"] += 1
    for n in unknown_names:   # チームの名前（個人ではない）。知らない表記として残し、確かめてから足す
        out["unknown"].append({"key": f"{gid}:{n}", "raw": f"得点表の形の行の知らない名前: {n}"})
    if not shapes:
        out["counts"]["no_team_row"] += 1
    elif found and not rows:
        out["counts"]["tail_not_rhe"] += 1
    else:
        out["counts"][f"team_rows_{len(rows)}"] += 1
    for i, k in shapes:
        out["counts"][f"team_cell_{i}_len_{k}"] += 1
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
