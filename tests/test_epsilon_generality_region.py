"""eps_generality.py の範囲指定（--eps-range / --scale-range MODE LO HI）の確認。

SYNTHETIC: 範囲に入る (A, 指数) の組、選ばれる確率、選んだ値、書き出し、README の説明を確かめる。結論には使わない。
指定しないときに、登録した乱数の値が変わらないことも確かめる。
"""
import importlib.util
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, DIR / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gen = _load("eps_generality", "eps_generality.py")
rp = _load("eps_range_profile", "eps_range_profile.py")
LO, HI = 8.14e-13, 2.22e-3                          # 利用者が挙げた 2 つの値
SEED = 18750922
REGISTERED = [2.22e-3, 1.76e-3, 3.54e-4, 3.20e-4, 7.82e-5, 6.60e-6, 9.82e-9, 2.28e-9, 6.29e-11, 8.14e-13]


def table(kind, mode, lo=LO, hi=HI):
    return {x: (m, a) for x, m, a in gen.region_table(kind, gen.make_region(kind, mode, lo, hi))}


def p_inside(kind, region):
    """規則で選ばれる値が範囲に入る確率。"""
    return sum(m * len(a) for _, m, a in gen.region_table(kind, region)) / (gen.A_MAX - gen.A_MIN + 1)


def test_without_a_range_the_registered_values_are_unchanged():
    assert [d["value"] for d in gen.draw_coefficients(10, SEED, "eps")] == REGISTERED
    assert gen.draw_coefficients(10, SEED, "eps", None) == gen.draw_coefficients(10, SEED, "eps")
    assert gen.make_draws(10, 10, SEED) == {"seed": SEED, "eps": gen.draw_coefficients(10, SEED, "eps"), "scales": gen.draw_coefficients(10, SEED, "scale")}
    assert "regions" not in gen.make_draws(3, 3, SEED)


@pytest.mark.parametrize("text", ["2.22×10^-3", "2.22x10^-3", "2.22 X 10 ^ -3", "2.22*10^-3", "2.22e-3", "2.22E-3", "0.00222", " 2.22×10^-3 "])
def test_parse_pow10_reads_the_ways_a_value_is_written(text):
    assert gen.parse_pow10(text) == 2.22e-3                                       # 文字のまま float にするので、同じ値


def test_parse_pow10_keeps_exponents_and_large_values():
    assert gen.parse_pow10("8.14×10^-13") == 8.14e-13 and gen.parse_pow10("1×10^+2") == 100.0 and gen.parse_pow10("5") == 5.0
    assert gen.parse_pow10("9.99×10^-307") == 9.99e-307


@pytest.mark.parametrize("text", ["", "abc", "0", "-1", "-2.22×10^-3", "inf", "nan", "2.22×10^", "×10^-3", "2.22×10-3"])
def test_parse_pow10_refuses_what_is_not_a_positive_finite_number(text):
    with pytest.raises(ValueError):
        gen.parse_pow10(text)


def test_make_region_checks_the_range_and_the_epsilon_domain():
    assert gen.make_region("eps", "inside", LO, HI) == {"mode": "inside", "lo": LO, "hi": HI}
    assert gen.make_region("eps", "below", 1e-3, 1e-3)["hi"] == 1e-3 and gen.make_region("eps", "inside", 1e-3, 1e-2)["hi"] == 1e-2
    for bad in (("sideways", LO, HI), ("inside", HI, LO), ("inside", 0.0, HI), ("inside", -1.0, HI), ("inside", LO, float("inf")), ("inside", LO, float("nan"))):
        with pytest.raises(ValueError):
            gen.make_region("eps", *bad)
    with pytest.raises(ValueError):
        gen.make_region("eps", "inside", LO, 1.0000001e-2)                       # ε は 1/100 まで
    assert gen.make_region("scale", "above", 1.0, 1e9)["hi"] == 1e9              # 倍率にその上限はない


