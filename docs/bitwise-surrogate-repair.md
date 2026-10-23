# Bitwise symbolic surrogate: what the measurements say

An external proposal described a bitmask rule and an active repair that edits the mask when a holdout label disagrees. The percentages in that proposal were treated as unverified. This note records what PythDRagoras already had, what Ironmate and Aoi have, and what a fresh implementation measured.

The short version: the bitmask predicate is exact for the fragment it describes, and the repair does what it says on a single clean slide or a single clean decoy. The published percentages, the three-query figure, and a collapse of a real NPB rule do not come out of the protocols below. The repair is not wired into proposition verdicts.

## Proposal

A rule is three integer masks over feature bits:

- `M_AND`: every one of these bits must be on.
- a list of OR-clause masks: each clause must share a bit with the row.
- `M_NOT`: none of these bits may be on.

`evaluate_fast(X)` is that predicate. Repair, when the predicate disagrees with an oracle label:

- False negative. `missing = M_AND & ~X`. For each missing bit, scan candidate bits `c` in `X & ~M_AND` and ask `oracle(X ^ c)`. The first `c` that makes the oracle false becomes an OR clause `(lost | c)`. If none does, the lost bit is deleted. Forbidden bits that the row actually has are cleared.
- False positive. Among `X & ~M_AND`, binary-search: if `oracle(X ^ left_half)` is true, the inhibitory bit is taken to be in the left half. The surviving bit is added to `M_NOT`.

Claimed illustrations included an NPB season slide of `F12 AND F19 AND NOT F25` to `F20` in place of `F19` (68.5% unrepaired, 99.6% repaired, 3 oracle queries), feature-shift 42.5% to 99.2%, new-decoy 58% to 100%, and surrogate inference of about 2–8 microseconds against a 2.2 ms initial search.

## Prior art

Nothing already in this repository, in Aoi, or in Ironmate is this repair. A GitHub code search of `myon-bioinformatics` for `BitwiseSymbolic`, `M_AND`, `evaluate_fast`, and `"active rule repair"` returned no hits. The new module was not vendored, because there was no canonical copy to pin.

| Place | What it actually does |
|---|---|
| `rule_search.py` | Exhaustive OR-of-AND search. Bitsets are over **rows**, not features. No holdout edit of a mask. |
| `littlebit_approx.py`, `littlebit_prune.py`, `littlebit_holdout.py` | Factor a 0/1 candidate matrix and score frozen rules on later seasons. Disagreement is recorded. Masks are not rewritten from counterfactual probes. |
| `tests/test_littlebit_holdout_drift.py` and Aoi workflow `LittleBit holdout drift` (`.github/workflows/littlebit-holdout-drift.yml`) | SHA-256 provenance of the frozen LittleBit holdout. "Drift" there means a byte changed, not a feature index sliding. |
| Ironmate `pixel_arcade_engine.py` | Occupancy bitmasks for pixel grids, including XOR rollback of swaps. The bits are cells, not proposition features. |
| Ironmate `scripts/survey_holdout.py` and `scripts/littlebit_jev_3way_survey.py` | Frozen image-survey settings scored on held-out shape and signal families. Mismatches stay mismatches. There is no symbolic repair. |
| Ironmate `vendor.lock.json` | Pins of shared parent tools (CLI helpers, image utilities, and similar). No rule surrogate is in that lock or under `vendor/`. |

`rule_search` remains the search. `bitwise_surrogate.py` is a separate experiment. `pythdragoras.py` does not call it.

## What was implemented

`bitwise_surrogate.py` is standard-library only at import (Python 3.9 syntax: no `match`, no `int.bit_count`). NPB loading imports polars only inside `season_report`.

Probe order is ascending feature index. The proposal does not name an order, so query counts are not a property of the written rule; they are a property of this choice. A false-negative probe stops at the first bit that flips the oracle. A false-positive search commits the last singleton even when flipping that bit alone leaves the oracle false. Both behaviors are the proposal, and the tests lock them in.

Fidelity means `(true positives + true negatives) / n` against the oracle labels of that split. The repair split and the eval split are different rows. Repaired fidelity below is always the eval split.

