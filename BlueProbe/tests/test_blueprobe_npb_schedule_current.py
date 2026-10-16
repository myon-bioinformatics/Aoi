"""今季の日程・結果のページ。形は WebFetch で確かめたリンク（/scores/2026/0901/g-db-20/、文字列 "4 - 3"）どおり、数値は架空。"""

from npb_schedule_current import check, pages, parse

URL = "https://npb.jp/games/2026/schedule_09_detail.html"
H = "https://npb.jp/scores/2026/0901/g-db-20/"


def row(href=H, text="4 - 3", home="巨人", away="DeNA"):
    return f"<tr><td>{home} <a href=\"{href}\">{text}</a> {away}</td></tr>"


def test_record_reads_teams_from_the_link_and_keeps_raw_text():
    rec = parse(row(), URL)["records"][0]
    assert rec == {"key": "20260901-g-db-20", "date": "2026-09-01", "home": "g", "away": "db", "hs": 4, "as": 3,
                   "raw_text": "4 - 3", "normalized": False, "href": H, "source_url": URL}


def test_relative_link_and_full_width_digits():
    r = parse(row(href="/scores/2026/0901/d-c-20/", text="１０ － ２"), URL)
    rec = r["records"][0]
    assert (rec["home"], rec["away"], rec["hs"], rec["as"], rec["normalized"]) == ("d", "c", 10, 2, True)
    assert rec["href"] == "https://npb.jp/scores/2026/0901/d-c-20/"


def test_not_yet_played_cancelled_and_unknown_are_counted_not_taken():
    html = (row(text="試合前") + row(href="https://npb.jp/scores/2026/0902/s-t-20/", text="中止")
            + row(href="https://npb.jp/scores/2026/0725/cl-pl-1/", text="5 - 4")
            + row(href="https://npb.jp/scores/2026/0903/d-c-22/", text="4回 2 - 1"))
    r = parse(html, URL)
    assert r["records"] == []
    assert (r["counts"]["scheduled:09"], r["counts"]["cancelled"]) == (1, 1)
    assert [u["key"] for u in r["unknown"]] == ["20260903-d-c-22"]
    assert r["counts"]["non_regular:オールスター"] == 1


def test_observed_spellings_in_preview_2026():
    """preview_2026 で実ページに見た表記: 結果前の「- （球場）18:00」（空白・改行つき）、オールスターの cl-pl・pl-cl。"""
    html = (row(href="https://npb.jp/scores/2026/1006/m-l-25/", text="\n  \n   -\n   （ZOZOマリン）18:00\n  ")
            + row(href="https://npb.jp/scores/2026/0724/pl-cl-2/", text="\n  3\n  -\n  2\n "))
    r = parse(html, URL)
    assert r["records"] == [] and r["unknown"] == []
    assert (r["counts"]["scheduled:10"], r["counts"]["non_regular:オールスター"]) == (1, 1)


def test_pair_over_the_regular_count_is_flagged():
    base = {"home": "g", "away": "t", "hs": 1, "as": 0}
    same = [{**base, "date": f"2026-{4 + i // 20:02d}-{1 + i % 20:02d}"} for i in range(26)]
    assert [c["ok"] for c in check(same)] == [False] and "pairs-over=g-t:26" in check(same)[0]["text"]
    inter = [{**base, "away": "h", "date": f"2026-06-{1 + i:02d}"} for i in range(4)]
    assert [c["ok"] for c in check(inter)] == [False]


def test_same_game_linked_twice_is_one_record_and_other_score_links_are_non_regular():
    r = parse(row() + row() + '<a href="/news/1">4 - 3</a>', URL)
    assert len(r["records"]) == 1 and r["counts"]["non_regular"] == 1


def test_pages_and_check():
    assert pages([2026])[0] == ("2026_03", "https://npb.jp/games/2026/schedule_03_detail.html", "2026")
    recs = parse(row(), URL)["records"]
    assert [c["ok"] for c in check(recs)] == [True]          # 進行中なので 143 に届かなくてよい
    over = [{**recs[0], "date": f"2026-{4 + i // 28:02d}-{1 + i % 28:02d}"} for i in range(144)]
    assert [c["ok"] for c in check(over)] == [False]          # 143 を超えたら公式戦以外の混入
    assert [c["ok"] for c in check(recs + recs)] == [False]   # 同じ日に同じ球団が2試合
