"""research/epsilon-generality/eps_range_profile.py の確認。

SYNTHETIC: 組み立てた行で、収まった単位・消えた単位・始まりで落ち着く単位の数え方、足し合わせ、すべてが収まる最大の ε、乱数の選び方の重み、
小さな合成の入力での書き出し（同じ入力なら同じバイト）を確かめる。結論には使わない。
"""
import csv
import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
spec = importlib.util.spec_from_file_location("eps_range_profile", DIR / "eps_range_profile.py")
rp = importlib.util.module_from_spec(spec)
sys.modules["eps_range_profile"] = rp
spec.loader.exec_module(rp)
gen = rp.load_gen()
REF = gen.ekey(gen.REF_EPS)


def er(decay, period=1.0, coef=1.0, at_start=False):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": at_start}


def row(boundary=True, devs=None, lost=(), start=(), ref_start=False, same=True):
    """格子の ε すべてで基準の ε と同じ係数 1.0 の単位。devs の ε は係数を 1+dev にずらし、lost の ε は波を残さず、start の ε は始まりで落ち着く。
    境界でない単位は、same なら選ばれる式が ε を入れる前と同じ、same=False なら周期が変わる。"""
    r = {"boundary": boundary, "decay": 0.0 if boundary else 1.0, "period": 1.0}
    for e in rp.GRID:
        if not boundary:
            r[gen.ekey(e)] = er(1.0, period=1.0 if same else 2.0)
        elif e == gen.REF_EPS:
            r[gen.ekey(e)] = er(e, at_start=ref_start)
        else:
            r[gen.ekey(e)] = er(0.0 if e in lost else e, coef=1.0 + (devs or {}).get(e, 0.0), at_start=e in start)
    return r


def test_grid_stays_inside_the_domain_and_includes_the_reference():
    assert all(0 < e <= 1e-2 for e in rp.GRID) and gen.REF_EPS in rp.GRID and list(rp.GRID) == sorted(rp.GRID, reverse=True)
    assert list(rp.DELTAS) == sorted(rp.DELTAS, reverse=True)


def test_coverage_counts_units_within_each_delta_and_the_reference_itself_is_always_inside():
    rows = [row(), row(devs={1e-3: 0.05}), row(devs={1e-3: 0.005}), row(devs={1e-3: -0.5})]
    c = rp.coverage_rows(gen, rows)
    ok = c["per_eps"][gen.ekey(1e-3)]["ok"]
    assert c["boundary"] == 4 and ok == {"0.1": 3, "0.01": 2, "0.001": 1, "0.0001": 1}
    assert c["per_eps"][REF]["ok"] == {"0.1": 4, "0.01": 4, "0.001": 4, "0.0001": 4}
    assert c["per_eps"][gen.ekey(1e-2)]["ok"] == {"0.1": 4, "0.01": 4, "0.001": 4, "0.0001": 4}


def test_lost_mismatched_and_at_start_units_are_kept_apart():
    rows = [row(lost=(1e-3,)), row(start=(1e-3,)), row(start=(1e-3,), ref_start=True), row(ref_start=True), row(), row(boundary=False)]
    c = rp.coverage_rows(gen, rows)
    k = c["per_eps"][gen.ekey(1e-3)]
    assert c["boundary"] == 5 and c["nonboundary"] == 1
    assert (k["lost"], k["mismatch"], k["at_start"]) == (1, 2, 1)                     # 片方だけ始まり（行 2 と 4）は比べない
    assert k["ok"]["0.0001"] == 2                                                     # 始まりで落ち着く単位（両方）と、ふつうの 1 単位
    assert c["per_eps"][gen.ekey(1e-2)]["lost"] == 0


def test_nonboundary_units_count_when_the_chosen_form_is_unchanged():
    rows = [row(boundary=False), row(boundary=False, same=False), row(boundary=False)]
    c = rp.coverage_rows(gen, rows)
    assert c["nonboundary"] == 3 and all(v["nonboundary_same"] == 2 for v in c["per_eps"].values()) and c["boundary"] == 0


def test_pool_adds_the_window_lengths():
    a = rp.coverage_rows(gen, [row(devs={5e-3: 0.5, 1e-3: 0.02}), row()])
    b = rp.coverage_rows(gen, [row(devs={7e-4: 0.005}), row(boundary=False)])
    t = rp.pool([a, b])
    assert t["boundary"] == 3 and t["nonboundary"] == 1
    assert t["per_eps"][gen.ekey(5e-3)]["ok"]["0.1"] == 2 and t["per_eps"][gen.ekey(7e-4)]["ok"] == {"0.1": 3, "0.01": 3, "0.001": 2, "0.0001": 2}
    assert t["per_eps"][gen.ekey(1e-3)]["nonboundary_same"] == 1 and t["per_eps"][gen.ekey(1e-3)]["eps"] == 1e-3


