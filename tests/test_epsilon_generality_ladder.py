"""research/epsilon-generality/posthoc_eps_ladder.py の確認。

SYNTHETIC: 組み立てた行で、基準を超えた単位・ε の波が消えた単位の数え方、動いた単位の書き出し、梯子が定義域（0 < ε ≤ 1/100）に収まること、
小さな合成の入力での書き出し（同じ入力なら同じバイト）を確かめる。結論には使わない。
"""
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "research" / "epsilon-generality"
spec = importlib.util.spec_from_file_location("posthoc_eps_ladder", DIR / "posthoc_eps_ladder.py")
lad = importlib.util.module_from_spec(spec)
sys.modules["posthoc_eps_ladder"] = lad
spec.loader.exec_module(lad)
gen = lad.load_gen()


def er(decay, period=1.0, coef=1.0):
    return {"decay": decay, "period": period, "rmse": 0.0, "limit": 1.0, "settle_x": 1.0, "coefficient": coef, "at_start": False}


def row(boundary=True, over=None, lost=(), start="2020-01"):
    """梯子の ε すべてで基準の ε と同じ係数の単位。over の ε は係数を 1 倍ずらして基準を超えさせ、lost の ε は波を残さない。"""
    r = {"boundary": boundary, "country": "AAA", "variable": "v", "source": "s", "start": start, gen.ekey(gen.REF_EPS): er(gen.REF_EPS)}
    for e in lad.LADDER:
        r[gen.ekey(e)] = er(0.0 if e in lost else e, coef=2.0 if e in (over or ()) else 1.0)
    return r


def test_ladder_stays_inside_the_domain_and_every_epsilon_has_a_finite_threshold():
    assert all(0 < e <= 1e-2 for e in lad.LADDER) and list(lad.LADDER) == sorted(lad.LADDER) and 1e-2 in lad.LADDER and 1e-3 in lad.LADDER
    assert all(math.isfinite(gen.threshold("c2", e)) for e in lad.LADDER)


def test_dev_of_is_relative_to_the_reference_and_none_when_it_cannot_be_compared():
    r = row(over=(1e-3,))
    assert lad.dev_of(gen, r, 1e-3) == 1.0 and lad.dev_of(gen, r, 5e-4) == 0.0
    low = row(); low[gen.ekey(1e-3)] = er(1e-3, coef=0.25)
    assert lad.dev_of(gen, low, 1e-3) == 0.75 and lad.count_rows(gen, [low])["per_eps"][gen.ekey(1e-3)]["over"] == 1          # 小さいほうへのずれも数える
    assert lad.dev_of(gen, row(lost=(1e-3,)), 1e-3) is None
    r2 = row(); r2[gen.ekey(gen.REF_EPS)] = er(0.0)
    assert lad.dev_of(gen, r2, 1e-3) is None
    r3 = row(); r3[gen.ekey(1e-3)]["coefficient"] = None
    assert lad.dev_of(gen, r3, 1e-3) is None


def test_count_rows_counts_over_and_lost_for_boundary_units_only_and_lists_the_moved_ones():
    rows = [row() for _ in range(5)] + [row(over=(1e-3, 1e-2), start="2021-02"), row(lost=(1e-2,), start="2022-03"), row(boundary=False, over=(1e-3,))]
    c = lad.count_rows(gen, rows)
    assert c["boundary"] == 7 and c["moved_total"] == 2 and [m["start"] for m in c["moved"]] == ["2021-02", "2022-03"]
    over = {e: c["per_eps"][gen.ekey(e)]["over"] for e in lad.LADDER}
    lost = {e: c["per_eps"][gen.ekey(e)]["lost"] for e in lad.LADDER}
    assert over[1e-3] == 1 and over[1e-2] == 1 and sum(over.values()) == 2 and lost[1e-2] == 1 and sum(lost.values()) == 1
    assert [p["eps"] for p in c["moved"][0]["path"]] == list(lad.LADDER) and c["moved"][0]["path"][5]["dev"] == 1.0


def test_the_threshold_used_is_the_registered_one_at_1e_3_and_the_extension_above():
    ok = lambda dev, e: lad.count_rows(gen, [row() | {gen.ekey(e): er(e, coef=1.0 + dev)}])["per_eps"][gen.ekey(e)]["over"]
    t3, t2 = gen.threshold("c2", 1e-3), gen.threshold("c2", 1e-2)
    assert (t3, round(t2, 4)) == (0.02, 0.1170)
    assert ok(t3 * 0.99, 1e-3) == 0 and ok(t3 * 1.01, 1e-3) == 1                    # 登録した 0.02
    assert ok(t2 * 0.99, 1e-2) == 0 and ok(t2 * 1.01, 1e-2) == 1                    # 1/100 では延長した 11.7%


def test_count_rows_stops_listing_after_the_cap_but_keeps_the_total(monkeypatch):
    monkeypatch.setattr(lad, "MAX_LISTED", 3)
    c = lad.count_rows(gen, [row(over=(1e-3,)) for _ in range(5)])
    assert c["moved_total"] == 5 and len(c["moved"]) == 3 and c["per_eps"][gen.ekey(1e-3)]["over"] == 5
    assert "動いた単位は 5 個。上の 3 個だけ" in lad.render(gen, {"ladder": list(lad.LADDER), "sets": {"12": c | {"units": 5}}})


def small_csv(tmp_path):
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


def test_main_writes_the_same_bytes_twice_and_clean_waves_do_not_move(tmp_path):
    outs = []
    for name in ("a", "b"):
        out = tmp_path / name
        assert lad.main(["--csv", str(small_csv(tmp_path)), "--outdir", str(out), "--repo", str(ROOT)]) == 0
        outs.append(out)
    for n in ("posthoc_eps_ladder.json", "posthoc_eps_ladder.md"):
        assert (outs[0] / n).read_bytes() == (outs[1] / n).read_bytes(), n
    res = json.loads((outs[0] / "posthoc_eps_ladder.json").read_text(encoding="utf-8"))
    assert res["ladder"] == list(lad.LADDER) and list(res["sets"]) == [str(n) for n in gen.LENGTHS]
    assert all(s["units"] > 0 and s["moved_total"] == 0 and set(s["per_eps"]) == {gen.ekey(e) for e in lad.LADDER} for s in res["sets"].values())
    md = (outs[0] / "posthoc_eps_ladder.md").read_text(encoding="utf-8")
    assert "登録した基準の外" in md and "| 12 |" in md and "動いた単位" not in md


def test_readme_points_to_the_script():
    text = (DIR / "README.md").read_text(encoding="utf-8")
    assert "posthoc_eps_ladder.py" in text and "tests/test_epsilon_generality_ladder.py" in text
