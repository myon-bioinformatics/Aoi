"""四つの形の 2×2 と論理記号。数は n と hold から。印は三つのラベル。"""
import json
from pathlib import Path

from ask import registration_status
from forms import contingency, format_contingency_cell, render_forms_table, render_item, render_logic, main

LABELS = ("事後構成", "事前登録", "不明")


def item(**extra):
    base = {
        "id": "P1",
        "if": [{"col": "rd", "op": ">", "value": 0}],
        "if_any": [[{"col": "A", "op": ">", "value": 0}], [{"col": "B", "op": ">", "value": 0}]],
        "then": [{"col": "upper_half", "op": "==", "value": True}],
        "forms": [
            {"form": "original", "n": 5, "hold": 3, "counterexamples": [{"unit": "only-one"}]},
            {"form": "converse", "n": 4, "hold": 3},
            {"form": "inverse", "n": 5, "hold": 4},
            {"form": "contrapositive", "n": 6, "hold": 4},
        ],
    }
    base.update(extra)
    return base


def test_contingency_cells_come_from_n_and_hold():
    cells = contingency(item())
    assert cells == {"P∧Q": 3, "P∧¬Q": 2, "¬P∧Q": 1, "¬P∧¬Q": 4}


def test_counterexample_count_uses_n_minus_hold_not_the_list():
    text = render_forms_table(item())
    assert "3/5（反例 2）" in text
    assert "only-one" not in text


def test_two_by_two_and_logic_share_the_registration_label():
    cases = [
        ({"posthoc": True}, "事後構成"),
        ({"posthoc": False}, "不明"),
        ({}, "不明"),
        ({"preregistered": True}, "事前登録"),
    ]
    for extra, label in cases:
        row = item(**extra)
        assert registration_status(row) == label
        assert label in LABELS
        table, logic = render_forms_table(row), render_logic(row)
        assert table.startswith(f"［{label}］")
        assert logic.startswith(f"［{label}］")
        assert "| P | 3 | 2 |" in table
        assert "| ¬P | 1 | 4 |" in table
        assert "元 P→Q" in table and "対偶 ¬Q→¬P" in table


def test_logic_symbols_keep_recorded_comparisons():
    text = render_logic(item())
    assert "元: rd>0 ∧ (A>0 ∨ B>0) → upper_half==true" in text
    assert "逆: upper_half==true → rd>0 ∧ (A>0 ∨ B>0)" in text
    assert "裏: ¬(rd>0 ∧ (A>0 ∨ B>0)) → ¬(upper_half==true)" in text
    assert "対偶: ¬(upper_half==true) → ¬(rd>0 ∧ (A>0 ∨ B>0))" in text
    for symbol in ("∧", "∨", "¬", "→"):
        assert symbol in text


def test_missing_form_is_unknown_and_disagreement_is_shown():
    row = item()
    row["forms"] = [f for f in row["forms"] if f["form"] == "original"]
    cells = contingency(row)
    assert cells["P∧Q"] == 3 and cells["P∧¬Q"] == 2
    assert cells["¬P∧Q"] is None and cells["¬P∧¬Q"] is None
    assert "不明" in render_forms_table(row)
    clash = item()
    clash["forms"][1]["hold"] = 9
    clash["forms"][1]["n"] = 9
    assert str(contingency(clash)["P∧Q"]).startswith("不一致")


def test_empty_antecedent_marks_not_p_as_zero_only_from_the_empty_lists():
    row = item()
    row["if"] = []
    row["if_any"] = []
    row["forms"] = [
        {"form": "original", "n": 8, "hold": 5},
        {"form": "contrapositive", "n": 3, "hold": 0},
    ]
    assert contingency(row)["¬P∧Q"] == 0
    assert contingency(row)["¬P∧¬Q"] == 0
    assert format_contingency_cell(row, "¬P∧Q") == "0（前件が空）"
    table = render_forms_table(row, heading=False)
    assert "0（前件が空）" in table
    text = render_logic(row)
    assert "（条件なし）" in text
    assert "（if も if_any も空）" in text


def test_cli_renders_one_id_and_refuses_a_missing_expression_file(tmp_path, capsys):
    results = tmp_path / "out"
    results.mkdir()
    (results / "propositions.jsonl").write_text(json.dumps(item(posthoc=True), ensure_ascii=False) + "\n", encoding="utf-8")
    assert main(["--results", str(results), "--id", "P1"]) == 0
    out = capsys.readouterr().out
    assert "［事後構成］ P1" in out
    assert "もしかして" not in out
    assert main(["--results", str(results), "--id", "E25"]) == 1
    err = capsys.readouterr().err
    assert "結果が読めない" in err
    assert "結果にない" not in err


def test_real_proposition_table_agrees_with_its_forms():
    path = Path(__file__).resolve().parents[2] / "cycles" / "c001-chunichi" / "outputs" / "propositions.jsonl"
    row = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    cells = contingency(row)
    assert all(not (isinstance(v, str) and v.startswith("不一致")) for v in cells.values())
    text = render_item(row)
    assert text.startswith(f"［{registration_status(row)}］")
    assert registration_status(row) in LABELS
