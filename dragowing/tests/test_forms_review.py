"""Compare the display against the existing evaluator, without changing its decisions."""
import itertools

import polars as pl

import propositions
from forms import contingency, logic_lines, render_forms_table


def test_every_small_two_by_two_table_round_trips_through_official_evaluator():
    definition = {"id": "P1", "statement": "display probe", "strength": "always", "min_n": 1,
                  "if": [{"col": "p", "op": "==", "value": True}],
                  "then": [{"col": "q", "op": "==", "value": True}]}
    for counts in itertools.product(range(3), repeat=4):
        if not sum(counts):
            continue
        rows = []
        for (p, q), count in zip([(True, True), (True, False), (False, True), (False, False)], counts):
            rows.extend({"p": p, "q": q, "team": "d", "team_name": "中日", "season": 2000 + len(rows) + i}
                        for i in range(count))
        saved = propositions.evaluate(definition, pl.DataFrame(rows))
        assert list(contingency(saved).values()) == list(counts)


def test_empty_antecedent_contrapositive_has_false_consequent():
    item = {"if": [], "if_any": [], "then": [{"col": "q", "op": "==", "value": True}]}
    lines = logic_lines(item)
    assert "⊤（条件なし）" in lines[0]
    assert lines[3] == "対偶: ¬(q==true) → ⊥（条件なしの否定）"
    assert "未評価" in lines[1] and "未評価" in lines[2]


def test_four_forms_are_a_markdown_table_with_a_separator():
    text = render_forms_table({"id": "P1", "if": [{"col": "x", "op": ">", "value": 0}]})
    tables = text.split("\n\n")
    assert len(tables) == 3
    assert tables[-1].splitlines()[1] == "|---|---|"
