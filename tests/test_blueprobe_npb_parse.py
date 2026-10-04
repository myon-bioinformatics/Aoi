"""HTML（DOM）側の揺れと、記録の契約（原文と派生値の併記）。

アサーションは部分一致ではなく、返ってきたレコードそのものを比べる。
"""

from pathlib import Path

import pytest

from blueprobe import merge, new_report
from npb_calendar import parse

P = "/bis/2024/games/s2024040201097.html"
CORE = ("key", "date", "home", "away", "hs", "as")
GAME = {"key": "2024040201097", "date": "2024-04-02", "home": "d", "away": "g", "hs": 4, "as": 3}
FIX = Path(__file__).parent / "fixtures" / "npb_calendar_sample.html"


def one(html, url=""):
    r = parse(html, url)
    return ([{k: g[k] for k in CORE} for g in r["records"]],
            r["counts"]["cancelled"], r["counts"]["non_regular"], r["unknown"])


def test_record_keeps_raw_and_derived_side_by_side():
    url = "https://npb.jp/bis/2024/calendar/index_04.html"
    raw = "中 4 - 3 巨"
    rec = parse(f'<a href="{P}">{raw}</a>', url)["records"][0]
    assert rec == {**GAME, "raw_text": raw, "normalized": True,
                   "href": "https://npb.jp" + P, "source_url": url}


def test_unnormalized_text_is_marked_false():
    assert parse(f'<a href="{P}">中 4 - 3 巨</a>')["records"][0]["normalized"] is False


@pytest.mark.parametrize("href", [
    P, f"https://npb.jp{P}", f"http://npb.jp{P}", f"//npb.jp{P}", f"{P}?from=calendar", f"{P}#top",
])
def test_href_forms(href):
    assert one(f'<a href="{href}">中 4 - 3 巨</a>') == ([GAME], 0, 0, [])


@pytest.mark.parametrize("html", [
    f"<a href='{P}'>中 4 - 3 巨</a>",
    f'<A HREF="{P}">中 4 - 3 巨</A>',
    f'<a class="x" title="t" href="{P}" target="_blank">中 4 - 3 巨</a>',
    f'<a href="{P}"><span>中</span> <b>4</b> - <b>3</b> <span>巨</span></a>',
    f'<a href="{P}">中 4<br>-<br>3 巨</a>',
    f'<a href="{P}">中&nbsp;4&nbsp;&#8722;&nbsp;3&nbsp;巨</a>',
    f'<a href="{P}">\n    中 4 - 3 巨\n  </a>',
    f'<table><tr><td><a href="{P}">中 4 - 3 巨<td>次のセル',
    f'<a href="{P}">中 4 - 3 巨</a><a href="{P}">中 4 - 3 巨</a>',
])
def test_markup_variants(html):
    assert one(html) == ([GAME], 0, 0, [])


def test_cancelled_is_counted_not_dropped():
    assert one(f'<a href="{P}">デ * - * 中</a>') == ([], 1, 0, [])


def test_unknown_keeps_original_text():
    assert one(f'<a href="{P}">中 4x - 3 巨</a>') == ([], 0, 0, [{"key": "2024040201097", "raw": "中 4x - 3 巨"}])


@pytest.mark.parametrize("html", [
    '<a href="/cs/2024/">神 1 - 3 デ</a>',
    '<a href="/nippons/2024/">デ 3 - 5 ソ</a>',
    '<a>中 4 - 3 巨</a>',
    '<a href="/bis/2023/games/s2024040201097.html">中 4 - 3 巨</a>',
    '<a href="/bis/2024/games/gm20240402.html">中 4 - 3 巨</a>',
])
def test_score_outside_regular_game_links(html):
    assert one(html) == ([], 0, 1, [])


@pytest.mark.parametrize("html", [
    "", "\x00", "<html><body>試合はありません</body></html>",
    '<a href="/bis/2024/games/gm20240402.html">2</a>', "<<<>>><a href=",
])
def test_no_games_without_error(html):
    assert one(html) == ([], 0, 0, [])


