"""チーム打撃成績のページ。表の形は実ページ（2012・2018・2024年）の見出しどおり、数値は架空。"""

import pytest

from npb_team_batting import check, pages, parse

URL = "https://npb.jp/bis/2024/stats/tmb_c.html"
HEAD = ["チーム", "打率", "試合", "打席", "打数", "得点", "安打", "二塁打", "三塁打", "本塁打", "塁打", "打点", "盗塁",
        "盗塁刺", "犠打", "犠飛", "四球", "故意四球", "死球", "三振", "併殺打", "長打率", "出塁率"]
ROW = ["中日", ".250", "143", "5300", "4800", "400", "1200", "200", "20", "60", "1620", "380", "40",
       "20", "100", "30", "350", "20", "40", "1000", "100", ".338", ".305"]


def page(*rows, head=HEAD):
    tr = lambda cells, tag="td": "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"  # noqa: E731
    return "<table>" + tr(head, "th") + "".join(tr(r) for r in rows) + "</table>"


def test_row_becomes_record_with_raw_kept():
    r = parse(page(ROW), URL)
    assert r["unknown"] == []
    rec = r["records"][0]
    assert (rec["key"], rec["season"], rec["team"], rec["league"]) == ("2024-d", 2024, "d", "C")
    assert (rec["g"], rec["pa"], rec["ab"], rec["r"], rec["hr"], rec["sf"], rec["hbp"], rec["ibb"]) == (143, 5300, 4800, 400, 60, 30, 40, 20)
    assert (rec["avg"], rec["slg"], rec["obp"]) == (0.25, 0.338, 0.305)
    assert rec["raw"] == " | ".join(ROW) and rec["source_url"] == URL


def test_header_spelling_variants_map_to_the_same_column():
    head = [("故意四" if h == "故意四球" else h) for h in HEAD]  # 2012・2018年の表記
    assert parse(page(ROW, head=head), URL)["records"][0]["ibb"] == 20


def test_unknown_header_is_recorded_and_rows_are_not_read_with_a_guessed_layout():
    head = [("新しい列" if h == "併殺打" else h) for h in HEAD]
    r = parse(page(ROW, head=head), URL)
    assert r["records"] == [] and r["unknown"][0]["raw"] == "新しい列"


@pytest.mark.parametrize("row,why", [
    (["横浜"] + ROW[1:], "知らないチーム名"),
    (["ソフトバンク"] + ROW[1:], "セのページにパの球団"),
    (ROW[:5] + ["4OO"] + ROW[6:], "数字でない値"),
])
def test_suspicious_rows_go_to_unknown(row, why):
    r = parse(page(row), URL)
    assert r["records"] == [] and len(r["unknown"]) == 1, why


def test_rows_with_other_cell_counts_are_not_team_rows():
    r = parse(page(ROW, ["合計", "1"]), URL)
    assert len(r["records"]) == 1 and r["unknown"] == []


def test_pages_and_check():
    assert pages([2024]) == [("2024_c", "https://npb.jp/bis/2024/stats/tmb_c.html", "2024"),
                             ("2024_p", "https://npb.jp/bis/2024/stats/tmb_p.html", "2024")]
    recs = parse(page(ROW), URL)["records"]
    assert [(c["group"], c["ok"]) for c in check(recs)] == [("2024", False)]


def test_headers_with_spaces_inside_words_are_read():
    # 実ページ 2012〜2024年の見出し（npb_team_batting の --strict で見つかった形）。「チ ー ム」も同じ扱い
    head = [h if len(h) < 2 else " ".join(h) for h in HEAD]
    r = parse(page(ROW, head=head), URL)
    assert r["unknown"] == [] and r["records"][0]["hr"] == 60


def test_spaces_are_removed_only_from_headers_not_from_team_names():
    # チーム名の空白は除かない。知らない表記として残す（見出しのように意味を推測しない）
    r = parse(page(["中 日"] + ROW[1:]), URL)
    assert r["records"] == [] and r["unknown"][0]["key"] == "2024:中 日"
