"""取得元: npb.jp の月別「公式戦カレンダー」。

URL   : https://npb.jp/bis/{year}/calendar/index_{MM}.html （2012〜2025年は同じ形式）
1ページ = 1か月・12球団すべての公式戦。

公式戦の試合は
  <a href="/bis/2024/games/s2024040201097.html">中 4 - 3 巨</a>
の形で載る。先に書かれたチームがホーム、スコアは「ホーム - ビジター」。

記録には原文と派生値を並べる（観測と解釈を分ける）:
  observed : raw_text（リンク文字列そのもの）, href, source_url
  derived  : date（URL の試合IDから）, home/away（略字から）, hs/as（得点）, normalized（正規化で文字列が変わったか）
勝敗・点差はここでは計算しない（SakAnalytics の仕事）。

公式戦以外の試合（CS・日本シリーズ・オールスターなど）も同じ /bis/{year}/games/ のリンクで、
同じ日に公式戦と並ぶことがある（例: 2013-10-12）。日付やパスでは分けられない。
ページでは日ごとの枠（class="stvsteam"）の中で、大会の見出し（class="tescheaten"）が後ろの試合の前に置かれる。
見出しのついた試合は採用しない。知らない見出しは unknown に入れる（黙って捨てない・黙って採用しない）。

採用しなかったものの区分（counts）:
  cancelled           : 試合リンクだが中止表記（* - *、中止、ノーゲーム）
  non_regular         : スコア形式だが試合リンクではない
  non_regular:<見出し> : 公式戦以外の大会の見出しがついた試合リンク（見出しごとに数える）
  unknown             : 試合リンクなのにどれにも当たらない、または知らない見出し → 表記の変化を疑う。原文を残す
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit

from selectolax.lexbor import LexborHTMLParser

from blueprobe import new_report, normalize

NAME = "npb_calendar"
URL = "https://npb.jp/bis/{year}/calendar/index_{month:02d}.html"
MONTHS = range(3, 12)

ABBR = {
    "巨": "g", "ヤ": "s", "デ": "db", "中": "d", "神": "t", "広": "c",
    "ソ": "h", "日": "f", "オ": "b", "楽": "e", "西": "l", "ロ": "m",
}
TEAM_NAME = {
    "g": "巨人", "s": "ヤクルト", "db": "DeNA", "d": "中日", "t": "阪神", "c": "広島",
    "h": "ソフトバンク", "f": "日本ハム", "b": "オリックス", "e": "楽天", "l": "西武", "m": "ロッテ",
}
LEAGUE = {t: ("C" if t in {"g", "s", "db", "d", "t", "c"} else "P") for t in TEAM_NAME}

# 1球団あたりの公式戦試合数の既知値。取りこぼしの判定に使い、npb.jp には問い合わせない
EXPECTED_GAMES = {2012: 144, 2013: 144, 2014: 144, 2020: 120}
EXPECTED_DEFAULT = 143

# 正規表現は狭く、全体一致で書く。略字は12文字、得点は半角0〜99
_TEAM = "[" + "".join(ABBR) + "]"
_DASH = "[-‐‑‒–—−]"
GAME_PATH = re.compile(r"/bis/(?P<y>\d{4})/games/s(?P<id>(?P=y)(?P<md>\d{4})\d+)\.html")
SCORE = re.compile(rf"(?P<home>{_TEAM}) ?(?P<hs>[0-9]{{1,2}}) ?{_DASH} ?(?P<as>[0-9]{{1,2}}) ?(?P<away>{_TEAM})")
CANCELLED = re.compile(rf"{_TEAM} ?\* ?{_DASH} ?\* ?{_TEAM}|.*(中止|ノーゲーム).*")

# 公式戦以外の大会の見出し（正規化後）。2013〜2025年の全ページで見つかったもの。2020年のセは CS なし、パは1ステージ
NON_REGULAR_LABELS = frozenset({
    "CS ファーストS", "CS ファイナルS", "クライマックスS", "日本シリーズ", "オールスター", "アジアシリーズ",
})
DAY_BLOCK, LABEL = "stvsteam", "tescheaten"


def _has_class(node, name: str) -> bool:
    return name in (node.attributes.get("class") or "").split()


def competition_label(a) -> str | None:
    """試合リンクの前に置かれた大会の見出し（正規化後）。日ごとの枠の外、または見出しがなければ None。"""
    node = a
    while node.parent is not None and not _has_class(node.parent, DAY_BLOCK):
        node = node.parent
    if node.parent is None:
        return None
    prev = node.prev
    while prev is not None:
        if _has_class(prev, LABEL):
            return normalize(prev.text(deep=True))
        prev = prev.prev
    return None


def pages(years) -> list[tuple[str, str, str]]:
    """取得すべきページ (key, url, group)。group は年。"""
    return [(f"{y}_{m:02d}", URL.format(year=y, month=m), str(y)) for y in years for m in MONTHS]


def read_score(text: str) -> tuple[str, dict | None]:
    """リンク文字列1つを分類する: ("game", {...}) / ("cancelled", None) / ("unknown", None)。"""
    t = normalize(text)
    if m := SCORE.fullmatch(t):
        return "game", {"home": ABBR[m["home"]], "away": ABBR[m["away"]],
                        "hs": int(m["hs"]), "as": int(m["as"])}
    if CANCELLED.fullmatch(t):
        return "cancelled", None
    return "unknown", None


def parse(html: str, url: str = "") -> dict:
    """1ページを読み、採用した試合と、採用しなかったものの件数・原文を返す。"""
    out = new_report()
    seen = set()
    for a in LexborHTMLParser(html).css("a"):
        href = a.attributes.get("href") or ""
        path = GAME_PATH.fullmatch(urlsplit(href).path) if href else None
        raw = a.text(deep=True)
        kind, score = read_score(raw)
        if path is None:
            if kind == "game":
                out["counts"]["non_regular"] += 1
            continue
        if path["id"] in seen:
            continue
        seen.add(path["id"])
        if (label := competition_label(a)) is not None:
            if label in NON_REGULAR_LABELS:
                out["counts"][f"non_regular:{label}"] += 1
            else:
                out["unknown"].append({"key": path["id"], "raw": f"[{label}] {raw}"})
            continue
        if kind == "game":
            md = path["md"]
            out["records"].append({
                "key": path["id"],
                "date": f'{path["y"]}-{md[:2]}-{md[2:]}',
                **score,
                "raw_text": raw,
                "normalized": normalize(raw) != raw,
                "href": urljoin(url, href) if url else href,
                "source_url": url,
            })
        elif kind == "cancelled":
            out["counts"]["cancelled"] += 1
        else:
            out["unknown"].append({"key": path["id"], "raw": raw})
    return out


def check(records: list[dict]) -> list[dict]:
    """年×球団の試合数を既知値と比べる。中止は振替で消化されるので、取りこぼしも混入もなければ一致する。

    返り値は年ごとに {"group", "ok", "text"}。判定は ok で行い、text は表示のためだけに使う。
    """
    from collections import Counter

    n = Counter()
    for r in records:
        y = int(r["date"][:4])
        n[(y, r["home"])] += 1
        n[(y, r["away"])] += 1
    out = []
    for y in sorted({y for y, _ in n}):
        got = [n[(y, t)] for t in TEAM_NAME]
        exp = EXPECTED_GAMES.get(y, EXPECTED_DEFAULT)
        ok = all(g == exp for g in got)
        text = (f"{y}: teams={sum(g > 0 for g in got)} games/team={min(got)}-{max(got)} expected={exp} "
                + ("OK" if ok else "要確認"))
        out.append({"group": str(y), "ok": ok, "text": text})
    return out


def group(record: dict) -> str:
    """記録がどの group（年）のページから来たか。データセットを年単位で作り直すときに使う。"""
    return record["date"][:4]