def test_fixture_page():
    games, cancelled, non_regular, unknown = one(FIX.read_text(encoding="utf-8"))
    assert [g["key"] for g in games] == ["2024040201097", "2024040201470", "2024040501108", "2024041201120"]
    assert games[2] == {"key": "2024040501108", "date": "2024-04-05", "home": "c", "away": "d", "hs": 0, "as": 1}
    assert (cancelled, non_regular, unknown) == (1, 1, [])


def test_merge_dedupes_across_pages():
    a = parse(f'<a href="{P}">中 4 - 3 巨</a>')
    b = parse(f'<a href="{P}">中 4 - 3 巨</a><a href="{P.replace("1097", "1098")}">デ * - * 中</a>')
    total = merge(merge(new_report(), a), b)
    assert [r["key"] for r in total["records"]] == ["2024040201097"]
    assert dict(total["counts"]) == {"cancelled": 1}


# ---------- 公式戦以外の大会（見出しで分ける） ----------
# 実ページの形（PR #3 の実データ観測）を、架空のスコアで再現する。日付だけでは分けられない例: 2013-10-12

def day(*children):
    return '<div class="stvsteam">' + "".join(children) + "</div>"


def game(gid, text):
    return f'<div><a href="/bis/{gid[:4]}/games/s{gid}.html">{text}</a></div>'


def label(text):
    return f'<div class="tescheaten">{text}</div>'


def test_same_day_postseason_is_excluded_by_label_and_counted_per_label():
    html = (day(label("CS ファーストS"), game("2013101200001", "神 2 - 1 広"))
            + day(game("2013101200002", "楽 3 - 2 オ")))
    r = parse(html)
    assert [(g["key"], g["home"], g["away"]) for g in r["records"]] == [("2013101200002", "e", "b")]
    assert dict(r["counts"]) == {"non_regular:CS ファーストS": 1}
    assert r["unknown"] == []


def test_label_applies_to_every_following_game_in_the_day_block_only():
    html = day(game("2013101200003", "ロ 1 - 0 西"), label("日本シリーズ"),
               game("2013101200004", "楽 2 - 0 巨"), game("2013101200005", "巨 4 - 2 楽"))
    r = parse(html)
    assert [g["key"] for g in r["records"]] == ["2013101200003"]
    assert r["counts"]["non_regular:日本シリーズ"] == 2


def test_allstar_teams_are_not_unknown_when_labelled():
    r = parse(day(label("オールスター"), game("2013071900001", "パ 2 - 2 セ")))
    assert (r["records"], r["unknown"]) == ([], [])
    assert r["counts"]["non_regular:オールスター"] == 1


def test_label_is_normalized_before_matching():
    r = parse(day(label(" ＣＳ　ファイナルＳ "), game("2013101700001", "巨 3 - 0 広")))
    assert r["records"] == [] and r["counts"]["non_regular:CS ファイナルS"] == 1


def test_unknown_label_is_recorded_not_adopted_and_not_dropped():
    r = parse(day(label("未知の大会"), game("2013101200001", "神 2 - 1 広")))
    assert r["records"] == []
    assert r["unknown"] == [{"key": "2013101200001", "raw": "[未知の大会] 神 2 - 1 広"}]


def test_label_found_through_nested_markup():
    html = day(label("<span>CS ファイナルS</span>"),
               '<div><p><span><a href="/bis/2013/games/s2013101700002.html">巨 1 - 0 広</a></span></p></div>')
    r = parse(html)
    assert r["records"] == [] and r["counts"]["non_regular:CS ファイナルS"] == 1


@pytest.mark.parametrize("name", sorted(__import__("npb_calendar").NON_REGULAR_LABELS))
def test_every_known_label_excludes(name):
    r = parse(day(label(name), game("2020111400001", "ソ 2 - 1 ロ")))
    assert r["records"] == [] and r["unknown"] == [] and r["counts"][f"non_regular:{name}"] == 1
