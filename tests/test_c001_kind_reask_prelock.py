"""cycles/c001-chunichi/exploratory/kind_reask_results の事前宣言と命題の固定を確かめる。"""
import hashlib
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "cycles" / "c001-chunichi" / "exploratory" / "kind_reask_results"
LOCKED = (RESULTS / "kind_reask_prelock_2026-11-13.md", RESULTS / "kind_reask_propositions.toml",
          RESULTS / "kind_reask_r2_propositions.toml",       # 第2弾・第4弾は、命題ファイルの冒頭が宣言
          RESULTS / "kind_reask_r4_propositions.toml", RESULTS / "kind_reask_r6_propositions.toml",
          RESULTS / "kind_reask_r10_propositions.toml")
STAMP = RESULTS / "kind_reask_prelock_timestamp.txt"


def test_prelock_hashes_match_stamp():
    # 宣言か命題を書き換えたら、固定時のハッシュと合わなくなる
    stamp = STAMP.read_text()
    for path in LOCKED:
        assert hashlib.sha256(path.read_bytes()).hexdigest() in stamp
        assert path.name in stamp
    assert "JST" in stamp
