"""cycles/c001-chunichi/exploratory/streak_unknown.py の確認。左端に届く連続、不明な行、3 つの表、ゲート。"""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXPLORATORY = ROOT / "cycles" / "c001-chunichi" / "exploratory"


def _load():
    spec = importlib.util.spec_from_file_location("c001_streak_unknown", EXPLORATORY / "streak_unknown.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


su = _load()
pl, P, PD = su.load_modules(ROOT)


def rows_for(col, **teams):
    """teams: {チーム: {年: 値}}。"""
    return [{"team": t, "season": s, col: v} for t, series in teams.items() for s, v in series.items()]


def proposition(col, op, value):
    return {"id": "T1", "if": [{"col": col, "op": op, "value": value}],
            "then": [{"col": "upper_half", "op": "==", "value": False}]}


# ---- 左端に届く連続 ---------------------------------------------------------------------------------------------------
def test_left_edge_runs_are_the_runs_that_start_at_the_first_known_year_of_the_team():
    rows = rows_for("c", x={2012: None, 2013: 1, 2014: 2, 2015: 0, 2016: 1},      # 左端 2013。2013〜2014 の連続だけ届く
                    y={2012: 1, 2013: 2, 2014: 0, 2015: 1},                         # 左端 2012。2012〜2013 が届く
                    z={2012: 1, 2013: None, 2014: 1})                               # 途中で空。2014 の連続は左端に届かない
    assert su.left_edge_runs(rows, "c") == {("x", 2013): 1, ("x", 2014): 2, ("y", 2012): 1, ("y", 2013): 2, ("z", 2012): 1}


def test_a_run_of_zero_or_an_empty_value_is_never_a_left_edge_run():
    rows = rows_for("c", x={2012: 0, 2013: 1}, y={2012: None, 2013: None})
    assert su.left_edge_runs(rows, "c") == {}


# ---- 不明な行 --------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("op,value,n,unknown", [
    (">=", 2, 1, True), (">=", 2, 2, False), (">=", 2, 3, False),
    (">", 1, 1, True), (">", 1, 2, False),
    ("<", 2, 1, True), ("<", 2, 2, False),
    ("<=", 2, 2, True), ("<=", 2, 3, False),
    ("==", 2, 2, True), ("==", 2, 1, False),
    ("!=", 2, 2, True), ("!=", 2, 1, False),
])
def test_a_row_is_unknown_when_u_can_change_the_truth_of_the_condition(op, value, n, unknown):
    p = proposition("c", op, value)
    assert (("x", 2013) in su.unknown_rows(p, "c", {("x", 2013): n}, P)) is unknown


def test_unknown_rows_look_at_every_condition_on_the_column_including_the_scope_where_and_then():
    p = {"id": "T", "if": [{"col": "c", "op": ">=", "value": 1}], "then": [{"col": "c", "op": "<=", "value": 3}],
         "scope": {"where": [{"col": "c", "op": "<", "value": 2}]}}
    assert su.unknown_rows(p, "c", {("x", 2013): 1, ("x", 2014): 2, ("x", 2015): 3}, P) == {("x", 2013), ("x", 2014), ("x", 2015)}
    only_if = proposition("c", ">=", 1)
    assert su.unknown_rows(only_if, "c", {("x", 2013): 1}, P) == set()
    only_where = {"id": "T", "if": [{"col": "o", "op": ">=", "value": 1}], "then": [{"col": "upper_half", "op": "==", "value": False}],
                  "scope": {"where": [{"col": "c", "op": "<", "value": 2}]}}
    assert su.unknown_rows(only_where, "c", {("x", 2013): 1, ("x", 2014): 2}, P) == {("x", 2013)}
    only_then = {"id": "T", "if": [{"col": "o", "op": ">=", "value": 1}], "then": [{"col": "c", "op": "<=", "value": 2}]}
    assert su.unknown_rows(only_then, "c", {("x", 2013): 1, ("x", 2014): 3}, P) == {("x", 2013)}


# ---- 3 つの表 --------------------------------------------------------------------------------------------------------
def table():
    return pl.DataFrame({
        "team": ["x", "x", "x", "y", "y"], "season": [2013, 2014, 2015, 2013, 2014],
        "c": [1, 2, 0, 1, 0], "other": [1, 2, 3, 4, 5], "upper_half": [False] * 5}, schema_overrides={"season": pl.Int64})


def test_treatment_a_is_the_table_itself():
    st = table()
    assert su.treated(st, proposition("c", ">=", 2), {"c": {("x", 2013): 1}}, "a", P, pl) is st


def test_treatment_b_sets_a_large_value_on_the_left_edge_rows_of_the_used_column_only():
    edge = {"c": {("x", 2013): 1, ("x", 2014): 2, ("y", 2013): 1}}
    out = su.treated(table(), proposition("c", ">=", 2), edge, "b", P, pl)
    assert out["c"].to_list() == [su.BIG, su.BIG, 0, su.BIG, 0]
    assert out["other"].to_list() == [1, 2, 3, 4, 5]
    unused = su.treated(table(), proposition("other", ">=", 2), edge, "b", P, pl)
    assert unused["c"].to_list() == [1, 2, 0, 1, 0]


def test_treatment_c_empties_only_the_unknown_rows():
    edge = {"c": {("x", 2013): 1, ("x", 2014): 2, ("y", 2013): 1}}
    out = su.treated(table(), proposition("c", ">=", 2), edge, "c", P, pl)
    assert out["c"].to_list() == [None, 2, 0, None, 0]
    assert out["c"].dtype == pl.Int64


