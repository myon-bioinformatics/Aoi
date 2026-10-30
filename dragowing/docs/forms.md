# 2×2 of the four forms and condition notation

`dragowing/forms.py` displays one judged row (`propositions.jsonl` or `sets.jsonl`). It never goes to the network. It builds counts from `n` and `hold`, and does not write reasons for holding or not holding.

```bash
python dragowing/forms.py --results cycles/c001-chunichi/outputs --id P1
```

## Observation

The cells of the 2×2 are counted from each form's `n` and `hold` as follows.

| Cell | Reading |
|---|---|
| P∧Q | The original's `hold`. That count if it equals the converse's `hold` |
| P∧¬Q | The original's `n - hold`. That count if it equals the contrapositive's `n - hold` |
| ¬P∧Q | The converse's `n - hold`. That count if it equals the inverse's `n - hold` |
| ¬P∧¬Q | The contrapositive's `hold`. That count if it equals the inverse's `hold` |

Here P is `if` and `if_any`, and Q is `then`. The number of counterexamples is `n - hold`, not the number of `counterexamples` entries (the list may be stored truncated).

When two forms give different counts, `不一致` (mismatch) is shown with both counts. A cell with no form that cannot be determined from an empty antecedent either is `不明` (unknown). When both `if` and `if_any` are empty, every unit in the record satisfies the antecedent, so 0 goes in the ¬P cells. If another form's count differs from 0, it stays `不一致`.

Conditions are displayed by joining the recorded `col` `op` `value` as-is. `if` conditions are joined with `∧`, `if_any` groups with `∨`, antecedent to consequent with `→`, and when the converse, inverse, or contrapositive negates the antecedent or consequent as a whole, `¬(…)` is used. `¬(rd>0)` is not rewritten as `rd<=0`.

When the antecedent is empty, P is shown as `⊤（条件なし）` (no condition) and its negation as `⊥（条件なしの否定）` (negation of no condition). The original is `⊤ → Q` and the contrapositive is `¬Q → ⊥`. The logical formulas for the converse and inverse are shown too, but the two forms the existing evaluator does not store in this case are marked "未評価" (not evaluated). Nothing is re-evaluated for display.

One marker is placed at the start of each display.

| Record | Display |
|---|---|
| `posthoc` is true | 事後構成 (post-hoc) |
| `preregistered` is true, or there is a preregistration record | 事前登録 (preregistered) |
| Otherwise (no field, `posthoc` is false) | 不明 (unknown) |

When a formula ID is given and `sets.jsonl` does not exist, it shows `結果が読めない` (results unreadable), and does not say the ID is absent from the results.

## Interpretation

This table places the stored judgment counts into cells. A large cell is not read as meaning the proposition is true or will hold next year. `不明` does not mean "it was not preregistered"; it means there is no machine-readable record.

Candidate IDs (`もしかして`, "did you mean") are not shown in this display. Handling on the query side is in [ask.md](../../queryu/docs/ask.md).

HTML (trajectories, team × year, condition overlap, list of propositions) is in [figures.md](figures.md).
