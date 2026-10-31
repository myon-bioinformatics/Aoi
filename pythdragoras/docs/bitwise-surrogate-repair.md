# Bitmask evaluator for candidate rules

`bitwise_surrogate.py` does two things.

1. It evaluates a candidate rule with integer masks. `evaluate_fast` is the predicate. `format_current_rule` prints the same rule.
2. It can propose one NOT condition as a new proposition to test. The rule under test is left as it is, so its verdict does not move.

`rule_search` is still the exhaustive search. Its combination step stays on bitsets over rows. This module rechecks rules that search, or a proposition antecedent, has already produced.

## Predicate

A row is a Python int. Bit `i` is on when candidate condition `i` holds.

- `M_AND`: every one of these bits is on.
- each OR-clause mask shares a bit with the row.
- `M_NOT`: none of these bits is on.

```text
evaluate_fast(X) = (X & M_AND) == M_AND
                   and (X & M_NOT) == 0
                   and every OR clause shares a bit with X
```

That is one conjunction of required bits, forbidden bits, and positive disjunctions. `compile_search_rule` returns that surrogate, or `None` for a general DNF such as `[A AND B] OR [C AND D]`. A general OR of conjunctions is still evaluated: each conjunction is one `evaluate_fast`, and the row matches if any conjunction matches. Null cells stay undetermined (`None`). They are not stored as false.

`format_current_rule` prints `col op value` joined by `AND`, `OR`, and `NOT`. With no names it prints `bit 0`.

`evaluate_antecedents` packs every candidate condition in one polars select, then runs the predicate. `screen_search_rules` does that for the `if_any` groups `rule_search.search` returns. `evaluate_proposition_antecedent` does it for one proposition's `if` / `if_any`. Flags match `propositions._antecedent` on the same rows. On the null-free frame the search scores, true-positive and false-positive counts match the search record.

The module imports only the standard library. Polars and the proposition helpers are imported inside the functions that read a frame. Syntax stays valid on Python 3.9 (no `match`, no `int.bit_count`).

## Measured on the registered rule search

Host: Python 3.12.3, Linux 6.12.94+, x86_64. `time.perf_counter`. Seven repeats after one warmup, except the combine-only line, which is one tight loop. Data: Aoi `cycles/c001-chunichi`, `season.jsonl` after the registered 2020 exclusion, nulls in the candidate columns dropped. 156 team-seasons, 17 candidates, `max_terms=2`, `max_conds=2`. The search returns 20 rules. Five of those twenty compile to a single mask. All 139 conjunction terms the search builds compile to a single mask. Flags from `evaluate_fast`, from `propositions._antecedent`, and from the row-bitset AND/OR agreed on every one of those rules and terms.

| Work | Median |
|---|---:|
| `evaluate_antecedents` on the 20 returned rules | 2.95 ms (min 2.76, max 3.04) |
| `propositions._antecedent` on those 20 rules | 9.74 ms (min 9.27, max 14.1) |
| `evaluate_antecedents` on the 139 conjunction terms | 5.55 ms (min 5.36, max 6.06) |
| `propositions._antecedent` on those 139 terms | 67.2 ms (min 65.2, max 68.4) |
| `evaluate_fast` on the 139 terms after the rows were packed | 2.15 ms (min 2.04, max 2.74) |
| `evaluate_fast` on one rule, per row | 0.105 µs |
| AND of the 139 terms from row masks that were already built | 0.186 ms |
| `rule_search.search` (`top=20`) | 8.52 ms (min 8.30, max 16.8) |

Rechecking the returned rules is about 3.3× the proposition antecedent (9.74 / 2.95). Rechecking the 139 conjunctions is about 12× (67.2 / 5.55). The search call itself is unchanged: `rule_search.py` is covered by the LittleBit source hash, and once the row masks exist the integer AND of those 139 terms (0.186 ms) is cheaper than walking `evaluate_fast` (2.15 ms). The combination loop stays there.

```bash
AOI_ROOT=/path/to/Aoi python bitwise_surrogate.py --aoi-root /path/to/Aoi
```

## NOT as a proposition to test