# ---- ゲート ----------------------------------------------------------------------------------------------------------
def _forms(**over):
    base = {"form": "original", "n": 16, "hold": 16, "undetermined": 0, "code": 0, "counterexamples": [{"unit": "d-2013"}]}
    return {**base, **over}


def test_gate_is_empty_when_the_summary_equals_the_stored_result():
    stored = {"forms": [_forms()]}
    assert su.gate({"id": "T"}, su.summarize(stored), stored) == []


@pytest.mark.parametrize("over", [{"n": 17}, {"hold": 15}, {"undetermined": 1}, {"code": 1},
                                   {"counterexamples": [{"unit": "s-2013"}]}])
def test_gate_reports_any_difference_in_the_counts_the_code_or_the_counterexample_units(over):
    stored = {"forms": [_forms()]}
    problems = su.gate({"id": "T"}, su.summarize({"forms": [_forms(**over)]}), stored)
    assert len(problems) == 1 and "original" in problems[0]


def test_gate_reports_a_missing_form():
    stored = {"forms": [_forms(), _forms(form="converse")]}
    assert su.gate({"id": "T"}, su.summarize({"forms": [_forms()]}), stored)


# ---- 確定済みの出力に当てる --------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def result():
    return su.analyze(ROOT)


def test_the_gate_passes_on_the_committed_outputs(result):
    assert result["gate"] == {"ok": True, "problems": []}
    assert [q["id"] for q in result["propositions"]] == ["P62", "P63", "P64", "P65"]
    assert result["inputs"]["exclusions"] == [2020]


def test_the_gate_stops_the_run_when_the_stored_result_differs(tmp_path):
    stored = ROOT / "cycles" / "c001-chunichi" / "outputs" / "propositions.jsonl"
    lines = [json.loads(x) for x in stored.read_text(encoding="utf-8").splitlines()]
    for r in lines:
        if r["id"] == "P62":
            r["forms"][0]["n"] += 1
    bad = tmp_path / "propositions.jsonl"
    bad.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in lines) + "\n", encoding="utf-8")
    res = su.analyze(ROOT, stored=bad)
    assert not res["gate"]["ok"] and res["propositions"] == []
    assert "通らなかった" in su.render(res) and "P62" in su.render(res)


def test_the_gate_exit_code_is_the_data_error_code_of_pythdragoras():
    assert su.EXIT_GATE == 65 == next(c for c, (ja, _) in P.EXIT.items() if ja == "データの誤り")


def test_main_returns_the_gate_exit_code_and_still_writes_the_files(tmp_path, monkeypatch):
    monkeypatch.setattr(su, "analyze", lambda repo: {"gate": {"ok": False, "problems": ["x"]}, "propositions": [], "inputs": {}})
    assert su.main(["--outdir", str(tmp_path)]) == su.EXIT_GATE
    assert (tmp_path / "streak_unknown.json").exists() and "通らなかった" in (tmp_path / "streak_unknown.md").read_text(encoding="utf-8")


# ---- 3 通りの比べ方と表示 --------------------------------------------------------------------------------------------
def cell(code=0, hold=16, n=16, undetermined=0, units=()):
    return {"code": code, "hold": hold, "n": n, "undetermined": undetermined, "units": list(units)}


def test_stability_calls_the_code_stable_only_when_all_three_codes_agree():
    same = {"a": cell(), "b": cell(), "c": cell()}
    assert su.stability(same) == {"code_stable": True, "counts_stable": True, "new_counterexamples_b": [], "gone_counterexamples_b": []}
    assert su.stability({**same, "c": cell(code=4)})["code_stable"] is False
    assert su.stability({**same, "b": cell(code=1)})["code_stable"] is False


def test_stability_keeps_the_counts_and_the_units_apart_from_the_code():
    moved = {"a": cell(units=["d-2013"]), "b": cell(n=20, hold=19, units=["d-2013", "l-2013"]), "c": cell(units=["d-2013"])}
    out = su.stability(moved)
    assert out["code_stable"] is True and out["counts_stable"] is False
    assert out["new_counterexamples_b"] == ["l-2013"] and out["gone_counterexamples_b"] == []
    gone = {"a": cell(units=["s-2013", "d-2013"]), "b": cell(units=["d-2013"]), "c": cell(units=["s-2013", "d-2013"])}
    out = su.stability(gone)
    assert out["gone_counterexamples_b"] == ["s-2013"] and out["new_counterexamples_b"] == []
    assert su.stability({"a": cell(), "b": cell(), "c": cell(undetermined=3)})["counts_stable"] is False


def test_render_shows_the_three_cells_the_verdict_and_the_pivot_rows():
    forms = {"original": {"a": cell(0, 16, 16, 0), "b": cell(1, 19, 20, 0, ["l-2013"]), "c": cell(0, 16, 16, 4)},
             "converse": {"a": cell(2), "b": cell(2), "c": cell(2)}}
    for v in forms.values():
        v.update(su.stability(v))
    res = {"gate": {"ok": True, "problems": []},
           "propositions": [{"id": "T1", "statement": "テスト", "unknown_units": {"c": ["l-2013"]}, "forms": forms}]}
    text = su.render(res)
    assert "通った" in text and "## T1 テスト" in text and "不明な行: c: l-2013" in text
    assert "| original | 0・16/16（0） | 1・19/20（0） | 0・16/16（4） | u しだい |" in text
    assert "| converse | 2・16/16（0） | 2・16/16（0） | 2・16/16（0） | u によらない |" in text
    assert "original: 終了コードは (a) 0・(b) 1・(c) 0。(b) で新しく判例になる行: l-2013。(b) で判例でなくなる行: なし" in text
    assert "converse: 終了コード" not in text
