"""research/shrink-index: 縮む商品の総量指標（カントリーマアム指標）と、仮想の縮む商品。

総量 = 枚数 x 1枚の重さ。補間しない、ゼロは log1p で扱う、点数が足りなければ判断を保留する、
という規則を小さな数字で確かめる。実データの数字は、記事から写した行を固定して確かめる。
"""
import csv
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "research" / "shrink-index"
sys.path.insert(0, str(DIR))
import shrink_index as si  # noqa: E402
import synthetic_shrink as syn  # noqa: E402

OBS = DIR / "countrymaam_observed_vertical.csv"
COMMITTED_SYN = ROOT / syn.DEFAULT_OUT
P = "shrink:countrymaam_family_vanilla_cocoa"
HEADER = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for year, variable, value in rows:
            w.writerow(["XXX", "%d-01-01" % year, year, variable, value, "u", "test", "", ""])
    return path


def _read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


# ---- 読み込みと総量 -------------------------------------------------------------------

def test_load_accepts_equal_duplicates_and_rejects_conflicts(tmp_path):
    ok = _write(tmp_path / "ok.csv", [(2024, "p:pieces", 18), (2024, "p:pieces", 18.0)])
    assert si.load(ok)["p"]["pieces"] == {2024: 18.0}
    bad = _write(tmp_path / "bad.csv", [(2024, "p:pieces", 18), (2024, "p:pieces", 14)])
    with pytest.raises(ValueError, match="conflict"):
        si.load(bad)


def test_total_needs_both_parts_and_does_not_interpolate():
    m = {"pieces": {1992: 28, 2005: 30, 2024: 18}, "grams_per_piece": {1992: 11.5, 2024: 10.0}}
    q, assumed = si.totals(m)
    assert q == {1992: 322.0, 2024: 180.0} and assumed == set()      # 2005 は重さが無いので出さない


def test_assumed_weight_fills_a_gap_but_observed_wins():
    m = {"pieces": {1992: 28, 2005: 30}, "grams_per_piece": {1992: 11.5}}
    q, assumed = si.totals(m, assume={2005: 10.5, 1992: 99.0})
    assert q == {1992: 322.0, 2005: 315.0} and assumed == {2005}


def test_direct_total_is_used():
    q, assumed = si.totals({"total_g": {2000: 250.0}})
    assert q == {2000: 250.0} and assumed == set()


# ---- 水準・区間・ゼロ・危険 ------------------------------------------------------------

def test_level_and_rates_only_join_known_neighbours():
    q = {1992: 322.0, 2024: 180.0}
    assert si.level(q)[2024] == pytest.approx(180 / 322)
    (a, b, r), = si.rates(q)                                          # 間の年を作らない：区間は1つだけ
    assert (a, b) == (1992, 2024) and r == pytest.approx((math.log1p(180) - math.log1p(322)) / 32)
    assert si.level({2000: 0.0, 2001: 5.0}) is None                   # 基準が 0 なら水準は出さない


def test_zero_content_is_safe():
    q = {2023: 10.0, 2024: 0.0}
    assert math.isfinite(si.rates(q)[0][2]) and si.rates(q)[0][2] < 0
    assert 0.98 < si.danger(0.0, 60.0) < 1.0 and math.isfinite(si.margin(0.0, 60.0))


def test_danger_is_half_at_the_level_smooth_and_decreasing():
    assert si.danger(60.0, 60.0) == pytest.approx(0.5)
    xs = [0, 10, 30, 60, 100, 300, 1000]
    ds = [si.danger(x, 60.0) for x in xs]
    assert all(a > b for a, b in zip(ds, ds[1:]))
    assert abs(si.danger(100.0 + 1e-6, 60.0) - si.danger(100.0, 60.0)) < 1e-6


def test_evidence_is_held_back_below_min_points():
    four = {y: 100.0 for y in range(4)}
    five = {y: 100.0 for y in range(5)}
    assert si.MIN_POINTS == 5
    assert si.evidence(four) == "insufficient" and si.evidence(five) == "sufficient"


