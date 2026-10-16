"""リンク文字列の表記揺れ。ケースは cases/npb_score_text.jsonl に置く。

新しい表記を観測したら、正規表現を広げる前にまずここへケースを足す。
フィールドは xprobe のコーパス形式（id / category / value / reason）に expected を加えたもの。
"""

import json
from itertools import product
from pathlib import Path

import pytest

from npb_calendar import ABBR, read_score

CASES = [json.loads(line) for line in
         (Path(__file__).parent / "cases" / "npb_score_text.jsonl").read_text(encoding="utf-8").splitlines()]


def test_corpus_contract():
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids))
    for c in CASES:
        assert set(c) == {"id", "category", "value", "expected", "reason"}, c["id"]
        assert c["reason"].strip(), c["id"]
    counts = {k: sum(c["category"] == k for c in CASES) for k in ("accept", "cancelled", "unknown")}
    assert min(counts.values()) >= 5, counts


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_read_score(case):
    kind, score = read_score(case["value"])
    exp = dict(case["expected"])
    assert kind == exp.pop("kind"), repr(case["value"])
    assert score == (exp if kind == "game" else None)


@pytest.mark.parametrize(("home", "away"), list(product(ABBR, ABBR)))
def test_every_team_pair(home, away):
    assert read_score(f"{home} 7 - 2 {away}") == ("game", {"home": ABBR[home], "away": ABBR[away], "hs": 7, "as": 2})


@pytest.mark.parametrize("hs,as_", [(0, 0), (9, 9), (10, 0), (0, 10), (99, 99)])
def test_score_digit_boundaries(hs, as_):
    assert read_score(f"中 {hs} - {as_} 巨") == ("game", {"home": "d", "away": "g", "hs": hs, "as": as_})


@pytest.mark.parametrize("text", ["中 100 - 0 巨", "中 0 - 100 巨"])
def test_score_digit_upper_bound_is_unknown(text):
    assert read_score(text) == ("unknown", None)