def test_inside_has_the_exponents_between_the_ends_and_keeps_both_ends():
    t = table("eps", "inside")
    assert sorted(t) == list(range(-13, -2))                                       # N = 3〜13
    assert t[-3][1] == list(range(100, 223)) and t[-13][1] == list(range(814, 1000))     # 2.22×10^-3 と 8.14×10^-13 は入る
    assert all(t[x][1] == list(range(100, 1000)) for x in range(-12, -3))


def test_above_and_below_leave_out_the_ends_and_the_three_regions_split_the_rule():
    up, down = table("eps", "above"), table("eps", "below")
    assert sorted(up) == [-3] and up[-3][1] == list(range(223, 1000))
    assert min(down) == -307 and max(down) == -13 and down[-13][1] == list(range(100, 814))
    assert all(down[x][1] == list(range(100, 1000)) for x in range(-306, -13))
    n = sum(len(a) for _, a in table("eps", "inside").values()) + sum(len(a) for _, a in up.values()) + sum(len(a) for _, a in down.values())
    assert n == 900 * (gen.N_CAP - gen.N_MIN + 1)                                  # 重ならず、抜けない
    ins = {(x, a) for x, (_, al) in table("eps", "inside").items() for a in al}
    assert not ins & {(x, a) for x, (_, al) in up.items() for a in al} and not ins & {(x, a) for x, (_, al) in down.items() for a in al}


def test_a_range_inside_one_decade_and_the_scale_kind_are_handled_the_same_way():
    t = table("eps", "inside", 1.5e-5, 2.5e-5)
    assert sorted(t) == [-5] and t[-5][1] == list(range(150, 251))
    s = table("scale", "inside", 1e-7, 1e-4)
    assert sorted(s) == [-7, -6, -5, -4] and s[-4][1] == [100] and s[-7][1] == list(range(100, 1000))
    assert table("scale", "above", 1e-4, 1e-4)[-4][1] == list(range(101, 1000)) and 0 in table("scale", "above", 1e-4, 1e-4)
    assert table("scale", "above", 1.0, 1.0)[0][1] == list(range(101, 1000)) and 0 not in table("scale", "below", 1.0, 1.0)     # 1.00 は above にも below にも入らない


def test_exponent_masses_follow_the_rule_including_the_ends():
    p, q = gen.P_STOP, 1 - gen.P_STOP
    e, s = gen.exponent_masses("eps"), gen.exponent_masses("scale")
    assert sorted(e) == list(range(-gen.N_CAP, -gen.N_MIN + 1)) and sorted(s) == list(range(-gen.E_CAP, gen.E_CAP + 1))
    assert e[-3] == p and e[-4] == q * p and e[-gen.N_CAP + 1] == q ** (gen.N_CAP - gen.N_MIN - 1) * p
    assert e[-gen.N_CAP] == q ** (gen.N_CAP - gen.N_MIN)                             # 上限 N_CAP は「止まる」を待たずに打ち切るので、q^(段の数) だけ
    assert s[0] == p and s[1] == s[-1] == 0.5 * q * p and s[gen.E_CAP] == s[-gen.E_CAP] == 0.5 * q ** gen.E_CAP
    assert sum(e.values()) == pytest.approx(1.0, abs=1e-12) and sum(s.values()) == pytest.approx(1.0, abs=1e-12)


def test_the_probabilities_of_the_three_regions_add_up_to_one_for_both_kinds():
    for kind, lo, hi in (("eps", LO, HI), ("scale", 1e-7, 1e-4), ("scale", 1.0, 3.0)):
        parts = [p_inside(kind, gen.make_region(kind, m, lo, hi)) for m in gen.MODES]
        assert sum(parts) == pytest.approx(1.0, abs=1e-12), kind
        assert all(p > 0 for p in parts)


def test_the_inside_probability_matches_the_draw_weights_of_the_profile_script():
    for x in (1e-2, 2.22e-3, 1e-4, 1e-9, 1e-13, 1e-100):
        assert p_inside("eps", gen.make_region("eps", "inside", 1e-308, x)) == pytest.approx(rp.share_le(gen, x), abs=1e-12), x
    assert p_inside("eps", gen.make_region("eps", "below", LO, HI)) == pytest.approx(0.15594, abs=2e-5)
    assert p_inside("eps", gen.make_region("eps", "above", LO, HI)) == pytest.approx(0.14389, abs=2e-5)


