"""cycles/c001-chunichi/exploratory/wave_eps_settle_coefficients.py の確認。

SYNTHETIC: 落ち着く位置が（係数 / ε）に小さな定数を足した形になるように作った行（実データではない）で、
ε = a × 10^-n の書き方、「係数 × 10^n」の係数が ε を替えても動かないこと（a を替えれば 1/a 倍になること）、
ε によらず一定の単位を分けること、最小の ε の係数で言い当てたときの外れ（絶対・相対）を出すことを確かめる。結論には使わない。
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("wave_eps_settle_coefficients", ROOT / "cycles" / "c001-chunichi" / "exploratory" / "wave_eps_settle_coefficients.py")
coef = importlib.util.module_from_spec(spec)
sys.modules["wave_eps_settle_coefficients"] = coef
spec.loader.exec_module(coef)

EPS = (1e-3, 1e-6, 1e-9)
INVALID_EPS = (float("nan"), float("inf"), float("-inf"), 0.0, -1e-6)


def row(eps, settle, *, committed_decay=0.0, decay=None):
    return {"season": 2024, "team": "x", "eps_provisional": eps, "committed_wave_decay": committed_decay,
            "eps_wave_decay": eps if decay is None else decay, "eps_wave_settle_x": settle}


def table(units, eps_list=EPS):
    """units: {(season, team): (係数 k, 上乗せ c) または 定数の位置}。位置は c + k / ε。"""
    out = {}
    for e in eps_list:
        out[e] = {}
        for key, v in units.items():
            s = v if isinstance(v, float) else v[1] + v[0] / e
            r = row(e, s)
            r["season"], r["team"] = key
            out[e][key] = r
    return out


def write_rows(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


@pytest.mark.parametrize("replacement_settle", [1.0, 2.0])
def test_load_rejects_identical_and_conflicting_duplicate_units(tmp_path, replacement_settle):
    path = write_rows(tmp_path / "rows.jsonl", [row(1e-6, 1.0), row(1e-6, replacement_settle)])
    with pytest.raises(ValueError, match="単位が重複") as exc:
        coef.load(path)
    assert f"{path}:2:" in str(exc.value) and "(2024, 'x')" in str(exc.value)


def test_load_preserves_distinct_seasons_and_teams_and_ignores_blank_lines(tmp_path):
    units = table({(2023, "x"): (0.1, 0.5), (2024, "x"): (0.2, 0.5), (2024, "y"): 0.062})[1e-6]
    path = write_rows(tmp_path / "rows.jsonl", units.values())
    path.write_text("\n" + path.read_text(encoding="utf-8") + " \n", encoding="utf-8")
    assert coef.load(path) == (1e-6, units)


@pytest.mark.parametrize("eps", INVALID_EPS + (True, None, "0.001"))
def test_load_rejects_invalid_eps_on_any_row(tmp_path, eps):
    invalid = row(eps, 2.0)
    invalid["team"] = "y"
    path = write_rows(tmp_path / "rows.jsonl", [row(1e-6, 1.0), invalid])
    with pytest.raises(ValueError, match="有限の正数") as exc:
        coef.load(path)
    assert f"{path}:2:" in str(exc.value)


@pytest.mark.parametrize("rows", [[], [row(1e-6, 1.0), dict(row(1e-3, 2.0), team="y")]])
def test_load_requires_exactly_one_eps(tmp_path, rows):
    with pytest.raises(ValueError, match="ε が 1 つに決まらない"):
        coef.load(write_rows(tmp_path / "rows.jsonl", rows))


@pytest.mark.parametrize("eps", INVALID_EPS)
def test_numeric_entry_points_reject_nonfinite_and_nonpositive_eps(eps):
    with pytest.raises(ValueError, match="有限の正数"):
        coef.eps_form(eps)
    # Validate the keys before sorting or looking up any wave data.
    with pytest.raises(ValueError, match="有限の正数"):
        coef.coefficients({1e-6: {}, eps: {}})


@pytest.mark.parametrize("eps", EPS)
@pytest.mark.parametrize("change", ["missing", "extra", "replacement"])
@pytest.mark.parametrize("committed_decay", [0.0, 0.5])
def test_all_eps_must_have_identical_unit_sets_even_for_nonboundary_units(eps, change, committed_decay):
    t = table({(2014, "b"): (0.1, 0.5), (2024, "x"): (0.2, 0.5)})
    for rows in t.values():
        rows[(2024, "x")]["committed_wave_decay"] = committed_decay
    if change in ("missing", "replacement"):
        del t[eps][(2024, "x")]
    if change in ("extra", "replacement"):
        t[eps][(2024, "y")] = dict(row(eps, 1.0, committed_decay=committed_decay), team="y")
    with pytest.raises(ValueError, match="単位集合") as exc:
        coef.coefficients(t)
    assert "欠落=" in str(exc.value) and "余剰=" in str(exc.value)
    assert "2024" in str(exc.value)


def test_unit_sets_are_validated_before_computing_any_coefficient():
    with pytest.raises(ValueError, match="単位集合"):
        coef.coefficients({1e-9: {(2024, "x"): {}}, 1e-6: {}})


def test_eps_is_written_as_a_times_ten_to_the_minus_n_and_positions_as_mantissa_times_power_of_ten():
    assert coef.eps_form(1e-6) == (1.0, 6) and coef.eps_form(1e-9) == (1.0, 9) and coef.eps_form(0.1) == (1.0, 1)
    assert coef.eps_form(3e-2) == (3.0, 2) and coef.eps_form(5e-3) == (5.0, 3) and coef.eps_form(7e-2) == (7.0, 2)   # 0.07 * 100 は 7.000000000000001
    a, n = coef.eps_form(7.23e-4)
    assert a == pytest.approx(7.23, rel=1e-9) and n == 4
    assert coef.sci(81500.0) == "8.15×10^4" and coef.sci(0.0774) == "7.74×10^-2" and coef.sci(9.996e3) == "1.00×10^4"


def test_coefficient_stays_put_when_eps_gets_ten_times_smaller_and_the_miss_is_reported():
    rows = coef.coefficients(table({(2014, "b"): (0.0815, 0.54), (2022, "l"): (1.595, 0.28), (2013, "g"): 0.062}))
    by = {(r["season"], r["team"]): r for r in rows}
    b = by[(2014, "b")]
    assert b["coefficient"] == pytest.approx(0.0815, rel=1e-6)
    assert [p["n"] for p in b["by_eps"]] == [9, 6, 3] and all(p["a"] == 1.0 for p in b["by_eps"])
    assert [p["coefficient"] for p in b["by_eps"]] == pytest.approx([0.0815, 0.0815, 0.0815 + 0.54e-3], rel=1e-5)
    assert b["abs_miss"] == pytest.approx(0.54, abs=1e-6) and b["rel_miss"] == pytest.approx(0.54 / (0.54 + 81.5), rel=1e-5)
    assert by[(2022, "l")]["coefficient"] == pytest.approx(1.595, rel=1e-6)
    assert abs(by[(2022, "l")]["amp"] - 0.5 * math.exp(1.595)) < 1e-6 and abs(b["amp"] - 0.5 * math.exp(0.0815)) < 1e-6   # 振れ幅 = 0.5 × exp(係数)
    g = by[(2013, "g")]
    assert g["settled_at_start"] and g["position"] == 0.062 and g["coefficient"] is None and g["by_eps"] == []
    assert g["abs_miss"] is None and g["rel_miss"] is None and g["amp"] is None


def test_coefficient_is_one_over_a_when_eps_starts_with_a_five():
    eps = (5e-3, 5e-6, 5e-9)
    r = coef.coefficients(table({(2014, "b"): (0.0815, 0.54)}, eps))[0]
    assert [(p["a"], p["n"]) for p in r["by_eps"]] == [(5.0, 9), (5.0, 6), (5.0, 3)]
    assert r["coefficient"] == pytest.approx(0.0815 / 5, rel=1e-6)
    assert r["abs_miss"] == pytest.approx(0.54, abs=1e-6)       # a を掛け替えても、外れは位置の上乗せ分だけ


def test_float_noise_between_epsilons_does_not_turn_a_constant_position_into_a_huge_coefficient():
    t = table({(2013, "g"): 0.062})
    t[1e-9][(2013, "g")]["eps_wave_settle_x"] += 1e-12      # 丸めの差
    r = coef.coefficients(t)[0]
    assert r["settled_at_start"] and r["coefficient"] is None


def test_a_unit_that_is_not_on_the_boundary_is_left_out():
    t = table({(2014, "b"): (0.1, 0.5)})
    for e in EPS:
        t[e][(2024, "h")] = row(e, 0.067, committed_decay=0.5, decay=0.001)
        t[e][(2024, "h")].update(season=2024, team="h")
    assert [(r["season"], r["team"]) for r in coef.coefficients(t)] == [(2014, "b")]


def test_the_miss_grows_when_the_largest_eps_row_does_not_follow_the_coefficient():
    t = table({(2014, "b"): (0.1, 0.5)})
    r0 = coef.coefficients(t)[0]
    assert (r0["abs_miss"], r0["rel_miss"]) == (pytest.approx(0.5, abs=1e-6), pytest.approx(0.5 / 100.5, rel=1e-5))
    t[1e-3][(2014, "b")]["eps_wave_settle_x"] += 5.0       # ε = 1e-3 の行だけ形から外す
    r = coef.coefficients(t)[0]
    assert (r["abs_miss"], r["rel_miss"]) == (pytest.approx(5.5, abs=1e-6), pytest.approx(5.5 / 105.5, rel=1e-5))


def test_refuses_one_eps_and_a_row_where_the_eps_wave_was_not_chosen():
    with pytest.raises(ValueError):
        coef.coefficients({1e-6: table({(2014, "b"): (0.1, 0.5)})[1e-6]})
    t = table({(2014, "b"): (0.1, 0.5)})
    t[1e-6][(2014, "b")]["eps_wave_decay"] = 0.5
    with pytest.raises(ValueError):
        coef.coefficients(t)


def test_cli_writes_json_and_markdown_without_a_separate_constant(tmp_path):
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
    assert md.startswith("# 落ち着く位置 = 係数 × 10^n") and "ε = 1×10^-9" in md
    assert "| 2014 | b | 8.20×10^1 | 8.15×10^4 | 8.15×10^7 | 0.0815 | 0.542 |" in md       # 指数が 3 ずつ動き、係数は 8.15（ε = 1e-3 だけ上乗せ分で 8.20）
    assert "K" not in md and "K" not in json.dumps(data)
    assert coef.main(["--rows", files[0], files[0], "--out-json", str(tmp_path / "d.json"), "--out-md", str(tmp_path / "d.md")]) == 2


@pytest.mark.parametrize("existing_outputs", [False, True])
@pytest.mark.parametrize("defect", ["duplicate", "extra", "missing", "repeated_eps", *INVALID_EPS])
def test_cli_invalid_inputs_do_not_create_or_overwrite_outputs(tmp_path, capsys, defect, existing_outputs):
    t = table({(2014, "b"): (0.1, 0.5), (2024, "x"): (0.2, 0.5)})
    inputs = [list(rows.values()) for rows in t.values()]
    if defect == "duplicate":
        inputs[0].append(dict(inputs[0][0]))
    elif defect == "extra":
        inputs[0].append(dict(row(EPS[0], 2.0), team="y"))
    elif defect == "missing":
        inputs[0].pop()
    elif defect == "repeated_eps":
        inputs[0] = inputs[1]
    else:
        for r in inputs[0]:
            r["eps_provisional"] = defect
    files = [str(write_rows(tmp_path / f"rows_{i}.jsonl", rows)) for i, rows in enumerate(inputs)]
    outputs = [tmp_path / "c.json", tmp_path / "c.md"]
    if existing_outputs:
        for path in outputs:
            path.write_text("unchanged\n", encoding="utf-8")
    assert coef.main(["--rows", *files, "--out-json", str(outputs[0]), "--out-md", str(outputs[1])]) == 2
    captured = capsys.readouterr()
    assert captured.err.strip() and not captured.out
    for path in outputs:
        if existing_outputs:
            assert path.read_text(encoding="utf-8") == "unchanged\n"
        else:
            assert not path.exists()


def test_committed_inputs_reproduce_existing_json_and_markdown_exactly(tmp_path):
    exploratory = ROOT / "cycles" / "c001-chunichi" / "exploratory"
    files = sorted((exploratory / "wave_eps_trial_results").glob("wave_eps_rows_*.jsonl"))
    by_eps = dict(coef.load(path) for path in files)
    assert len(files) == len(by_eps) == 3
    assert all(len(units) == 156 for units in by_eps.values())
    out_json, out_md = tmp_path / "c.json", tmp_path / "c.md"
    assert coef.main(["--rows", *map(str, files), "--out-json", str(out_json), "--out-md", str(out_md)]) == 0
    saved = exploratory / "wave_eps_sensitivity_results"
    assert out_json.read_bytes() == (saved / "wave_eps_settle_coefficients.json").read_bytes()
    assert out_md.read_bytes() == (saved / "wave_eps_settle_coefficients.md").read_bytes()


def input_files(tmp_path, units):
    return [str(write_rows(tmp_path / f"rows_{e:g}.jsonl", rows.values())) for e, rows in table(units).items()]


@pytest.mark.parametrize("units", [{(2013, "g"): 0.062, (2019, "h"): 0.060}, {}])
def test_cli_handles_inputs_where_no_unit_moves_with_eps(tmp_path, units):
    """全単位が最初から一定（または境界の単位が 0）でも、集計対象が空だからといって落ちない。"""
    files = input_files(tmp_path, units or {(2024, "x"): 0.5})
    if not units:                                   # 境界の単位が 1 つもない入力
        for path in files:
            rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()]
            write_rows(Path(path), [dict(r, committed_wave_decay=0.5, eps_wave_decay=0.001) for r in rows])
    out_json, out_md = tmp_path / "c.json", tmp_path / "c.md"
    assert coef.main(["--rows", *files, "--out-json", str(out_json), "--out-md", str(out_md)]) == 0
    data = json.loads(out_json.read_text(encoding="utf-8"))
    md = out_md.read_text(encoding="utf-8")
    assert len(data["units"]) == len(units) and all(u["settled_at_start"] for u in data["units"])
    assert md.count(coef.NONE) == 2 and f"減衰 0 だった単位: {len(units)}。落ち着く位置が最初から ε によらず一定: {len(units)}" in md
    for r in units:
        assert f"| {r[0]} | {r[1]} | （最初から一定。位置" in md


def test_cli_builds_both_texts_before_writing_either_output(tmp_path, monkeypatch):
    files = input_files(tmp_path, {(2014, "b"): (0.1, 0.5)})
    outputs = [tmp_path / "c.json", tmp_path / "c.md"]
    for path in outputs:
        path.write_text("unchanged\n", encoding="utf-8")

    def broken(rows, eps):
        raise RuntimeError("render failed")

    monkeypatch.setattr(coef, "render", broken)
    with pytest.raises(RuntimeError, match="render failed"):
        coef.main(["--rows", *files, "--out-json", str(outputs[0]), "--out-md", str(outputs[1])])
    assert [p.read_text(encoding="utf-8") for p in outputs] == ["unchanged\n", "unchanged\n"]
