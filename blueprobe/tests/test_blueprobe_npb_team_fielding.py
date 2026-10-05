"""チーム守備成績のページ。表の形は WebFetch で確かめた見出しどおり（併殺が2列にまたがる）、数値は架空。"""

from npb_team_fielding import check, pages, parse

URL = "https://npb.jp/bis/2018/stats/tmf_c.html"
HEAD = ["チーム", "守 備 率", "試 合", "守備機会", "刺 殺", "補 殺", "失 策", ("併殺", 2), "捕 逸"]
SUB = ["参加", "球団"]
ROW = ["中 日", ".991", "143", "5488", "3788", "1648", "52", "328", "122", "10"]


def page(*rows, head=HEAD, sub=SUB):
    th = "".join(f'<th colspan="{h[1]}">{h[0]}</th>' if isinstance(h, tuple) else f"<th>{h}</th>" for h in head)
    out = "<table><tr>" + th + "</tr>"
    if sub is not None:
        out += "<tr>" + "".join(f"<th>{c}</th>" for c in sub) + "</tr>"
    return out + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table>"


def test_spanned_header_is_read_with_the_row_below():
    r = parse(page(ROW), URL)
    assert r["unknown"] == []
    rec = r["records"][0]
    assert (rec["key"], rec["team"], rec["league"]) == ("2018-d", "d", "C")
    assert (rec["fpct"], rec["g"], rec["tc"], rec["po"], rec["a"], rec["e"], rec["dp_part"], rec["dp"], rec["pb"]) == \
        (0.991, 143, 5488, 3788, 1648, 52, 328, 122, 10)


def test_missing_row_below_the_spanned_header_is_recorded_not_guessed():
    r = parse(page(ROW, sub=None), URL)
    assert r["records"] == [] and "読めない" in r["unknown"][0]["raw"]


def test_unknown_sub_header_is_recorded():
    r = parse(page(ROW, sub=["参加", "新しい"]), URL)
    assert r["records"] == [] and "併殺新しい" in r["unknown"][0]["raw"]


def test_pages_and_check():
    assert pages([2025])[0] == ("2025_c", "https://npb.jp/bis/2025/stats/tmf_c.html", "2025")
    assert [c["ok"] for c in check(parse(page(ROW), URL)["records"])] == [False]


def test_observed_spelling_variants():
    """preview_fielding で見た実ページの表記: 2012〜2024年の「守機備会」、2025年の別々のセル「併殺・参加」「併殺・球団」。"""
    head = [("守　機\n備　会" if h == "守備機会" else h) for h in HEAD]
    assert parse(page(ROW, head=head), URL)["records"][0]["tc"] == 5488
    head25 = ["チーム", "守備率", "試合", "守備機会", "刺殺", "補殺", "失策", "併殺・参加", "併殺・球団", "捕逸"]
    rec = parse(page(["中日"] + ROW[1:], head=head25, sub=None), "https://npb.jp/bis/2025/stats/tmf_c.html")["records"][0]
    assert (rec["dp_part"], rec["dp"], rec["e"]) == (328, 122, 52)