def test_drawn_values_are_in_the_region_distinct_sorted_and_not_the_fixed_ones():
    for mode, ok in (("inside", lambda v: LO <= v <= HI), ("above", lambda v: v > HI), ("below", lambda v: v < LO)):
        r = gen.make_region("eps", mode, LO, HI)
        d = gen.draw_coefficients(10, SEED, "eps", r)
        vals = [x["value"] for x in d]
        assert len(set(vals)) == 10 and vals == sorted(vals, reverse=True) and all(ok(v) for v in vals) and all(v not in gen.EPS for v in vals), mode
        assert all(x["value"] == float(f"{x['a']:.2f}e{x['exp']}") and 1.0 <= x["a"] <= 9.99 for x in d)
        assert d == gen.draw_coefficients(10, SEED, "eps", r) and d != gen.draw_coefficients(10, SEED + 1, "eps", r)
    sc = gen.draw_coefficients(10, SEED, "scale", gen.make_region("scale", "inside", 1e-7, 1e-4))
    assert all(1e-7 <= x["value"] <= 1e-4 for x in sc) and all(x["value"] not in gen.SCALES for x in sc)


def test_the_fixed_values_are_left_out_even_when_the_range_holds_them():
    r = gen.make_region("eps", "inside", 1e-9, 1e-9)
    with pytest.raises(ValueError):                                                  # 範囲に入る値は 1e-9 の 1 個だけで、それは決め打ちなので選べない
        gen.draw_coefficients(1, SEED, "eps", r)


def test_asking_for_more_values_than_the_range_holds_stops():
    r = gen.make_region("eps", "inside", 1.5e-5, 1.54e-5)                            # 1.50〜1.54 の 5 個
    assert len(gen.draw_coefficients(5, SEED, "eps", r)) == 5
    with pytest.raises(ValueError, match="に入る値は 5 個で、6 個は選べない"):
        gen.draw_coefficients(6, SEED, "eps", r)
    with pytest.raises(ValueError):
        gen.draw_coefficients(1, SEED, "eps", gen.make_region("eps", "above", 1e-3, 9.99e-3))     # 9.99×10^-3 より上は ε の定義域の外で空
    with pytest.raises(ValueError):
        gen.draw_coefficients(1, SEED, "eps", gen.make_region("eps", "below", 1e-307, 1e-300))    # 下は N_CAP の 1.00×10^-307 まで


def test_exponents_are_chosen_with_the_weights_of_the_rule_not_evenly():
    r = gen.make_region("eps", "inside", 1e-8, 9.99e-4)                              # N = 4〜8: 4 の確率は (5/6)^1 を (5/6)^1〜(5/6)^5 の和で割った 0.279（一様なら 0.2）
    n4 = sum(gen.draw_coefficients(1, s, "eps", r)[0]["exp"] == -4 for s in range(1500))
    assert n4 / 1500 == pytest.approx((5 / 6) / sum((5 / 6) ** k for k in range(1, 6)), abs=0.04)


def test_the_number_of_values_in_each_exponent_counts_not_only_the_rule_probability():
    r = gen.make_region("eps", "inside", 9.5e-5, 1.05e-4)                            # N = 5 の A = 9.50〜9.99（50 個）と N = 4 の A = 1.00〜1.05（6 個）
    t = {x: (m, a) for x, m, a in gen.region_table("eps", r)}
    assert sorted(t) == [-5, -4] and len(t[-5][1]) == 50 and len(t[-4][1]) == 6
    want = t[-4][0] * 6 / (t[-4][0] * 6 + t[-5][0] * 50)                             # 0.126（rule の確率だけで比べると 0.545）
    n4 = sum(gen.draw_coefficients(1, s, "eps", r)[0]["exp"] == -4 for s in range(1500))
    assert want == pytest.approx(0.126, abs=0.001) and n4 / 1500 == pytest.approx(want, abs=0.04)


