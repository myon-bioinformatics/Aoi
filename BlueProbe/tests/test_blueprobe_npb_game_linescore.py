"""試合ごとの得点表。表の形は WebFetch で見た 2024年の1試合どおり（チーム名の空白、巨人 = 読売、最後の3つが R・H・E）。"""

import json

from npb_game_linescore import check, pages, parse

URL = "https://npb.jp/bis/2024/games/s2024040201097.html"


def page(*rows):
    return "<table>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table>"


AWAY = ["読 売", *"0 0 0 3 0 0 0 0 0 0 0".split(), "-", "3", "11", "0"]
HOME = ["中 日", *"0 0 0 0 0 1 2 0 0 0".split(), "1X", "-", "4", "9", "1"]


def test_two_rows_become_team_records():
    r = parse(page(["", *[str(i) for i in range(1, 12)], "", "R", "H", "E"], AWAY, HOME), URL)
    assert r["unknown"] == []
    by = {x["team"]: x for x in r["records"]}
    assert (by["g"]["r"], by["g"]["h"], by["g"]["e"]) == (3, 11, 0)
    assert (by["d"]["r"], by["d"]["h"], by["d"]["e"], by["d"]["game_id"], by["d"]["date"]) == (4, 9, 1, "2024040201097", "2024-04-02")
    assert by["d"]["key"] == "2024040201097-d"


def test_player_rows_are_not_read_or_recorded():
    """選手の行（投手の成績など）は読まず、unknown にも counts にも入れない（個人の記録は扱わない）。"""
    pitcher = ["", "ウィック", "1", "", "2", "0", "1", "0", "0", "0"]
    r = parse(page(AWAY, HOME, pitcher), URL)
    assert len(r["records"]) == 2 and r["unknown"] == [] and not r["counts"]


def test_unreadable_page_leaves_shape_hints_only():
    r = parse(page(HOME), URL)
    assert r["records"] == [] and r["counts"]["no_linescore_page"] == 1 and r["counts"]["team_rows_1"] == 1
    assert r["counts"]["team_cell_0_len_16"] == 1
    r = parse(page(["", "中 日", "0", "0"]), URL)
    assert r["counts"]["team_cell_1_len_4"] == 1 and r["records"] == []
    assert parse(page(["x", "1"]), URL)["counts"]["no_team_row"] == 1


def test_pages_from_calendar_observations(tmp_path):
    f = tmp_path / "games.jsonl"
    f.write_text("".join(json.dumps(g) + "\n" for g in [
        {"key": "2024040201097", "href": "https://npb.jp/bis/2024/games/s2024040201097.html"},
        {"key": "2023040201097", "href": "https://npb.jp/bis/2023/games/s2023040201097.html"}]), encoding="utf-8")
    assert pages([2024], games=f) == [("2024040201097", "https://npb.jp/bis/2024/games/s2024040201097.html", "2024")]
    assert pages([2024], games=tmp_path / "none.jsonl") == []


def test_check_counts_rows_per_game():
    recs = parse(page(AWAY, HOME), URL)["records"]
    assert [c["ok"] for c in check(recs)] == [True]
    assert [c["ok"] for c in check(recs[:1])] == [False]


def test_unknown_team_name_in_a_line_score_shaped_row_is_reported():
    """得点表の形の行の先頭が知らない名前なら、チーム名の候補として unknown に残す（選手の行は残さない）。"""
    other = ["横浜大洋", *"0 0 1 0 0 0 0 0 0".split(), "-", "1", "6", "0"]   # 架空（今の12球団にない表記）
    r = parse(page(other, HOME), URL)
    assert r["records"] == [] and [u["raw"] for u in r["unknown"]] == ["得点表の形の行の知らない名前: 横浜大洋"]
    # 実ページの選手の行は先頭のセルが空（1回目の preview で見た形 「 | E.ラミレス | # | …」）か、「+」「.###」を含む
    for pitcher in (["", "ウィック", "1", "", "2", "0", "1", "0", "0", "0", "3", "1", "2", "0"],
                    ["ウィック", "", "+", "2", "0", "1", "0", "0", "0", "3", "1", "2", "0"]):
        assert parse(page(pitcher, HOME), URL)["unknown"] == []


def test_full_club_names_seen_on_real_pages():
    names = {"北海道日本ハム": "f", "千葉ロッテ": "m", "埼玉西武": "l", "広島東洋": "c", "東京ヤクルト": "s",
             "東北楽天": "e", "横浜DeNA": "db", "福岡ソフトバンク": "h"}
    for name, code in names.items():
        row = [name, *"0 0 0 0 0 0 0 0 0".split(), "-", "0", "3", "1"]
        teams = {x["team"] for x in parse(page(row, HOME), URL)["records"]}
        assert teams == {code, "d"}, name
