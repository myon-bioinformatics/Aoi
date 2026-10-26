"""cycles/c001-chunichi/exploratory/r18_partial_confirmation.py の確認。

SYNTHETIC: 合成の「単位ごとの状態」（実データではない）で、R18 に登録された読み方（P52 の逆の判例 2 件以上・判例 3 件以上、P79 の半分）、
期待値、学習データ側の対照が違えば止まること、を確かめる。最後の 1 件だけ、リポジトリに保存済みの実データ
（確定済み season.jsonl と、2026年の行）から、保存済みの結果が 1 バイトも違わず再現できることを確かめる。結論には使わない。
"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
C001 = ROOT / "cycles" / "c001-chunichi"
spec = importlib.util.spec_from_file_location("r18_partial_confirmation", C001 / "exploratory" / "r18_partial_confirmation.py")
r18 = importlib.util.module_from_spec(spec)
sys.modules["r18_partial_confirmation"] = r18
spec.loader.exec_module(r18)

NAMES = {"d": "中日", "g": "巨人", "s": "ヤクルト"}


def check(pid, **statuses):
    """check("P52", 成立=["d-2026"], 判例=["g-2026"])"""
    return {"id": pid, "units": [{"unit": u, "status": s} for s, us in statuses.items() for u in us]}


def n(**kw):
    return Counter(kw)


def test_counts_group_units_by_status():
    c = r18.counts(check("P52", 成立=["d-2026", "s-2026"], 判例=["g-2026"]))
    assert c["成立"] == 2 and c["判例"] == 1 and c["逆の判例"] == 0


@pytest.mark.parametrize("kw, expected", [
    (dict(逆の判例=0, 判例=0), "学習データと矛盾しない"),
    (dict(逆の判例=1, 判例=2), "学習データと矛盾しない"),
    (dict(逆の判例=2, 判例=0), "B クラスを学習データほどは拾えていない"),
    (dict(逆の判例=0, 判例=3), "A クラスを誤って拾いすぎ"),
])
def test_p52_is_read_with_the_registered_thresholds(kw, expected):
    assert expected in r18.read_p52(Counter(kw))


def test_p52_can_be_read_both_ways_at_once():
    text = r18.read_p52(Counter(逆の判例=2, 判例=3))
    assert "拾えていない" in text and "拾いすぎ" in text and "矛盾しない" not in text


@pytest.mark.parametrize("win, exc, expected", [
    (3, 3, "半分を超えない（ちょうど半分）"), (4, 2, "半分を超える"), (2, 4, "半分を超えない"), (0, 0, "前件に当たる単位がない")])
def test_p79_records_whether_more_than_half_hold(win, exc, expected):
    text = r18.read_p79(Counter(成立=win, 判例=exc))
    assert expected in text
    assert ("ちょうど" in text) == (win == exc and win > 0)
    assert ("取り下げない" in text) == (win + exc > 0)


def test_expected_applies_the_training_rates_to_the_2026_counts():
    train = Counter(成立=73, 判例=10, 逆の判例=5, どちらも当たらない=68)      # P52: B 78・A 78
    e = r18.expected(train, Counter(成立=6, どちらも当たらない=6))
    assert round(e["converse"], 2) == 0.38 and round(e["exception"], 2) == 0.77
    e = r18.expected(train, Counter(成立=3, 逆の判例=1, どちらも当たらない=7, 判例=1))   # 2026年の後件に当たる単位が 4、当たらない単位が 8
    assert e["converse"] == pytest.approx(5 / 78 * 4) and e["exception"] == pytest.approx(10 / 78 * 8)


def registered_checks():
    """登録どおりの数になる合成の単位（学習データ側）。"""
    out = {}
    for pid, want in r18.REGISTERED.items():
        if pid == "P52":
            c = {"成立": 73, "判例": 10, "逆の判例": 5, "どちらも当たらない": 68}
        elif pid == "P50":
            c = {"成立": 68, "判例": 9, "逆の判例": 10, "どちらも当たらない": 69}
        else:
            c = {k: v for k, v in want.items()}
        out[pid] = {"id": pid, "units": [{"unit": f"x{i}-{s}", "status": s} for s, k in c.items() for i in range(k)]}
    return out


def test_expected_cannot_be_computed_without_training_units():
    with pytest.raises(ValueError, match="期待値を出せない"):
        r18.expected(Counter(), Counter(成立=6))
    with pytest.raises(ValueError, match="期待値を出せない"):
        r18.expected(Counter(成立=1, 逆の判例=1), Counter(成立=6))     # 後件に当たらない単位がない


def test_control_passes_when_the_training_counts_are_the_registered_ones():
    assert r18.control(registered_checks()) == []


@pytest.mark.parametrize("pid, status, delta, message", [
    ("P52", "判例", +1, "P52 判例: 手元 11 ≠ 登録 10"),
    ("P64", "成立", -1, "P64 成立: 手元 21 ≠ 登録 22"),
    ("P79", "判例", -1, "P79 判例: 手元 26 ≠ 登録 27"),
    ("P51", "成立", -1, "P51 成立: 手元 9 ≠ 登録 10"),
])
def test_control_names_every_count_that_differs(pid, status, delta, message):
    checks = registered_checks()
    units = checks[pid]["units"]
    if delta > 0:
        units.append({"unit": "extra", "status": status})
    else:
        units.remove(next(u for u in units if u["status"] == status))
    assert message in r18.control(checks)


@pytest.mark.parametrize("pid, status, message", [
    ("P52", "どちらも当たらない", "P52 Aクラスの単位数: 手元 77 ≠ 登録 78"),
    ("P52", "成立", "P52 Bクラスの単位数: 手元 77 ≠ 登録 78"),
    ("P50", "どちらも当たらない", "P50 Bクラスの単位数: 手元 77 ≠ 登録 78"),
    ("P50", "成立", "P50 Aクラスの単位数: 手元 77 ≠ 登録 78"),
])
def test_control_checks_the_numbers_of_a_and_b_class_units_too(pid, status, message):
    checks = registered_checks()
    units = checks[pid]["units"]
    units.remove(next(u for u in units if u["status"] == status))
    assert message in r18.control(checks)


def test_p64_record_names_the_units_that_met_the_antecedent():
    tr = Counter(成立=22, 判例=4, 逆の判例=56, どちらも当たらない=74)
    text = r18.read_record("P64", tr, Counter(成立=1, 逆の判例=5, どちらも当たらない=6),
                           check("P64", 成立=["c-2026"], 逆の判例=["d-2026"]), {"c": "広島", "d": "中日"})
    assert "前件に当たる 1 単位（学習データの率なら 2.0）" in text and "成立 1（広島（c-2026））" in text and "判例 0（なし）" in text
    text = r18.read_record("P64", tr, Counter(成立=1, 判例=1, どちらも当たらない=10), check("P64", 成立=["c-2026"], 判例=["d-2026"]), {"c": "広島", "d": "中日"})
    assert "判例 1（中日（d-2026））" in text


def test_scope_propositions_record_the_units_inside_their_scope():
    none_inside = r18.read_record("P78", Counter(成立=7, 判例=1), Counter(), check("P78"), NAMES)
    assert "範囲に入る単位なし" in none_inside
    inside = r18.read_record("P76", Counter(成立=5, 判例=7), Counter(判例=1, 判定不能=1),
                             check("P76", 判例=["g-2026"], 判定不能=["s-2026"]), NAMES)
    assert "巨人（g-2026）判例" in inside and "ヤクルト" not in inside     # 値が空の単位は範囲に入ったとは数えない


def test_p62_is_unknown_only_when_every_unit_is_unknown():
    trains = registered_checks()
    news = {pid: check(pid) for pid in r18.REGISTERED}
    news["P62"] = check("P62", 判定不能=["d-2026", "g-2026"])
    assert r18.build_result(trains, news, NAMES)["P62"]["reading"].startswith("判定不能")
    news["P62"] = check("P62", 判定不能=["d-2026"], 成立=["g-2026"])
    assert r18.build_result(trains, news, NAMES)["P62"]["reading"] == "記録のみ"


def test_cli_needs_exactly_one_source_for_2026(tmp_path):
    base = ["--config", "c", "--propositions", "p", "--committed", "s", "--out-md", str(tmp_path / "a.md"), "--out-json", str(tmp_path / "a.json")]
    assert r18.main(base) == 2
    assert r18.main([*base, "--games", "g", "--panel", "p"]) == 2
    assert r18.main([*base, "--panel", "p", "--out-panel-2026", str(tmp_path / "p.jsonl")]) == 2
    assert not (tmp_path / "a.md").exists() and not (tmp_path / "p.jsonl").exists()