The repair needs `oracle(X with bits flipped)`. A column of observed B-class labels does not answer that. Historical team-seasons were therefore not "repaired" against `upper_half`. Planted labels below are a function of candidate bits, so the probes are legal. They are not the league table.

## Synthetic protocol

40 features. The claimed indexes are used as synthetic bit numbers: required bits 12 and 19, forbidden bit 25, slide target 20, decoy 30. They are not columns. `rule_candidates.toml` has 17 candidates, so indexes 19 and 25 do not exist there. Index 12 does: it is `rank_ra >= 3`.

Classes are balanced. Other bits are independent fair coins, then the literals are forced. A negative violates exactly one literal of the labeling rule (a near miss). The repair stream starts with one constructed disagreement, then fresh draws. Eval rows are a further fresh draw. Seeds 1 through 40, `n_initial=256`, `n_repair=64` plus the constructed row, `n_eval=512` (513 when one injected false positive is added).

| Protocol | Label after the change |
|---|---|
| Dead slide | `12 AND 20 AND NOT 25`, and bit 19 is forced off |
| Residual slide | same label, but bit 19 stays a free coin |
| New decoy | `12 AND 19 AND NOT 25 AND NOT 30` |

Under those generators the expectations, before any repair, are 1/2 (dead; the old rule can never fire), 2/3 (residual), and 7/8 (decoy).

## Synthetic results

Seeds 1–40. "Once" is a single repair. "All" keeps repairing every later disagreement in the repair stream. Probe counts are counterfactual oracle calls, not including the label of the row itself.

| Protocol | Unrepaired eval | Repaired once, eval | Repaired all, eval | Probes, once |
|---|---|---|---|---|
| Dead slide | 0.500 on every seed | 1.000 on every seed | 1.000 on every seed | min 6, median 10, mean 10.05, max 14 |
| Residual slide | min 0.608, median 0.663, mean 0.663, max 0.702 | min 0.883, median 0.912, mean 0.913, max 0.938 | min 0.596, median 0.912, mean 0.866, max 0.938 | min 6, median 10, mean 9.75, max 13 |
| New decoy | min 0.852, median 0.879, mean 0.877, max 0.900 | 1.000 on every seed | 1.000 on every seed | min 4, median 4, mean 4.33, max 5 |

Exactly 3 probes occurred on **0 of 40** canonical repairs in each protocol. A further 32 canonical draws from seed `20261023` also had zero draws with exactly 3 probes (dead-slide probes 6–15, median 10; decoy probes 4–5, median 4).

Seed `20261023` alone, which is one draw from the same generator: dead 0.500 → 1.000 in 9 probes; residual 0.651 → 0.932 once and 0.7368 if every disagreement is repaired (31 probes); decoy 0.879 → 1.000 in 5 probes. Counts for that seed: dead unrepaired `fn=256, tn=256`; residual once `tp=256, fp=35, fn=0, tn=222` out of 513; decoy unrepaired `tp=256, fp=62, tn=194` out of 512.

The residual "all" column is the important failure. On some seeds, continuing to repair drives eval fidelity down to 0.596, below the unrepaired number. The false-positive step treats a missing required bit as if some extra bit were inhibitory, then forbids that extra bit.

## Claimed numbers against these measurements

| Claim | What came out | Reading |
|---|---|---|
| Feature shift 42.5% → 99.2% | Dead slide is 50% → 100%. Residual unrepaired stays inside 60.8–70.2%, and one repair stays inside 88.3–93.8%. | 42.5% and 99.2% are outside those ranges. |
| Season slide 68.5% → 99.6% in 3 queries | Residual mean unrepaired is 66.3% (the 2/3 expectation). 68.5% sits inside the seed range and is not the mean. Repaired-once never reached 99.6% (maximum 93.8%). Dead slide is 100%, not 99.6%, and uses 6–14 probes. | 68.5% is sampling noise around 2/3 in one unspecified-looking protocol, not a stable result. 99.6% and 3 queries do not occur. |
| New decoy 58% → 100% | Unrepaired 85.2–90.0% (expectation 87.5%). Repaired once is 100% on every seed. | The single monotone decoy is repaired exactly. 58% does not occur. |
| Surrogate ~2–8 µs, search 2.2 ms | See the timing section. | The two endpoints were not observed on this host. |

