"""cycles/c002-gohantrust/us-midterm の確認。事前宣言の固定、宣言の数値、計算が走っていないこと。"""
import hashlib
import math
import re
from pathlib import Path

US = Path(__file__).resolve().parent.parent / "cycles" / "c002-gohantrust" / "us-midterm"
LOCK = US / "us_midterm_prelock_2026-10-27.md"
STAMP = US / "us_midterm_prelock_timestamp.txt"


def test_prelock_hash_matches_stamp():
    # 事前宣言を書き換えたら、固定時のハッシュと合わなくなる
    digest = hashlib.sha256(LOCK.read_bytes()).hexdigest()
    stamp = STAMP.read_text()
    assert digest in stamp
    assert LOCK.name in stamp
    assert "JST" in stamp


def test_nothing_but_the_declaration_is_here_until_the_signal():
    # 宣言の時点ではデータの取得も計算もしていない。合図のあとに走らせたら、この一覧と宣言を更新する
    names = sorted(p.name for p in US.iterdir())
    assert names == [LOCK.name, STAMP.name]


def _table_rows(text):
    # §2 の表（w, m, ln m, ln(1+m), A_eq）を読む。§4 の表にも「ln(1+m)」で始まる行があるので、最初のものだけ取る
    rows = {}
    for line in text.splitlines():
        if line.startswith("| w（大きい側の割合）") or line.startswith("| m |") or line.startswith("| ln m |") \
                or line.startswith("| ln(1+m) |") or line.startswith("| A_eq |"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.setdefault(cells[0], cells[1:])
    return rows


def test_section2_table_matches_the_definition():
    rows = _table_rows(LOCK.read_text())
    ws = [float(x) / 100 for x in rows["w（大きい側の割合）"]]
    assert len(ws) == 8
    for w, m_cell, lnm_cell, ln1p_cell, aeq_cell in zip(
        ws, rows["m"], rows["ln m"], rows["ln(1+m)"], rows["A_eq"]
    ):
        m = 2 * w - 1
        assert math.isclose(float(m_cell), m, abs_tol=5e-4)
        if lnm_cell == "ε":
            assert w == 0.5 and m_cell == "0"
        else:
            assert math.isclose(float(lnm_cell.replace("−", "-")), math.log(m), abs_tol=5e-4)
        assert math.isclose(float(ln1p_cell), math.log1p(m), abs_tol=5e-5)
        assert math.isclose(float(aeq_cell), 100 * (1 - m), abs_tol=5e-2)


def test_declared_counts_follow_from_the_election_years():
    text = LOCK.read_text()
    # 選挙 2000, 2002, ..., 2024 → 効くのは翌年の奇数年 2001..2025 の 13 回
    changes = [y + 1 for y in range(2000, 2025, 2)]
    assert changes == list(range(2001, 2026, 2))
    assert len(changes) == 13
    midterm_effect = [y + 1 for y in range(2002, 2025, 4)]
    assert midterm_effect == [2003, 2007, 2011, 2015, 2019, 2023]
    assert "**13 回**" in text
    assert "2003・2007・2011・2015・2019・2023" in text
    # 検定の総数: 形 2 × 基準 2 × 検定の種類 2 × ε の版 2
    assert 2 * 2 * 2 * 2 == 16
    assert "**m_test = 16**" in text
    # 訓練の最小 5 点を引いたテストの点数
    assert len(changes) - 5 == 8
    assert "テストは 8 点" in text


def test_epsilon_stays_a_symbol():
    # ε に数値を置いていないこと（記号のまま・数値は別の宣言で決める）
    text = LOCK.read_text()
    assert not re.search(r"ε\s*[=＝]\s*[0-9]", text)
    assert "記号のまま" in text
    assert "eps_used" in text
