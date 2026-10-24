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


def test_lag_test_years_follow_the_prelock():
    assert [r["t"] for r in lag_run.rolling(2005, 1)] == list(range(2012, 2026))
    assert [r["t"] for r in lag_run.rolling(2015, 1)] == list(range(2022, 2026))


def test_sign_p_is_one_sided_binomial():
    assert lag_run.sign_p(0, 7) == 1.0
    assert lag_run.sign_p(4, 4) == 1 / 16
    assert abs(lag_run.sign_p(7, 14) - 0.6047) < 1e-4
