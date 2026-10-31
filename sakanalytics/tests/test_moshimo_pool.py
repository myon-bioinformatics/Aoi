import itertools
import json
import operator
from pathlib import Path

import pytest

import moshimo_box as mb
import moshimo_pool as mp

pl = pytest.importorskip("polars")

PY_OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}

ROWS = [  # x counts up, z alternates in a pattern, win is the target
    {"season": 2001 + i, "team": "t", "x": i + 1, "z": z, "win": w}
    for i, (z, w) in enumerate([(0, False), (1, False), (0, False), (1, True), (1, False), (0, True), (1, True), (0, True)])
]
TARGET = [{"col": "win", "op": "==", "value": True}]
CANDIDATES = [
    {"col": "x", "op": "<", "value": 4}, {"col": "x", "op": "<", "value": 7}, {"col": "x", "op": ">=", "value": 1},  # last: always true
    {"col": "z", "op": "==", "value": 1}, {"col": "z", "op": "==", "value": 0},
]


def frame(rows=ROWS):
    return pl.DataFrame(rows)


def brute_force(rows, target, candidates, max_terms, max_conds):
    """Every formula judged unit by unit in plain Python (no bit sets): (cells, units picked, conditions)."""
    def holds(c, row):
        return PY_OPS[c["op"]](row[c["col"]], c["value"])

    terms = [t for k in range(1, max_conds + 1) for t in itertools.combinations(candidates, k)
             if len({c["col"] for c in t}) == k]
    out = []
    for k in range(1, max_terms + 1):
        for formula in itertools.combinations(terms, k):
            picked = {i for i, r in enumerate(rows) if any(all(holds(c, r) for c in t) for t in formula)}
            goal = {i for i, r in enumerate(rows) if all(holds(c, r) for c in target)}
            cells = (len(picked & goal), len(picked - goal), len(goal - picked), len(rows) - len(picked | goal))
            out.append((cells, frozenset(picked), sum(len(t) for t in formula)))
    return out


def mcc_of(cells):
    a, b, c, d = cells
    q = (a + b) * (a + c) * (b + d) * (c + d)
    return (a * d - b * c) / q ** 0.5 if q else 0.0


def zero_pattern(cells):
    return "".join(cell for cell, v in zip("abcd", cells) if v == 0) or "interior"


def test_every_formula_is_counted_as_a_plain_unit_by_unit_check_would_count_it():
    expected = brute_force(ROWS, TARGET, CANDIDATES, 2, 2)
    r = mp.scan(frame(), TARGET, CANDIDATES, max_terms=2, max_conds=2, top=10_000, listing=0)
    assert r["formulas"] == len(expected) == 66 and r["terms"] == 11 and r["units"] == 8 and r["target_units"] == 4
    assert sorted((x["tp"], x["fp"], x["fn"], x["tn"]) for x in r["top_rows"]) == sorted(c for c, _, _ in expected)
    by_pattern = {t["zero_cells"]: t for t in r["tables"]}
    for pattern in {zero_pattern(c) for c, _, _ in expected}:
        mine = [e for e in expected if zero_pattern(e[0]) == pattern]
        assert by_pattern[pattern]["formulas"] == len(mine)
        assert by_pattern[pattern]["unit_sets"] == len({picked for _, picked, _ in mine})
    assert set(by_pattern) == {zero_pattern(c) for c, _, _ in expected}
    assert sum(t["share"] for t in r["tables"]) == pytest.approx(1.0)


def test_a_term_never_uses_a_column_twice_but_a_formula_may():
    r = mp.scan(frame(), TARGET, CANDIDATES, max_terms=1, max_conds=2, top=100, listing=0)
    assert r["terms"] == 11 and r["formulas"] == 11  # 5 singles + (3 x-conditions) * (2 z-conditions) pairs
    r2 = mp.scan(frame(), TARGET, CANDIDATES, max_terms=2, max_conds=1, top=100, listing=0)
    assert r2["terms"] == 5 and r2["formulas"] == 5 + 10
    assert any(len({c["col"] for g in row["if_any"] for c in g}) < sum(len(g) for g in row["if_any"]) for row in r2["top_rows"])


