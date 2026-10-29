"""条件の重なりの図（マスの格子と内訳の積み上げ棒）。

load_overlap は stdlib の経路だけを使う。numpy・polars・Chrome は要らない。
"""
import json
import random

import pytest

from dragowing.cli import main
from dragowing.htmlout import embed_json, figure_block, spec_from, standalone
from dragowing.overlap import B_COND, MAX_SETS, finalize_conditions, load_overlap
from dragowing.venn import BY_KEYS, MAX_SERIES, breakdown_figure, grid_figure, karnaugh, venn_figures


def make(tmp_path, n, units=60, seed=0):
    """n 個の集合（x1..x{n-1} > 0 と B クラス）で 12 球団 × 年の合成データ。"""
    rng = random.Random(seed)
    rows = [
        dict(team=f"t{i % 12}", team_name=f"球団{i % 12}", season=2013 + i % 5, league="C" if i % 12 < 6 else "P",
             upper_half=rng.random() < 0.5, **{f"x{k}": rng.randint(-2, 2) for k in range(1, n)})
        for i in range(units)
    ]
    path = tmp_path / "season.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    conds = [{"col": f"x{k}", "op": ">", "value": 0} for k in range(1, n)] + [dict(B_COND)]
    return load_overlap(path, conds, backend="stdlib")


@pytest.mark.parametrize("n", range(2, MAX_SETS + 1))
def test_karnaugh_places_every_region_once_and_neighbours_differ_by_one_set(n):
    rows, cols = karnaugh(n)
    assert len(rows) * len(cols) == 2**n
    assert len({r + c for r in rows for c in cols}) == 2**n
    for line in (rows, cols):
        for a, b in zip(line, line[1:]):
            assert sum(x != y for x, y in zip(a, b)) == 1


def test_karnaugh_four_sets_is_the_known_layout():
    # 行 (A,B) も列 (C,D) も 10, 11, 01, 00 の順（先頭の集合が入る側から）。
    rows, cols = karnaugh(4)
    text = lambda pats: ["".join("1" if b else "0" for b in p) for p in pats]  # noqa: E731
    assert text(rows) == text(cols) == ["10", "11", "01", "00"]


def test_karnaugh_needs_two_sets():
    with pytest.raises(ValueError):
        karnaugh(1)


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 8])
def test_grid_puts_each_region_count_in_its_cell(tmp_path, n):
    overlap = make(tmp_path, n, units=40, seed=n)
    heat = grid_figure(overlap)["data"][0]
    by_bits = {tuple(r["bits"]): r["count"] for r in overlap["regions"]}
    rows, cols = karnaugh(n)
    for ri, rp in enumerate(rows):
        for ci, cp in enumerate(cols):
            assert heat["z"][ri][ci] == by_bits[rp + cp]
            assert heat["customdata"][ri][ci]["count"] == by_bits[rp + cp]
    assert sum(map(sum, heat["z"])) == len(overlap["units"])


def test_grid_keeps_empty_regions_as_zero(tmp_path):
    overlap = make(tmp_path, 6, units=3)
    z = grid_figure(overlap)["data"][0]["z"]
    cells = [v for row in z for v in row]
    assert len(cells) == 64
    assert cells.count(0) >= 61  # 3 件しかないので空の領域がほとんど。None にも省略にもしない
    assert all(type(v) is int for v in cells)


@pytest.mark.parametrize("n", [3, 4, 6, 8])
def test_grid_frames_cover_exactly_the_cells_inside_each_set(tmp_path, n):
    overlap = make(tmp_path, n, units=30, seed=n)
    fig = grid_figure(overlap)
    rows, cols = karnaugh(n)
    shapes = fig["layout"]["shapes"]
    assert all(s["type"] == "rect" and s["xref"] == s["yref"] == "paper" for s in shapes)

    def covered(name, ri, ci):
        for s in (s for s in shapes if s["name"] == name):
            x_lo, x_hi = sorted((s["x0"] * len(cols) - 0.5, s["x1"] * len(cols) - 0.5))
            y_lo, y_hi = sorted(((1 - s["y0"]) * len(rows) - 0.5, (1 - s["y1"]) * len(rows) - 0.5))
            if x_lo <= ci <= x_hi and y_lo <= ri <= y_hi:
                return True
        return False

    for ri, rp in enumerate(rows):
        for ci, cp in enumerate(cols):
            for i, bit in enumerate(rp + cp):
                assert covered(f"S{i + 1}", ri, ci) == bit
    legend = [t for t in fig["data"][1:]]
    assert [t["name"].split(":")[0] for t in legend] == [f"S{i + 1}" for i in range(n)]
    assert all(t["x"] == [None] for t in legend)  # 空配列だと Plotly が凡例から落とす


def test_grid_does_not_draw_circles(tmp_path):
    fig = grid_figure(make(tmp_path, 4))
    assert "circle" not in json.dumps(fig)


