# GPT R001: score pairing and the limits of season totals

Status: exploratory protocol, written before this study's calculations, 2026-10-03.
Base: Aoi PR #2, `672d9c69031528ed2dfd5f942e889173cfafb283`.

The researcher has already seen the user's 2013–2026 aggregate report, including
Chunichi 2019/2020/2024 exceptions. This is NOT a blind preregistration or an
independent confirmation of those discoveries. The protocol freezes the new
comparison before its results are inspected. Revisions must be documented.

## Questions and competing explanations

- R1: Is Chunichi's realized win-equivalent rate above or below what would result
  if its observed runs allowed were paired differently with its runs scored?
  An excess could reflect strategy, game-state interaction, dependence, or chance;
  it is not automatically managerial skill or luck.
- R2: Does this pairing excess persist into the next season across teams?
  Persistence would motivate a repeatable-mechanism hypothesis. Weak persistence
  would weaken a stable-team-label explanation, without proving absence of skill.
- R3: Does Chunichi's home/away run differential gap exceed the contemporaneous
  Central League benchmark? This is descriptive; park, travel, roster, opponents,
  and game-ending rules cannot be separated with these records alone.

## Accessible evidence

Use the existing QueRyu/BlueProbe NPB monthly-calendar acquisition and parser.
2013–2025 completed regular seasons, all 12 teams (including interleague games).
2020 stays in the primary descriptive tables; report a sensitivity excluding it.
2026 is outside this study. No interviews, private data, inning scraping, or
claims to recover a professional's internal reasoning.

Gate: zero unknown score strings; unique game IDs; all 12 teams must have 144
games in 2013–14, 120 in 2020, and 143 otherwise. Independently compare Central
League W/L/D and runs scored/allowed with official season tables. Record the
coverage of that check. Do not silently proceed on a mismatch.

## Frozen comparison

For each team-season, retain every observed runs-scored value. Randomly permute
runs allowed (a) within home/away strata and (b) within home/away × opponent
strata. These preserve the marginal score distributions, season run differential,
and stratum sizes; (b) also preserves opponent-specific margins. Use 4,000
replicates per team-season and mode, seed 20261003, deterministic team ordering.

The response is win equivalents W + D/2, and its rate over ALL games. This avoids
a shifting denominator when shuffling creates or removes ties. Also report actual
NPB win rate W/(W+L), but never confuse the two. Report shuffle mean, 2.5/97.5
percentiles, and actual minus shuffle mean in win equivalents.

This is a diagnostic reference distribution, NOT a calibrated sampling confidence
interval or a causal intervention. Shuffling can create games incompatible with
the actual inning/game-ending process. Each team is shuffled independently, so
the results do not constitute a coherent alternative league or predicted standings.
Scores depend on strategy and game state; exchangeability is not established.
Do not turn extreme reference percentiles into p-values or universal verdicts.

R2: Pearson correlation of adjacent-season excess/G, separately CL and PL and
for each shuffle mode; report n. Excluding 2020 removes both adjoining pairs,
not a fabricated 2019→2021 adjacency. Dependence between teams and seasons is
not corrected; report descriptive correlation, not statistical significance.

R3: home RD/G minus away RD/G, compared with the other five CL teams in that
season. No post-hoc thresholds or significance claims. Include all years and
the 2020-excluded mean.

## Deliverable and boundaries

Publish reproducible analysis code, source/hash receipts, derived team-season
results, and a Japanese interpretation separating observations, reference-model
comparisons, hypotheses and unknowns. Keep raw NPB HTML/game rows in ignored
`data/`, consistent with the existing repository policy; do not publish those rows.
No conclusion that residuals are luck, score pairing is skill, or low scoring is
a causal explanation. No cherry-picking only supportive years. Do not modify
PR #2's implementation or its proposition semantics as part of this research.
