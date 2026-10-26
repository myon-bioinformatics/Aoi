"""research/epsilon-generality/eps_generality.py の「乱数の ε と倍率」の確認。

SYNTHETIC: 合成の入力で、乱数の選び方（A×10^-N の形・範囲・種で決まること）、基準値のつなぎ方、乱数の ε を足したときの判定と書き出しを確かめる。
結論には使わない。

乱数の種: 環境変数 EPS_COEF_SEED（省略すると実行ごとに変わる）。失敗したときは、メッセージの EPS_COEF_SEED=... を渡せば同じ値で再現する。
どの種でも成り立つ性質だけを確かめている（種によって通ったり落ちたりする確認は置かない）。
"""
import importlib.util
import json
import math
import os
import secrets
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
spec = importlib.util.spec_from_file_location("eps_generality", DIR / "eps_generality.py")
gen = importlib.util.module_from_spec(spec)
sys.modules["eps_generality"] = gen
spec.loader.exec_module(gen)
sa, trial = gen.load_modules(ROOT)

COEF_SEED = os.environ.get("EPS_COEF_SEED") or str(secrets.randbelow(10**9))
WHY = f"EPS_COEF_SEED={COEF_SEED}"
SEEDS = (COEF_SEED, "1", "2", "20261026")          # 乱数の種（先頭だけ実行ごとに変わる）


# ---- 乱数の選び方 ----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("seed", SEEDS)
def test_random_eps_are_A_times_power_of_ten_inside_the_registered_range(seed):
    d = gen.draw_coefficients(6, seed, "eps")
    assert len(d) == 6 and len({x["value"] for x in d}) == 6, WHY
    for x in d:
        assert 1.1 <= x["a"] <= 9.9 and abs(x["a"] * 10 - round(x["a"] * 10)) < 1e-9, WHY            # A は小数 1 桁（1.0 は選ばない）
        assert x["exp"] in range(-8, -3) and x["value"] == float(f"{x['a']}e{x['exp']}"), WHY
        assert gen.REF_EPS < x["value"] < 1e-3 and x["value"] not in gen.EPS, WHY
    assert [x["value"] for x in d] == sorted((x["value"] for x in d), reverse=True), WHY


@pytest.mark.parametrize("seed", SEEDS)
def test_random_scales_are_A_times_power_of_ten_up_to_one(seed):
    d = gen.draw_coefficients(8, seed, "scale")
    assert len(d) == 8 and len({x["value"] for x in d}) == 8, WHY
    for x in d:
        assert 1.1 <= x["a"] <= 9.9 and x["exp"] in range(-8, 1) and x["value"] == float(f"{x['a']}e{x['exp']}"), WHY
        assert 1.1e-8 <= x["value"] <= 9.9, WHY


def test_draws_depend_only_on_the_seed_and_the_kind():
    a = gen.draw_coefficients(6, 7, "eps")
    assert a == gen.draw_coefficients(6, 7, "eps") and a != gen.draw_coefficients(6, 8, "eps")
    assert gen.draw_coefficients(6, 7, "eps") != gen.draw_coefficients(6, 7, "scale")
    assert gen.draw_coefficients(6, "7", "eps") == a                          # 整数でも文字列でも同じ種
    assert gen.draw_coefficients(0, 7, "eps") == []


def test_draws_are_not_a_grid_of_one_times_power_of_ten():
    seen_a, seen_exp = set(), set()
    for seed in range(1, 21):
        for x in gen.draw_coefficients(6, seed, "eps"):
            seen_a.add(x["a"])
            seen_exp.add(x["exp"])
    assert len(seen_a) > 40 and seen_exp == {-8, -7, -6, -5, -4}          # A が 1.0 に偏らず、指数は 3 刻みに偏らない


def test_asking_for_more_values_than_exist_stops():
    with pytest.raises(ValueError):
        gen.draw_coefficients(len(gen.RANDOM_A) * len(gen.RANDOM_EPS_N) + 1, 1, "eps")
    assert len(gen.draw_coefficients(len(gen.RANDOM_A) * len(gen.RANDOM_EPS_N), 1, "eps")) == 445


def test_labels_show_A_times_power_of_ten_and_keep_the_registered_spelling():
    assert gen.pow10_text(3.7e-5) == "3.7×10^-5" and gen.pow10_text(9.9e-4) == "9.9×10^-4" and gen.pow10_text(1.1e-8) == "1.1×10^-8"
    assert gen.pow10_text(float("4.2e0")) == "4.2×10^0"
    assert [gen.elabel(e) for e in gen.EPS] == ["0.001", "1e-06", "1e-09"] and gen.elabel(2.5e-7) == "2.5×10^-7"


