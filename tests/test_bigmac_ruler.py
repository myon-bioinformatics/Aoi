"""research/bigmac-ruler: 主食の価格をビッグマックの物差しで見るコードと、合成データ。

小さな縦持ちCSV（log b = log B0 + 0.5*log E + 0.5*log M が厳密に成り立つ）を作り、
紛らわしい系列（包装単位・通貨違い・月数不足・複数系列・インフレ国・ビッグマック1点）を混ぜて、
パネルの規則と推定がそのとおりに働くことを確かめる。実データは使わない
（最後の1件だけ、置いてある合成CSVが生成規則どおりに再現できるかを見る）。
"""
import csv
import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "research" / "bigmac-ruler"


def _load(name):
    spec = importlib.util.spec_from_file_location("bigmac_ruler_" + name, DIR / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


chk = _load("staple_bigmac_check")
syn = _load("synthetic_staples")

HEADER = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
RICE = "staple_price:rice:test"
BETA, GAMMA, B0 = 0.5, 0.5, 0.5
YEARS = range(2021, 2026)
POP = 1_000_000.0


def _row(country, date, variable, value, unit):
    return [country, date, int(date[:4]), variable, "%.12g" % value, unit, "test", "", ""]


def _toy_rows():
    """通常国10 + 紛らわしい国5。b は E と M から厳密に決まる。"""
    rng = np.random.default_rng(1)
    rows = []

    def covariates(c, cur, i, y, P, *, one_bigmac_point=False):
        E = rng.uniform(0.10, 0.40)
        M = float(np.exp(rng.normal(3.0, 1.0)))
        rows.append(_row(c, "%d-01-01" % y, "engel_share_food", E * 100, "percent"))
        rows.append(_row(c, "%d-01-01" % y, "household_consumption_total_lcu", M * P * POP, cur))
        rows.append(_row(c, "%d-01-01" % y, "population_total", POP, "persons"))
        rows.append(_row(c, "%d-01-01" % y, "bigmac_local_price", P * 0.99, cur))
        if not one_bigmac_point:
            rows.append(_row(c, "%d-07-01" % y, "bigmac_local_price", P * 1.01, cur))
        return E, M

    def staple(c, variable, unit, y, price, months=12):
        for m in range(1, months + 1):
            rows.append(_row(c, "%d-%02d-01" % (y, m), variable, price, unit))

    specs = ([("N%02d" % i, "X%02d" % i) for i in range(10)]
             + [("INF", "INF"), ("TWO", "TWO"), ("PK5", "PK5"), ("WCUR", "WCU"), ("FEW", "FEW")])
    for i, (c, cur) in enumerate(specs):
        for k, y in enumerate(YEARS):
            P = 2.0 * (3.0 ** (k / 4) if c == "INF" else 1.03 ** k) * (1 + 0.1 * i)   # INF は4年で3倍
            E, M = covariates(c, cur, i, y, P, one_bigmac_point=(c == "N01" and y == 2021))
            price = (B0 * E ** BETA * M ** GAMMA) * P
            if c == "PK5":
                staple(c, RICE, "%s per 5 kg" % cur, y, price)          # 包装単位は使わない
            elif c == "WCUR":
                staple(c, RICE, "ZZZ per kg", y, price)                  # 通貨がビッグマックと違う
            elif c == "FEW":
                staple(c, RICE, "%s per kg" % cur, y, price, months=3)   # 月数が足りない
            elif c == "N00":
                staple(c, RICE, "%s per KG" % cur, y, price)             # KG は per kg と同一視
            else:
                staple(c, RICE, "%s per kg" % cur, y, price)
            if c == "TWO" and y == 2023:                                 # 年数が少ない別系列は選ばれない
                staple(c, "staple_price:rice:other", "%s per kg" % cur, y, 1.0e6)
    return rows


@pytest.fixture(scope="module")
def toy(tmp_path_factory):
    path = tmp_path_factory.mktemp("bigmac") / "toy.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(_toy_rows())
    return path


# ---- staple_bigmac_check ------------------------------------------------------------

def test_is_per_kg_accepts_only_plain_kg():
    for u in ("EUR per kg", "EUR per KG", "EUR per Kg"):
        assert chk._is_per_kg(u)
    for u in ("EUR per 5 kg", "EUR per 1.5 kg", "EUR per litre", "EUR per kg of rice"):
        assert not chk._is_per_kg(u)


def test_panel_rules(toy):
    S = chk.load_survey(str(toy))
    panel, dropped = chk.build_panel(S, "staple_price:rice")
    countries = {r["country"] for r in panel}
    assert countries == {"N%02d" % i for i in range(10)} | {"INF", "TWO"}   # PK5・WCUR・FEW は入らない
    assert dropped["currency_mismatch:WCUR"] == 1                           # 通貨違いは換算せず除く
    assert dropped["no_bigmac_pair"] == 1                                   # N01 の2021年はビッグマックが1点
    assert len(panel) == 12 * 5 - 1
    assert ("N01", 2021) not in {(r["country"], r["year"]) for r in panel}
    two = [r for r in panel if r["country"] == "TWO"]
    assert len(two) == 5 and {r["series"] for r in two} == {RICE}           # 年数が多い系列を選ぶ
    assert all(r["price"] < 1e5 for r in two)


def test_bigmac_ratio_and_missing_year(toy):
    S = chk.load_survey(str(toy))
    assert chk.bigmac_ratio(S, "INF") == pytest.approx(3.0)
    assert chk.bigmac_ratio(S, "N00") == pytest.approx(1.03 ** 4)
    assert chk.bigmac_ratio(S, "N01") is None            # 2021年が1点だけ → 比を作らない（除外の対象にしない）
    assert chk.bigmac_ratio(S, "NOWHERE") is None


def test_analyze_recovers_exact_relation(toy):
    S = chk.load_survey(str(toy))
    panel, _ = chk.build_panel(S, "staple_price:rice")
    res = chk.analyze(panel, boot=200)
    assert res["beta"] == pytest.approx(BETA, abs=1e-6)
    assert res["gamma"] == pytest.approx(GAMMA, abs=1e-6)
    assert res["r2"] == pytest.approx(1.0, abs=1e-9)
    lo, hi = res["ci"]["gamma"]
    assert lo <= GAMMA <= hi and hi - lo < 1e-5
    assert res["p_gamma_ge_1"] == 0.0


def test_main_exit_codes_and_exclusion(toy, tmp_path, capsys):
    panel_out = tmp_path / "panel.csv"
    assert chk.main([str(toy), "--prefix", "staple_price:rice", "--boot", "50",
                     "--exclude-inflation", "2.0", "--panel-out", str(panel_out)]) == 0
    out = capsys.readouterr().out
    assert "['INF']" in out                                  # 除外の指定と結果が出力に残る
    with open(panel_out, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert "INF" not in {r["country"] for r in rows} and len(rows) == 11 * 5 - 1
    assert chk.main([str(toy), "--prefix", "staple_price:nonexistent", "--boot", "10"]) == 66


def test_main_without_exclusion_keeps_inflation_country(toy, capsys):
    assert chk.main([str(toy), "--prefix", "staple_price:rice", "--boot", "20"]) == 0
    assert "excluded" not in capsys.readouterr().out


# ---- ゼロ・NaN のログ（値は変えない。出なかったときも「none」と必ず出す）-------------------------

def _blank_row(country, date, variable, unit):
    return [country, date, int(date[:4]), variable, "", unit, "test", "", ""]


def test_load_logs_zero_nan_inf_blank_and_keeps_values(tmp_path):
    rows = [
        _row("A", "2021-01-01", "household_consumption_total_lcu", 0.0, "AAA"),   # ZERO: 記録して値は残す
        _row("A", "2022-01-01", "engel_share_food", float("nan"), "percent"),     # NaN: 記録して値は残す
        _row("A", "2023-01-01", "population_total", float("inf"), "persons"),     # INF: 記録して値は残す
        _blank_row("A", "2024-01-01", "bigmac_local_price", "AAA"),               # BLANK: 使わず記録
        _row("A", "2021-01-01", "staple_price:rice:test", 0.0, "AAA per kg"),     # 主食の価格のゼロ
        _blank_row("A", "2021-02-01", "staple_price:rice:test", "AAA per kg"),    # 主食の価格の空欄
        _row("A", "2021-03-01", "staple_price:rice:test", 1.5, "AAA per kg"),     # ふつうの行は記録しない
    ]
    path = tmp_path / "odd.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    log = chk.ZeroNaNLog()
    S = chk.load_survey(str(path), log)
    assert S["C"][("A", 2021)] == 0.0 and math.isnan(S["E"][("A", 2022)]) and math.isinf(S["POP"][("A", 2023)])
    assert ("A", 2024) not in S["BM"] and "A" not in S["cur"]               # 空欄の行は使わない
    assert [r["value"] for r in S["staple"]] == ["0", "1.5"]                 # ゼロは残り、空欄は残らない
    assert dict(log.count) == {
        ("load", "household_consumption_total_lcu", "ZERO"): 1,
        ("load", "engel_share_food", "NaN"): 1,
        ("load", "population_total", "INF"): 1,
        ("load", "bigmac_local_price", "BLANK"): 1,
        ("load", "staple_price", "ZERO"): 1,
        ("load", "staple_price", "BLANK"): 1,
    }
    text = "\n".join(log.lines("load"))
    assert "household_consumption_total_lcu ZERO x1  e.g. A 2021" in text and "[zero/NaN log] load: none" not in text


def test_log_says_none_when_nothing_happened_and_does_not_change_the_numbers(toy):
    log = chk.ZeroNaNLog()
    assert chk.load_survey(str(toy), log) == chk.load_survey(str(toy))      # ログを付けても読み込みの結果は同じ
    assert log.lines("load") == ["[zero/NaN log] load: none"]
    assert log.lines("compute") == ["[zero/NaN log] compute: none"]


def test_main_prints_the_log_for_load_and_compute(toy, capsys):
    assert chk.main([str(toy), "--prefix", "staple_price:rice", "--boot", "50"]) == 0
    out = capsys.readouterr().out
    assert "[zero/NaN log] load: none" in out
    assert "[zero/NaN log] compute: fit ZERO x1  e.g. p_gamma_ge_1" in out   # 計算結果の 0（確率が 0）も出る
    assert out.index("[zero/NaN log] load") < out.index("panel rows")        # 読み込みのログは先に出る


def _fake_result():
    panel = [dict(country="A", year=2021, price=1.0, bigmac=2.0, E=0.2, C_pc=3.0, b=0.5, M=1.5, k=0.5)]
    res = dict(a=1.0, beta=0.5, gamma=0.5, r2=0.9, corr_E_M=0.1, p_gamma_ge_1=0.2,
               sd={"log_b": (1.0, 1.0, 1.0)}, ci={"beta": (0.1, 0.9), "gamma": (0.1, 0.9)},
               by_year={2021: dict(beta=0.5, gamma=0.5, r2=0.9)}, draws=10)
    return panel, res


def test_computed_zero_nan_and_dropped_bootstrap_draws_are_logged():
    panel, res = _fake_result()
    log = chk.ZeroNaNLog()
    chk.log_computed(log, panel, res, 10)
    assert log.lines("compute") == ["[zero/NaN log] compute: none"]
    panel[0]["b"] = 0.0
    res["r2"] = float("nan")
    res["ci"]["gamma"] = (float("-inf"), 0.9)
    res["draws"] = 7
    log = chk.ZeroNaNLog()
    chk.log_computed(log, panel, res, 10)
    assert dict(log.count) == {
        ("compute", "panel.b", "ZERO"): 1,
        ("compute", "fit", "NaN"): 1,
        ("compute", "ci.gamma", "INF"): 1,
        ("compute", "bootstrap", "DROPPED"): 1,
    }
    assert "3 of 10 draws failed" in "\n".join(log.lines("compute"))


def test_bigmac_ratio_with_a_zero_year_is_skipped_and_logged_not_silent():
    S = dict(BM={("A", 2021): 0.0, ("A", 2025): 2.0, ("B", 2021): 1.0, ("B", 2025): 2.0})
    log = chk.ZeroNaNLog()
    assert chk.bigmac_ratio(S, "A", log=log) is None                          # 以前と同じく比は作らない
    assert chk.bigmac_ratio(S, "B", log=log) == 2.0
    assert chk.bigmac_ratio(S, "NOWHERE", log=log) is None                    # 欠けはゼロではないので記録しない
    assert dict(log.count) == {("compute", "bigmac_ratio", "SKIPPED"): 1}
    assert "A (2021: 0, 2025: 2)" in "\n".join(log.lines("compute"))


# ---- 使えない入力（0・NaN・inf）は、計算に渡す前に外して記録する。止まらない -------------------------

def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    return path


def _set(rows, country, year, variable, value, *, only_first=False):
    """(country, year, variable) の行の値を差し替えた新しい行のリスト。only_first なら最初の1行だけ。"""
    out, done = [], False
    for r in rows:
        r = list(r)
        if r[0] == country and r[2] == year and r[3] == variable and not (only_first and done):
            r[4] = value
            done = True
        out.append(r)
    return out


ANOMALIES = [
    # (名前, variable, 差し替える値, 1行だけか, compute ログの入力名, 外れる件数)
    ("staple_zero", RICE, "0", False, "input.staple_price", 12),
    ("staple_nan", RICE, "nan", False, "input.staple_price", 12),
    ("staple_inf", RICE, "inf", False, "input.staple_price", 12),
    ("staple_negative", RICE, "-3", False, "input.staple_price", 12),
    ("bigmac_both_zero", "bigmac_local_price", "0", False, "input.bigmac_local_price", 1),
    ("bigmac_one_zero", "bigmac_local_price", "0", True, "input.bigmac_local_price", 1),   # 0 と 100 の平均 50 を作らない
    ("bigmac_one_nan", "bigmac_local_price", "nan", True, "input.bigmac_local_price", 1),
    ("engel_zero", "engel_share_food", "0", False, "input.engel_share_food", 1),
    ("engel_nan", "engel_share_food", "nan", False, "input.engel_share_food", 1),
    ("consumption_zero", "household_consumption_total_lcu", "0", False, "input.household_consumption_total_lcu", 1),
    ("consumption_nan", "household_consumption_total_lcu", "nan", False, "input.household_consumption_total_lcu", 1),
    ("consumption_inf", "household_consumption_total_lcu", "inf", False, "input.household_consumption_total_lcu", 1),
    ("population_zero", "population_total", "0", False, "input.population_total", 1),
    ("population_nan", "population_total", "nan", False, "input.population_total", 1),
    ("population_inf", "population_total", "inf", False, "input.population_total", 1),
]


@pytest.mark.parametrize("name,variable,value,only_first,logname,count", ANOMALIES, ids=[a[0] for a in ANOMALIES])
def test_cli_with_an_unusable_input_does_not_crash_and_logs_the_skip(tmp_path, capsys, name, variable, value, only_first, logname, count):
    """対象年に 0・NaN・inf・負がある。traceback で止まらず、compute ログにどれを外したかが残り、その国・年だけがパネルから消える。"""
    rows = _set(_toy_rows(), "N02", 2023, variable, value, only_first=only_first)
    path = _write(tmp_path / (name + ".csv"), rows)
    panel_out = tmp_path / "panel.csv"
    assert chk.main([str(path), "--prefix", "staple_price:rice", "--boot", "20", "--panel-out", str(panel_out)]) == 0
    out = capsys.readouterr().out
    assert "[zero/NaN log] compute: %s SKIPPED x%d" % (logname, count) in out
    assert "N02" in next(l for l in out.splitlines() if logname in l and l.startswith("[zero/NaN log] compute"))
    with open(panel_out, encoding="utf-8", newline="") as f:
        got = {(r["country"], int(r["year"])) for r in csv.DictReader(f)}
    assert ("N02", 2023) not in got and len(got) == 12 * 5 - 1 - 1              # 基準のパネル（59 行）から、この1行だけが消える
    assert {("N02", y) for y in (2021, 2022, 2024, 2025)} <= got


def test_one_unusable_month_is_skipped_and_the_year_stays(tmp_path, capsys):
    """主食の価格の1か月だけが 0 なら、その月を外す。残り11か月で年は成り立ち、平均は 0 に引かれない。"""
    rows = _set(_toy_rows(), "N02", 2023, RICE, "0", only_first=True)
    path = _write(tmp_path / "one_month.csv", rows)
    log = chk.ZeroNaNLog()
    panel, dropped = chk.build_panel(chk.load_survey(str(path)), "staple_price:rice", log=log)
    assert dict(log.count) == {("compute", "input.staple_price", "SKIPPED"): 1}
    base, _ = chk.build_panel(chk.load_survey(str(_write(tmp_path / "base.csv", _toy_rows()))), "staple_price:rice")
    pick = lambda p: next(r["price"] for r in p if r["country"] == "N02" and r["year"] == 2023)
    assert pick(panel) == pytest.approx(pick(base)) and len(panel) == len(base)


def test_anomalies_outside_the_target_years_or_other_staples_are_not_reported_as_skipped(tmp_path):
    rows = _toy_rows()
    rows.append(_row("N02", "2010-01-01", "household_consumption_total_lcu", 0.0, "X02"))       # 対象年の外
    rows.append(_row("N02", "2023-01-01", "staple_price:wheat", 0.0, "X02 per kg"))               # 別の品目
    rows.append(_row("N02", "2023-01-01", RICE, 0.0, "X02 per 5 kg"))                              # 使わない単位
    path = _write(tmp_path / "unused.csv", rows)
    log = chk.ZeroNaNLog()
    chk.build_panel(chk.load_survey(str(path)), "staple_price:rice", log=log)
    assert log.lines("compute") == ["[zero/NaN log] compute: none"]


def test_precheck_twice_logs_nothing_new_and_keeps_the_input_untouched(tmp_path):
    rows = _set(_set(_toy_rows(), "N02", 2023, "bigmac_local_price", "0", only_first=True), "N03", 2022, RICE, "nan")
    S = chk.load_survey(str(_write(tmp_path / "twice.csv", rows)))
    before = {k: (dict(v) if isinstance(v, dict) else list(v)) for k, v in S.items()}
    log = chk.ZeroNaNLog()
    once = chk.precheck(S, log, prefix="staple_price:rice")
    n = dict(log.count)
    assert n == {("compute", "input.bigmac_local_price", "SKIPPED"): 1, ("compute", "input.staple_price", "SKIPPED"): 12}
    chk.precheck(once, log, prefix="staple_price:rice")
    assert dict(log.count) == n                                   # 2回目は何も重ねない
    assert S == before and ("N02", 2023) in S["BM"]               # 渡した S は変えない（0 と 0.0 の平均は元のまま残っている）


def test_the_inflation_exclusion_does_not_use_a_big_mac_year_with_an_unusable_point(tmp_path, capsys):
    """INF 国の2021年のビッグマックの1点が 0 → 平均（約半分）で比を作って除外しない。その年を使わず、比は作らず、除外もしない。"""
    rows = _set(_toy_rows(), "INF", 2021, "bigmac_local_price", "0", only_first=True)
    path = _write(tmp_path / "inf_zero.csv", rows)
    panel_out = tmp_path / "panel.csv"
    assert chk.main([str(path), "--prefix", "staple_price:rice", "--boot", "10",
                     "--exclude-inflation", "2.0", "--panel-out", str(panel_out)]) == 0
    out = capsys.readouterr().out
    assert "excluded (Big Mac ratio >= threshold): []" in out
    assert "input.bigmac_local_price SKIPPED x1  e.g. INF 2021" in out
    with open(panel_out, encoding="utf-8", newline="") as f:
        got = {(r["country"], int(r["year"])) for r in csv.DictReader(f)}
    assert ("INF", 2021) not in got and {("INF", y) for y in (2022, 2023, 2024, 2025)} <= got


def test_a_row_whose_division_underflows_is_skipped_and_logged_not_passed_to_the_fit(tmp_path, capsys):
    """入力はどれも 0 より大きい有限の数でも、1人あたり消費 = 消費 / 人口 が 0 に潰れる行は、対数・回帰に渡さない。"""
    rows = _set(_toy_rows(), "N02", 2023, "household_consumption_total_lcu", "1e-320")
    path = _write(tmp_path / "underflow.csv", rows)
    log = chk.ZeroNaNLog()
    panel, dropped = chk.build_panel(chk.load_survey(str(path)), "staple_price:rice", log=log)
    assert ("N02", 2023) not in {(r["country"], r["year"]) for r in panel} and len(panel) == 12 * 5 - 1 - 1
    assert dropped["unusable_derived:N02"] == 1 and dict(log.count) == {("compute", "panel.C_pc", "SKIPPED"): 1}
    assert chk.main([str(path), "--prefix", "staple_price:rice", "--boot", "10"]) == 0


def test_all_input_unusable_gives_the_empty_panel_exit_with_the_log(tmp_path, capsys):
    rows = [_set([r], "N00", r[2], r[3], "0")[0] if r[3] == RICE else r for r in _toy_rows() if r[0] == "N00"]
    path = _write(tmp_path / "all_zero.csv", rows)
    assert chk.main([str(path), "--prefix", "staple_price:rice", "--boot", "10"]) == 66
    cap = capsys.readouterr()
    assert "[zero/NaN log] compute: input.staple_price SKIPPED x60" in cap.out and "empty panel" in cap.err


def test_when_the_fit_cannot_be_computed_the_cli_prints_the_log_and_exits_65(toy, monkeypatch, capsys):
    def boom(panel, boot=0, seed=0):
        raise np.linalg.LinAlgError("SVD did not converge")
    monkeypatch.setattr(chk, "analyze", boom)
    assert chk.main([str(toy), "--prefix", "staple_price:rice", "--boot", "10"]) == 65
    cap = capsys.readouterr()
    assert "[zero/NaN log] compute: none" in cap.out and "cannot compute: LinAlgError" in cap.err


def test_no_bootstrap_draw_succeeding_is_logged_not_an_index_error(toy, monkeypatch, capsys):
    real, calls = chk._fit, {"n": 0}

    def flaky(X, y):
        calls["n"] += 1
        if 2 <= calls["n"] <= 11:                      # 点推定（1回目）と年ごとの当てはめは通し、ブートストラップの10回だけ失敗させる
            raise np.linalg.LinAlgError("x")
        return real(X, y)
    monkeypatch.setattr(chk, "_fit", flaky)
    assert chk.main([str(toy), "--prefix", "staple_price:rice", "--boot", "10"]) == 0
    out = capsys.readouterr().out
    assert "compute: bootstrap DROPPED x1  e.g. 10 of 10 draws failed" in out
    assert "compute: ci.gamma NaN x2  e.g. lo, hi" in out and "compute: fit NaN x1  e.g. p_gamma_ge_1" in out


# ---- 系列の識別: 別の市場・別の出どころは、月をまたいで混ぜない ----------------------------------

def _srow(country, date, value, unit, source="test", note=""):
    return [country, date, int(date[:4]), RICE, "%.12g" % value, unit, source, note, ""]


def _mini(years, staple):
    """国 A（通貨 AAA）が1つだけのCSV行。ビッグマックは2点、E・C・人口は固定。staple は主食の行のリスト。"""
    rows = []
    for y in years:
        rows += [_row("A", "%d-01-01" % y, "engel_share_food", 20.0, "percent"),
                 _row("A", "%d-01-01" % y, "household_consumption_total_lcu", 5.0e9, "AAA"),
                 _row("A", "%d-01-01" % y, "population_total", POP, "persons"),
                 _row("A", "%d-01-01" % y, "bigmac_local_price", 1.98, "AAA"),
                 _row("A", "%d-07-01" % y, "bigmac_local_price", 2.02, "AAA")]
    return rows + staple


@pytest.mark.parametrize("a,b", [(("test", "market=X"), ("test", "market=Y")),          # note（市場）が違う
                                 (("src1", "market=X"), ("src2", "market=X"))])         # source（出どころ）が違う
def test_two_three_month_series_are_not_added_up_to_six_months(tmp_path, a, b):
    staple = []
    for y in (2021, 2022):
        staple += [_srow("A", "%d-%02d-01" % (y, m), 10.0, "AAA per kg", *a) for m in (1, 2, 3)]
        staple += [_srow("A", "%d-%02d-01" % (y, m), 30.0, "AAA per kg", *b) for m in (4, 5, 6)]
    path = _write(tmp_path / "split.csv", _mini((2021, 2022), staple))
    panel, dropped = chk.build_panel(chk.load_survey(str(path)), "staple_price:rice")
    assert panel == []                                # どちらの系列も3か月。足して6か月にして平均 20 を作らない


def test_same_months_in_two_markets_are_not_averaged_and_the_pick_is_reported(tmp_path):
    staple = []
    for y in (2021, 2022, 2023):
        for m in range(1, 13):
            staple.append(_srow("A", "%d-%02d-01" % (y, m), 10.0, "AAA per kg", note="market=X"))
            staple.append(_srow("A", "%d-%02d-01" % (y, m), 30.0, "AAA per kg", note="market=Y"))
    path = _write(tmp_path / "two_markets.csv", _mini((2021, 2022, 2023), staple))
    panel, dropped = chk.build_panel(chk.load_survey(str(path)), "staple_price:rice")
    assert [r["price"] for r in panel] == [30.0, 30.0, 30.0]                 # 平均 20 ではなく、1系列の値
    assert dropped["other_series_not_used"] == 1
    assert dropped["series_tie_broken_by_text:A"] == 1                       # 年数・行数が同じなので、文字列の順で選んだ（記録に出る）


def test_the_series_with_more_years_wins_over_text_order(tmp_path):
    staple = []
    for y in (2021, 2022, 2023):
        for m in range(1, 13):
            staple.append(_srow("A", "%d-%02d-01" % (y, m), 10.0, "AAA per kg", note="market=X"))
            if y != 2023:
                staple.append(_srow("A", "%d-%02d-01" % (y, m), 30.0, "AAA per kg", note="market=Y"))
    path = _write(tmp_path / "more_years.csv", _mini((2021, 2022, 2023), staple))
    panel, dropped = chk.build_panel(chk.load_survey(str(path)), "staple_price:rice")
    assert [r["price"] for r in panel] == [10.0, 10.0, 10.0]
    assert "series_tie_broken_by_text:A" not in dropped


def test_a_duplicated_date_in_one_series_counts_as_one_month(tmp_path):
    staple = [_srow("A", "2021-%02d-01" % m, 10.0, "AAA per kg") for m in range(1, 7)]
    staple.append(_srow("A", "2021-06-01", 40.0, "AAA per kg"))               # 6月が2行（10 と 40）→ 6月は 25 の1か月
    path = _write(tmp_path / "dup.csv", _mini((2021,), staple))
    panel, _ = chk.build_panel(chk.load_survey(str(path)), "staple_price:rice")
    assert [r["price"] for r in panel] == [pytest.approx((5 * 10.0 + 25.0) / 6)]
    staple5 = [_srow("A", "2021-%02d-01" % m, 10.0, "AAA per kg") for m in range(1, 6)] + [_srow("A", "2021-05-01", 10.0, "AAA per kg")]
    path = _write(tmp_path / "dup5.csv", _mini((2021,), staple5))
    assert chk.build_panel(chk.load_survey(str(path)), "staple_price:rice")[0] == []      # 5日付 + 重複 = 6行でも5か月


# ---- synthetic_staples --------------------------------------------------------------

def test_scaffold_uses_real_covariates_only_with_both_bigmac_points(toy):
    sc = syn.scaffold(str(toy))
    keys = {(r["country"], r["year"]) for r in sc}
    assert len(sc) == 15 * 5 - 1 and ("N01", 2021) not in keys
    r = next(r for r in sc if r["country"] == "N00" and r["year"] == 2021)
    assert r["P"] == pytest.approx(2.0, rel=1e-9) and r["M"] == pytest.approx(r["Cpc"] / r["P"])


def _pattern(pid):
    return next((i, p) for i, p in enumerate(syn.PATTERNS) if p[0] == pid)


def test_generate_is_deterministic_and_constant_pattern_is_exact(toy):
    sc = syn.scaffold(str(toy))
    i1, p1 = _pattern("S1")
    assert np.array_equal(syn.generate(sc, i1, p1), syn.generate(sc, i1, p1))
    i8, p8 = _pattern("S8")
    assert np.allclose(syn.generate(sc, i8, p8), syn.B0, rtol=1e-12, atol=0)


def test_generate_step_discontinuity_triples_above_median(toy):
    sc = syn.scaffold(str(toy))
    b = syn.generate(sc, 0, ("T", "step", 0.0, 0.0, 0.0, 3.0))
    M = np.array([r["M"] for r in sc])
    assert np.allclose(b[M <= np.median(M)], syn.B0) and np.allclose(b[M > np.median(M)], 3 * syn.B0)


def test_written_rows_are_labelled_synthetic(toy, tmp_path):
    sc = syn.scaffold(str(toy))
    out = tmp_path / "syn.csv"
    syn.write_vertical(sc, str(out))
    with open(out, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(syn.PATTERNS) * len(sc)
    assert list(rows[0].keys()) == HEADER
    assert all(r["variable"].startswith("synthetic_staple:") and r["unit"].endswith("(synthetic)")
               and r["source"].startswith("SYNTHETIC") and r["estimated_value"] == "" for r in rows)
    s8 = [r for r in rows if r["variable"].startswith("synthetic_staple:S8_")]
    for r, s in zip(s8, sc):                                       # 価格 = b * ビッグマック価格
        assert float(r["value"]) == pytest.approx(syn.B0 * s["P"], rel=1e-5)


def test_check_recovers_known_truth(toy):
    sc = syn.scaffold(str(toy))
    rows = {r["id"]: r for r in syn.check(sc, boot=200, verbose=False)}
    assert set(rows) == {p[0] for p in syn.PATTERNS}
    assert rows["S8"]["gamma_hat"] == pytest.approx(0.0, abs=1e-9) and math.isnan(rows["S8"]["r2"])
    for pid in ("S1", "S3", "S4", "S5"):
        assert rows[pid]["gamma_hat"] == pytest.approx(rows[pid]["gamma_true"], abs=0.25)
    # 家計に連動(S3)なら価格/(E*C_pc) のばらつき(log k)は小さく、ビッグマックだけに連動(S2)なら大きい
    assert rows["S3"]["sd_log_k"] < rows["S3"]["sd_log_b"]
    assert rows["S2"]["sd_log_k"] > rows["S2"]["sd_log_b"]


def test_calibrate_smoke(toy):
    sc = syn.scaffold(str(toy))
    out = syn.calibrate(sc, clusters=(5,), reps=3, boot=20, verbose=False)
    assert set(out) == {(si, 5) for si in range(len(syn.CAL_SCENARIOS))}
    assert all(0.0 <= v <= 1.0 for v in out.values())


def test_main_empty_scaffold_exits_66(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text(",".join(HEADER) + "\n", encoding="utf-8")
    assert syn.main([str(empty), "--out", str(tmp_path / "x.csv")]) == 66


def test_main_writes_output(toy, tmp_path):
    out = tmp_path / "syn.csv"
    assert syn.main([str(toy), "--out", str(out)]) == 0 and out.exists()


SURVEY = ROOT / syn.DEFAULT_CSV
COMMITTED = ROOT / syn.DEFAULT_OUT


@pytest.mark.skipif(not (SURVEY.exists() and COMMITTED.exists()), reason="survey data or committed synthetic CSV absent")
def test_committed_synthetic_csv_matches_the_generation_rule(tmp_path):
    out = tmp_path / "regen.csv"
    assert syn.main([str(SURVEY), "--out", str(out)]) == 0

    def read(p):
        with open(p, encoding="utf-8", newline="") as f:
            return list(csv.reader(f))

    assert read(out) == read(COMMITTED)