Initial fidelity, before any slide, is 1 on the training draws: the surrogate is the old rule, and the draws are labeled by that rule. That part of "a distilled rule matches its source" holds.

## NPB candidate rows

Data: Aoi `cycles/c001-chunichi`, `season.jsonl` after the registered 2020 exclusion (120-game season, CS not played; 12 rows removed). No nulls in the candidate columns. 156 team-seasons, 17 candidates in file order. The split is by season count, fixed before looking at fidelity: first 7 of the remaining seasons train, next 3 repair, last 3 eval.

- Train: 2012–2018 (84 rows).
- Repair: 2019, 2021, 2022 (36 rows).
- Eval: 2023–2025 (36 rows).

2026 is named as a confirmation season in `analysis.toml` and is not in this file.

### Observed B-class target

`rule_search` on the training seasons, `max_terms=1`, `max_conds=2`, selects `[sim_p_upper < 0.5]`. The bitmask compiler agrees with that search on the training rows: `tp=37, fp=7, fn=5, tn=35` (fidelity 72/84 = 0.857). On 2023–2025 the same frozen rule scores `tp=17, fp=1, fn=1, tn=17` (34/36 = 0.944). Agreement went up. There is no counterfactual oracle for `upper_half`, so active repair was not run. This is the measurement that uses real labels.

### Planted slides on the same masks

Two planted rules. Neither is `F12 AND F19 AND NOT F25`.

File order, first condition of the first four distinct columns: `(sim_p_upper < 0.3) AND (rd < -50) AND NOT (rank_rf >= 4)`, sliding `rd < -50` to `wins_vs_pythag < -4`. Positives under the new rule: 3 train, 0 repair, 1 eval. Eval fidelity is then mostly true negatives (35/36 = 0.972) both before repair and after the observational repair.

Prevalence window, chosen from **training** bit rates in `[0.40, 0.80]` and the first eligible condition of four distinct columns, after the file-order rule turned out to have a single eval positive: `(sim_p_upper < 0.4) AND (rd < 0) AND NOT (rank_rf >= 4)`, sliding `rd < 0` to `wins_vs_pythag < 0`. Positives: 10 train, 4 repair, 2 eval. The window was not chosen by scanning repaired fidelity.

| Setting | Unrepaired eval | One repair, eval | All repairs, eval | Probes, once | What the one repair did |
|---|---:|---:|---:|---:|---|
| File-order, observational rows only | 35/36 = 0.972 | 35/36 = 0.972 | 35/36 = 0.972 | 4 | False positive on `s-2019`. Added `NOT one_run_net < 0`. The slide was not learned. The one eval positive stayed a miss. |
| File-order, constructed positive first | 35/36 = 0.972 | 36/36 = 1 | 35/36 = 0.972 | 6 | Correct OR `(rd < -50 OR wins_vs_pythag < -4)`, then a later repair added a spurious `NOT` and the eval positive became a miss again. |
| File-order, old bit cleared on drifted rows | 35/36 = 0.972 | 36/36 = 1 | 36/36 = 1 | 6 | OR relaxation matches the new rule because the old bit is off. |
| Prevalence, observational rows only | 35/36 = 0.972 | 35/36 = 0.972 | 34/36 = 0.944 | 3 | False positive on `c-2021`. Three probes. Added `NOT bat_d_r_runner < 0`. Holdout fidelity did not rise. Repairing the rest lowered it. |
| Prevalence, constructed positive first | 35/36 = 0.972 | 35/36 = 0.972 (`tp=2, fp=1, fn=0`) | 34/36 = 0.944 (`fn=2`) | 6 | The OR is the right slide and recall becomes 1, but one negative still carries the old bit, so fidelity does not move. Further repairs forbid `rank_ra >= 4` and both positives become misses. |
| Prevalence, old bit cleared | 34/36 = 0.944 | 36/36 = 1 | 36/36 = 1 | 6 | Same equivalence as the other dead-bit case. |

