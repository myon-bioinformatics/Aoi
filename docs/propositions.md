# Propositions, Counterexamples And Objections

> 異議あり。— Objection.

This document defines how PythDRagoras states an explanation as a proposition (命題), searches for counterexamples (判例), and decides a verdict.

It is the operational core of [validation.md](validation.md) and [hypothesis.md](hypothesis.md).
Every sub-project and every future cycle must use the same rules, so that verdicts stay comparable across pull requests.

If an implementation disagrees with this document, this document wins and the implementation is a bug.

---

# Why Propositions

An analysis usually ends with a sentence such as:

> Teams with a positive run differential finish in the upper half.

That sentence is an explanation.

Aoi asks a different question:

> Where does this sentence stop being true, and why?

To ask that question precisely, the explanation must be written as a proposition whose truth can be checked unit by unit.

---

# Units

A proposition is evaluated over **units**.

In cycle 1 a unit is one team-season (for example, Chunichi 2019).

A unit is a row of observed and derived values.
Every value used by a proposition must exist as a column. A missing column is an error, never a silent false.

---

# The Form Of A Proposition

```text
For every unit u in the scope:   A(u)  ⇒  B(u)
```

- `A` is the condition (前件), `B` is the consequence (後件).
- Both are conjunctions of simple comparisons: `column op value`, where `op` is one of `< <= > >= == !=`.
- Comparisons only use constants. A comparison between two columns is first computed as a derived column (for example `rank_gap = rank - rank_pythag`) so that every derived value is visible and documented.
- An empty `A` means "every unit in the scope". Such a proposition has no converse or inverse.

Arbitrary code is never evaluated.

---

# Four Forms

For `A ⇒ B`, PythDRagoras evaluates four forms.

| Form | Japanese | Statement | Counterexample (判例) |
|---|---|---|---|
| original | 元の命題 | A ⇒ B | A and not B |
| contrapositive | 対偶 | not B ⇒ not A | A and not B |
| converse | 逆 | B ⇒ A | B and not A |
| inverse | 裏 | not A ⇒ not B | B and not A |

Two invariants follow from logic and are checked by the implementation every time:

- The original and its contrapositive have exactly the same counterexamples.
- The converse and the inverse have exactly the same counterexamples.

When the condition only selects a subject (for example "if the team is Chunichi"), the converse ("if expectations are met, the team is Chunichi") has no meaning.
Such a proposition may declare `skip_forms = ["converse", "inverse"]` with a `skip_reason`. The reason is printed with the result.
The original and the contrapositive can never be skipped.

A data-driven proposition is not a logical identity. The original may survive while its converse fails.
That difference is information: "positive run differential usually means the upper half" does not imply "the upper half usually has a positive run differential".

---

# Measures

For each form, with `X` as its condition and `Y` as its consequence:

| Measure | Meaning |
|---|---|
| `n` | units satisfying X |
| `hold` | units satisfying X and Y |
| `rate` | hold / n, the observed support |
| `ci_low`, `ci_high` | 95% Wilson interval of rate |
| `base_rate` | share of all units satisfying Y |
| `lift` | rate / base_rate |
| `fisher_p` | one-sided Fisher exact test: does X raise the chance of Y? |
| `counterexamples` | units satisfying X and not Y |
| `undetermined` | units where X or Y cannot be decided because a value is missing. They are counted and shown, never silently dropped |

---

# Falsifier And Note

A proposition may declare:

- `falsifier`: what observation would make us revise it. Writing it down before the evaluation keeps the proposition honest.
- `note`: what the proposition can and cannot say. For example, a relation that is partly built into the arithmetic describes *how* a gap appeared, not *why*.

Neither changes the definition (they are not part of the pre-registration fingerprint), and both are printed with the result.

The output also shows the number of conditions, as a reminder of how many exceptions have been built into the proposition.

---

# Strength Is Declared In Words

A proposition declares how strong its claim is.
The words map to fixed thresholds, so the same wording always means the same criterion.

| `strength` | Wording | Kind | Threshold |
|---|---|---|---|
| `always` | 必ず | universal | no counterexample allowed |
| `almost_always` | ほとんど | statistical | 0.90 |
| `usually` | 概ね | statistical | 0.75 |
| `more_often_than_not` | 多くの場合 | statistical | 0.50 |

A threshold is never tuned to the data. If a claim needs another strength, it is a different claim.

