# R001 follow-up: home/away decomposition (exploratory)

Recorded before the new cross-tabulation, after seeing R001 and the user-supplied Grok report. Not an independent confirmatory study.

Question: does Chunichi's home-minus-away run-difference gap arise from scoring, allowing runs, or both; does it persist when opponents have equal weights?

Frozen data: same verified 2013–2025 final-score dataset as R001. No new acquisition and no 2026 extension.

For each team-year compute: R_H/G_H, R_A/G_A, RA_H/G_H, RA_A/G_A. Scoring component = R_H/G_H − R_A/G_A. Prevention component = RA_A/G_A − RA_H/G_H. Their sum equals RD_H/G_H − RD_A/G_A. Positive means home is better. Also retain the average scoring and allowing levels at each side relative to other CL teams.

Primary opponent comparison: CL intra-league games only. For every CL team-year and each of its five CL opponents, calculate both components from home and away games; then give the five opponents equal weight. Every cell must exist. Compare Chunichi to the unweighted average of the other five CL teams, retaining annual values. Report all-game raw, CL-only raw, and CL-only opponent-balanced results. This avoids pretending that interleague opponents absent from one side in a year can be balanced. Give each season equal weight. Sensitivity excludes 2020 without replacing it. Retain all five Chunichi opponent pairings, including contrary examples.

No significance/causal claim or threshold for success. Opponent-balanced values remove different opponent frequencies within this selected schedule, not opponent strength, starting pitchers, dates, park effects or all confounding. Other teams have different opponent sets, include games against Chunichi, and share games: comparisons are descriptive and dependent. Home means designated home, not one particular stadium. Runs per game do not adjust for innings/opportunities, walk-offs or omitted bottom ninth innings.

Revision rule: if balanced gap disappears/reverses, weaken the claim that the raw gap is robust to opponent mix. If it remains, proceed to actual venues and inning/opportunity information; do not label the residual a park or travel effect. No inference about the fraction of CS absences caused is permitted.
