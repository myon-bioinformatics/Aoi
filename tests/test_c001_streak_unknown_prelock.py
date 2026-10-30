"""cycles/c001-chunichi/exploratory/streak_unknown_results の事前宣言の固定を確かめる。"""
import hashlib
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "cycles" / "c001-chunichi" / "exploratory" / "streak_unknown_results"
LOCK = RESULTS / "streak_unknown_prelock_2026-10-27.md"
STAMP = RESULTS / "streak_unknown_prelock_timestamp.txt"


def test_prelock_hash_matches_stamp():
    # 事前宣言を書き換えたら、固定時のハッシュと合わなくなる
    stamp = STAMP.read_text()
    assert hashlib.sha256(LOCK.read_bytes()).hexdigest() in stamp
    assert LOCK.name in stamp and "JST" in stamp
