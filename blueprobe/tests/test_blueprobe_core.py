"""取得元に依存しない部分: 正規化、報告の契約、オフライン再解析。"""

import pytest

import npb_calendar
from blueprobe import inspect, load_source, mask_digits, normalize, to_markdown

P = "/bis/2024/games/s2024040201097.html"


@pytest.mark.parametrize("text,expected", [
    ("", ""), (" ", ""), ("\n", ""), ("a\r\nb", "a b"), ("a b", "a b"), ("a　b", "a b"),
    ("４", "4"), ("\x00", "�"), ("日本語🙂", "日本語🙂"), ("ﾔ", "ヤ"),
])
def test_normalize_matrix(text, expected):
    assert normalize(text) == expected


def test_normalize_is_idempotent():
    for s in ["中 ４　-　3 巨", "\x00x", " a  b "]:
        assert normalize(normalize(s)) == normalize(s)


@pytest.mark.parametrize("name", ["", "../x", "Npb", "a-b", "a b"])
def test_load_source_rejects_odd_names(name):
    with pytest.raises(ValueError):
        load_source(name)


def test_mask_digits():
    assert mask_digits("中 4x - 3 巨 ４") == "中 #x - # 巨 #"


def test_inspect_groups_counts_and_unknown_shapes():
    pages = [
        ("2024_03", "u", "2024", ""),  # 存在しない月（空）
        ("2024_04", "u", "2024", f'<a href="{P}">中 4 - 3 巨</a><a href="/cs/">神 1 - 3 デ</a>'),
        ("2024_05", "u", "2024", f'<a href="{P.replace("1097", "1200")}">中 4x - 3 巨</a>'),
    ]
    rows = inspect(npb_calendar, pages)
    assert rows == [{"group": "2024", "pages": 2, "empty_pages": 1, "records": 1,
                     "n_non_regular": 1, "unknown": 1, "unknown_shapes": ["中 #x - # 巨"]}]
    md = to_markdown(rows, "t")
    assert "中 #x - # 巨" in md and "中 4x" not in md  # 生の得点は docs に残さない


def test_inspect_can_hand_back_records_and_markdown_shows_checks():
    recs = []
    inspect(npb_calendar, [("2024_04", "u", "2024", f'<a href="{P}">中 4 - 3 巨</a>')], recs)
    assert [r["key"] for r in recs] == ["2024040201097"]
    checks = npb_calendar.check(recs)
    assert checks == ["2024: teams=2 games/team=0-1 expected=143 要確認"]
    assert "取りこぼしの確認" in to_markdown([], "t", checks)