# ---- 基準値のつなぎ方 --------------------------------------------------------------------------------------------------------
def test_registered_epsilons_keep_their_registered_thresholds():
    assert [gen.threshold("c1", e) for e in gen.EPS] == [0.98, 1.0, 1.0]
    assert [gen.threshold("c2", e) for e in gen.EPS[:2]] == [0.02, 1e-4]
    assert [gen.threshold("c3", e) for e in gen.EPS] == [0.02, 0.005, 0.005]


def test_thresholds_between_the_registered_points_follow_log10_eps():
    mid = 10 ** -4.5
    assert gen.threshold("c1", mid) == pytest.approx(0.99)                        # 割合の直線: 1.0 と 0.98 の中間
    assert gen.threshold("c2", mid) == pytest.approx(math.sqrt(0.02 * 1e-4))      # 値の対数の直線: 幾何平均
    assert gen.threshold("c3", mid) == pytest.approx(math.sqrt(0.02 * 0.005))
    f = (math.log10(2.5e-5) + 6) / 3
    assert gen.threshold("c2", 2.5e-5) == pytest.approx(1e-4 * (0.02 / 1e-4) ** f)
    assert gen.threshold("c3", 2.5e-5) == pytest.approx(0.005 * (0.02 / 0.005) ** f)
    assert gen.threshold("c1", 2.5e-5) == pytest.approx(1.0 + (0.98 - 1.0) * f)
    for e in (5e-7, 1.1e-8, 9.9e-7):                                              # 1e-6 以下は 1e-6 の値のまま
        assert (gen.threshold("c1", e), gen.threshold("c2", e), gen.threshold("c3", e)) == (1.0, 1e-4, 0.005)


@pytest.mark.parametrize("seed", SEEDS)
def test_thresholds_of_drawn_epsilons_lie_between_the_registered_ones_and_loosen_with_epsilon(seed):
    es = sorted(x["value"] for x in gen.draw_coefficients(20, seed, "eps"))
    for kind, lo, hi in (("c1", 0.98, 1.0), ("c2", 1e-4, 0.02), ("c3", 0.005, 0.02)):
        t = [gen.threshold(kind, e) for e in es]
        assert all(min(lo, hi) <= x <= max(lo, hi) for x in t), (kind, WHY)
        assert t == sorted(t, reverse=(kind == "c1")), (kind, WHY)               # ε が大きいほど許す幅が広い（C1 は必要な割合が下がる）


def test_thresholds_outside_the_registered_range_stop():
    for bad in (2e-3, 1e-2, 1e-10, 0.0):
        with pytest.raises(ValueError, match="（1e-9 < ε < 1e-3）の外"):
            gen.threshold("c3", bad)
    with pytest.raises(ValueError):
        gen.threshold("c2", 1e-9)                                                # 基準の ε は比べる相手で、判定しない


# ---- 判定に乱数の ε を入れる -------------------------------------------------------------------------------------------------
def er(decay, period=1.0, coef=1.0, at_start=False):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": at_start}


def unit(eps, boundary=True, overrides=None):
    u = {"decay": 0.0 if boundary else 1.0, "period": 1.0, "rmse": 0.0, "limit": None, "settle_x": None, "boundary": boundary}
    for e in eps:
        u[gen.ekey(e)] = er(e if boundary else 1.0)
    for k, v in (overrides or {}).items():
        u[k] = er(**v)
    return u


def judged(rows, eps):
    return gen.judge_real(gen.stats(rows, eps), "t", eps)


def one(v, cid, e):
    (c,) = [c for c in v if c["id"] == cid and f"ε={gen.elabel(e)} " in c["text"]]            # どの基準の文でも ε の表記のあとに空白が来る
    return c


def drawn_eps(seed=COEF_SEED, k=6):
    return gen.EPS + tuple(x["value"] for x in gen.draw_coefficients(k, seed, "eps"))


def test_every_epsilon_gets_a_row_in_each_criterion_and_clean_data_passes_all():
    eps = drawn_eps()
    v = judged([unit(eps) for _ in range(30)] + [unit(eps, False) for _ in range(30)], eps)
    assert [c["id"] for c in v].count("C1") == 9 and [c["id"] for c in v].count("C2") == 8 and [c["id"] for c in v].count("C3") == 9, WHY
    assert all(c["ok"] is True for c in v), WHY
    assert len(judged([unit(gen.EPS) for _ in range(30)] + [unit(gen.EPS, False) for _ in range(30)], gen.EPS)) == 8      # 決め打ちだけなら従来どおり 8 行


