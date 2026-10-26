"""cycles/c002-gohantrust/lag1 の確認。事前宣言の固定、再現ゲート、テスト年の構成、符号検定。"""
import hashlib
import importlib.util
from pathlib import Path

LAG1 = Path(__file__).resolve().parent.parent / "cycles" / "c002-gohantrust" / "lag1"


def _load():
    spec = importlib.util.spec_from_file_location("c002_lag_run", LAG1 / "lag_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


lag_run = _load()


def test_prelock_hash_matches_stamp():
    # 事前宣言を書き換えたら、固定時のハッシュと合わなくなる
    digest = hashlib.sha256((LAG1 / "lag_prelock_2026-10-24.md").read_bytes()).hexdigest()
    stamp = (LAG1 / "lag_prelock_timestamp.txt").read_text()
    assert digest in stamp


def test_replication_gate_passes():
    # 同年版が Grok の報告（勝敗件数・γ̂・順列 p）を再現できること。通らなければ遅れ版は走らせない
    ok, lines, _ = lag_run.gate()
    assert ok, "\n".join(lines)


def test_inputs_match_staple_survey_japan_series():
    # 転記した E と P のうち、research/staple-price-survey（e-Stat）で裏が取れる範囲を固定する。
    # E: 2005–2025 は家計調査（二人以上の世帯。2024–2025 は統計局の年平均結果の概要）、
    # P: 2005–2015 は小売物価統計調査の 5kg 月次の年平均
    import csv
    import statistics

    import pytest

    path = LAG1.parent.parent.parent / "research" / "staple-price-survey" / "staple_survey_vertical.csv"
    if not path.exists():
        pytest.skip("staple-price-survey is not in this checkout")
    engel, rice = {}, {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["country"] != "JPN":
                continue
            if r["variable"] == "engel_share_food_national_hh_survey":
                engel[int(r["year"])] = float(r["value"]) / 100
            elif r["variable"] == "staple_price:rice_uruchi_5kg":
                rice.setdefault(int(r["year"]), []).append(float(r["value"]))
    for y in range(2005, 2026):
        assert abs(lag_run.E[y] - engel[y]) < 5e-4, y
    for y in range(2005, 2016):
        assert len(rice[y]) == 12, y
        assert abs(lag_run.P[y] - statistics.mean(rice[y])) < 0.05, y


def test_lag_test_years_follow_the_prelock():
    assert [r["t"] for r in lag_run.rolling(2005, 1)] == list(range(2012, 2026))
    assert [r["t"] for r in lag_run.rolling(2015, 1)] == list(range(2022, 2026))


def test_sign_p_is_one_sided_binomial():
    assert lag_run.sign_p(0, 7) == 1.0
    assert lag_run.sign_p(4, 4) == 1 / 16
    assert abs(lag_run.sign_p(7, 14) - 0.6047) < 1e-4


# ---- 順列検定の母集団（2026-10-25 レビュー指摘：lag=1 は最終年の ΔlogE を読まない）-------------------

def test_perm_years_are_exactly_the_years_the_statistic_reads():
    for ws in (2005, 2015):
        used = lag_run.used_years(ws, 1)
        assert used == list(range(ws + 1, lag_run.LAST))              # ΔlogE[win_start+1 .. LAST-1]
        assert lag_run.LAST not in used                                # 最終年は統計に入らない
        assert lag_run.used_years(ws, 0) == list(range(ws + 1, lag_run.LAST + 1))  # 同年版は最終年まで読む


def test_permuted_keys_are_all_read_and_the_last_year_is_never_shuffled(monkeypatch):
    seen = []
    real = lag_run.rolling

    def spy(win_start, lag, dE=None):
        if dE is not None and not hasattr(dE, "read"):                # 順列の呼び出し（読み取り記録用の辞書は除く）
            seen.append(sorted(dE))
        return real(win_start, lag, dE=dE)

    monkeypatch.setattr(lag_run, "rolling", spy)
    monkeypatch.setattr(lag_run, "B", 3)
    lag_run.perm_test(2005, 1)
    assert len(seen) == 3 and all(k == list(range(2006, lag_run.LAST)) for k in seen)
    seen.clear()
    lag_run.perm_test(2005, 1, scope="declared")                       # 宣言 §7.2 の文面どおりの版は、最終年も混ぜる
    assert len(seen) == 3 and all(k == list(range(2006, lag_run.LAST + 1)) for k in seen)


def test_gate_permutation_is_unchanged_by_the_scope_fix(monkeypatch):
    monkeypatch.setattr(lag_run, "B", 50)
    assert lag_run.perm_test(2015, 0, "used") == lag_run.perm_test(2015, 0, "declared")   # lag=0 は同じ母集団


def test_committed_lag_results_are_what_the_code_produces():
    import json

    committed = json.loads((LAG1 / "lag_results.json").read_text(encoding="utf-8"))
    assert json.loads(json.dumps(lag_run.run_lag(), default=float)) == committed
    for name, ws in (("extended", 2005), ("legacy", 2015)):
        scope = committed[name]["perm_scope"]
        assert scope["main"] == "used" and scope["years_used"] == list(range(ws + 1, lag_run.LAST))
        assert scope["years_declared"] == list(range(ws + 1, lag_run.LAST + 1))


def test_gamma_stops_with_a_reason_when_every_training_dlogE_is_zero():
    # 分母 Σx² が 0 のとき、numpy は警告だけで nan を返し、その年が「負け」に数えられる。置き換えず、理由を書いて止める
    import pytest

    zero = {t: 0.0 for t in lag_run.DE}
    for lag in (0, 1):
        with pytest.raises(ValueError, match=rf"分母ゼロ.*win_start=2015, lag={lag}, t=\d{{4}}"):
            lag_run.rolling(2015, lag, dE=zero)


def test_gamma_is_still_computed_when_only_some_training_dlogE_are_zero():
    # E が同じ値の年（ΔlogE = 0）はデータにもある。分母が 0 でなければ、これまでの値のまま
    assert any(v == 0.0 for v in lag_run.DE.values())
    rows = lag_run.rolling(2015, 0)
    assert rows and all(r["gamma"] == r["gamma"] for r in rows)         # nan でない