@pytest.mark.parametrize("observed_count, assumed_count, expected", [
    (0, 5, "insufficient"),
    (5, 0, "sufficient"),
    (4, 1, "insufficient"),
    (5, 2, "sufficient"),
])
def test_cli_evidence_counts_only_observed_totals(
        tmp_path, capsys, observed_count, assumed_count, expected):
    observed_years = list(range(2000, 2000 + observed_count))
    assumed_years = list(range(2010, 2010 + assumed_count))
    years = observed_years + assumed_years
    rows = [(y, "p:pieces", 10) for y in years]
    rows += [(y, "p:grams_per_piece", 10) for y in observed_years]
    path = _write(tmp_path / "evidence.csv", rows)
    args = [str(path), "--product", "p", "--danger-total", "60", "--whatif"]
    if assumed_years:
        args += ["--assume-weight", ",".join("%d:5" % y for y in assumed_years)]
    assert si.main(args) == 0
    out = capsys.readouterr().out
    assert ("evidence      %s (%d observed points, MIN_POINTS=5)" %
            (expected, observed_count)) in out
    total_line = next(line for line in out.splitlines() if line.startswith("total g"))
    for y in observed_years:
        assert "%d: 100.0" % y in total_line
    for y in assumed_years:
        assert "%d: 50.0" % y in total_line
    assert ("ASSUMED" in total_line) == bool(assumed_years)
    # Assumptions still participate in the displayed analysis and WHAT-IF.
    q = {y: 100.0 for y in observed_years}
    q.update({y: 50.0 for y in assumed_years})
    assert "total level    %s" % si._r(si.level(q)) in out
    assert "rate per year  %s" % [(a, b, round(r, 5)) for a, b, r in si.rates(q)] in out
    assert "WHAT-IF (not a forecast)" in out


def test_report_evidence_observed_weight_and_direct_total_override_assumptions(capsys):
    m = {"pieces": {2000: 10, 2001: 10, 2002: 10},
         "grams_per_piece": {2000: 10, 2001: 10, 2002: 10},
         "total_g": {2003: 90, 2004: 80}}
    q, assumed = si.report("p", m, assume={y: 999 for y in range(2000, 2005)})
    assert q == {2000: 100, 2001: 100, 2002: 100, 2003: 90, 2004: 80}
    assert assumed == set()
    out = capsys.readouterr().out
    assert "evidence      sufficient (5 observed points, MIN_POINTS=5)" in out
    assert "ASSUMED" not in out


def test_whatif_years():
    assert si.whatif_years(300.0, 60.0, 0.0) is None and si.whatif_years(300.0, 60.0, 0.01) is None
    assert si.whatif_years(50.0, 60.0, -0.02) == 0.0
    r = -(math.log1p(300.0) - math.log1p(60.0)) / 10
    assert si.whatif_years(300.0, 60.0, r) == pytest.approx(10.0)


def test_unit_price_rises_when_the_price_is_held():
    up = si.unit_price_index({1992: 300.0, 2000: 300.0, 2024: 300.0}, {1992: 300.0, 2000: 0.0, 2024: 150.0})
    assert up == {1992: 1.0, 2024: pytest.approx(2.0)}                # 総量 0 の年は出さない


# ---- 実データ（記事から写した行）---------------------------------------------------------

def test_observed_rows_give_the_numbers_quoted_to_the_user():
    m = si.load(OBS)[P]
    q, assumed = si.totals(m)
    assert q == {1992: 322.0, 2024: 180.0} and assumed == set()
    assert si.evidence(q) == "insufficient"
    q2, assumed2 = si.totals(m, assume={2005: 10.5, 2007: 10.5})
    assert q2 == {1992: 322.0, 2005: 315.0, 2007: 294.0, 2024: 180.0} and assumed2 == {2005, 2007}
    assert si.evidence(q2) == "insufficient"                          # 仮置きしても 4 点：足りない
    assert si.level(m["pieces"])[2005] > 1.0 > si.level(q2)[2005]     # 枚数だけだと増えて見える


