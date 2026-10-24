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