def test_make_draws_records_the_regions_only_when_they_are_used():
    d = gen.make_draws(4, 3, SEED, ("below", LO, HI), None)
    assert d["regions"] == {"eps": {"mode": "below", "lo": LO, "hi": HI}} and all(x["value"] < LO for x in d["eps"])
    assert d["scales"] == gen.draw_coefficients(3, SEED, "scale")                    # 範囲を指定しない方は変わらない
    d2 = gen.make_draws(2, 2, SEED, None, ("inside", 1e-7, 1e-4))
    assert list(d2["regions"]) == ["scales"] and d2["eps"] == gen.draw_coefficients(2, SEED, "eps")
    with pytest.raises(ValueError):
        gen.make_draws(2, 2, SEED, ("inside", HI, LO), None)


def test_region_lines_say_which_range_the_values_were_chosen_from():
    rc = {"seed": SEED, "eps": [], "scales": []}
    assert gen.region_lines(rc) == [] and gen.region_lines(dict(rc, regions={})) == []
    lines = gen.region_lines(dict(rc, regions={"eps": {"mode": "above", "lo": LO, "hi": HI}}))
    assert len(lines) == 1 and lines[0].startswith("- εを選んだ範囲: above（8.14×10^-13 〜 2.22×10^-3")
    both = gen.region_lines(dict(rc, regions={"scales": {"mode": "inside", "lo": 1e-7, "hi": 1e-4}, "eps": {"mode": "below", "lo": LO, "hi": HI}}))
    assert [l.split(":")[0] for l in both] == ["- εを選んだ範囲", "- 倍率を選んだ範囲"]


def small_csv(tmp_path):
    import csv
    cols = ["country", "date", "year", "variable", "value", "unit", "source", "note", "estimated_value"]
    rows = [{"country": "AAA", "date": f"{2020 + i // 12:04d}-{i % 12 + 1:02d}-01", "year": str(2020 + i // 12), "variable": f"staple_price:c{j}",
             "value": str(3.0 + 2.0 * math.cos(2 * math.pi * i / 23 + 0.3 * j) + 0.001 * ((i * 7 + j) % 5)), "unit": "USD per kg",
             "source": "https://github.com/tezamo/FPMA (x)", "note": f"market={j}", "estimated_value": ""} for j in range(3) for i in range(48)]
    p = tmp_path / "s.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return p


def run(tmp_path, name, *flags):
    out = tmp_path / name
    assert gen.main(["--csv", str(small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT), *flags]) == 0
    return out


def test_cli_with_a_range_records_it_uses_it_and_is_byte_reproducible(tmp_path):
    import json
    flags = ("--random-eps", "3", "--eps-range", "below", "8.14×10^-13", "2.22×10^-3", "--random-scales", "2", "--scale-range", "inside", "1e-7", "1e-4", "--coef-seed", "11")
    o1, o2 = run(tmp_path, "a", *flags), run(tmp_path, "b", *flags)
    for n in sorted(p.name for p in o1.iterdir()):
        assert (o1 / n).read_bytes() == (o2 / n).read_bytes(), n
    rc = json.loads((o1 / "eps_generality.json").read_text(encoding="utf-8"))["random_coefficients"]
    assert rc["regions"] == {"eps": {"mode": "below", "lo": LO, "hi": HI}, "scales": {"mode": "inside", "lo": 1e-7, "hi": 1e-4}}
    assert rc["eps"] == gen.draw_coefficients(3, 11, "eps", gen.make_region("eps", "below", LO, HI)) and all(d["value"] < LO for d in rc["eps"])
    assert all(1e-7 <= d["value"] <= 1e-4 for d in rc["scales"])
    md = (o1 / "eps_generality.md").read_text(encoding="utf-8")
    assert "εを選んだ範囲: below（8.14×10^-13 〜 2.22×10^-3" in md and "倍率を選んだ範囲: inside（1.00×10^-7 〜 1.00×10^-4" in md


def test_cli_without_a_range_has_no_regions_in_the_output(tmp_path):
    import json
    o = run(tmp_path, "c", "--random-eps", "2", "--coef-seed", "11")
    assert "regions" not in json.loads((o / "eps_generality.json").read_text(encoding="utf-8"))["random_coefficients"]
    assert "を選んだ範囲" not in (o / "eps_generality.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("flags", [
    ("--eps-range", "inside", "1e-5", "1e-3"),                                       # --random-eps がない
    ("--random-eps", "0", "--eps-range", "inside", "1e-5", "1e-3"),
    ("--random-scales", "2", "--eps-range", "inside", "1e-5", "1e-3"),               # 倍率だけを足すのに ε の範囲
    ("--random-eps", "2", "--scale-range", "inside", "1e-5", "1e-3"),
    ("--random-eps", "2", "--eps-range", "sideways", "1e-5", "1e-3"),
    ("--random-eps", "2", "--eps-range", "inside", "1e-3", "1e-5"),                  # LO > HI
    ("--random-eps", "2", "--eps-range", "inside", "abc", "1e-3"),
    ("--random-eps", "2", "--eps-range", "inside", "1e-5", "1"),                     # ε は 1/100 まで
    ("--random-eps", "2", "--eps-range", "inside", "1e-5"),                          # 3 つ要る
])
def test_cli_refuses_a_bad_range_before_doing_anything(tmp_path, flags):
    with pytest.raises(SystemExit) as e:
        gen.main(["--csv", str(small_csv(tmp_path)), "--outdir", str(tmp_path / "x"), "--repo", str(ROOT), *flags])
    assert e.value.code == 2 and not (tmp_path / "x").exists()