The only place a planted NPB slide reached perfect eval agreement without clearing the old bit by hand was the file-order rule with a constructed counterexample, on a holdout that contains one positive. The next disagreement removed that agreement. Three probes occurred once, on `c-2021`, and that repair did not implement the slide.

A separate check draws four distinct candidate indexes from the logged test seed and clears the old bit on the drifted seasons. Repaired-once eval agreement is exact for that draw as well. That is the algebraic case (the OR is equivalent once the retired bit is off), not a percentage target.

## Timing

Host: Python 3.12.3, Linux 6.12.94+, x86_64. `time.perf_counter` around a tight loop of at least 0.05 s and 2,000 calls, after a warmup. This is not a nanosecond harness. Absolute times will move if the machine is busy; the five search repeats below were taken alone.

| Operation | Measured |
|---|---|
| `evaluate_fast` on 32 synthetic masks | 0.093 µs/call over 536,000 calls |
| Same predicate written with Python sets | 2.55 µs/call |
| Empty Python function, same loop | 0.029 µs/call |
| `evaluate_fast` on the 36 eval masks | 0.085 µs/call over 585,360 calls |
| `rule_search.search`, train seasons, `max_terms=2`, `max_conds=2`, `top=20`, 5 repeats | min 5.30 ms, median 5.50 ms, max 5.52 ms |
| Same search, `max_terms=1`, `top=1` | min 4.66 ms, median 4.89 ms, max 5.37 ms |

The claimed search time, 2.2 ms, is below every repeat here. The claimed inference band, 2–8 µs, is above the bitmask loop. The set-based reference landed at 2.55 µs, inside that band, on this one run. That is a coincidence with a slower implementation of the same predicate, not a reproduction of an unseen harness. Qualitatively, a mask evaluation is much cheaper than `rule_search` on these 84 rows. The specific endpoints are not.

## Flaws the tests force, on every seed

These are not rare accidents. The edit rules produce them for any legal index assignment the seed draws.

- The first extra bit that flips the oracle is kept, even when a later extra bit is also required. The repaired rule then accepts a row that has the early bit and lacks the later one.
- Two lost bits on one row are both paired with that same earliest bit. A row that has only the early replacement is accepted and is not a positive.
- A positive label that happens to carry a real forbidden bit clears that ban. Later rows with the ban are accepted.
- A false positive caused by a missing required bit still commits some extra bit to `M_NOT`. Flipping that bit alone does not make the oracle true, and a real positive that happens to carry the bit is then rejected.
- If a lost bit has no flipping candidate, it is deleted.
- If a false positive has no extra bit, the rule is unchanged and stays wrong.
- Noisy labels are obeyed. The probes and the stored label are not checked against each other.

Multiple drift and label noise are outside what one clean repair can mean. The code does not paper over them.

## What was reproduced

- The bitmask predicate matches an independent set implementation, and a DNF that fits the fragment matches `rule_search` on the toy frame in `tests/test_rule_search.py`.
- One false-negative repair recovers a rule equivalent to a single-bit slide when the retired bit is afterwards off. Eval agreement is exact, including on real candidate rows used only as background bits.
- One false-positive repair finds a single monotone decoy bit. Eval agreement is exact. The binary search's left-half test is true exactly when the decoy is in the left half.
- Doing the same repair to every later disagreement can destroy that agreement. On NPB masks, an observational repair often edits a different bit than the planted slide.
- The registered early-season B-class conjunction does not fall apart on 2023–2025. Its agreement rises from 0.857 to 0.944. That is not a repaired model.

## Reproduce

```bash
python -S bitwise_surrogate.py --seed 20261023
AOI_ROOT=/path/to/Aoi python bitwise_surrogate.py --seed 20261023 --season --aoi-root /path/to/Aoi
```

Tests draw `secrets.randbits(63)` on each run and emit `bitwise_surrogate seed=...` as a warning. They assert structural facts (exact agreement where the generator makes the rules equivalent, disjoint repair and eval ids, probe accounting, the forced failure cases). They do not assert 68.5, 99.6, 42.5, 99.2, 58, 100 as a decoy baseline, 3 queries, 2.2 ms, or 2–8 µs.
