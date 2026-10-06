"""取得元: npb.jp の今季の月別「日程・結果」（詳細）。進行中のシーズン用（2026年〜）。

URL   : https://npb.jp/games/{year}/schedule_{MM}_detail.html
過去の年の「公式戦カレンダー」（/bis/{year}/calendar/、npb_calendar）は、今季はまだ作られていない（2026年は 404）。
1ページ = 1か月・12球団すべての試合。

試合は
  巨人 <a href="https://npb.jp/scores/2026/0901/g-db-20/">4 - 3</a> DeNA
の形で載る（2026-10-06 に WebFetch で確かめた）。リンク先の
/scores/{年}/{月日}/{ホーム}-{ビジター}-{番号}/ の先のコードがホームで、文字列の先のチームと一致する。
スコアは「ホーム - ビジター」。チームは URL のコードから読み、文字列の球団名は読まない。

記録の形は npb_calendar と同じ（SakAnalytics が同じように読める）:
  observed : raw_text（リンク文字列そのもの）, href, source_url
  derived  : date, home/away, hs/as, normalized
key は「年月日-ホーム-ビジター-番号」。

採用しなかったものの区分（counts）:
  scheduled      : 試合のリンクだが、まだ結果がない（スコアの形でない、「試合前」など）
  cancelled      : 中止・ノーゲーム
  non_regular    : スコアの形だが、試合のリンクではない
  unknown        : 知らないチームコード（オールスターなど）、または読めない文字列 → 原文を残す

注意:
- CS・日本シリーズも同じ /scores/ のリンクで、同じリーグのコードで載るかもしれない。日付やコードでは分けられないので、
  check() は1球団の試合数が公式戦の数（143）を超えたら止める。進行中のシーズンだけに使い、公式戦が終わった後のページは
  R18（全球団が 143試合を終えてから本体に取り込む）のときに人が確かめる
- 進行中のシーズンのページは、QueRyu が更新を確認する（If-Modified-Since）。中身の変わったページは台帳の changed に出る
"""

from __future__ import annotations

import re
from collections import Counter
from urllib.parse import urljoin, urlsplit

from blueprobe import new_report, normalize
from selectolax.lexbor import LexborHTMLParser

NAME = "npb_schedule_current"
URL = "https://npb.jp/games/{year}/schedule_{month:02d}_detail.html"
MONTHS = range(3, 12)

CODES = {"g", "s", "db", "d", "t", "c", "h", "f", "b", "e", "l", "m"}
EXPECTED_MAX = 143   # 1球団の公式戦の数。これを超えたら公式戦以外が混ざっている

_DASH = "[-‐‑‒–—−]"
GAME_PATH = re.compile(r"/scores/(?P<y>\d{4})/(?P<md>\d{4})/(?P<home>[a-z]+)-(?P<away>[a-z]+)-(?P<n>\d+)/?")
SCORE = re.compile(rf"(?P<hs>[0-9]{{1,2}}) ?{_DASH} ?(?P<as>[0-9]{{1,2}})")
CANCELLED = re.compile(r".*(中止|ノーゲーム).*")


def pages(years) -> list[tuple[str, str, str]]:
    """取得すべきページ (key, url, group)。group は年。"""
    return [(f"{y}_{m:02d}", URL.format(year=y, month=m), str(y)) for y in years for m in MONTHS]


def parse(html: str, url: str = "") -> dict:
    """1ページを読み、結果の出た試合と、採用しなかったものの件数・原文を返す。"""
    out = new_report()
    seen = set()
    for a in LexborHTMLParser(html).css("a"):
        href = a.attributes.get("href") or ""
        raw = a.text(deep=True)
        t = normalize(raw)
        path = GAME_PATH.fullmatch(urlsplit(href).path) if href else None
        if path is None:
            if SCORE.fullmatch(t):
                out["counts"]["non_regular"] += 1
            continue
        key = f'{path["y"]}{path["md"]}-{path["home"]}-{path["away"]}-{path["n"]}'
        if key in seen:
            continue
        seen.add(key)
        if path["home"] not in CODES or path["away"] not in CODES:
            out["unknown"].append({"key": key, "raw": f"[{path['home']}-{path['away']}] {raw}"})
            continue
        if m := SCORE.fullmatch(t):
            md = path["md"]
            out["records"].append({
                "key": key,
                "date": f'{path["y"]}-{md[:2]}-{md[2:]}',
                "home": path["home"], "away": path["away"], "hs": int(m["hs"]), "as": int(m["as"]),
                "raw_text": raw,
                "normalized": t != raw,
                "href": urljoin(url, href) if url else href,
                "source_url": url,
            })
        elif CANCELLED.fullmatch(t):
            out["counts"]["cancelled"] += 1
        elif not re.search(r"[0-9]", t):
            out["counts"]["scheduled"] += 1
        else:
            out["unknown"].append({"key": key, "raw": raw})
    return out


def check(records: list[dict]) -> list[dict]:
    """年ごとに、1球団の試合数の範囲を書く。143 を超える球団があれば ok=False（公式戦以外の混入）。

    進行中のシーズンなので、143 に届かないのは正常。同じ日に同じ球団の試合が2つあっても ok=False。
    """
    n, day = Counter(), Counter()
    for r in records:
        y = int(r["date"][:4])
        for t in (r["home"], r["away"]):
            n[(y, t)] += 1
            day[(r["date"], t)] += 1
    out = []
    for y in sorted({y for y, _ in n}):
        got = {t: n[(y, t)] for t in sorted(CODES)}
        double = sorted(f"{d}:{t}" for (d, t), k in day.items() if k > 1 and d.startswith(str(y)))
        ok = max(got.values()) <= EXPECTED_MAX and not double
        text = (f"{y}: teams={sum(g > 0 for g in got.values())} games/team={min(got.values())}-{max(got.values())} "
                f"max={EXPECTED_MAX} finished={sum(g == EXPECTED_MAX for g in got.values())} "
                + (f"same-day={','.join(double)} " if double else "")
                + ("OK（進行中）" if ok else "要確認"))
        out.append({"group": str(y), "ok": ok, "text": text})
    return out


def group(record: dict) -> str:
    return record["date"][:4]