def test_the_top_rows_are_the_best_by_mcc_then_fewer_conditions():
    expected = brute_force(ROWS, TARGET, CANDIDATES, 2, 2)
    r = mp.scan(frame(), TARGET, CANDIDATES, top=7, listing=0)
    rows = r["top_rows"]
    assert len(rows) == 7 and r["cut"] == rows[-1]["mcc"]
    keys = [(-round(x["mcc"], 12), x["conditions"]) for x in rows]
    assert keys == sorted(keys)
    best = sorted(((-round(mcc_of(c), 12), n) for c, _, n in expected))[:7]
    assert keys == best
    assert mp.scan(frame(), TARGET, CANDIDATES, top=1000, listing=0)["cut"] is None  # fewer formulas than the cut asks for


def test_an_empty_margin_is_counted_where_rule_search_scores_it_zero_without_saying():
    expected = brute_force(ROWS, TARGET, CANDIDATES, 2, 2)
    r = mp.scan(frame(), TARGET, CANDIDATES, top=5, listing=0)
    always_true = [c for c, _, _ in expected if c[2] + c[3] == 0]  # nothing outside the formula: the inverse has no unit
    assert always_true and r["silent_zero_mcc"] == sum(1 for c, _, _ in expected if mcc_of(c) == 0.0 and
                                                       0 in ((c[0] + c[1]), (c[0] + c[2]), (c[1] + c[3]), (c[2] + c[3])))
    row = next(t for t in r["tables"] if t["zero_cells"] == "cd")
    assert row["at_boundary"] == {"contrapositive": 0.0, "converse": 1.0, "inverse": None}


def test_which_forms_a_zero_cell_puts_on_the_boundary():
    expected = {"a": {"original": 0.0, "converse": 0.0}, "b": {"original": 1.0, "contrapositive": 1.0},
                "c": {"converse": 1.0, "inverse": 1.0}, "d": {"contrapositive": 0.0, "inverse": 0.0}}
    for cell, forms in expected.items():
        assert mp._boundary(*mp._filled_except(cell)) == forms
    assert mp._boundary(*mp._filled_except("")) == {}
    assert mp._boundary(*mp._filled_except("ab")) == {"original": None, "converse": 0.0, "contrapositive": 1.0}


def test_the_boundary_listing_has_ranks_by_mcc_and_nothing_substituted():
    expected = brute_force(ROWS, TARGET, CANDIDATES, 2, 2)
    scores = [round(mcc_of(c), 12) for c, _, _ in expected]
    r = mp.scan(frame(), TARGET, CANDIDATES, top=5, listing=6)
    best = r["boundary"]["best"]
    assert len(best) == 6 and r["boundary"]["formulas"] == sum(1 for c, _, _ in expected if 0 in c)
    assert r["boundary"]["unit_sets"] == len({p for c, p, _ in expected if 0 in c})
    for row in best:
        cells = (row["tp"], row["fp"], row["fn"], row["tn"])
        assert 0 in cells and row["zero_cells"] == zero_pattern(cells)
        assert row["rank"] == 1 + sum(1 for s in scores if s > round(row["mcc"], 12))  # ties share a rank
        assert row["at_boundary"] == {f: v for f, v in mb.rates(*cells).items() if v is None or v in (0.0, 1.0)}
    assert [b["mcc"] for b in best] == sorted((b["mcc"] for b in best), reverse=True)
    assert r["boundary"]["in_top"] == sum(1 for row in r["top_rows"] if row["zero_cells"])


def test_a_pool_row_can_be_given_to_the_box_when_it_has_no_boundary():
    r = mp.scan(frame(), TARGET, CANDIDATES, top=50, listing=0)
    inner = next(row for row in r["top_rows"] if row["zero_cells"] == "")
    dials = mb.anchor(inner)
    table = mb.build(**dials)
    assert tuple(table["cells"].values()) == (inner["tp"], inner["fp"], inner["fn"], inner["tn"])
    edge = next(row for row in r["top_rows"] if row["zero_cells"])
    with pytest.raises(mb.MoshimoError):  # the box still refuses the boundary
        mb.build(**mb.anchor(edge))


def test_units_follow_rule_search_exclusions_need_a_reason_and_only_used_columns_may_not_be_empty(tmp_path):
    rows = [{"season": 2019, "team": "a", "x": 1, "z": 1}, {"season": 2020, "team": "a", "x": 2, "z": 1},
            {"season": 2021, "team": "a", "x": None, "z": 1}, {"season": 2022, "team": "a", "x": 4, "z": None}]
    path = tmp_path / "season.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    df = mp.load_units(path, [{"season": 2020, "reason": "short season"}], ["x"])
    assert df["season"].to_list() == [2019, 2022]  # 2020 excluded, 2021 has no x; 2022's empty z is not a used column
    with pytest.raises(mp.PoolError, match="needs a reason"):
        mp.load_units(path, [{"season": 2020, "reason": " "}], ["x"])
    with pytest.raises(mp.PoolError, match="no such column"):
        mp.load_units(path, [], ["nope"])