Defaults: `min_n = 10`, `alpha = 0.05`, 95% intervals.

---

# Verdict

The verdict is decided by the first matching rule.

| Order | Condition | Verdict | Japanese |
|---|---|---|---|
| 1 | `n < min_n` | Inconclusive | 判断保留 |
| 2 | universal and no counterexample | Supported | 支持 |
| 3 | universal and at least one counterexample | Rejected | 棄却 |
| 4 | statistical and `ci_low >= threshold` | Supported | 支持 |
| 5 | statistical and `ci_low < threshold <= ci_high` | Inconclusive | 判断保留 |
| 6 | statistical and `ci_high < threshold` and `fisher_p < alpha` | Refined | 修正 |
| 7 | statistical and `ci_high < threshold` and `fisher_p >= alpha` | Rejected | 棄却 |

Refined means: a relationship exists, but it is weaker than the proposition claims. The proposition should be restated with a weaker strength or a narrower scope, under a new ID.

Split is not decided automatically. When counterexamples cluster (for example, one team or one period), a human splits the proposition into narrower propositions with new IDs. The original verdict is kept.

A verdict is about the proposition within its scope. It is not a statement about causes.

---

# Objection (異議あり)

An objection is raised whenever a form has at least one counterexample — **even when the verdict is Supported**.

A supported proposition with counterexamples is exactly where an explanation stops being sufficient.

Each objection lists its counterexamples (判例). Each counterexample records:

- the unit (for example, Chunichi 2019)
- the values of every column used by A and B
- declared context columns (for example run differential, Pythagorean rank, residual wins)
- a surprise score, taken from a declared column, used only for ordering
- a question generated from the counterexample: *Why does this unit satisfy A but not B?*
- linked hypotheses that could answer the question

Counterexamples are ordered by the absolute surprise score, largest first.
Units of the focus team are marked.

---

# Exclusions Must Not Hide Counterexamples

Some seasons are excluded from statistics by a human decision with a recorded reason (see `analysis.toml`).

Exclusion changes the measures. It does not change the evidence.

Counterexamples found among excluded units are always listed separately as **excluded counterexamples (除外中の判例)**, with the exclusion reason.

---

# Pre-registration

Criteria are written before the results are seen.

- Propositions live in a file under version control. Every evaluation records the SHA-256 of that file and the code version.
- Changing a threshold, scope or condition after seeing results creates a new proposition ID. The old proposition and its verdict stay in the record (archived), as required by [hypothesis.md](hypothesis.md): rejected hypotheses are valuable.

---

# Exit Codes

A verdict is returned as a number. Words are only a rendering of that number (Japanese and English are provided).
Judgement logic and tests compare numbers, never display text.

| Code | Japanese | English | Meaning |
|---|---|---|---|
| 0 | 異議なし | No objection | every examined form has no counterexample |
| 1 | 異議あり（例外あり） | Objection! | counterexamples exist, within the declared strength (Supported) |
| 2 | 異議あり（主張が強すぎる） | Objection! | a relationship exists but is weaker than claimed (Refined) |
| 3 | 異議あり（不成立） | Objection! | not supported (Rejected) |
| 4 | 待った！判断保留 | Hold it! | too few units, or the interval straddles the threshold (Inconclusive) |
| 5 | 待った！判定できない単位がある | Hold it! | no counterexample, but some units could not be decided (missing values). Unknown is never 0 |
| 6 | 事前登録の違反の疑い | Pre-registration breach | the ledger holds more than one definition under the same ID |
| 64 | 命題ファイルの誤り | Invalid proposition file | |
| 65 | データの誤り | Data error | a referenced column does not exist |
| 66 | 入力がない | No input | |
| 70 | 実装の誤り | Internal error | a logical invariant failed (for example, original and contrapositive disagree) |

Codes 1 to 6 are results of the inquiry. Codes 64 and above are failures of the system.

The forms are examined in a fixed order, and examination stops at the first non-zero code:

```text
original → held-out (restated propositions only) → contrapositive
    all zero so far → provisional "no objection" (仮の異議なし)
→ converse → inverse
    all zero → confirmed "no objection" (異議なし)
```

When converse and inverse are skipped with a reason, the best possible stage is provisional.

