"""cycles/c001-chunichi/exploratory/games_table_from_observed.py の確認。

SYNTHETIC: 小さな合成の観測（実データではない）で、試合数での打ち切り・key・日付・得点の検査・合計の照合を確かめる。
最後の 1 件だけ、リポジトリに保存済みの実データ（games_raw.json、season-2026）で、作った表の球団年ごとの G/W/L/T/RF/RA が
確定済みの値と全部一致することを確かめる。結論には使わない。
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
C001 = ROOT / "cycles" / "c001-chunichi"
spec = importlib.util.spec_from_file_location("games_table_from_observed", C001 / "exploratory" / "games_table_from_observed.py")
gt = importlib.util.module_from_spec(spec)
sys.modules["games_table_from_observed"] = gt
spec.loader.exec_module(gt)


def raw(n, home="a", away="b", hr=3, ar=1, year=2013, date="20130401", status="final"):
    return {"year": year, "date": date, "home": home, "away": away, "home_R": hr, "away_R": ar, "status": status,
            "url": f"https://npb.jp/bis/{year}/games/s{date}{n:05d}.html"}


G = {(2013, "a"): 2, (2013, "b"): 2}


def test_takes_games_until_each_team_reaches_its_game_count_and_drops_the_rest():
    games = [raw(3, date="20130403"), raw(1, date="20130401"), raw(2, date="20130402"), raw(4, date="20131001")]
    out = gt.from_games_raw(games, G)
    assert [r["key"] for r in out] == ["s2013040100001", "s2013040200002"]      # 日付の順。3 試合目以降（ポストシーズン等）は外れる
    assert out[0] == {"key": "s2013040100001", "date": "2013-04-01", "home": "a", "away": "b", "hs": 3, "as": 1}


def test_a_game_is_dropped_when_either_team_has_already_played_its_games():
    g = {(2013, "a"): 1, (2013, "b"): 2, (2013, "c"): 1, (2013, "d"): 2}
    games = [raw(1, "a", "b", date="20130401"), raw(2, "c", "d", date="20130401"), raw(3, "a", "d", date="20130402"), raw(4, "b", "d", date="20130403")]
    out = gt.from_games_raw(games, g)
    assert [r["key"] for r in out] == ["s2013040100001", "s2013040100002", "s2013040300004"]       # a は 1 試合で終わり、a-d は外れる


def test_ignores_games_that_are_not_final_or_outside_the_years():
    games = [raw(1), raw(2, status="cancelled"), raw(3, status="noGame"), raw(4, year=2012, date="20120401"), raw(5, year=2026, date="20260401"),
             raw(6, date="20130402")]
    assert [r["key"] for r in gt.from_games_raw(games, G)] == ["s2013040100001", "s2013040200006"]


def test_games_without_a_team_id_are_ignored():
    games = [raw(1), dict(raw(2), home=None), raw(3, date="20130402")]
    assert len(gt.from_games_raw(games, G)) == 2


def test_a_team_that_does_not_reach_its_game_count_is_an_error():
    with pytest.raises(ValueError, match="試合数に届かない"):
        gt.from_games_raw([raw(1)], G)


def test_a_team_without_a_game_count_is_an_error():
    with pytest.raises(ValueError, match="試合数（G）が確定済みの表にない"):
        gt.from_games_raw([raw(1, home="z")], G)


def test_duplicate_keys_are_an_error():
    with pytest.raises(ValueError, match="key が重複"):
        gt.from_games_raw([raw(1), dict(raw(1), date="20130402")], G)       # url（= key）が同じ 2 試合


@pytest.mark.parametrize("bad", [None, True, -1, 2.5, "3"])
def test_scores_must_be_non_negative_integers(bad):
    with pytest.raises(ValueError, match="得点が 0 以上の整数でない"):
        gt.from_games_raw([raw(1, hr=bad)], {(2013, "a"): 1, (2013, "b"): 1})


def test_dates_must_be_yyyymmdd():
    with pytest.raises(ValueError, match="日付が YYYYMMDD でない"):
        gt.from_games_raw([raw(1, date="2013-04-01")], {(2013, "a"): 1, (2013, "b"): 1})


def s26(n, home="b", away="e", hr=0, ar=10, md="0327", status="final"):
    return {"status": status, "year": 2026, "date": f"2026{md}", "home": home, "away": away, "home_R": hr, "away_R": ar,
            "url": f"https://npb.jp/scores/2026/{md}/{home}-{away}-{n:02d}/"}


def test_season_2026_rows_become_table_rows_sorted_by_date_and_key():
    out = gt.from_season_games([s26(2, md="0328"), s26(1), s26(1, home="c", away="d", md="0327", hr=6, ar=5)])
    assert [r["key"] for r in out] == ["s20260327-b-e-01", "s20260327-c-d-01", "s20260328-b-e-02"]
    assert out[0] == {"key": "s20260327-b-e-01", "date": "2026-03-27", "home": "b", "away": "e", "hs": 0, "as": 10}


@pytest.mark.parametrize("change, message", [
    ({"status": "inProgress"}, "終了（final）でない"),
    ({"url": "https://npb.jp/scores/2026/0327/b-e/"}, "URL が想定の形でない"),
    ({"home": "c"}, "URL と home/away/date が合わない"),
    ({"date": "20260328"}, "URL と home/away/date が合わない"),
])
def test_season_2026_rows_that_do_not_match_their_url_are_errors(change, message):
    with pytest.raises(ValueError, match=message):
        gt.from_season_games([dict(s26(1), **change)])


def test_season_2026_duplicate_keys_are_an_error():
    with pytest.raises(ValueError, match="key が重複"):
        gt.from_season_games([s26(1), s26(1)])


def table(*rows):
    return [dict(zip(("key", "date", "home", "away", "hs", "as"), r)) for r in rows]


def test_team_totals_count_wins_losses_ties_and_runs():
    games = table(("k1", "2026-04-01", "a", "b", 3, 1), ("k2", "2026-04-02", "b", "a", 2, 2), ("k3", "2026-04-03", "b", "a", 5, 0))
    t = gt.team_totals(games)
    assert t[(2026, "a")] == {"G": 3, "W": 1, "L": 1, "T": 1, "RF": 5, "RA": 8}
    assert t[(2026, "b")] == {"G": 3, "W": 1, "L": 1, "T": 1, "RF": 8, "RA": 5}


def test_check_totals_reports_every_kind_of_difference_and_ignores_other_years():
    games = table(("k1", "2026-04-01", "a", "b", 3, 1))
    ok = {(2026, "a"): {"G": 1, "W": 1, "L": 0, "T": 0, "RF": 3, "RA": 1}, (2026, "b"): {"G": 1, "W": 0, "L": 1, "T": 0, "RF": 1, "RA": 3},
          (2025, "z"): {"G": 143, "W": 0, "L": 0, "T": 0, "RF": 0, "RA": 0}}
    assert gt.check_totals(games, ok) == []
    wrong = {**ok, (2026, "a"): {**ok[(2026, "a")], "RF": 4}}
    assert gt.check_totals(games, wrong) == ["(2026, 'a') RF: 試合表 3 ≠ 確定済み 4"]
    assert gt.check_totals(games, {k: v for k, v in ok.items() if k != (2026, "b")}) == ["(2026, 'b'): 確定済みの表にない"]
    assert gt.check_totals(games, {**ok, (2026, "c"): ok[(2026, "a")]}) == ["(2026, 'c'): 試合表にない"]


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def test_cli_writes_the_table_only_when_totals_match(tmp_path):
    games = write_jsonl(tmp_path / "games.jsonl", [s26(1), s26(2, md="0328", hr=4, ar=4)])
    good = write_jsonl(tmp_path / "good.jsonl", [{"season": 2026, "team": "b", "G": 2, "W": 0, "L": 1, "T": 1, "RF": 4, "RA": 14},
                                                 {"season": 2026, "team": "e", "G": 2, "W": 1, "L": 0, "T": 1, "RF": 14, "RA": 4}])
    out = tmp_path / "out.jsonl"
    assert gt.main(["--season-2026", str(games), "--totals-2026", str(good), "--out", str(out)]) == 0
    assert [json.loads(line)["key"] for line in out.read_text(encoding="utf-8").splitlines()] == ["s20260327-b-e-01", "s20260328-b-e-02"]
    bad = write_jsonl(tmp_path / "bad.jsonl", [{"season": 2026, "team": "b", "G": 2, "W": 0, "L": 1, "T": 1, "RF": 5, "RA": 14},
                                               {"season": 2026, "team": "e", "G": 2, "W": 1, "L": 0, "T": 1, "RF": 14, "RA": 5}])
    out2 = tmp_path / "out2.jsonl"
    assert gt.main(["--season-2026", str(games), "--totals-2026", str(bad), "--out", str(out2)]) == 2
    assert not out2.exists()


@pytest.mark.parametrize("argv", [[], ["--games-raw", "x.json"]])
def test_cli_needs_an_input_and_game_counts(tmp_path, argv):
    assert gt.main([*argv, "--out", str(tmp_path / "o.jsonl")]) == 2
    assert not (tmp_path / "o.jsonl").exists()


def test_saved_observations_reproduce_the_confirmed_team_totals(tmp_path):
    """保存済みの実データから作った表は、2013〜2025年の 156 球団年（season.jsonl）と 2026年の 12 球団年（team_totals.jsonl）の
    G/W/L/T/RF/RA に全部一致する（一致しなければ main は書き出さずに止まる）。"""
    out = tmp_path / "games.jsonl"
    assert gt.main(["--games-raw", str(C001 / "recovered-inputs" / "observed" / "games_raw.json"),
                    "--season-jsonl", str(C001 / "outputs" / "season.jsonl"),
                    "--season-2026", str(C001 / "season-2026" / "observed" / "games.jsonl"),
                    "--totals-2026", str(C001 / "season-2026" / "derived" / "team_totals.jsonl"), "--out", str(out)]) == 0
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 11028 + 858
    assert len({r["key"] for r in rows}) == len(rows)
    assert len(gt.team_totals(rows)) == 156 + 12