@pytest.mark.parametrize("bad", [{"col": "x", "op": "~", "value": 1}, {"col": "x", "op": "<"}, "x < 1"])
def test_a_malformed_condition_is_refused(bad):
    with pytest.raises(mp.PoolError, match="condition"):
        mp.scan(frame(), TARGET, [bad])


@pytest.mark.parametrize("top", [0, -1, True, 2.0, None])
def test_top_must_be_a_positive_integer(top):
    with pytest.raises(mp.PoolError, match="top"):
        mp.scan(frame(), TARGET, CANDIDATES, top=top)


def test_cli_prints_the_census_and_writes_json(tmp_path, capsys):
    season = tmp_path / "season.jsonl"
    season.write_text("\n".join(json.dumps(r) for r in ROWS), encoding="utf-8")
    config = tmp_path / "analysis.toml"
    config.write_text('[[exclude]]\nseason = 2001\nreason = "test"\n', encoding="utf-8")
    cands = tmp_path / "cands.toml"
    cands.write_text('target = [{ col = "win", op = "==", value = true }]\nmax_terms = 2\nmax_conds = 1\n'
                     + "".join(f'[[candidate]]\ncol = "{c["col"]}"\nop = "{c["op"]}"\nvalue = {c["value"]}\n' for c in CANDIDATES),
                     encoding="utf-8")
    out = tmp_path / "sub" / "pool.json"
    rc = mp.main(["--season", str(season), "--config", str(config), "--candidates", str(cands), "--top", "3",
                  "--list", "2", "--json", str(out)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "units 7" in text and "different unit sets" in text and "on the boundary" in text and "rank by MCC" in text
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["units"] == 7 and data["formulas"] == 15 and len(data["top_rows"]) == 3 and len(data["boundary"]["best"]) == 2


@pytest.mark.parametrize("args", [["--season", "nope.jsonl"], ["--candidates", "nope.toml"]])
def test_cli_missing_files_are_a_message_not_a_traceback(tmp_path, capsys, args):
    base = {"--season": str(tmp_path / "s.jsonl"), "--config": str(tmp_path / "c.toml"), "--candidates": str(tmp_path / "k.toml")}
    base.update(dict(zip(args[::2], args[1::2])))
    with pytest.raises(SystemExit) as exc:
        mp.main([x for kv in base.items() for x in kv])
    assert exc.value.code == 2 and "Error" in capsys.readouterr().err


@pytest.mark.parametrize("candidates,rules", [("rule_candidates.toml", "rules.jsonl"), ("rule_candidates_r21.toml", "rules_r21.jsonl")])
def test_the_top_rows_are_the_recorded_rule_search_output(aoi_root, candidates, rules):
    import tomllib

    cycle = aoi_root / "cycles" / "c001-chunichi"
    needed = [cycle / "outputs" / "season.jsonl", cycle / "analysis.toml", cycle / candidates, cycle / "outputs" / rules]
    if not all(p.is_file() for p in needed):
        pytest.skip("the c001 rule_search inputs and recorded output are not in this Aoi")
    spec = tomllib.loads((cycle / candidates).read_text(encoding="utf-8"))
    cfg = tomllib.loads((cycle / "analysis.toml").read_text(encoding="utf-8"))
    cols = sorted({c["col"] for c in [*spec["target"], *spec["candidate"]]})
    result = mp.scan(mp.load_units(cycle / "outputs" / "season.jsonl", cfg.get("exclude", []), cols), spec["target"],
                     spec["candidate"], max_terms=int(spec["max_terms"]), max_conds=int(spec["max_conds"]), top=20, listing=3)
    recorded = [json.loads(line) for line in (cycle / "outputs" / rules).read_text(encoding="utf-8").splitlines() if line]
    assert len(recorded) == 20
    for mine, theirs in zip(result["top_rows"], recorded):
        assert {k: mine[k] for k in ("if_any", "conditions", "tp", "fp", "fn", "tn")} == \
            {k: theirs[k] for k in ("if_any", "conditions", "tp", "fp", "fn", "tn")}
        assert mine["mcc"] == pytest.approx(theirs["mcc"], abs=1e-12)
    assert result["units"] == recorded[0]["units"]
