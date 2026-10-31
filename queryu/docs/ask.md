# Queries (`queryu/ask/ask.py`)

Turns a Japanese question (「E25 に阪神 2015 以外の判例はある？」, "Does E25 have counterexamples other than Hanshin 2015?") into a fixed type (`Query`) and answers it from results PythDRagoras has already judged (`propositions.jsonl`, `sets.jsonl`). It never goes to the network. It uses no model and no API key.

## Approach (taken from Jev's "choices constrained by types")

| Jev | Here |
|---|---|
| The return type becomes the kind of question (yes/no, choices, scores) | Each `Query` field is a choice from fixed values (`ask`, `kind`, and `form` are enums; IDs and units are strings with a fixed shape) |
| Only answers from allowed values | Reading picks only registered values (proposition/formula IDs, team names, the 4 forms, question kinds). Unread words are returned in `unread` (not silently dropped) |
| Bad at counting and arithmetic | Numbers (%, years) are read with regular expressions. Whether counterexamples exist, their count, and hold rates are not recounted; they are looked up from judged results |

Role: separate **reading** (question → Query) from **answering** (Query → judged results). Reading is swappable:

1. Now: classic reading (regular expressions and word lists)
2. Later: pass the `--schema` JSON Schema to llama.cpp (constraining output with `json_schema`) or as MCP tool arguments, and let a local LLM choose the Query. The chosen Query is passed directly with `--query`. The same function produces the answer, so the same Query gives the same answer

## Query

| Field | Values |
|---|---|
| `ask` | `has_counterexample` (yes/no), `counterexamples` (list), `unique_exception` (exactly 1 counterexample), `rate` (hold-rate condition) |
| `target` | `P96`, `E25`, etc. All if absent |
| `kind` | `any`, `proposition` (「命題」), `expression` (「式」) |
| `form` | `original`, `contrapositive` (対偶), `converse` (逆; 「逆に」 is not read as a form), `inverse` (裏) |
| `exclude` | Units excluded from counterexamples (「阪神 2015 以外」 → `t-2015`) |
| `about` | Only those where this unit or team is a counterexample (`t-2015`, `d`) |
| `min_rate`, `max_rate` | Hold rate (「95% 以上」, 「8割以上」) |

## Usage

```
python queryu/ask/ask.py "判例がただ1つの式は？"
python queryu/ask/ask.py "P96 の対偶の判例" --json
python queryu/ask/ask.py --query '{"ask": "has_counterexample", "target": "E26"}'
python queryu/ask/ask.py --schema
python queryu/ask/ask.py "中日が判例の命題" --results <results-folder> --teams <teams.json> --log <log.jsonl>
```

Run questions that include 「式」 (formula) in a results directory that has `sets.jsonl`. Passing only main's `outputs` gives `結果が読めない` (results unreadable), because that file is not there.

- `--log` records the original question and the parsed Query one line each (for reproducibility)
- If the counterexample list was truncated in the judge's output, it prints 「一覧は一部」 (partial list)
- `--results` is required. Resolving from a cycle's `pipeline.toml` or a results ref is done by Aoi's `aoi_paths.py`, which passes the resolved folder
- `--teams` is JSON mapping team names → codes. If not given, team names are not read and are returned as unread (Aoi passes the NPB table)
- With `--cycle-dir`, its `ask.toml` is read; otherwise the `ask.toml` in the results folder's parent
- Exit codes: 0 = answered, 1 = undeterminable (results unreadable, ID not in results, unread words), 2 = `--query` outside the type

If unsupported words or conditions remain, it also exits 1 and asks for clarification, rather than dropping conditions and answering.

### Evidence for uninterpreted input (Issue #30)

`parse_input()` separates the NFKC and whitespace normalization used for reading from the stored original text.
The existing `(Query, unread)` contract of `parse()` is kept.
The CLI JSON, the `--log` JSONL, and intake receipts carry the same evidence.

