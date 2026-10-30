# Remaining games, CS probability, and title magic numbers

Standalone shared components of SakAnalytics. They do not depend on the analysis in research Draft PR #3.
This is the implementation of the [pre-implementation plan](SEASON_SIMULATOR_PLAN.md); it does not establish the cause of Chunichi's slump.

## Quick start

Python 3.11–3.14. Probability calculation alone runs on the standard library.
Mathematical clinch determination uses OR-Tools.

```sh
python -m pip install -r sakanalytics/season-requirements.txt
python -m pip install "pytest>=9.1.1"
python sakanalytics/season_simulator.py sakanalytics/season-example.json \
  --as-of 2022-01-01 --through 2022-01-04 --trials 10000 --seed 42 \
  --exact --output /tmp/season-forecast.json
PYTHONPATH=sakanalytics python -m pytest sakanalytics/tests/test_season_simulator.py -q
```

The example is entirely fictional. A's magic number changes 2 → out → 1 → 0.
Omitting `--through` gives a single day. A date means after all that day's games, not the time a number lit during a game.
`--exact` adds clinch determination and magic numbers. `--solver-seconds` is the limit **per constraint solve**, not for the whole day.
With 6 teams and a CS, there are 24 solves per day. If each uses the default 10 seconds, one day takes about 240 seconds plus model-building time.

## Input and connection

The input JSON has the following 4 items. See [season-example.json](season-example.json) for an example.

| Item | Contents |
|---|---|
| `teams` | All team IDs, including interleague opponents |
| `rules` | Target league members, previous-year order, tie rules, number of CS slots, rules name and source |
| `schedule_basis` | Origin of the schedule: the schedule known at the time, or the schedule as actually played, settled later |
| `games` | Unique `id`, ISO `date`, `home`, `away`, `result` (H/A/D/null) |
| `expected_total_games` | (Optional) Scheduled total games per team (an integer, or a dict of team name → integer). Validation errors if it doesn't match |

Even if future results are in the input, `snapshot()` removes `result` after the point in time.
Undecided games on past dates are an error. The caller updates postponed games.
The engine does not check schedule completeness externally, but specifying `expected_total_games` (`--expected-total-games` in the CLI) checks that every team's games played plus remaining games equals the scheduled total.

It can also read Aoi's existing `data/observations/npb_calendar/games.jsonl`.
Prepare a settings JSON without `games` and pass it as follows.

```sh
python sakanalytics/season_simulator.py /tmp/season-config.json \
  --calendar-jsonl data/observations/npb_calendar/games.jsonl --season 2022 \
  --as-of 2022-09-01 --through 2022-09-30 --trials 10000 --seed 42 \
  --output /tmp/september.json
```

Calendar input uses **observations filtered to official games only** on the fetching side.
It reads `key/date/home/away/hs/as` and does not copy the source text to the output.
In this mode the remaining schedule is retroactive use of the schedule as actually played.
Unless the schedule announced at the time was saved, this cannot be called a reproduction of strict real-time prediction.
Raw input, HTML, and game rows are not committed.

To use the API from other subprojects, add the `sakanalytics` directory to Python's search path and
`from season_simulator import ...`. The existing `sakanalytics.py` is not turned into a package.

## Probability and clinching are different outputs

- `forecast()`: jointly simulates the rest of the season and returns rank counts, title probability, CS probability, and Monte Carlo 95% intervals. The same game is not drawn separately for each team.
- `qualification()`: checks whether a consistent assignment of remaining results exists that puts the team in the top slots / outside them, and returns `open / clinched / eliminated / unknown`. `not_held` if there is no CS.
- `title_magic()`: finds each team's self-controlled title and guaranteed title wins, and returns `off / lit / clinched / unknown`.
- `crossing_events()`: records when probability fell below 5%, 1%, 0.1%, and when it rose above again afterwards. If below from the start of observation, it is `initial_below`, not called a first-reached date.
- `magic_events()`: records state changes: lit, out, relit, clinched.

The constraint solver assigns integer remaining wins, losses, and ties per matchup.
Feasible assignments are returned as witnesses and cross-checked against a separate rational-number standings calculation.
A timeout is `unknown`. In searches for a maximum, obtaining one feasible example is not accepted as the optimum.

## Definition of the magic number

In this implementation, `self_control` means "if the team wins all its remaining games, it wins the title however other matchups end".
`lit` is the state where exactly one team in the league satisfies that and the guaranteed wins are settled.
`guaranteed_wins_needed` is the minimum wins such that "winning at least this many remaining games wins the title regardless of other wins, losses, ties, or tie-break order".
Among assignments where the team does not win the title, it searches for the one with the most wins for the team, and adds 1.
0 if the team already wins the title under all assignments; null if it cannot be guaranteed within the remaining games.

`magic` is the guaranteed wins when lit, 0 when clinched, and null when out or undetermined.
Even if a self-controlled title is proven, the number is undetermined if the maximum-wins search is `FEASIBLE` (optimum not proven) or `UNKNOWN`.
In that case `self_control=true` is kept and the lit candidate's `status` is `unknown`. `magic_events()` also records the change from undetermined to lit.
Identity with newspapers' customary notation in all cases has not been verified.
It is not mixed with values from formulas that omit ties or tie rules, and the definition is recorded in the output.
It is recalculated per date, so decreases and going out from head-to-head results or other teams' losses are reflected.