def test_c2_for_a_drawn_epsilon_is_inclusive_at_its_own_threshold_on_both_sides():
    eps = drawn_eps()
    for e in eps[3:]:
        thr = gen.threshold("c2", e)
        for sign in (1, -1):
            def case(dev):
                rows = [unit(eps) for _ in range(30)] + [unit(eps, overrides={gen.ekey(e): dict(decay=e, coef=1.0 + sign * dev), gen.ekey(1e-9): dict(decay=1e-9, coef=1.0)})]
                return one(judged(rows, eps), "C2", e)
            assert case(thr * 0.99)["ok"] is True and case(thr * 1.01)["ok"] is False, (e, sign, WHY)
        assert one(judged([unit(eps) for _ in range(30)], eps), "C2", e)["threshold"] == thr


def test_c1_for_a_drawn_epsilon_needs_the_interpolated_share_and_counts_a_lost_wave():
    eps = drawn_eps()
    for e in eps[3:]:
        need = 1.0 + (0.98 - 1.0) * min(1.0, max(0.0, (math.log10(e) + 6) / 3))          # 登録の 2 点を log10(ε) でつないだ式（threshold とは別に書いた）
        for lost in range(0, 4):
            rows = [unit(eps) for _ in range(100 - lost)] + [unit(eps, overrides={gen.ekey(e): dict(decay=1.0)}) for _ in range(lost)]
            c = one(judged(rows, eps), "C1", e)
            assert c["ok"] is (((100 - lost) / 100) >= need), (e, lost, need, WHY)
            assert c["threshold"] == pytest.approx(need), WHY


def test_c3_for_a_drawn_epsilon_counts_changed_forms_against_the_interpolated_share():
    eps = drawn_eps()
    for e in eps[3:]:
        f = min(1.0, max(0.0, (math.log10(e) + 6) / 3))
        thr = 0.005 * (0.02 / 0.005) ** f
        for changed in (0, 2, 5, 8, 20):
            rows = [unit(eps, False) for _ in range(1000 - changed)] + [unit(eps, False, overrides={gen.ekey(e): dict(decay=2.0)}) for _ in range(changed)]
            c = one(judged(rows, eps), "C3", e)
            assert c["ok"] is ((changed / 1000) <= thr), (e, changed, thr, WHY)


def test_synthetic_damped_c3_also_covers_the_drawn_epsilons():
    eps = drawn_eps(k=2)
    rows = {"damped_l1": [dict(unit(eps, False), true_amp=2.5) for _ in range(25)], "undamped_p1": [dict(unit(eps), true_amp=2.5) for _ in range(25)]}
    texts = [c["text"] for c in gen.judge_synth(rows, eps) if c["id"] == "C3"]
    assert len(texts) == 5 and any("×10^-" in t for t in texts), WHY
    assert len(gen.judge_synth(rows)) == 5                                                   # 決め打ちだけなら C5 が 2 行と C3 が 3 行


# ---- 実際の当てはめ: どの乱数の ε でも、減衰しない波は ε の波が残って係数が基準の ε と合う -----------------------------------------------
def wave(period, phi, decay=0.0):
    xs = [i / 23 for i in range(24)]
    return [3.0 + 2.0 * math.exp(-decay * x) * math.cos(2 * math.pi * x / period + phi) for x in xs]


@pytest.mark.parametrize("seed", SEEDS)
def test_fits_with_drawn_epsilons_keep_the_wave_and_the_coefficient_for_undamped_waves_and_leave_damped_ones_alone(seed):
    eps = drawn_eps(seed)
    xs = [i / 23 for i in range(24)]
    bases = gen.make_bases(sa, trial, xs, eps)
    assert list(bases) == [None, *eps]
    for period, phi in ((1.0, 0.7), (0.5, 0.3), (0.25, 1.9)):
        r = gen.fit_row(sa, bases, gen.normalize(wave(period, phi))[1], 0.5)
        assert r["boundary"], WHY
        ref = r[gen.ekey(gen.REF_EPS)]["coefficient"]
        for e in eps[3:]:
            f = r[gen.ekey(e)]
            assert f["decay"] == e and f["limit"] is not None and f["settle_x"] is not None and not f["at_start"], (e, WHY)
            assert abs(f["coefficient"] - ref) / abs(ref) <= gen.threshold("c2", e), (e, WHY)
            assert f["coefficient"] == pytest.approx(f["settle_x"] * e)                  # 位置 = 係数 / ε（ε = A×10^-N なら 位置 = (係数 / A) × 10^N）
    d = gen.fit_row(sa, bases, gen.normalize(wave(0.5, 0.3, decay=3.0))[1], 0.5)
    assert not d["boundary"]
    assert all((d[gen.ekey(e)]["decay"], d[gen.ekey(e)]["period"]) == (d["decay"], d["period"]) for e in eps[3:]), WHY


