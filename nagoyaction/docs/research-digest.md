# Research digest (compaction-pattern / Aoi #20)

The target is `cycles/c001-chunichi/research/R*.md`. It is an index that scans all R records without omission, needing no network and no LLM. It does not re-judge research conclusions.

## Running

```bash
uv run python nagoyaction/research_digest.py cycles/c001-chunichi
uv run python nagoyaction/research_digest.py cycles/c001-chunichi --check
uv run pytest -q nagoyaction/tests/test_research_digest.py
```

The `digest` step in `pipeline.toml` runs after `judge`. A full run with the existing `--offline` needs the fetched cache, but this script alone needs no cache. CI generates twice from the same input (the second with `--check`) and saves the two generated files as artifacts.

## Reading the data

- `research_digest.jsonl`: one line per R, recording ID, title, record date, references, proposition IDs from the first cell of tables in the Markdown, review conditions, and current exit codes. `duplicate_table_ids`, `unknown_ids`, `missing_judgements`, and `missing_fields` are never dropped.
- `research_digest.md`: a human-readable list, plus unknown/unparsed items, registered judgement criteria, and a limited cross-check against FINDINGS.
- `proposition_ids` are the IDs seen in the first column of tables. `defines` are those propositions the research record handles, but **R18's table is a re-verification plan for propositions set up in the past, so it is `defines=[]`**, with `confirmation_focus_ids` recorded separately. An R without table rows is diagnosed as `proposition_ids=[]` (it does not automatically conclude "there is no research").
- `review.status`: `explicit` means the bullet list under `見直す条件` (conditions for review) was extracted; `pre_registered` means pre-registered criteria under a separate heading were extracted; `unparsed` means the heading exists but rules couldn't be extracted; `unknown` means the target heading couldn't be identified. Neither of the last two means "no conditions".
- `review.criteria`: from reading-table rows whose first cell has a proposition ID, saved **without changing the reading text**. R18's P52 keeps the separate thresholds 『逆の判例2件以上』 (2+ counterexamples of the converse) and 『判例3件以上』 (3+ counterexamples). If a new notation can't be handled, extraction is improved; judgements are not guessed to fill in.
- `current_judgements`: joined by projecting only `judgement.code` from `propositions.jsonl` with Polars. Columns in the JSONL with compound types or mixed numbers are not bulk-read into Polars as NDJSON. The overall judgement can include later-added observations, so **it is not the pass/fail of the 2026 independent verification**.
- **The 2026 independent verification** uses the readings pre-registered in R18 and the 2026 units in the separate `outputs/confirmation.md`. Condition searches on historical data, hypotheses made after seeing results, and ordinary overall judgements are not reused to write "supported by independent verification".

## Limits of the FINDINGS cross-check

Proposition IDs in `FINDINGS.md` are matched against IDs in the register and research records. Numeric comparison of exit codes is done only when `Pnn` and `exit N` appear explicitly on the same line. Prose "supported" or "objection" is not guessed by keyword, so `unverified_prose=true`. Transcribed numbers and text are not updated on their own.

The pinned Markdown helper is `vendor/markdown.py`, its origin and SHA-256 are in `vendor.lock.json`, and the MIT license is `vendor/markdown-LICENSE`. Dependencies are not implicitly moved to the latest upstream.

The polars surface `collect` uses is covered by Aoi's `shrink/polars_min.py`, placed byte-identical at `vendor/aoi/shrink/polars_min.py`. `research_digest.py` still does `import polars`. In processes without polars, that file is loaded into `sys.modules["polars"]` before import.

```bash
python -S nagoyaction/scripts/collect_with_polars_min.py --deps min /tmp/collect.json
```
