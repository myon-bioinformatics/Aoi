"""cycles/c001-chunichi/exploratory/wave_eps_settle_coefficients.py の確認。

SYNTHETIC: 落ち着く位置が K/ε に小さな定数を足した形になるように作った行（実データではない）で、K を取り戻せること、
ε によらず一定の単位を分けること、K/ε からの外れ（絶対・相対）を出すことを確かめる。結論には使わない。
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("wave_eps_settle_coefficients", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps_settle_coefficients.py")
coef = importlib.util.module_from_spec(spec)
sys.modules["wave_eps_settle_coefficients"] = coef
spec.loader.exec_module(coef)

EPS = (1e-3, 1e-6, 1e-9)


def row(eps, settle, *, committed_decay=0.0, decay=None):
    return {"season": 2024, "team": "x", "eps_provisional": eps, "committed_wave_decay": committed_decay,
            "eps_wave_decay": eps if decay is None else decay, "eps_wave_settle_x": settle}


def table(units):
    """units: {(season, team): (K, c) または 定数の位置}。"""
    out = {}
    for e in EPS:
        out[e] = {}
        for key, v in units.items():
            s = v if isinstance(v, float) else v[1] + v[0] / e
            r = row(e, s)
            r["season"], r["team"] = key
            out[e][key] = r
    return out


def test_recovers_k_reports_the_miss_from_k_over_eps_and_flags_the_unit_that_is_settled_from_the_start():
    rows = coef.coefficients(table({(2014, "b"): (0.0815, 0.54), (2022, "l"): (1.595, 0.28), (2013, "g"): 0.062}))
    by = {(r["season"], r["team"]): r for r in rows}
    assert by[(2014, "b")]["K"] == pytest.approx(0.0815, rel=1e-6)
    assert by[(2014, "b")]["abs_miss"] == pytest.approx(0.54, abs=1e-6) and by[(2014, "b")]["rel_miss"] == pytest.approx(0.54 / (0.54 + 81.5), rel=1e-5)
    assert by[(2022, "l")]["K"] == pytest.approx(1.595, rel=1e-6) and by[(2022, "l")]["amp"] == pytest.approx(0.5 * 2.718281828 ** 1.595, rel=1e-6)
    assert by[(2013, "g")]["settled_at_start"] and by[(2013, "g")]["position"] == 0.062 and by[(2013, "g")]["K"] == 0.0
    assert by[(2013, "g")]["abs_miss"] is None and by[(2013, "g")]["rel_miss"] is None


def test_float_noise_between_epsilons_does_not_turn_a_constant_position_into_a_huge_k():
    t = table({(2013, "g"): 0.062})
    t[1e-9][(2013, "g")]["eps_wave_settle_x"] += 1e-12      # 丸めの差
    r = coef.coefficients(t)[0]
    assert r["settled_at_start"] and r["K"] == 0.0


def test_a_unit_that_is_not_on_the_boundary_is_left_out():
    t = table({(2014, "b"): (0.1, 0.5)})
    for e in EPS:
        t[e][(2024, "h")] = row(e, 0.067, committed_decay=0.5, decay=0.001)
        t[e][(2024, "h")].update(season=2024, team="h")
    assert [(r["season"], r["team"]) for r in coef.coefficients(t)] == [(2014, "b")]


def test_the_miss_grows_when_the_largest_eps_row_does_not_follow_k_over_eps():
    t = table({(2014, "b"): (0.1, 0.5)})
    r0 = coef.coefficients(t)[0]
    assert (r0["abs_miss"], r0["rel_miss"]) == (pytest.approx(0.5, abs=1e-6), pytest.approx(0.5 / 100.5, rel=1e-5))
    t[1e-3][(2014, "b")]["eps_wave_settle_x"] += 5.0       # ε = 1e-3 の行だけ式から外す
    r = coef.coefficients(t)[0]
    assert (r["abs_miss"], r["rel_miss"]) == (pytest.approx(5.5, abs=1e-6), pytest.approx(5.5 / 105.5, rel=1e-5))


def test_refuses_one_eps_and_a_row_where_the_eps_wave_was_not_chosen():
    with pytest.raises(ValueError):
        coef.coefficients({1e-6: table({(2014, "b"): (0.1, 0.5)})[1e-6]})
    t = table({(2014, "b"): (0.1, 0.5)})
    t[1e-6][(2014, "b")]["eps_wave_decay"] = 0.5
    with pytest.raises(ValueError):
        coef.coefficients(t)


def test_cli_writes_json_and_markdown(tmp_path):
    t = table({(2014, "b"): (0.0815, 0.54), (2013, "g"): 0.062})
    files = []
    for e, rows in t.items():
        p = tmp_path / f"wave_eps_rows_{e:g}.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows.values()) + "\n", encoding="utf-8")
        files.append(str(p))
    assert coef.main(["--rows", *files, "--out-json", str(tmp_path / "c.json"), "--out-md", str(tmp_path / "c.md")]) == 0
    data = json.loads((tmp_path / "c.json").read_text(encoding="utf-8"))
    assert data["eps"] == [1e-9, 1e-6, 1e-3] and len(data["units"]) == 2
    md = (tmp_path / "c.md").read_text(encoding="utf-8")
    assert md.startswith("# 落ち着く位置 ≈ K/ε") and "| 2014 | b |" in md
    assert coef.main(["--rows", files[0], files[0], "--out-json", str(tmp_path / "d.json"), "--out-md", str(tmp_path / "d.md")]) == 2