def test_scale_summary_takes_the_scales_it_is_given_and_keeps_the_default():
    xs = [i / 23 for i in range(24)]
    wins = [{"key": "k", "start": "2020-01", "values": wave(1.0, p)} for p in (0.1, 0.7)]
    bases = gen.make_bases(sa, trial, xs)
    assert list(gen.scale_summary(sa, bases, wins, (3.7e-5, 1.0))) == ["3.7e-05", "1"]
    assert list(gen.scale_summary(sa, bases, wins)) == [f"{f:g}" for f in gen.SCALES]


# ---- 書き出し ----------------------------------------------------------------------------------------------------------------
def small_csv(tmp_path):
    import csv
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = []
    for j in range(3):
        for i in range(48):
            y, m = 2020 + i // 12, i % 12 + 1
            v = 3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)
            rows.append({"country": "AAA", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": f"staple_price:c{j}", "value": str(v),
                         "unit": "USD per kg", "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""})
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def run(tmp_path, name, *flags):
    out = tmp_path / name
    assert gen.main(["--csv", str(small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT), *flags]) == 0
    return out, json.loads((out / "eps_generality.json").read_text(encoding="utf-8"))


def test_cli_adds_drawn_values_records_them_and_is_byte_reproducible(tmp_path):
    o1, r1 = run(tmp_path, "a", "--random-eps", "3", "--random-scales", "3", "--coef-seed", "11")
    o2, _ = run(tmp_path, "b", "--random-eps", "3", "--random-scales", "3", "--coef-seed", "11")
    for n in sorted(p.name for p in o1.iterdir()):
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes(), n
    rc = r1["random_coefficients"]
    assert rc == {"seed": 11, "eps": gen.draw_coefficients(3, 11, "eps"), "scales": gen.draw_coefficients(3, 11, "scale")}
    assert len(r1["criteria"]) == 3 * (6 + 5 + 6) + 2 + 6                                        # N=12,24,48 の C1・C2・C3 と、合成の C5 2 行・C3 6 行
    assert len(r1["scales"]) == len(gen.SCALES) + 3 and all(f"{x['value']:g}" in r1["scales"] for x in rc["scales"])
    units = [json.loads(x) for x in (o1 / "eps_generality_units_n24.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all(gen.ekey(x["value"]) in u for u in units for x in rc["eps"])
    md = (o1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "## 乱数で選んだ ε と倍率" in md and "種 11" in md and all(gen.pow10_text(x["value"]) in md for x in rc["eps"] + rc["scales"])
    assert "確かめられた" not in md.replace("「確かめられた」とは書かない", "")


def test_cli_without_random_flags_is_unchanged_even_when_a_seed_is_given(tmp_path):
    o0, r0 = run(tmp_path, "d")
    o1, _ = run(tmp_path, "e", "--coef-seed", "5")
    o2, _ = run(tmp_path, "f", "--random-eps", "0", "--random-scales", "0", "--coef-seed", "5")
    for n in sorted(p.name for p in o0.iterdir()):
        assert (o0 / n).read_bytes() == (o1 / n).read_bytes() == (o2 / n).read_bytes(), n
    assert "random_coefficients" not in r0 and "scales" not in r0 and len(r0["criteria"]) == 3 * 8 + 2 + 3


def test_cli_auto_seed_is_recorded_so_the_same_values_can_be_drawn_again(tmp_path):
    o1, r1 = run(tmp_path, "g", "--random-eps", "2", "--coef-seed", "auto")
    seed = r1["random_coefficients"]["seed"]
    assert isinstance(seed, int) and 0 <= seed < 10**9 and r1["random_coefficients"]["scales"] == []
    o2, _ = run(tmp_path, "h", "--random-eps", "2", "--coef-seed", str(seed))
    assert (o1 / "eps_generality.json").read_bytes() == (o2 / "eps_generality.json").read_bytes()
    assert "scales" not in r1                                                                    # 倍率を足さなければ、主食価格の回に倍率の表は出ない


def test_cli_random_scales_alone_add_the_scale_table_without_new_epsilons(tmp_path):
    _, r = run(tmp_path, "i", "--random-scales", "2", "--coef-seed", "3")
    assert len(r["criteria"]) == 3 * 8 + 2 + 3 and len(r["scales"]) == len(gen.SCALES) + 2


def test_readme_states_the_random_ranges_and_the_threshold_rule():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    for needle in ("乱数の ε と倍率の確認", "A = 1.1〜9.9", "N = 4〜8", "e = -8〜0", "log10(ε)", "--random-eps", "--coef-seed",
                   "tests/test_epsilon_generality_random.py", "EPS_COEF_SEED"):
        assert needle in text, needle
    assert (gen.RANDOM_A, gen.RANDOM_EPS_N, gen.RANDOM_SCALE_E) == (range(11, 100), range(4, 9), range(-8, 1))
