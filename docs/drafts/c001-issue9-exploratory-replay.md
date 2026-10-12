# C001 Issue #9: three **unregistered** exploratory candidates

This is a reproducibility record, **not** a registration of propositions/sets or a promotion to V2 results. The candidate selection is post-hoc, following [Issue #9's 2026-10-09 discussion](https://github.com/myon-bioinformatics/Aoi/issues/9#issuecomment-6079868287). Both OR proposals share P62 and P196 and must not be counted as independent explanations.

## Source lock and boundaries

- Research definitions commit: `0723d1137fc8448fbabb7bbe5fc14333ddfaabe2`.
- Saved annual-input replay: [run 37919737005, artifact 11611346346](https://github.com/myon-bioinformatics/Aoi/actions/runs/37919737005/artifacts/11611346346).
- ZIP SHA-256: `789f1b5ca457727120171032c023ec214319fe6a42c2d90f314a0c66cb97edfa`.
- `v1/season.jsonl` SHA-256: `20466c46628f4657233ef6289c628f076a0c665a2129594f5651d29a0d05d350`.
- `definitions/propositions.toml` SHA-256: `20ebf739caa0f2b14c2ae8c3662d178a6694aaa43a3f0ad9a475b84ebcf6acf0`.
- `definitions/sets.toml` SHA-256: `c72179713973ebe58d7a78eed4888fe7ff65eaf166ede8e549d61a08cdf813c3`.

The ZIP's manifest records `saved_annual_input_replay`: annual game-level data were inherited from V1; original NPB acquisition/parsing was **not** independently replayed. The full ZIP (and SHA lock) is checked before running the artifact mode. The tracked, narrow, human-readable snapshot consists of 168 team-years projected from that same frozen season input plus the selected locked definitions, retained for offline CI even after the GitHub artifact expires. The source annual JSONL at this commit has Git blob `ed59427f8e679c44c931e7b79a6b48b6f23a0027`.

Baseline comparison: 2013–2025, excluding **all 12 team-years in 2020**, yielding **144** team-years (12 seasons × 12 clubs). 2012 is intentionally outside the common comparison because P62's streak has no previous year; its missing premise must never be reinterpreted as false. For sensitivity, add back **all 12** of 2020, yielding **156** team-years. The precomputed P62 streak **retains 2020** for continuity even when that year is excluded from evaluation: Chunichi 2019=3, 2020=4, 2021=5. The outcome is the final B classification (rank 4–6), **not** the CS participation rule (CS was not held in the Central League in 2020). 2026 has no corresponding input in the artifact and is not scored.

## Expressions resolved from the immutable definition files

- `OR_A = P62 | P138 | P196` (P62: `inn_size_low_streak >= 2`; P138: `rf_adv < -0.6`; P196: `rf_state2 == 'B' AND ra_state2 == 'AB'`)
- `OR_B = P62 | P189 | P196` (P189: `course_rank_q3 >= 5`)
- `E7 & E22`:
  - `E7 = F96 | (OFF_SHORT & ~TOP_WIN)`. `F96` points to P96's three-way `if_any`; `OFF_SHORT` to P147; `TOP_WIN` to P144's *if* condition, excluding its scope (as specified in sets.toml).
  - `E22 = Q3_LOW | (Q3_MID & ~Q4_POS)`, using P189, P191's `scope.where` and P191's `if` respectively.

The evaluator resolves the pinned predicates and set references rather than hardcoding the composite outcomes. Comparisons use unrounded saved floating-point values. A missing predicate is **undetermined**, not false; invalid expressions are rejected by a restricted parser.

## Recalculated observations (antecedent matches, B holds)

| Candidate | Base: B holds / antecedent | Chunichi B covered | With 2020: B holds / antecedent | Counterexample after restoring 2020 |
|---|---:|---:|---:|---|
| OR_A | 32 / 32 | 12 / 12 | 33 / 34 | Chunichi 2020 (3rd place) |
| OR_B | 54 / 54 | 12 / 12 | 58 / 59 | Chunichi 2020 (3rd place) |
| E7 AND E22 | 59 / 59 | 12 / 12 | 64 / 64 | None |

All three base comparisons have zero undetermined team-years. Chunichi 2020 is not covered by `E7 & E22` because Q3 position was 4 and the final quarter had `q_wl_4 = +8`. This narrower AND avoids that counterexample; it does **not** explain away the original E7 counterexample or establish causation. Another historically important E7 counterexample is Hanshin 2015 (3rd place, Q3 position 1), retained in the original research.

The CLI's JSON report includes candidate expression strings, relevant locked parent predicates and set definitions, both cohort sizes/exclusions, per-candidate holds, antecedent counts, unknowns, final-rank counterexamples, and individual Chunichi-year coverage/active paths. It also keeps **raw saved feature values and active parent paths for each counterexample**, plus the units removed from the original E7 antecedent by adding E22: 5 team-years without 2020 (including Hanshin 2015), 8 team-years with 2020 (including Hanshin 2015 and Chunichi 2020). The original E7 result remains unchanged.

## Run without downloading anything in CI

```bash
python -S scripts/check_c001_exploratory_candidates.py \
  --snapshot pythdragoras/tests/fixtures/c001_exploratory_snapshot.json \
  --out build/c001-exploratory-candidates.json
pytest -q pythdragoras/tests/test_c001_exploratory_candidates.py \
  --junitxml=build/c001-exploratory-junit.xml
```

The existing repo-wide CI Python matrix runs these pytest cases and uploads JUnit XML alongside the other tests. CI uses the checked-in locked projection and never depends on artifact retention or NPB network access.

## Revalidate directly against the original artifact

Download the ZIP from the link above, then:

```bash
python -S scripts/check_c001_exploratory_candidates.py \
  --artifact c001-saved-input-replay.zip \
  --write-snapshot /tmp/c001-exploratory-regenerated.json \
  --out /tmp/c001-exploratory-artifact-report.json
```

The artifact mode first checks the **entire ZIP SHA-256**, embedded manifest, and source-definition SHA-256 values, then reconstructs the projection and recomputes the results. Compare the regenerated and tracked projections **as parsed JSON**, not byte-for-byte text: JSON key order and whitespace may differ. The original artifact and tracked projection produced identical report values in the 2026-10-10 local check.

## Research interpretation

These candidates were selected after inspecting the same historical records used for scoring. `32/32`, `54/54` and `59/59` are **observed sample counts**, neither independent held-out tests nor universal predictions. In particular, a tighter conjunction naturally removes counterexamples at the expense of covering fewer units. Do not overwrite P62/P138/P189/P196, E7/E22, the pre-existing E7/Hanshin-2015 counterexample or the earlier V1/V2 outcomes. A future independent dataset or untouched season is needed to assess generalization, and a separate causal research design is needed for a claim about *why* the Dragons repeatedly finished in the B class.