```bash
python pythdragoras/propositions.py judge outputs/propositions.jsonl              # stop at the first non-zero
python pythdragoras/propositions.py judge outputs/propositions.jsonl --id P2       # one proposition
python pythdragoras/propositions.py judge outputs/propositions.jsonl --keep-going --lang en
python pythdragoras/propositions.py judge outputs/propositions.jsonl --report-only # objections do not fail; system errors do
```

---

# Restating A Proposition

An objection is not the end of a proposition. It is the reason to write the next one.

A restated proposition:

- has a new ID and declares `parent` (the proposition it restates)
- declares `change`: what was changed and why
- declares `motivated_by`: the counterexamples that led to the change (for example `d-2019`)

Adding conditions until no counterexample remains is always possible. A proposition tailored to its own counterexamples will always look correct.

For that reason a restated proposition is also evaluated **without the units that motivated it** (held-out evaluation). Its support is read from the held-out verdict. If other units object there, the restatement has not yet learned anything general; inspect those counterexamples next.

The parent and its verdict stay in the record. The lineage of restatements is printed at the top of the output.

---

# Choosing Among Surviving Propositions

Passing every examination is the minimum before a conclusion is stated.
Making every proposition true is not the goal.

A proposition may survive while its converse objects. Saying "this indicator works as a sufficient condition but not as a necessary one" is progress.
A statistical proposition with exceptions within its declared strength has not failed.

Passing means: objections were examined without hiding them, and the claim is stated with the strength and scope the evidence supports.

When several propositions survive, prefer the one that:

- applies the same criterion to every unit it compares (the comparison baseline is explicit)
- holds beyond the counterexamples that motivated it (held-out evaluation)
- does not accumulate convenient exception conditions (number of conditions)
- explains more than its alternatives, and states what remains unexplained
- declares what would make us revise it (falsifier)

"Weak" or "strong" always needs a stated comparison: weak compared with whom, over which period, measured how.

---

# Ledger

Every evaluation is appended to a ledger (`ledger.jsonl`), once per pair of proposition definition and data version.

From the ledger, each proposition reports:

| Measure | Meaning |
|---|---|
| evaluations | how many data versions it has been evaluated on |
| objections | how many of those had a counterexample to the original form (any form is counted separately) |
| no-objection streak | how many of the most recent evaluations had no counterexample to the original form |
| definitions | how many different definitions were recorded under the same ID |

More than one definition under the same ID means the proposition was changed in place. That breaks pre-registration and is flagged in the output.

The ledger answers the questions that matter over time: how often reality objected, where, and how long a proposition has survived without objection.

---

# External Claims

Claims from outside the pipeline (articles, reports, other AI systems) are recorded as **claims**, not observations, together with their source and date.

A claim states a number that the pipeline can reproduce (a sum, a mean, a count, or a ratio of sums such as a period-total win rate) and a tolerance.
When the claim leaves something unstated (the period, pooled or averaged), the assumption is written into the claim's statement.
The pipeline reports whether it reproduces the claim:

| Status | Meaning |
|---|---|
| reproduced | the computed value is within the tolerance |
| not reproduced | the computed value is outside the tolerance, or no unit meets the claim's own conditions |
| not measurable | the pipeline has no data in the claim's scope (for example, years outside the collected range) |
| interpretation | the claim is an interpretation, not a number; it is recorded as such |

The pipeline reports whether it reproduces the claim. Agreement does not make the claim an observation; disagreement is itself a contradiction worth investigating.

---

# Output

For every proposition the output contains:

```text
P2: Pythagorean upper half ⇒ actual upper half     (strength: usually = 0.75)
  scope: league=C, units=78, excluded: 2020 (6 units)
  original        n=40 hold=33 rate=0.83 [0.68, 0.91] lift=1.65 p=0.000  → Inconclusive
  contrapositive  n=38 ...                                               → ...
  converse        ...
  inverse         ...
  異議あり！ 判例 (original):
    Chunichi 2019 (focus): rank_pythag=2 → rank=5   wins_vs_pythag=-4.7
      Why does it satisfy "rank_pythag <= 3" but not "rank <= 3"?   → H3, H5
  除外中の判例:
    Chunichi 2020 (excluded: shortened season): ...
```

(The numbers above illustrate the format only.)

---

# Final Principle

A proposition is not written to be defended.

It is written so that reality can object to it.

When reality objects, the objection is recorded, the question is asked, and the next proposition begins.