def test_readme_describes_the_options_and_points_to_the_tests():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    for needle in ("--eps-range MODE LO HI", "--scale-range MODE LO HI", "**inside**", "**above**", "**below**", "tests/test_epsilon_generality_region.py", "2.22×10^-3", "範囲の既定値は置かない"):
        assert needle in text, needle


REGISTERED_4 = {
    "inside": [4.91e-4, 3.05e-5, 1.65e-5, 3.30e-6, 3.71e-7, 9.99e-8, 8.43e-8, 2.13e-8, 1.88e-8, 3.78e-12],
    "above": [9.66e-3, 7.79e-3, 6.14e-3, 5.01e-3, 4.94e-3, 4.53e-3, 4.28e-3, 3.36e-3, 3.11e-3, 2.88e-3],
    "below": [4.91e-13, 3.05e-15, 1.65e-15, 3.30e-16, 3.71e-18, 9.99e-19, 8.43e-19, 2.13e-19, 1.88e-19, 3.78e-29],
}


@pytest.mark.parametrize("mode", gen.MODES)
def test_fourth_round_values_come_from_the_seed_and_the_rule_and_are_listed_in_the_readme(mode):
    d = gen.draw_coefficients(10, 20261026, "eps", gen.make_region("eps", mode, LO, HI))
    assert [x["value"] for x in d] == REGISTERED_4[mode]
    text = (DIR / "README.md").read_text(encoding="utf-8")
    assert f"  - {mode}: " + ", ".join(gen.pow10_text(v) for v in REGISTERED_4[mode]) in text
    assert all(0 < v <= 1e-2 for v in REGISTERED_4[mode])


def test_fourth_round_registration_names_the_range_the_seed_and_the_counts():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    sec = text[text.index("## 乱数の ε を範囲から選ぶ確認（第 4 回）"):]
    for needle in ("LO = 8.14×10^-13、HI = 2.22×10^-3", "種: `20261026`", "それぞれ ε を 10 個", "--eps-range <inside|above|below> 8.14e-13 2.22e-3 --coef-seed 20261026", "3 入力の合計 280 件（主食価格 100、物理量の月次 90、日次 90）", "予想（結果を見る前。判定には使わない）"):
        assert needle in sec, needle
