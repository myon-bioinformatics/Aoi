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


def test_unknown_team_row_is_recorded():
    r = parse(page(["横 浜", *"0 0 0".split(), "-", "1", "5", "0"], HOME), URL)
    assert r["records"] == [] and any("横浜" in u["key"] for u in r["unknown"])


def test_not_two_rows_is_not_read():
    r = parse(page(HOME), URL)
    assert r["records"] == [] and "2つでない" in r["unknown"][0]["raw"]


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
