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
    ("==", 2, 2, True), ("==", 2, 1, True), ("==", 2, 3, False),
    ("!=", 2, 2, True), ("!=", 2, 1, True), ("!=", 2, 3, False),
    ("==", 2.5, 1, False), ("!=", 2.5, 1, False),
    ("==", 2.0, 1, True), ("!=", 2.0, 1, True),
    (">=", 2.5, 2, True), ("<", 2.5, 2, True),
    (">", 2.5, 3, False), ("<=", 2.5, 3, False),
])
def test_a_row_is_unknown_when_u_can_change_the_truth_of_the_condition(op, value, n, unknown):
    p = proposition("c", op, value)
    assert (("x", 2013) in su.unknown_rows(p, "c", {("x", 2013): n}, P)) is unknown


@pytest.mark.parametrize("op", list(P.OPS))
def test_unknown_rows_match_all_integer_truth_values_across_small_synthetic_thresholds(op):
    for n in range(1, 6):
        for twice_value in range(-4, 15):
            value = twice_value / 2
            # This finite oracle includes every threshold in the fixture and a point beyond all of them.
            truths = {P.OPS[op](n + u, value) for u in range(10)}
            got = su.unknown_rows(proposition("c", op, value), "c", {("x", 2013): n}, P)
            assert bool(got) == (len(truths) == 2), (op, value, n)


@pytest.mark.parametrize("op", list(P.OPS))
def test_unknown_rows_have_no_big_sentinel_ceiling(op):
    for n, value in ((1, su.BIG), (su.BIG + 1, su.BIG + 2), (10**100, 10**100 + 1)):
        assert su.unknown_rows(proposition("c", op, value), "c", {("x", 2013): n}, P) == {("x", 2013)}


@pytest.mark.parametrize("op", list(P.OPS))
@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_nonfinite_thresholds_do_not_invent_reachable_integer_values(op, value):
    assert su.unknown_rows(proposition("c", op, value), "c", {("x", 2013): 1}, P) == set()


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


@pytest.mark.parametrize("op", ["==", "!="])
def test_treatment_c_empties_rows_with_an_interior_equality_crossing(op):
    edge = {"c": {("x", 2013): 1, ("x", 2014): 2, ("y", 2013): 1}}
    out = su.treated(table(), proposition("c", op, 2), edge, "c", P, pl)
    assert out["c"].to_list() == [None, None, 0, None, 0]
    assert out["other"].to_list() == [1, 2, 3, 4, 5]
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


# ---- 置いた結果が、スクリプト・予想・README と合っている ------------------------------------------------------------------
RESULTS = EXPLORATORY / "streak_unknown_results"


def results_json():
    return json.loads((RESULTS / "streak_unknown.json").read_text(encoding="utf-8"))


def test_the_committed_results_are_what_the_script_makes_from_the_committed_inputs(result):
    assert results_json() == json.loads(json.dumps(result))
    assert (RESULTS / "streak_unknown.md").read_text(encoding="utf-8") == su.render(results_json())


def test_the_readme_names_the_inputs_by_their_full_sha256():
    import hashlib
    md = (RESULTS / "README.md").read_text(encoding="utf-8")
    base = ROOT / "cycles" / "c001-chunichi"
    for path in (base / "outputs" / "season.jsonl", base / "propositions.toml"):
        assert hashlib.sha256(path.read_bytes()).hexdigest() in md


def by_id():
    return {q["id"]: q for q in results_json()["propositions"]}


def test_the_written_predictions_hold_or_fail_in_the_results_json_as_the_readme_says():
    q, md = by_id(), (RESULTS / "README.md").read_text(encoding="utf-8")
    res = results_json()
    assert res["gate"]["ok"] and "4 命題・16 形すべて同じ" in md and sum(len(v["forms"]) for v in q.values()) == 16
    # (b) inn は 4 行で予想どおり。rf は 0 の予想が外れて 4 行（2012年）
    assert q["P62"]["unknown_units"] == {"inn_size_low_streak": ["b-2013", "d-2013", "l-2013", "s-2013"]}
    assert q["P64"]["unknown_units"] == {"rf_low_streak": ["b-2012", "db-2012", "h-2012", "t-2012"]}
    assert q["P65"]["unknown_units"] == q["P64"]["unknown_units"]
    assert "rf は外れ" in md
    # P64 は終了コードが同じでも数は同じではない
    p64 = q["P64"]["forms"]["original"]
    assert (p64["a"]["hold"], p64["a"]["n"], p64["b"]["hold"], p64["b"]["n"]) == (22, 26, 25, 30)
    assert p64["new_counterexamples_b"] == ["h-2012"] and p64["counts_stable"] is False
    # P63 は d が範囲外なので原命題は 3 行だけ増える
    p63 = q["P63"]["forms"]["original"]
    assert (p63["a"]["n"], p63["b"]["n"]) == (7, 10)
    # (c) P62 の原命題
    p62 = q["P62"]["forms"]["original"]
    assert [(p62[t]["code"], p62[t]["hold"], p62[t]["n"]) for t in "ab"] == [(0, 16, 16), (1, 19, 20)]
    assert p62["a"]["units"] == [] and p62["b"]["units"] == ["l-2013"] and p62["new_counterexamples_b"] == ["l-2013"]
    # (d) u しだい = P62（原命題・対偶）と P63（対偶）。P64・P65 は u によらない
    assert q["P62"]["u_dependent_forms"] == ["original", "contrapositive"]
    assert q["P63"]["u_dependent_forms"] == ["contrapositive"]
    assert q["P64"]["u_dependent_forms"] == q["P65"]["u_dependent_forms"] == []
    assert [q[i]["verdict_depends_on_u"] for i in ("P62", "P63", "P64", "P65")] == [True, True, False, False]


def test_the_codes_the_readme_quotes_are_the_codes_in_the_json():
    q = by_id()
    code = lambda pid, form: [q[pid]["forms"][form][t]["code"] for t in "abc"]
    assert code("P62", "original") == [0, 1, 5] and code("P62", "contrapositive") == [0, 1, 5]
    assert code("P63", "contrapositive") == [0, 1, 5] and code("P63", "original") == [4, 4, 4]
    for pid in ("P62", "P63", "P64", "P65"):
        assert code(pid, "converse") == [2, 2, 2] and code(pid, "inverse") == [2, 2, 2]
    for pid in ("P64", "P65"):
        assert code(pid, "original") == [4, 4, 4] and code(pid, "contrapositive") == [1, 1, 1]


def test_the_readme_tables_are_the_rows_the_script_renders():
    md = (RESULTS / "README.md").read_text(encoding="utf-8")
    rendered = su.render(results_json())
    for pid in ("P62", "P63"):
        section = rendered[rendered.index(f"## {pid} "):]
        rows = [x for x in section.splitlines()[:12] if x.startswith("| ") and "---" not in x]
        assert len(rows) == 5 and all(r in md for r in rows)


def test_forms_are_shown_in_the_fixed_order_even_after_the_json_sorts_its_keys():
    forms = {"inverse": 1, "original": 2, "converse": 3, "contrapositive": 4, "held_out": 5}
    assert su.forms_in_order(forms) == ["original", "contrapositive", "converse", "inverse", "held_out"]
