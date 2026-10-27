"""research/epsilon-generality/README.md の「倍率を帯から選ぶ確認（第 5 回）」の事前登録の確認。

SYNTHETIC: 登録した倍率が種と規則から出ること、予想に書いた数が事後の格子の JSON と合うこと、実行の書式が README と同じであること、
小さな合成の入力で同じ書式が通り、帯の内側の倍率が書き出されることを確かめる。結果の当否は確かめない（結論には使わない）。
"""
import csv
import importlib.util
import json
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
SEED, LO, HI, COUNT = 20261027, 1e-7, 1e-4, 10
REGISTERED_5 = [9.57e-5, 5.98e-5, 3.16e-5, 8.91e-6, 5.00e-6, 1.92e-6, 9.50e-7, 8.63e-7, 7.66e-7, 1.03e-7]


def section():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    return text[text.index("## 倍率を帯から選ぶ確認（第 5 回）: 事前登録"):]


def test_the_registered_scales_come_from_the_seed_and_the_rule_and_are_listed_in_the_readme():
    d = gen.draw_coefficients(COUNT, SEED, "scale", gen.make_region("scale", "inside", LO, HI))
    assert [x["value"] for x in d] == REGISTERED_5 and all(LO <= v <= HI for v in REGISTERED_5)
    assert ", ".join(gen.pow10_text(v) for v in REGISTERED_5) in section()
    assert gen.make_draws(0, COUNT, SEED, None, ("inside", LO, HI))["scales"] == d                   # 実行と同じ呼び方


def test_the_seed_is_the_decision_date_and_differs_from_the_earlier_rounds():
    assert SEED == 20261027 and SEED != gen.SEED


def test_the_registration_names_the_range_the_seed_the_count_and_the_command():
    sec = section()
    for needle in ("inside、LO = 1×10^-7、HI = 1×10^-4（両端を含む）", "倍率を 10 個", "種: `20261027`", "予想（結果を見る前。判定には使わない）",
                   "--random-scales 10 --scale-range inside 1e-7 1e-4 --coef-seed 20261027", "`eps_generality.py` は変えない",
                   "倍率は報告だけで基準はない"):
        assert needle in sec, needle
    assert "（1e-5 以上 3 個、1e-6 以上 1e-5 未満 3 個、1e-7 以上 1e-6 未満 4 個）" in sec
    assert "PR #24 は触らない" in sec and "「矛盾する材料はなかった」とは書かない" in sec


def test_the_numbers_in_the_predictions_are_the_numbers_of_the_posthoc_grid_json():
    st = json.loads((DIR / "results-random" / "staple" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))["staple"]
    ph = json.loads((DIR / "results-physical" / "posthoc_scale_tolerance.json").read_text(encoding="utf-8"))
    sec = section()
    n_hi = sum(v >= 1e-5 for v in REGISTERED_5)
    n_mid = sum(1e-6 <= v < 1e-5 for v in REGISTERED_5)
    n_lo = sum(v < 1e-6 for v in REGISTERED_5)
    assert (n_hi, n_mid, n_lo) == (3, 3, 4)
    for name, d in (("主食価格", st), ("物理量の月次", ph["monthly"]), ("物理量の日次", ph["daily"])):
        c = {k: v["forms_changed"] for k, v in d["tolerance_unchanged"].items()}
        line = (f"- {name}: 1e-5 以上（{n_hi} 個）は {c['0.0001']}〜{c['1e-05']}、1e-6 以上 1e-5 未満（{n_mid} 個）は {c['1e-05']}〜{c['1e-06']}、"
                f"1e-7 以上 1e-6 未満（{n_lo} 個）は {c['1e-06']}〜{c['1e-07']}")
        assert line in sec, line
        assert c["0.0001"] <= c["1e-05"] <= c["1e-06"] <= c["1e-07"]                                    # 格子の値は倍率が小さいほど多い（予想 (a) の土台）
    assert ph["monthly"]["tolerance_unchanged"]["1e-05"]["forms_changed"] == 0                         # 予想 (c)


def small_csv(tmp_path):
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


def test_the_registered_command_runs_writes_the_registered_scales_and_no_epsilons_and_is_byte_reproducible(tmp_path):
    flags = ("--random-scales", "10", "--scale-range", "inside", "1e-7", "1e-4", "--coef-seed", "20261027")
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert gen.main(["--csv", str(small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT), *flags]) == 0
        outs.append(out)
    for n in sorted(p.name for p in outs[0].iterdir()):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    j = json.loads((outs[0] / "eps_generality.json").read_text(encoding="utf-8"))
    rc = j["random_coefficients"]
    assert rc["seed"] == SEED and rc["eps"] == [] and [d["value"] for d in rc["scales"]] == REGISTERED_5
    assert rc["regions"] == {"scales": {"mode": "inside", "lo": LO, "hi": HI}}
    assert set(j["scales"]) >= {f"{v:g}" for v in REGISTERED_5} and j["control"]["pass"] and j["repeat_identical"]