def test_pool_adds_the_lost_mismatched_and_at_start_counts_too():
    a = rp.coverage_rows(gen, [row(lost=(1e-3,)), row(start=(1e-3,))])
    b = rp.coverage_rows(gen, [row(start=(1e-3,), ref_start=True), row(lost=(1e-3,))])
    k = rp.pool([a, b])["per_eps"][gen.ekey(1e-3)]
    assert (k["lost"], k["mismatch"], k["at_start"]) == (2, 1, 1) and k["ok"]["0.1"] == 1


def test_largest_full_is_the_biggest_epsilon_before_the_first_one_that_fails():
    t = rp.pool([rp.coverage_rows(gen, [row(devs={5e-3: 0.5, 1e-3: 0.02}), row(devs={7e-4: 0.005}), row()])])
    assert [rp.largest_full(t, d) for d in rp.DELTAS] == [3e-3, 7e-4, 5e-4, 5e-4]


def test_largest_full_stops_at_a_failure_even_when_larger_epsilons_are_fine():
    t = rp.pool([rp.coverage_rows(gen, [row(devs={1e-7: 0.5}), row()])])
    assert t["per_eps"][gen.ekey(1e-2)]["ok"]["0.1"] == 2                            # 大きい ε は収まっている
    assert rp.largest_full(t, 0.1) == 1e-9                                           # でも途中の 1e-7 で外れたので、その手前まで


def test_largest_full_is_none_when_the_smallest_epsilon_fails_or_there_is_nothing_to_judge():
    assert rp.largest_full(rp.pool([rp.coverage_rows(gen, [row(lost=tuple(rp.GRID))])]), 0.1) is None     # 一番小さい ε が消える
    assert rp.largest_full(rp.pool([rp.coverage_rows(gen, [row(boundary=False)])]), 0.1) is None          # 境界の単位がない
    assert rp.largest_full(rp.pool([rp.coverage_rows(gen, [row()])]), 0.0001) == 1e-2                     # 全部収まれば格子の最大


def test_draw_share_is_a_probability_that_rises_with_epsilon_and_matches_the_decades():
    xs = [1e-308, 1e-300, 1e-100, 1e-13, 1e-9, 1e-6, 1e-4, 1e-3, 5e-3, 1e-2]
    s = [rp.share_le(gen, x) for x in xs]
    assert s == sorted(s) and s[0] == 0.0 and 0 < s[1] < 1e-20 and s[-1] == pytest.approx(1.0) and all(0 <= v <= 1 for v in s)
    assert rp.share_le(gen, 1e-2) == pytest.approx(1.0)
    assert rp.share_le(gen, 1e-3) == pytest.approx(5 / 6 + (1 / 6) / 900)             # N = 3 の十進の桁のうち A = 1.00 の 1 つだけが 1e-3 以下
    assert rp.share_le(gen, 9.99e-4) == pytest.approx(5 / 6)                          # N >= 4 の全部
    assert rp.share_le(gen, 9.99e-5) == pytest.approx((5 / 6) ** 2)                   # N >= 5 の全部


def test_draw_share_matches_a_simulation_of_the_same_rule():
    rng = random.Random(1)
    es = []
    for _ in range(20000):
        a = rng.randint(gen.A_MIN, gen.A_MAX)
        es.append(float(f"{a // 100}.{a % 100:02d}e-{gen.N_MIN + gen._steps(rng, gen.N_CAP - gen.N_MIN)}"))
    for x in (1e-2, 1e-3, 7e-4, 1e-5, 1e-9, 1e-13):
        assert sum(e <= x for e in es) / len(es) == pytest.approx(rp.share_le(gen, x), abs=0.012), x


def test_draw_share_follows_the_cap_and_the_stop_probability(monkeypatch):
    monkeypatch.setattr(gen, "P_STOP", 1.0)                                           # N = 3 だけ
    assert rp.share_le(gen, 1e-3) == pytest.approx(1 / 900) and rp.share_le(gen, 9.99e-3) == pytest.approx(1.0)
    monkeypatch.setattr(gen, "P_STOP", 0.0)                                           # N_CAP だけ
    assert rp.share_le(gen, 1e-308) == 0.0 and rp.share_le(gen, 1e-300) == pytest.approx(1.0) and rp.share_le(gen, 1e-13) == pytest.approx(1.0)
    assert rp.share_le(gen, 5e-307) == pytest.approx(401 / 900)                       # N = 307 で A = 1.00〜5.00 の 401 通り


