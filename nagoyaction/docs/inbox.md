# NagoyAction question intake

#10 adds **only question intake** to main. The exploration worker, HTML feedback, and local LLM model fetching and Docker startup are out of scope for this PR and split into follow-up PRs fitted to main's layout.

## Available commands

| Comment | Behavior |
|---|---|
| `/ask E25 に阪神 2015 以外の判例はある？` | Answers from saved results ("Does E25 have counterexamples other than Hanshin 2015?") |
| `/ask {"ask":"has_counterexample","target":"E25"}` | Asks with typed JSON |
| `/status` | Shows intake count, answer cache, and replies awaiting resend |
| `/explore ...` | Exits stating it is not introduced in #10 |
| `/stop ...` | Replies that there is nothing to stop, since exploration isn't introduced in #10 |

It does not react to ordinary conversation. One command per comment, up to 4000 characters. Comment edits are not re-run. Post a corrected request as a new comment.

## Separating code and results

Execution code is checked out from the default branch (main). Results are checked out from the ref given in `AOI_RESULTS_REF` into a separate directory, copied to `.aoi-results/<cycle>/`, and read **only as data**. Python on the results side is never imported or run.

The intake fingerprint includes only the following code that exists on main, plus the results JSONL actually read.

- `queryu/ask/ask.py`
- `queryu/ask/bank.py`
- `nagoyaction/inbox/inbox.py`
- `outputs/sets.jsonl` (if present)
- `outputs/propositions.jsonl` (if present)

If both `sets.jsonl` and `propositions.jsonl` are missing, it is not treated as "ID not found"; intake stops as 「結果が読めない」 (results unreadable).

If only one is missing, intake itself does not stop. Questions that need that file (`sets.jsonl` for formula IDs, `propositions.jsonl` for proposition IDs) get `結果が読めない: <file name>`, never `判定済みの結果にない` (not in the judged results). When the results ref checkout is missing, it does not switch to main's `cycles/<cycle>/outputs`.

Known answers and the answer cache use the same key tuple.

```text
(cycle, results SHA and file hashes, ask.py and bank.py hashes, Query)
```

The directories are `state/<cycle>/<results SHA>/known` and `state/<cycle>/<results SHA>/answers`, passed by the caller. It does not read `known` by assuming it is the parent of `answers`.

When there are unread words, or the ID isn't in the readable results, the reply gets up to 5 `もしかして: …（候補。答えではない）` (did you mean: … (candidates, not an answer)). Candidates are not made into answers. When a needed file can't be read, this line is not added. The threshold is `suggest_threshold` in `cycles/<cycle>/ask.toml`. Without the key, no candidate is confirmed.

## State and duplicate prevention

The state branch is `aoi-research-state-<cycle>` per cycle. It stores receipts, the answer cache, and replies awaiting resend.

If a receipt for the same comment ID already exists, it is not recomputed. If a reply was lost, it is resent with the same marker; if the bot's marker is already visible on GitHub, it does not post twice.

If an ordinary `Exception` occurs for one comment during intake, that comment is recorded as 「判定不能」 (undeterminable) and later comments continue to be processed. `KeyboardInterrupt` / `SystemExit` and the like are not swallowed.

## First production check

The following 4 comments, placed on Issue #9 before intake started, are the targets of the first intake.

1. `/ask E25 に阪神 2015 以外の判例はある？`
2. `/ask {"ask":"has_counterexample","target":"E25"}`
3. `/ask 判例がただ1つの式は？` ("Which formulas have exactly one counterexample?")
4. `/status`

Receipts are matched against reply counts, and it is confirmed that re-running the same intake does not add replies. NPB is not refetched.

## Required settings

- `AOI_INBOX_ISSUE`: intake issue number
- `AOI_RESEARCH_CYCLE`: e.g. `c001-chunichi`
- `AOI_RESULTS_REF`: e.g. `cycle-001/chunichi`
- `AOI_INBOX_ALLOWED_ACTORS`: optional. JSON array of additionally allowed GitHub logins

The workflow uses `contents: write` (state branch) and `issues: write` (replies).

To stop intake, empty `AOI_INBOX_ISSUE`.

## Follow-up PRs

- Exploration (`/explore`, worker, stopping, checkpointing)
- HTML feedback for DRAgoWing / BlueProbe
- Local LLM model fetching, Docker startup, and `when_env`-style execution control
- Combining multiple commands in one comment

These will be introduced separately, fitted to main's actual directory layout and existing NagoyAction contracts.