def test_observed_rows_are_labelled_secondary_and_unmixed():
    rows = list(csv.DictReader(open(OBS, encoding="utf-8", newline="")))
    assert len(rows) >= 11
    for r in rows:
        assert r["source"].startswith("https://") and r["variable"].startswith("shrink:")
        assert "SYNTHETIC" not in " ".join(r.values()) and r["estimated_value"] == ""
        assert "secondary source" in r["note"] and "Retrieved 2026-10-24" in r["note"]


def test_cli_exit_codes_and_labels(capsys, tmp_path):
    assert si.main([str(OBS), "--product", P]) == 0
    out = capsys.readouterr().out
    assert "insufficient" in out and "WHAT-IF" not in out and "ASSUMED" not in out
    assert si.main([str(OBS), "--product", P, "--assume-weight", "2005:10.5,2007:10.5"]) == 0
    assert "ASSUMED" in capsys.readouterr().out
    assert si.main([str(OBS), "--product", P, "--danger-total", "60", "--whatif"]) == 0
    assert "WHAT-IF (not a forecast)" in capsys.readouterr().out
    assert si.main([str(OBS), "--product", "nothing"]) == 66
    bad = _write(tmp_path / "bad.csv", [(2024, "p:pieces", 18), (2024, "p:pieces", 14)])
    assert si.main([str(bad), "--product", "p"]) == 65


# ---- 仮想の縮む商品 --------------------------------------------------------------------

def test_synthetic_patterns_behave_as_declared():
    r = {x["id"]: x for x in syn.check(verbose=False)}
    assert set(r) == {p[0] for p in syn.PATTERNS}
    assert r["M1"]["total_last"] == pytest.approx(math.exp(-0.64), abs=1e-6) and r["M1"]["first_year_in_zone"] is None
    assert r["M2"]["total_last"] == pytest.approx(200 / 300)
    assert r["M3"]["first_year_in_zone"] == 2021                       # q <= 60 g になる最初の年
    assert r["M4"]["pieces_last"] == pytest.approx(1.0) and r["M4"]["total_last"] < 0.7   # 枚数だけだと縮んでいない
    assert r["M5"]["unit_price_last"] == pytest.approx(math.exp(0.64), abs=1e-6)
    assert r["M6"]["total_last"] > 1.0 and r["M6"]["rate_min"] > 0
    assert si.whatif_years(300.0, 60.0, r["M6"]["rate_min"]) is None   # 減っていないので「いつ危険域か」は出さない
    assert r["M7"]["total_last"] == pytest.approx(0.0) and r["M7"]["d_last"] > 0.98 and r["M7"]["first_year_in_zone"] == 2018
    assert r["M8"]["points"] == 4 and r["M8"]["evidence"] == "insufficient"
    assert all(x["evidence"] == "sufficient" for k, x in r.items() if k != "M8")