LO, HI = 8.14e-13, 2.22e-3
REGION = {"mode": "inside", "lo": LO, "hi": HI}


def test_side_of_includes_both_ends_in_inside_and_leaves_them_out_of_above_and_below():
    assert [rp.side_of(REGION, e) for e in (1e-2, 2.23e-3, HI, 1e-5, LO, 8.13e-13, 1e-20)] == ["above", "above", "inside", "inside", "inside", "below", "below"]


def pooled(rows):
    return rp.pool([rp.coverage_rows(gen, rows)])


def test_region_summary_looks_only_at_the_grid_points_on_the_chosen_side():
    t = pooled([row(devs={5e-3: 0.5, 1e-3: 0.02, 1e-7: 0.2}), row(devs={5e-3: 0.05}), row()])
    above = rp.region_summary(gen, t, dict(REGION, mode="above"))
    assert above["eps"] == [1e-2, 5e-3, 3e-3] and above["worst_ok_share"] == {"0.1": pytest.approx(2 / 3), "0.01": pytest.approx(1 / 3), "0.001": pytest.approx(1 / 3), "0.0001": pytest.approx(1 / 3)}
    assert above["all_within"] == {"0.1": False, "0.01": False, "0.001": False, "0.0001": False}
    inside = rp.region_summary(gen, t, REGION)
    assert inside["eps"][0] == 2e-3 and inside["eps"][-1] == 1e-11 and 5e-3 not in inside["eps"]
    assert inside["worst_ok_share"]["0.1"] == pytest.approx(2 / 3) and inside["all_within"]["0.1"] is False        # 1e-7 で 0.2 ずれる行がある
    assert inside["worst_ok_share"]["0.01"] == pytest.approx(2 / 3)                                                    # 1e-3 の 0.02 と 1e-7 の 0.2 は、それぞれ別の点で 1 行だけ外れる
    assert rp.region_summary(gen, t, dict(REGION, mode="below"))["eps"] == [1e-13]
    below = rp.region_summary(gen, t, {"mode": "below", "lo": 1e-14, "hi": HI})                                       # 1e-14 より小さい格子の ε はない
    assert below["eps"] == [] and below["worst_ok_share"]["0.1"] is None and below["all_within"]["0.1"] is False and below["max_lost"] is None
    ok = rp.region_summary(gen, pooled([row(), row()]), REGION)
    assert all(ok["all_within"].values()) and all(v == 1.0 for v in ok["worst_ok_share"].values())


def test_region_summary_counts_lost_and_changed_units_as_the_maximum_over_the_side():
    t = pooled([row(lost=(1e-2,)), row(boundary=False), row(boundary=False, same=False)])
    s = rp.region_summary(gen, t, dict(REGION, mode="above"))
    assert s["max_lost"] == 1 and s["max_nonboundary_changed"] == 1 and s["worst_ok_share"]["0.1"] == 0.0
    assert rp.region_summary(gen, t, REGION)["max_lost"] == 0


def test_region_summary_changed_units_is_the_largest_count_over_the_points_not_the_smallest():
    r = row(boundary=False)
    r[gen.ekey(5e-3)] = er(1.0, period=2.0)                                           # 5e-3 のときだけ式が変わる非境界の単位
    s = rp.region_summary(gen, pooled([row(), r]), dict(REGION, mode="above"))
    assert s["max_nonboundary_changed"] == 1 and s["eps"] == [1e-2, 5e-3, 3e-3]
    assert rp.region_summary(gen, pooled([row(), r]), REGION)["max_nonboundary_changed"] == 0


def test_region_summary_probabilities_of_the_three_sides_add_up_to_one_and_match_the_rule():
    t = pooled([row()])
    p = {m: rp.region_summary(gen, t, dict(REGION, mode=m))["draw_probability"] for m in gen.MODES}
    assert sum(p.values()) == pytest.approx(1.0, abs=1e-12) and p["inside"] == pytest.approx(0.70017, abs=1e-5)
    assert p["inside"] == pytest.approx(rp.share_le(gen, HI) - rp.share_le(gen, 8.13e-13), abs=1e-12)