`suggest_not_proposition(rule, x, oracle)` is for one row the rule accepts and the oracle rejects. It binary-searches extra bits (`X & ~M_AND`), low index to high. If `oracle(X ^ left_half)` is true, the inhibitory bit is taken to lie in that half. The surviving bit is proposed only when flipping that bit alone makes the oracle true. The proposal is a new rule text from `format_current_rule` (the old literals, plus `NOT` of that condition). The masks of the rule under test are the same after the call, and `evaluate_fast` on that row is still true.

The monotone decoy is the case this covers: the oracle is the old conjunction plus one extra forbidden bit. The suggestion names that bit, and the suggested rule agrees with the oracle on every row of that predicate. A false positive caused by a missing required bit has no extra bit that restores the oracle by itself, so the function returns no suggestion. The old repair committed such a bit into `M_NOT` anyway.

The suggestion needs `oracle(X with bits flipped)`. A column of observed labels does not answer that. Historical team-seasons are not rewritten.

## Removed

An earlier draft also edited the mask when a row disagreed: a false negative relaxed a lost AND bit into an OR clause `(lost | replacement)`, or deleted it, and cleared forbidden bits the row actually had. Repeating that on later disagreements was measured and dropped. The numbers below are from that draft (seeds 1–40, balanced classes, near-miss negatives, repair rows disjoint from the eval rows). They are a record of why the edit is gone. They are not pass thresholds.

| Protocol | Unrepaired eval | One repair | Every later disagreement | Probes, once |
|---|---|---|---|---|
| Dead slide (retired bit forced off) | 0.500 on every seed | 1.000 on every seed | 1.000 on every seed | min 6, median 10, mean 10.05, max 14 |
| Residual slide (retired bit stays free) | min 0.608, median 0.663, mean 0.663, max 0.702 | min 0.883, median 0.912, mean 0.913, max 0.938 | min 0.596, median 0.912, mean 0.866, max 0.938 | min 6, median 10, mean 9.75, max 13 |
| New decoy (one added NOT) | min 0.852, median 0.879, mean 0.877, max 0.900 | 1.000 on every seed | 1.000 on every seed | min 4, median 4, mean 4.33, max 5 |

Exactly 3 probes occurred on 0 of 40 canonical repairs in each protocol. Seed `20261023`: dead 0.500 → 1.000 in 9 probes; residual 0.651 → 0.932 once and 0.737 if every disagreement was repaired (31 probes); decoy 0.879 → 1.000 in 5 probes.

The false-negative edit is an equivalence only when the retired bit is afterwards off. On the residual slide, repairing every later disagreement drove some seeds down to 0.596, below the unrepaired fidelity, because a false positive with no inhibitory bit was still written into `M_NOT`. On the registered NPB candidates the same observational repair added NOT conditions that were not the planted slide (`NOT one_run_net < 0`, `NOT bat_d_r_runner < 0`) and holdout agreement did not rise; repairing the rest lowered one setting from 35/36 to 34/36. The registered early-season rule for `upper_half == false` is `[sim_p_upper < 0.5]`. Train 2012–2018 was tp=37, fp=7, fn=5, tn=35 (72/84). Eval 2023–2025 was tp=17, fp=1, fn=1, tn=17 (34/36). Agreement rose with the frozen rule. There is no counterfactual oracle for that label, so the repair was not run on it.

Claimed illustrations that this repo did not reproduce: feature-shift 42.5% → 99.2%, season slide 68.5% → 99.6% in 3 queries, new-decoy baseline 58%, surrogate inference of 2–8 µs against a 2.2 ms search. The decoy repair reached exact agreement; 58% did not occur. `evaluate_fast` on these rows is about 0.1 µs, under that band. `rule_search.search` on this host is several milliseconds, over 2.2 ms.

Nothing in this repository, in Aoi's LittleBit holdout (that "drift" is a SHA-256 change), or in Ironmate (pixel occupancy masks and frozen image surveys) was this repair. There was no canonical copy to vendor.

Tests draw `secrets.randbits(63)` when they randomize and emit `bitwise_surrogate seed=...`. They assert exact agreement where the two evaluators, or the decoy predicate and the suggestion, are the same function. They do not assert 68.5, 99.6, 42.5, 99.2, 58, 3 queries, 2.2 ms, or 2–8 µs.
