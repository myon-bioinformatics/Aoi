# Shared components for remaining games, standings, and magic numbers (pre-implementation plan)

2026-10-04. Independent of research Draft PR #3; added to main.

## What to build

- Separate wins/losses up to the input point (including ties) from the remaining schedule, which contains no results.
- Winning percentage excludes ties from the denominator, and standings are decided by a rules object with explicit tie rules.
- Assign each remaining game consistently to both teams, and determine by constraint satisfaction whether top k is possible or clinched.
- Determine whether a team can fail to win the title depending on other teams' results even if it wins all its games, and track magic numbers lighting and going out from whether the team controls its own fate.
- Compute the required wins as a guarantee: "win at least this many and you win the title regardless of other results". Because of ties and tie rules, agreement with newspapers' customary magic number display is not assumed.
- Provide a baseline model that builds matchup probabilities from smoothed winning percentages at the time, and a simulator that accepts explicit matchup probabilities. Distinguish a probability of 0/1 from mathematical certainty.
- Provide an API/CLI that can save per-date recalculation, threshold crossings and re-emergence, and magic numbers lighting and going out.

## Boundaries

- This time is implementation verification of the shared engine. It does not claim a causal explanation of Chunichi's slump or support for new propositions.
- Provide profiles with confirmed official rules for NPB 2022 Central and Pacific, and 2025 Central. Do not implicitly reuse them for other years. Differences such as the 2020 CS format need separate settings.
- Head-to-head winning percentage for a tied group aggregates games against that whole group. The engine defines the rate for zero decisions as 0, and documents the difference from a normal completed season.
- The calculation is conditional on all input games being played. Games past the CS qualification deadline, postponements, and cancellations are not inferred automatically.
- Simulation intervals are error from finite iterations and do not include model error or future changes in ability.
- Raw game records are not committed. Only synthetic examples, code, and summaries of verification results are added.

## Conditions for adopting the implementation

1. Possible/clinched, self-controlled title, and guaranteed wins agree with full enumeration of small leagues.
2. Covers ties, head-to-head, ties of 3 or more teams, interleague play, previous-year standings, and lit → out → relit.
3. If the constraint solver times out, report unknown; do not read it as clinched.
4. Reproducible with a fixed seed, and rewriting future results does not change past dates' probabilities.
5. Confirm the connection with local NPB 2022 input, recording dates, input fingerprints, and settings. Newspaper dates are verification material.
6. Merge the shared-components PR into main after the dedicated CI succeeds. Keep Draft PR #3.