def test_synthetic_is_deterministic_and_labelled(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    syn.write_vertical(a)
    syn.write_vertical(b)
    assert a.read_bytes() == b.read_bytes()
    rows = list(csv.DictReader(open(a, encoding="utf-8", newline="")))
    assert list(rows[0].keys()) == HEADER
    for r in rows:
        assert r["country"] == "SYN" and r["variable"].startswith("synthetic_shrink:")
        assert r["unit"].endswith("(synthetic)") and r["source"].startswith("SYNTHETIC") and r["estimated_value"] == ""


@pytest.mark.skipif(not COMMITTED_SYN.exists(), reason="committed synthetic CSV absent")
def test_committed_synthetic_csv_matches_the_generation_rule(tmp_path):
    out = tmp_path / "regen.csv"
    assert syn.main(["--out", str(out)]) == 0
    assert _read(out) == _read(COMMITTED_SYN)


def test_committed_synthetic_csv_can_be_read_by_the_index():
    m = si.load(COMMITTED_SYN)["synthetic_shrink:M3_accelerating"]
    q, _ = si.totals(m)
    assert len(q) == 33 and q[1992] == pytest.approx(300.0, rel=1e-5)
    assert q[2024] == pytest.approx(30 * 10 * math.exp(-0.002 * 32 * 32), rel=1e-5)


# ---- ゼロ・NaN のログ（値は変えない。出なかったときも「none」と必ず出す）-------------------------

def test_load_logs_zero_nan_inf_and_blank_and_keeps_values(tmp_path):
    path = _write(tmp_path / "odd.csv", [
        (2000, "p:pieces", 0),                  # ZERO: 記録して値は残す
        (2001, "p:pieces", float("nan")),       # NaN: 記録して値は残す
        (2002, "p:pieces", float("inf")),       # INF: 記録して値は残す
        (2003, "p:pieces", ""),                 # BLANK: 使わず記録
        (2004, "p:pieces", 5),                  # ふつうの値は記録しない
    ])
    log = si.ZeroNaNLog()
    m = si.load(path, log)["p"]["pieces"]
    assert m[2000] == 0.0 and math.isnan(m[2001]) and math.isinf(m[2002]) and m[2004] == 5.0 and 2003 not in m
    assert dict(log.count) == {("load", "p:pieces", "ZERO"): 1, ("load", "p:pieces", "NaN"): 1,
                               ("load", "p:pieces", "INF"): 1, ("load", "p:pieces", "BLANK"): 1}
    assert "[zero/NaN log] load: p:pieces ZERO x1  e.g. 2000" in log.lines("load")


def test_two_nan_rows_for_one_year_are_not_a_conflict_but_nan_vs_number_is(tmp_path):
    same = _write(tmp_path / "nan2.csv", [(2000, "p:pieces", float("nan")), (2000, "p:pieces", float("nan"))])
    assert math.isnan(si.load(same)["p"]["pieces"][2000])
    bad = _write(tmp_path / "nan_vs_num.csv", [(2000, "p:pieces", float("nan")), (2000, "p:pieces", 3)])
    with pytest.raises(ValueError, match="conflict"):
        si.load(bad)


def test_report_logs_zero_totals_flat_zero_rates_and_skipped_unit_prices(tmp_path, capsys):
    rows = [(y, "p:pieces", n) for y, n in ((2000, 10), (2001, 0), (2002, 0))]
    rows += [(y, "p:grams_per_piece", 10) for y in (2000, 2001, 2002)]
    rows += [(y, "p:price", 100) for y in (2000, 2001, 2002)]
    path = _write(tmp_path / "zero.csv", rows)
    assert si.main([str(path), "--product", "p", "--danger-total", "60"]) == 0
    out = capsys.readouterr().out
    assert "[zero/NaN log] load: p:pieces ZERO x2  e.g. 2001, 2002" in out
    assert "[zero/NaN log] compute: total g ZERO x2  e.g. 2001, 2002" in out
    assert "[zero/NaN log] compute: rate per year ZERO x1  e.g. 2001-2002" in out    # 総量が変わらない区間
    assert "[zero/NaN log] compute: unit price SKIPPED x2  e.g. total q is 0 in 2001, total q is 0 in 2002" in out
    assert out.index("[zero/NaN log] load") < out.index("total g")                    # 読み込みのログは先に出る


def test_report_logs_a_zero_base_level_as_skipped_and_the_value_stays_none(tmp_path, capsys):
    path = _write(tmp_path / "base0.csv", [(2000, "p:total_g", 0), (2001, "p:total_g", 5)])
    assert si.main([str(path), "--product", "p"]) == 0
    out = capsys.readouterr().out
    assert "[zero/NaN log] compute: total level SKIPPED x1  e.g. base q is 0 in 2000" in out
    assert "total level    None" in out                                               # 値は以前と同じ


def test_cli_prints_the_log_even_when_nothing_happens(capsys):
    assert si.main([str(OBS), "--product", P]) == 0
    out = capsys.readouterr().out
    assert "[zero/NaN log] load: none" in out and "[zero/NaN log] compute: none" in out
    assert out.index("[zero/NaN log] load") < out.index(P) < out.index("[zero/NaN log] compute")


def test_load_log_is_printed_even_when_the_run_stops_with_a_conflict(tmp_path, capsys):
    bad = _write(tmp_path / "c.csv", [(2000, "p:pieces", 0), (2001, "p:pieces", 18), (2001, "p:pieces", 14)])
    assert si.main([str(bad), "--product", "p"]) == 65
    cap = capsys.readouterr()
    assert "[zero/NaN log] load: p:pieces ZERO x1" in cap.out and "conflict" in cap.err
