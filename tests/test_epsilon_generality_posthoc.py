"""research/epsilon-generality/posthoc_boundary_forms.py の確認。

SYNTHETIC: 小さな合成の入力で、周期が変わった単位の数え方・単式の誤差の2乗和・除いたときの係数のずれ・書き出しを確かめる。
野球の周期の数だけ、リポジトリに保存済みの行（wave_eps_rows_1e-06.jsonl）と照らす。結論には使わない。
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
spec = importlib.util.spec_from_file_location("posthoc_boundary_forms", DIR / "posthoc_boundary_forms.py")
ph = importlib.util.module_from_spec(spec)
sys.modules["posthoc_boundary_forms"] = ph
spec.loader.exec_module(ph)
gen = ph.gen
sa, trial = gen.load_modules(ROOT)
K3, K6, K9 = (gen.ekey(e) for e in gen.EPS)


def er(period=1.0, coef=1.0):
    return {"decay": 0.0, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": False}


def row(boundary=True, p3=1.0, p6=1.0, p9=1.0, c3=1.0, c6=1.0, c9=1.0):
    return {"boundary": boundary, K3: er(p3, c3), K6: er(p6, c6), K9: er(p9, c9)}


def test_changed_period_lists_only_boundary_units_whose_period_differs_from_the_1e9_one():
    rows = [row(), row(p3=2.0), row(p6=0.5), row(False, p3=2.0), row(p3=2.0, p6=2.0)]
    assert ph.changed_period(rows) == {K3: [1, 4], K6: [2, 4]}
    assert ph.changed_period([row()]) == {K3: [], K6: []}


def test_corrected_c2_drops_the_skipped_units_and_divides_by_the_1e9_coefficient():
    rows = [row(), row(c3=1.5, c6=1.0001), row(c3=1.002, c6=1.0), row(False, c3=9.0), row(c3=None)]
    rows[4][K3]["coefficient"] = None
    full = ph.corrected_c2(rows, set())
    assert full[K3]["n"] == 3 and full[K3]["max"] == pytest.approx(0.5) and full[K6]["max"] == pytest.approx(1e-4)
    skipped = ph.corrected_c2(rows, {1})
    assert skipped[K3] == {"max": pytest.approx(0.002), "n": 2}
    assert ph.corrected_c2([], set())[K3] == {"max": None, "n": 0}
    two = ph.corrected_c2([row(c3=1.5, c9=2.0)], set())
    assert two[K3]["max"] == pytest.approx(0.25)                    # 基準の係数（2.0）で割る


def wave_ys(period=1.0, n=24):
    xs = [i / (n - 1) for i in range(n)]
    return gen.normalize([3.0 + 2.0 * math.cos(2 * math.pi * x / period + 0.7) for x in xs])[1]


def test_sse_of_form_is_near_zero_for_the_true_period_and_large_for_another_and_checks_the_grid():
    ys = wave_ys(1.0)
    xs = [i / 23 for i in range(24)]
    assert ph.sse_of_form(sa, trial, xs, ys, 0.0, 1.0) < 1e-9
    assert ph.sse_of_form(sa, trial, xs, ys, 1e-6, 1.0) < 1e-6
    assert ph.sse_of_form(sa, trial, xs, ys, 0.0, 2.0) > 1.0
    assert ph.sse_of_form(sa, trial, xs, ys, 1e-3, 2.0) > 1.0
    with pytest.raises(ValueError, match="格子に周期 0.6"):
        ph.sse_of_form(sa, trial, xs, ys, 0.0, 0.6)


def test_tie_table_has_one_line_per_epsilon_including_zero_and_the_difference_is_second_minus_first():
    t = ph.tie_table(sa, trial, wave_ys(1.0), 1.0, 2.0)
    assert [x["eps"] for x in t] == [0.0, 1e-3, 1e-6, 1e-9]
    for x in t:
        assert x["diff"] == x["sse_other_period"] - x["sse_small_eps_period"] and x["diff"] > 1.0
    assert t[0]["sse_small_eps_period"] < 1e-9 and t[3]["sse_small_eps_period"] < 1e-6        # x は窓の長さで [0, 1] を等分した点
    flipped = ph.tie_table(sa, trial, wave_ys(1.0), 2.0, 1.0)
    assert all(x["diff"] < -1.0 for x in flipped)


def test_baseball_periods_match_the_saved_rows():
    b = ph.baseball_periods(ROOT)
    assert b == {"units": 168, "boundary": 24, "periods": {0.75: 3, 1.0: 4, 2.0: 17}}


def small_csv(tmp_path):
    rows = []
    for j in range(3):
        vals = [3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5) for i in range(48)]
        for i, v in enumerate(vals):
            y, m = 2020 + i // 12, i % 12 + 1
            rows.append({"country": "AAA", "date": f"{y}-{m:02d}-01", "year": str(y), "variable": f"staple_price:c{j}", "value": str(v),
                         "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""})
    import csv
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return p


def test_analyse_finds_nothing_in_a_clean_series_and_builds_the_table_for_a_forced_unit(tmp_path, monkeypatch):
    series = gen.read_series(small_csv(tmp_path))
    res = ph.analyse(sa, trial, series, ROOT)
    assert res["units"] == [] and set(res["by_n"]) == {"12", "24", "48"} and res["baseball"]["boundary"] == 24
    assert res["by_n"]["24"]["changed_period"] == {K3: 0, K6: 0}
    monkeypatch.setattr(ph, "changed_period", lambda rows: {K3: [0], K6: []})
    forced = ph.analyse(sa, trial, series, ROOT)
    (u,) = [x for x in forced["units"] if x["n"] == 12]
    assert (u["eps"], u["series_index"], u["start"], u["unit"]) == (1e-3, 0, "2020-01", "USD per kg") and len(u["table"]) == 4
    assert forced["by_n"]["12"]["changed_period"] == {K3: 1, K6: 0}
    seen = []
    real_c2 = ph.corrected_c2
    monkeypatch.setattr(ph, "corrected_c2", lambda rows, skip: seen.append(set(skip)) or real_c2(rows, skip))
    ph.analyse(sa, trial, series, ROOT)
    assert seen == [{0}, {0}, {0}]                                           # 周期が変わった単位は、窓の長さごとに除いて測る


def test_analyse_stops_when_windows_and_rows_do_not_line_up(tmp_path, monkeypatch):
    series = gen.read_series(small_csv(tmp_path))
    real = gen.compute

    def short(*a, **k):
        r = real(*a, **k)
        r["rows"]["real"]["12"] = r["rows"]["real"]["12"][:-1]
        return r
    monkeypatch.setattr(gen, "compute", short)
    with pytest.raises(ValueError, match="窓の数が合わない"):
        ph.analyse(sa, trial, series, ROOT)
    monkeypatch.setattr(gen, "compute", real)
    monkeypatch.setattr(ph, "changed_period", lambda rows: {K3: [1], K6: []})

    def swapped(*a, **k):
        r = real(*a, **k)
        rows = r["rows"]["real"]["12"]
        rows[1]["series_index"] = 99
        return r
    monkeypatch.setattr(gen, "compute", swapped)
    with pytest.raises(ValueError, match="窓と行が対応しない"):
        ph.analyse(sa, trial, series, ROOT)


def test_render_and_cli_write_json_and_markdown_and_are_reproducible(tmp_path, monkeypatch):
    csv_path = small_csv(tmp_path)
    o1, o2 = tmp_path / "o1", tmp_path / "o2"
    for o in (o1, o2):
        assert ph.main(["--csv", str(csv_path), "--outdir", str(o), "--repo", str(ROOT)]) == 0
    for n in ("posthoc_boundary_forms.json", "posthoc_boundary_forms.md"):
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes()
    md = (o1 / "posthoc_boundary_forms.md").read_text(encoding="utf-8")
    assert "登録した基準の外" in md and "なし。" in md and "24 単位" not in md and "3: " not in md
    assert json.loads((o1 / "posthoc_boundary_forms.json").read_text(encoding="utf-8"))["baseball"]["periods"]["2.0"] == 17
    monkeypatch.setattr(ph, "changed_period", lambda rows: {K3: [0], K6: []})
    o3 = tmp_path / "o3"
    assert ph.main(["--csv", str(csv_path), "--outdir", str(o3), "--repo", str(ROOT)]) == 0
    md3 = (o3 / "posthoc_boundary_forms.md").read_text(encoding="utf-8")
    assert "### 12 か月・ε=0.001: FPMA AAA staple_price:c0（USD per kg、系列 0）2020-01 から" in md3 and "| 0 |" in md3 and "1e-12" in md3


# ---- 境界でない単位で式が変わった場合 ------------------------------------------------------------------------------------
def nrow(boundary, d0, p0, e3, e6=None):
    r = {"boundary": boundary, "decay": d0, "period": p0}
    r[K3] = {"decay": e3[0], "period": e3[1]}
    r[K6] = {"decay": (e6 or (d0, p0))[0], "period": (e6 or (d0, p0))[1]}
    r[K9] = {"decay": d0, "period": p0}
    return r


def test_nonboundary_changes_counts_decay_or_period_changes_of_non_boundary_units_only():
    rows = [nrow(False, 0.5, 2.0, (0.001, 2.0)), nrow(False, 0.5, 2.0, (0.5, 1.0)), nrow(False, 0.5, 2.0, (0.5, 2.0)),
            nrow(True, 0.0, 1.0, (0.001, 1.0)), nrow(False, 1.0, None, (1.0, None), e6=(1.0, 2.0))]
    assert ph.nonboundary_changes(rows) == {K3: [0, 1], K6: [4]}
    assert ph.nonboundary_changes([]) == {K3: [], K6: []}


def damped_ys(lam=0.5, period=2.0, n=24):
    xs = [i / (n - 1) for i in range(n)]
    return gen.normalize([3.0 + 2.0 * math.exp(-lam * x) * math.cos(2 * math.pi * x / period + 0.4) for x in xs])[1]


def test_sse_of_form_can_pick_a_damped_form_by_its_decay():
    ys = damped_ys()
    xs = [i / 23 for i in range(24)]
    assert ph.sse_of_form(sa, trial, xs, ys, 1e-3, 2.0, lam=0.5) < 1e-9
    assert ph.sse_of_form(sa, trial, xs, ys, 1e-3, 2.0, lam=3.0) > 0.01
    with pytest.raises(ValueError, match="格子に周期 2.0・減衰 0.7"):
        ph.sse_of_form(sa, trial, xs, ys, 1e-3, 2.0, lam=0.7)
    with pytest.raises(ValueError, match="減衰 0.0 の式が 0 個"):
        ph.sse_of_form(sa, trial, xs, ys, 1e-3, 2.0, lam=0.0)             # ε の格子には減衰 0 の式がない


def test_form_table_lists_the_current_form_the_undamped_one_and_each_epsilon_wave():
    t = ph.form_table(sa, trial, damped_ys(), (0.5, 2.0), 1e-3, 2.0)
    assert [x["label"] for x in t] == ["今のコードで選ばれた式", "同じ周期の減衰しない波（減衰 0）", "同じ周期の ε の波（ε=0.001）",
                                       "同じ周期の ε の波（ε=1e-06）", "同じ周期の ε の波（ε=1e-09）"]
    assert [(x["decay"], x["period"]) for x in t] == [(0.5, 2.0), (0.0, 2.0), (1e-3, 2.0), (1e-6, 2.0), (1e-9, 2.0)]
    assert t[0]["sse"] < 1e-9 and all(x["sse"] > 1e-3 for x in t[1:])
    d3, d6, d9 = (abs(t[i]["sse"] - t[1]["sse"]) for i in (2, 3, 4))          # ε が小さいほど、減衰しない波の誤差に近づく（ε にほぼ比例）
    assert d3 > 1e-7 and 0 < d6 < 2e-3 * d3 and d9 < 2e-3 * d6


def test_analyse_builds_the_table_for_a_non_boundary_unit_whose_form_changed(tmp_path, monkeypatch):
    series = gen.read_series(small_csv(tmp_path))
    real = gen.compute
    seen = {}

    def forced(*a, **k):
        r = real(*a, **k)
        row0 = r["rows"]["real"]["12"][0]
        seen["eps_period"] = row0[K3]["period"]
        seen["p"] = 0.25 if row0[K3]["period"] != 0.25 else 0.5
        row0["boundary"], row0["decay"], row0["period"] = False, 0.5, seen["p"]          # 今のコードは減衰 0.5 の式を選んだことにする
        row0[K6] = {"decay": 0.5, "period": seen["p"]}                                  # ε=1e-6 では変わらなかったことにする
        return r
    monkeypatch.setattr(gen, "compute", forced)
    res = ph.analyse(sa, trial, series, ROOT)
    (u,) = res["nonboundary_units"]
    p, ep = seen["p"], seen["eps_period"]
    assert (u["n"], u["eps"], u["unmodified"], u["epsilon_form"]) == (12, 1e-3, [0.5, p], [1e-3, ep])
    assert [x["period"] for x in u["table"]] == [p, ep, ep, ep, ep] and len(u["table"]) == 5
    assert u["series_index"] == 0 and u["start"] == "2020-01"
    assert res["by_n"]["12"]["nonboundary_changed"] == {K3: 1, K6: 0} and res["by_n"]["24"]["nonboundary_changed"] == {K3: 0, K6: 0}
    md = ph.render(res)
    assert "12 か月: 1 / 0、24 か月: 0 / 0、48 か月: 0 / 0" in md and "今のコードの式は 減衰 0.5・周期 " + format(p, "g") + "、" in md
    assert "同じ周期の減衰しない波（減衰 0）" in md and "ε の格子では 減衰 0.001・周期 " + format(ep, "g") in md
    # 窓と行が対応しないときは止まる
    def swapped(*a, **k):
        r = forced(*a, **k)
        r["rows"]["real"]["12"][0]["series_index"] = 99
        return r
    monkeypatch.setattr(gen, "compute", swapped)
    with pytest.raises(ValueError, match="窓と行が対応しない"):
        ph.analyse(sa, trial, series, ROOT)


def test_render_without_changes_says_none_in_both_sections(tmp_path):
    res = ph.analyse(sa, trial, gen.read_series(small_csv(tmp_path)), ROOT)
    assert ph.render(res).count("なし。") == 2