## Standings rules

Winning percentage is W/(W+L). Ties are not in the denominator, and rational/integer comparisons are used.
Standard profiles are limited to the following confirmed rules.

| Profile | Priority when winning pct is equal | CS slots |
|---|---|---|
| NPB 2022 Central, 2025 Central | Wins, winning pct against the group, winning pct within the league, previous-year standing | 3 |
| NPB 2022 Pacific | Winning pct against the group, winning pct within the league, previous-year standing | 3 |

Sources: [2022 Central](https://npb.jp/games/2022/info_cscl.html), [2022 Pacific](https://npb.jp/games/2022/info_cspl.html), [2025 Central](https://npb.jp/games/2025/info_cscl.html).
The NPB presets in this table (`npb_rules()`) live in Aoi's `aoi_npb.py`. SakAnalytics only receives `Rules` and holds no league-specific rules. `npb_rules()` rejects unconfirmed years and leagues. For other years, pass a `Rules` with a confirmed source explicitly.
The previous-year standing is also supplied by the caller. 2020 is not automatically converted to the usual 3 slots.

The group is fixed as the whole group tied on winning pct (and on wins in the Central), and games against that group are aggregated.
When only part of a group of 3 or more teams remains tied, whether head-to-head is reapplied to that subgroup needs further confirmation in the official text. This implementation does not reapply it.
The engine defines the rate with 0 decided games as 0. Under conditions that aren't a normal finished season, such as all ties, results also depend on this convention.
It does not automatically apply qualification deadlines, cancellation of unplayed games, or special rulings in official documents.
The answer assumes all input games are played, so in such cases the caller settles the schedule subject to qualification.

## Bounds of the probability model and intervals

The default model uses winning pct smoothed with a prior of 20 games at .500 from wins/losses up to the time,
and a Log5-style matchup formula. The tie rate is estimated from all input teams' played games plus a prior of 20 games at 5%.
Home advantage, park factors, players, starting pitchers, and future changes in ability are not included.
Passing (home win, visitor win, tie) per game ID in the API's `probabilities` connects another model.

The output is the result of a conditional baseline model, and its predictive accuracy is uncalibrated.
Monte Carlo intervals represent only the finiteness of iterations and do not include model error or uncertainty in ability estimates.
Do not read 0 advancements as mathematical elimination. Read threshold crossings near the boundary together with the intervals.
Even with 1,100 team-days, days of the same team in the same season are not 1,100 independent examples.
Aggregates cut off at the point of low probability have selection bias, so aggregates over the whole season and up to the mathematical clinch date are also kept.

## Verification

The [2022 connection verification JSON](season-validation-2022.json) contains only computed aggregates.
To rerun with local permitted input, use the following at Aoi's root (moved to Aoi's `scripts/` because it is NPB 2022-specific).

```sh
python scripts/season_verify_2022.py data/observations/npb_calendar/games.jsonl \
  --output /tmp/season-validation-2022.json
```

- With 20 synthetic league conditions × 3 teams, top 1 and 2 slots, self-controlled title, and maximum wins without the title were cross-checked between full enumeration of 27 cases and constraint satisfaction.
- Verified the coupling of remaining head-to-head games, Central and Pacific tie order, 3-team ties, in-league records, previous-year standings, interleague play, ties, timeouts, not referring to future results, and the daily CLI.
- With 858 games of 2022 input, Chunichi could still advance through September 26 and was eliminated on the 27th, with 139 games played and 4 left.
- Yakult had a guaranteed magic number of 2 on September 24 and clinched the title on the 25th.
- The 2022 Central and Pacific final standings matched the [official Central standings](https://npb.jp/bis/2022/stats/std_c.html) and [official Pacific standings](https://npb.jp/bis/2022/stats/std_p.html). The Pacific's tie for first was also resolved.
- Chunichi's elimination date also matched the [September 27 report](https://www.nikkansports.com/baseball/news/202209270001523.html?mode=all). The report date was not used as input to the determination.

The source data for the connection verification is the 2022 portion of the existing inning input (SHA-256 `0e98d6ce001eaca565378814a551d8b694e66dff7f4ef856d4e636e39bb87beb`) aggregated into final scores.
If row order or extra columns of the observations differ on rerun, the file fingerprint changes. `canonical_games_sha256` and per-date fingerprints allow separate comparison of the games and snapshots used.
The dedicated CI runs on synthetic input only, and does not fetch or publish raw data.
On each of Python 3.11–3.14, it runs separately with and without OR-Tools.
When it is not installed, only tests that use the solver are skipped; tests for standings, probabilities, thresholds, input, the CLI, and undetermined states run.
The CLI is also verified from a working directory outside the repository, and the probability-only path disables external packages with `python -S`.

## Remaining work

Confirming other years' rules, schedule snapshots from the time, probability calibration split by year, examples of thresholds re-emerging, and further comparison with newspapers' magic number notation.
(The option to check against a specified scheduled total, `--expected-total-games` / `expected_total_games`, is implemented.)
These are recorded separately from operational verification of the shared engine. Calculations for new research propositions come after a research plan.