def test_breakdown_sums_back_to_region_counts_and_folds_the_rest(tmp_path):
    overlap = make(tmp_path, 4, units=80)
    fig = breakdown_figure(overlap, "team", keep=("t11",))
    traces, meta = fig["data"], fig["layout"]["meta"]
    nonempty = sorted((r for r in overlap["regions"] if r["count"]), key=lambda r: -r["count"])
    labels = traces[0]["y"]
    assert len(labels) == len(nonempty)
    for i, region in enumerate(nonempty):
        assert sum(t["x"][i] for t in traces) == region["count"]
        assert labels[i].endswith(f"({region['count']})")
    assert sum(sum(t["x"]) for t in traces) == len(overlap["units"])
    names = [t["name"] for t in traces]
    assert "t11" in names  # keep は件数にかかわらず残す
    assert names[-1] == "その他" and len(names) == MAX_SERIES + 1
    assert len(meta["folded"]) == 12 - MAX_SERIES
    assert meta["empty_regions"] == len(overlap["regions"]) - len(nonempty)
    other = traces[-1]  # 「その他」は、まとめた値の行だけを数える。中身はホバーの文字（customdata）に出る
    assert sum(other["x"]) == sum(1 for u in overlap["units"] if u["team"] in meta["folded"])
    assert any(meta["folded"][0] in text for text in other["customdata"])


def test_breakdown_color_follows_the_value_not_its_rank(tmp_path):
    overlap = make(tmp_path, 3, units=60)
    fig = breakdown_figure(overlap, "team")
    shown = [t["meta"]["value"] for t in fig["data"] if t["meta"]["role"] == "series"]
    assert shown == sorted(shown)  # 昇順の並びで同じ順の色
    colors = [t["marker"]["color"] for t in fig["data"] if t["meta"]["role"] == "series"]
    assert len(set(colors)) == len(colors)


@pytest.mark.parametrize("by,names", [("league", ["C", "P"]), ("season", [str(2013 + k) for k in range(5)])])
def test_breakdown_without_folding_when_few_values(tmp_path, by, names):
    fig = breakdown_figure(make(tmp_path, 3), by)
    assert [t["name"] for t in fig["data"]] == names
    assert fig["layout"]["meta"]["folded"] == []


def test_breakdown_rejects_a_column_that_is_not_a_unit_field(tmp_path):
    overlap = make(tmp_path, 3)
    assert set(BY_KEYS) <= set(overlap["units"][0])
    for by in BY_KEYS:
        assert breakdown_figure(overlap, by)["data"]
    with pytest.raises(ValueError, match="内訳の列"):
        breakdown_figure(overlap, "x1")


def test_figures_survive_the_page_round_trip(tmp_path):
    figs = venn_figures(make(tmp_path, 5, units=50), "team", ("t0",))
    assert list(figs) == ["overlap_grid", "overlap_breakdown"]
    for name, fig in figs.items():
        json.loads(embed_json(fig))  # NaN・numpy を含まない
        page = standalone("t", figure_block(fig, name), plotly=True)
        assert spec_from(page, name) == json.loads(json.dumps(fig))


def test_condition_count_is_two_to_max_sets():
    rows = [{"upper_half": False}]
    cond = lambda k: {"col": "x", "op": ">", "value": k}  # noqa: E731
    assert len(finalize_conditions([cond(0)], [], rows)) == 2
    assert len(finalize_conditions([cond(k) for k in range(MAX_SETS - 1)], [], rows)) == MAX_SETS
    with pytest.raises(ValueError, match="条件集合"):
        finalize_conditions([cond(k) for k in range(MAX_SETS)], [], rows)  # B を足すと MAX_SETS + 1
    with pytest.raises(ValueError, match="条件集合"):
        finalize_conditions([dict(B_COND)], [], rows)


def test_cli_draws_five_sets_with_a_breakdown_on_the_recorded_cycle(tmp_path, aoi_root):
    out = tmp_path / "out"
    conds = ["rd,>,0", "rank_ra,<=,2", "rank_rf,<=,3", "wins_vs_pythag,<,0"]  # + B クラス = 5 集合
    args = ["--results", str(aoi_root / "cycles/c001-chunichi/outputs"), "--out", str(out), "--id", "P1",
            "--breakdown", "team", "--breakdown-keep", "d", "--overlap-backend", "stdlib"]
    for text in conds:
        args += ["--cond", text]
    assert main(args) == 0
    index = (out / "index.html").read_text(encoding="utf-8")
    grid = spec_from(index, "overlap_grid")
    breakdown = spec_from(index, "overlap_breakdown")
    assert len(grid["layout"]["meta"]["sets"]) == 5
    assert sum(map(sum, grid["data"][0]["z"])) == 168
    assert sum(sum(t["x"]) for t in breakdown["data"]) == 168
    assert "d" in [t["name"] for t in breakdown["data"]]  # 中日は件数にかかわらず残る
    assert '"type":"circle"' not in index
    # 条件が多すぎるときは図を書かずに止まる
    too_many = ["--results", str(aoi_root / "cycles/c001-chunichi/outputs"), "--out", str(tmp_path / "x")]
    for k in range(MAX_SETS):
        too_many += ["--cond", f"rd,>,{k}"]
    assert main(too_many) == 1