def test_region_summary_without_boundary_units_cannot_summarise():
    s = rp.region_summary(gen, pooled([row(boundary=False)]), REGION)
    assert s["eps"] and all(v is None for v in s["worst_ok_share"].values()) and not any(s["all_within"].values())


def test_render_with_a_range_lists_the_side_and_says_when_it_is_empty():
    def res_of(rows, region):
        t = pooled(rows)
        return {"grid": list(rp.GRID), "deltas": list(rp.DELTAS), "sets": {}, "total": t, "region": region, "region_summary": rp.region_summary(gen, t, region),
                "full_coverage_max_eps": {format(d, "g"): rp.largest_full(t, d) for d in rp.DELTAS}, "draw_share_le": {format(e, "g"): rp.share_le(gen, e) for e in rp.GRID}}
    md = rp.render(gen, res_of([row()], dict(REGION, mode="above")))
    assert "## 指定した範囲: above（8.14×10^-13 〜 2.22×10^-3" in md and "この側にある格子の ε 3 個: 0.01, 0.005, 0.003。" in md and "| 10% | 100.00% | はい |" in md
    assert "| 0.01 | above |" in md and "| 0.002 | inside |" in md and "| 1e-13 | below |" in md and "ε がこの側に入る確率: 14.4%" in md
    empty = rp.render(gen, res_of([row()], {"mode": "below", "lo": 1e-14, "hi": HI}))
    assert "この側にある格子の ε 0 個: なし。" in empty and "まとめられません" in empty and "最悪の収まった割合" not in empty
    none = rp.render(gen, res_of([row(boundary=False)], REGION))
    assert "まとめられません" in none