| Field | Meaning |
|---|---|
| `raw_text` | The whole question before normalization. For intake, the `/ask` argument (the whole command text is the receipt's `body`) |
| `unread_spans` | `start`, `end`, and `raw_text` of uninterpreted ranges. 0-based, end-exclusive, in Python Unicode code points. `raw_text[start:end]` always equals the range's original text. Not UTF-8 bytes or UTF-16 offsets |
| `parse_status` | Machine value `parsed` / `undetermined`. `parsed` means the syntax was read, not a research judgment of holding |
| `parse_diagnostics` | A stable `code` and a human-readable `explanation`. The explanation text is not used for machine decisions |
| `unread` | Human-readable display kept for compatibility. Not the source of truth for original text or spans |

Q5 `P121 は 2026 年で確かめられた？` ("Was P121 confirmed in 2026?") is `parse_status=undetermined`.
`unread_spans` holds `{start: 7, end: 20, raw_text: "2026 年で確かめられた"}`.
Reason codes are `unrecognized_ask` and `unsupported_text`. The answer is still 「判定不能」 (undeterminable),
and it is not mapped to P121's existing results or provisional 2026 results.
An answer stopped by uninterpreted input carries the machine values `status=undetermined` and `reason_codes`,
while the Japanese `answer`, `error`, and `unread` are kept separately for display.

Particles are handled only when the whole remaining range is a known connective, or when it is a leading particle separated by whitespace.
Characters such as 「か」 or 「で」 in the middle of unknown words are not stripped. Unknown conditions such as 「とか」 are not emptied by deleting characters either.
Uninterpreted input bypasses reads and writes of known answers and the answer cache, and candidates are presented only as candidates.
The new evidence also lives in `ask.py`, so the existing answer-code hash invalidates old caches.
Fetch plans, the official evaluator, and research data are unchanged.

When there are no results, no matching form, or undeterminable units remain, the inability to confirm a counterexample
is not asserted as 「いいえ」 (no). Exclusions and team filters using an incomplete counterexample list are handled the same way.
The counterexample count is `n - hold`. `undetermined` is counted outside `n`, so it is not subtracted twice.

Comment intake and search operations are in [NagoyAction](../../nagoyaction/docs/inbox.md).

## Presenting candidates (`queryu/ask/suggest.py`)

For questions without an ID, it lists up to 5 registered proposition/formula sentences that are close. It reduces character 1–3-gram TF-IDF with SVD, and can optionally use an index compressed to signs and per-dimension scales.

This is not an answer. It calls neither `ask.py`'s reading (`parse`) nor answering (`answer`). If the top similarity is below the threshold, it is 「判定不能」 and no candidate is confirmed. Even at or above the threshold, the status is 「要確認」 (needs confirmation) and no chosen ID is set. The top candidate is never passed to `ask.py` to answer automatically.

There is no default threshold. In the prototype it was set just above the highest similarity of hand-written out-of-scope questions. That value fits a small set and risks overfitting. Neighboring IDs (propositions/formulas with similar content) can also be confused. When the question contains an ID, the index is not used and that ID is returned. The written ID may differ from what the question actually refers to.

Note: candidates with the same similarity are listed in document order (stable sort). When an ID written in the question is not among the loaded propositions/formulas, it reports `known: false` with a note (`selected` stays as the written ID).

## Candidates when undeterminable (did you mean)

When there are unread words, or the specified ID is not among the readable results, up to 5 are appended to the end of the reply.

```text
もしかして: P46 / P47（候補。答えではない）
```

(「もしかして」 = "did you mean"; 「候補。答えではない」 = "candidates, not an answer".)

### Observation

- Candidates come from `queryu/ask/suggest.py` similarity. An ID written in the question is excluded, not to repeat that ID but to rank IDs close to the rest of the sentence.
- The similarity threshold is `suggest_threshold` in `cycles/<cycle>/ask.toml`, or the number passed with `--suggest-threshold`.
- c001's `ask.toml` does not have this key.

### Interpretation

- This line is a list of candidates, not a judgment. Neither `answer` nor `Query.target` is rewritten by candidates.
- While the key is absent, no candidate is treated as "above the threshold". Similarities fitted to hand-written questions in the prototype are not copied into cycle settings.
- When a needed results file is missing, it says 「結果が読めない」 and shows no candidates. This is written separately from "the ID doesn't exist". Even for questions sent to clarification because of unsupported words, no candidates are shown if files needed by the parsed Query are missing.

## Results unreadable

A formula ID such as `E25` needs `sets.jsonl`. A proposition ID needs `propositions.jsonl`. A "propositions and formulas" question without an ID needs both.

### Observation

- main's `cycles/c001-chunichi/outputs` has `propositions.jsonl` but not `sets.jsonl`.
- The error when a needed file is missing includes the file name, as in `結果が読めない: sets.jsonl`.
- Only when the file exists but the ID is not in it does it say `判定済みの結果にない` (not in the judged results).

### Interpretation

- A missing file is not read as "that ID has not been judged". Formula results are read from the results ref checkout (`.aoi-results/<cycle>/outputs`), as in Issue #9.
- When the specified results folder doesn't exist, it does not switch to another folder. Nor does it create and fill `sets.jsonl` in this repository.

The four-forms table and condition notation are in [DRAgoWing](../../dragowing/docs/forms.md).
