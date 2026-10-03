import math
from itertools import product

import polars as pl
import pytest

from pythdragoras import apply_exclusions, binom_tail, cumulative_test, rank_test, run_tail, summary_markdown


@pytest.mark.parametrize("n,r,p", [(1, 1, 0.5), (3, 2, 0.5), (5, 3, 0.3), (6, 2, 0.5), (8, 4, 0.7), (4, 0, 0.5)])
def test_run_tail_matches_brute_force(n, r, p):
    def longest(seq):
        best = cur = 0
        for s in seq:
            cur = cur + 1 if s else 0
            best = max(best, cur)
        return best

    brute = sum(p ** sum(s) * (1 - p) ** (n - sum(s)) for s in product([0, 1], repeat=n) if longest(s) >= r)
    assert run_tail(n, r, p) == pytest.approx(brute)


def test_known_values():
    assert run_tail(14, 14, 0.5) == pytest.approx(0.5**14)  # 14年連続で下位半分
    assert binom_tail(14, 14, 0.5) == pytest.approx(0.5**14)
    assert binom_tail(14, 0, 0.5) == pytest.approx(1.0)
    assert binom_tail(4, 3, 0.5) == pytest.approx(5 / 16)


def test_exclusion_requires_reason_and_is_recorded():
    st = pl.DataFrame({"season": [2019, 2020, 2020], "team": ["d", "d", "g"]})
    with pytest.raises(ValueError):
        apply_exclusions(st, [{"season": 2020}])
    with pytest.raises(ValueError):
        apply_exclusions(st, [{"season": 2020, "reason": "  "}])
    kept, rec = apply_exclusions(st, [{"season": 2020, "reason": "短縮シーズン"}])
    assert kept["season"].to_list() == [2019]
    assert rec == [{"season": 2020, "reason": "短縮シーズン", "rows_removed": 2}]


def _ranks(team_ranks):
    rows = []
    for team, ranks in team_ranks.items():
        for i, r in enumerate(ranks):
            rows.append({"season": 2012 + i, "team": team, "team_name": team, "rank": r,
                         "rank_tie": False, "league_size": 6})
    return pl.DataFrame(rows)


def test_rank_test_counts_streaks_and_compares_with_all_teams():
    st = _ranks({"d": [2, 4, 5, 6, 3, 5], "g": [1, 1, 2, 4, 1, 1], "t": [6, 6, 1, 1, 2, 2]})
    res = {r["team"]: r for r in rank_test(st)}
    d = res["d"]
    assert (d["bottom_seasons"], d["longest_bottom_run"], d["p_bottom_null"]) == (4, 3, 0.5)
    assert d["null_p_at_least_k"] == pytest.approx(binom_tail(6, 4, 0.5))
    assert d["null_p_run_at_least"] == pytest.approx(run_tail(6, 3, 0.5))
    assert d["empirical_share_at_least_k"] == pytest.approx(1 / 3)  # 3球団中、下位4シーズン以上は中日だけ
    assert res["t"]["longest_bottom_run"] == 2 and res["g"]["bottom_seasons"] == 1


def test_cumulative_z():
    st = pl.DataFrame({"season": [2024, 2025], "team": ["d", "d"], "team_name": ["中日", "中日"],
                       "W": [60, 60], "L": [80, 80], "pythag_fixed": [0.5, 0.5], "pythag_var": [0.5, 0.5]})
    ct = cumulative_test(st).filter(pl.col("model") == "fixed").row(0, named=True)
    assert ct["excess_wins"] == pytest.approx(-20)
    assert ct["z"] == pytest.approx(-20 / math.sqrt(70))


def test_summary_separates_observation_from_cause():
    st = _ranks({"d": [4, 5, 6]})
    md = summary_markdown("d", [{"season": 2020, "reason": "r", "rows_removed": 6}],
                          pl.DataFrame({"model": ["fixed"], "team": ["d"], "team_name": ["d"], "seasons": [3],
                                        "excess_wins": [-3.0], "z": [-1.0], "p_two_sided": [0.3]}),
                          rank_test(st), [{"id": "H1", "statement": "s", "status": "untested"}])
    assert "原因は示さない" in md and "2020: r" in md and "(focus)" in md and "| H1 |" in md