def small_csv(tmp_path):
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = []
    for j in range(3):
        for i in range(48):
            y, m = 2020 + i // 12, i % 12 + 1
            v = 3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)
            rows.append({"country": "AAA", "date": f"{y:04d}-{m:02d}-01", "year": str(y), "variable": f"mine:c{j}", "value": str(v),
                         "unit": "x", "source": "https://github.com/tezamo/FPMA (x)", "note": f"m={j}", "estimated_value": ""})
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def test_main_takes_another_variable_prefix_writes_the_same_bytes_twice_and_says_it_is_not_a_constant(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert rp.main(["--csv", str(small_csv(tmp_path)), "--prefix", "mine:", "--cadence", "month", "--outdir", str(out), "--repo", str(ROOT)]) == 0
        outs.append(out)
    for n in ("eps_range_profile.json", "eps_range_profile.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    res = json.loads((outs[0] / "eps_range_profile.json").read_text(encoding="utf-8"))
    assert res["grid"] == list(rp.GRID) and list(res["sets"]) == [str(n) for n in gen.LENGTHS]
    assert res["total"]["boundary"] == sum(s["boundary"] for s in res["sets"].values()) > 0
    assert all(res["total"]["per_eps"][gen.ekey(e)]["ok"]["0.1"] == res["total"]["boundary"] for e in rp.GRID if e <= 1e-6)      # きれいな波は ε が小さければ動かない
    assert set(res["full_coverage_max_eps"]) == {"0.1", "0.01", "0.001", "0.0001"} and set(res["draw_share_le"]) == {format(e, "g") for e in rp.GRID}
    md = (outs[0] / "eps_range_profile.md").read_text(encoding="utf-8")
    assert "ε の範囲を決める値ではありません" in md and "| 0.01 |" in md and "乱数の選び方の重み" in md


def test_main_without_matching_variables_stops_with_an_error(tmp_path):
    with pytest.raises(SystemExit) as ei:
        rp.main(["--csv", str(small_csv(tmp_path)), "--prefix", "nothing:", "--outdir", str(tmp_path / "o"), "--repo", str(ROOT)])
    assert "nothing:" in str(ei.value) and not (tmp_path / "o").exists()


def test_render_says_so_when_nothing_can_be_judged_or_the_smallest_epsilon_fails():
    def res_of(rows):
        t = rp.pool([rp.coverage_rows(gen, rows)])
        return {"grid": list(rp.GRID), "deltas": list(rp.DELTAS), "sets": {}, "total": t,
                "full_coverage_max_eps": {format(d, "g"): rp.largest_full(t, d) for d in rp.DELTAS},
                "draw_share_le": {format(e, "g"): rp.share_le(gen, e) for e in rp.GRID}}
    assert "境界の単位がないので判定できない" in rp.render(gen, res_of([row(boundary=False)]))
    md = rp.render(gen, res_of([row(lost=tuple(rp.GRID))]))
    assert "一番小さい ε でも外れた単位がある" in md and "境界の単位がないので" not in md
    assert "0.01（これ以下の格子の ε ではすべて収まった）" in rp.render(gen, res_of([row()]))


def test_readme_points_to_the_script():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    assert "eps_range_profile.py" in text and "tests/test_epsilon_generality_range.py" in text
    assert "その側の格子の ε について、許容ごとの最悪の収まった割合などをまとめる" in text and "`--eps-range MODE LO HI`（`eps_generality.py` と同じ書き方" in text


def test_results_readme_and_files_match_the_json_and_say_it_is_not_a_constant():
    R = DIR / "results-random"
    res = {k: json.loads((R / k / "eps_range_profile.json").read_text(encoding="utf-8")) for k in ("staple", "monthly", "daily")}
    text = (R / "README.md").read_text(encoding="utf-8")
    assert "## ε が動いた範囲" in text and "定数ではない" in text and "決める値ではありません" in text
    total = rp.pool([r["total"] for r in res.values()])
    assert f"{total['boundary']:,}" in text and f"{total['nonboundary']:,}" in text
    for d in rp.DELTAS:
        row = f"| {d * 100:g}% | {rp.largest_full(total, d):g} |"
        assert row in text, row
    for k, r in res.items():
        assert r["grid"] == list(rp.GRID)
        assert (R / k / "eps_range_profile.md").read_text(encoding="utf-8") == rp.render(gen, r), k


def test_main_with_a_range_adds_the_ends_and_random_points_and_a_summary(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert rp.main(["--csv", str(small_csv(tmp_path)), "--prefix", "mine:", "--cadence", "month", "--outdir", str(out), "--repo", str(ROOT),
                        "--eps-range", "below", "8.14×10^-13", "2.22e-3", "--random-eps", "3", "--coef-seed", "7"]) == 0
        outs.append(out)
    for n in ("eps_range_profile.json", "eps_range_profile.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    res = json.loads((outs[0] / "eps_range_profile.json").read_text(encoding="utf-8"))
    drawn = [d["value"] for d in gen.draw_coefficients(3, 7, "eps", gen.make_region("eps", "below", LO, HI))]
    assert res["region"] == {"mode": "below", "lo": LO, "hi": HI} and len(drawn) == 3 and all(v < LO for v in drawn)
    assert res["grid"] == sorted(set(rp.GRID) | {LO, HI} | set(drawn), reverse=True)
    sm = res["region_summary"]
    assert sm["eps"] == sorted([1e-13] + drawn, reverse=True) and sm["draw_probability"] == pytest.approx(0.15594, abs=2e-5)
    md = (outs[0] / "eps_range_profile.md").read_text(encoding="utf-8")
    assert "## 指定した範囲: below（8.14×10^-13 〜 2.22×10^-3" in md and "| ε | 範囲 |" in md and "| 8.14e-13 | inside |" in md and "| 0.0022200000000000002 |" not in md


def test_main_without_a_range_has_no_range_section_or_column(tmp_path):
    out = tmp_path / "plain"
    assert rp.main(["--csv", str(small_csv(tmp_path)), "--prefix", "mine:", "--cadence", "month", "--outdir", str(out), "--repo", str(ROOT)]) == 0
    res = json.loads((out / "eps_range_profile.json").read_text(encoding="utf-8"))
    assert "region" not in res and "region_summary" not in res and res["grid"] == list(rp.GRID)
    md = (out / "eps_range_profile.md").read_text(encoding="utf-8")
    assert "指定した範囲" not in md and "| ε | δ=10%" in md


@pytest.mark.parametrize("flags", [
    ("--random-eps", "3"),                                                           # 範囲がない
    ("--eps-range", "sideways", "1e-5", "1e-3"),
    ("--eps-range", "inside", "1e-3", "1e-5"),                                       # LO > HI
    ("--eps-range", "inside", "abc", "1e-3"),
    ("--eps-range", "inside", "1e-5", "1"),                                          # ε は 1/100 まで
    ("--eps-range", "above", "1e-3", "9.99e-3", "--random-eps", "1"),                # その側に選べる値がない
    ("--eps-range", "inside", "1e-5"),                                               # 3 つ要る
])
def test_main_refuses_a_bad_range_before_doing_anything(tmp_path, flags):
    with pytest.raises(SystemExit) as e:
        rp.main(["--csv", str(small_csv(tmp_path)), "--prefix", "mine:", "--outdir", str(tmp_path / "x"), "--repo", str(ROOT), *flags])
    assert e.value.code == 2 and not (tmp_path / "x").exists()
