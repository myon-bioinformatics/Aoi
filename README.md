# SakAnalytics

<p align="center">
  <img src="docs/brand/icon.png" alt="SakAnalytics icon" width="160" />
</p>

[Icon](docs/brand/icon.png) · [Favicon](docs/brand/favicon.png)

> The numbers speak, but they haven't said everything yet.
>
> Team-season metrics, remaining-game and clinch-magic simulation, and synthetic-league experiments for NPB baseball game records. Split out from Aoi's sakanalytics/ (git subtree).

![SakAnalytics](https://github.com/myon-bioinformatics/Aoi/raw/main/docs/images/sakanalytics.webp)

*Concept image (a figure for sharing the idea; not the actual data or HTML structure)*

## Role in Aoi

**Analysis of team and season trends.**

| Challenges | Approach | Outcomes & value |
|---|---|---|
| Match records are hard to analyze | 1. Compute metrics | Data-driven analysis |
| Numbers are hard to visualize and interpret | 2. Project the remaining games | A visible outlook |
| The analysis procedure is unclear | 3. Compute clinch numbers and simulate leagues | Easier comparison and discussion |

Topics: data analysis, sports, visualization

## Overview

Builds team × season metrics from observation datasets (one game per line: `key, date, home, away, hs, as`).
It only measures; it does not exclude or judge good and bad (that is the job of PythDRagoras and the analysis settings).

Team membership and display names are given explicitly in the analysis settings' `[teams]`. If an undefined team appears, it is an error rather than being silently dropped.

The main columns are listed at the top of `sakanalytics.py`. Rank (`rank`) is a value derived from winning percentage and
does not reproduce the official tie rules, so ties are marked `rank_tie = true`.

There are also the outlook for remaining games, CS probability, and clinch magic numbers (`season_simulator.py`, [SEASON_SIMULATOR.md](SEASON_SIMULATOR.md)), annual stats auditing (`annual_audit.py`), and synthetic league generation (`synthetic_league.py`).

This repository was split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) (see "Relationship with Aoi" below).

## Installation and usage

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). The only runtime dependency is polars. ortools is optional; exact solving (`season_exact.py`) runs only when `season-requirements.txt` is installed.

```bash
git clone https://github.com/myon-bioinformatics/SakAnalytics.git
cd SakAnalytics
uv sync
uv run python sakanalytics.py --help
uv run python sakanalytics.py --games <games.jsonl> --config <analysis.toml> --out <season.jsonl>
```

The input `--games` is an observation dataset (one game per line: `key, date, home, away, hs, as`, the form [QueRyu](https://github.com/myon-bioinformatics/QueRyu) builds), and `--config` is the analysis settings TOML including `[teams]`. If batting, fielding, or line score observations exist, `--batting`, `--fielding`, and `--linescore` add columns.

## Layout

| File | Contents |
|---|---|
| `sakanalytics.py` | CLI. Team × season metrics (main columns listed at the top) |
| `season_simulator.py`, `season_exact.py` | Outlook for remaining games (standard library) and optional OR-Tools clinch determination ([SEASON_SIMULATOR.md](SEASON_SIMULATOR.md), [SEASON_SIMULATOR_PLAN.md](SEASON_SIMULATOR_PLAN.md)) |
| `annual_audit.py` | Auditing annual team tables (integer fields and published digits) |
| `synthetic_league.py`, `league_laboratory.py` | Synthetic leagues with annual stats fixed first, and experiments on them |
| `neighbors.py` | Descriptive neighbors that don't use results |
| `proposition_seed_audit.py`, `synthetic_rule_discovery.py` | Seed sensitivity of propositions, and tracking on synthetic data only (uses PythDRagoras) |
| `tests/` | pytest |

## Tests

Cycle data (`cycles/`) and [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) (`propositions`) stay in Aoi. They are not copied; Aoi's main is checked out and passed in. CI resolves that SHA at run time with `git ls-remote https://github.com/myon-bioinformatics/Aoi refs/heads/main`.

```bash
git clone https://github.com/myon-bioinformatics/Aoi.git .test-deps/aoi
git -C .test-deps/aoi checkout main
AOI_ROOT=$PWD/.test-deps/aoi PYTHONPATH=$PWD/.test-deps/aoi/pythdragoras \
  uv run --locked pytest -q --junitxml=reports/junit.xml
```

- CLIs take paths such as `--cycle-dir` explicitly. Tests receive Aoi only through `AOI_ROOT` and ask Aoi's `aoi_paths.py` for data locations.
- If `AOI_ROOT` doesn't point to Aoi (no `cycles/`), pytest stops at the start and gives the reason.
- The only runtime dependency is polars. ortools is optional; exact solving runs only when `season-requirements.txt` is installed, and otherwise those tests are skipped.
- In addition, tests use Aoi at `AOI_ROOT`.
  - Cycle data in `cycles/`.
  - PythDRagoras's `propositions`: `proposition_seed_audit.py` and `synthetic_rule_discovery.py` (`pythdragoras` on `PYTHONPATH`).
  - `tests/test_no_sibling_imports.py` confirms that no other Aoi sibling subprojects or `scripts/` are used (`propositions` is the known exception).

CI (`.github/workflows/ci.yml`) does the same on Python 3.11–3.15. The default ref is `refs/heads/main`, overridable via `aoi_ref` in `workflow_dispatch`. The resolved SHA is left in the job summary. pytest is `uv run pytest`.

In parallel, it resolves the parent [myon-bioinformatics](https://github.com/myon-bioinformatics/myon-bioinformatics)'s main with `git ls-remote` and the repository id, leaves that SHA in the summary, and then runs `pilot/vendor_dispatch.py` in verification mode against this repository's `vendor.lock.json` (without `--record`). Node is 24+, and that job's Python is 3.11+. Skipped rows are only reported; a mismatch with a recorded digest fails. This repository vendors no files from other repositories, so `files` in `vendor.lock.json` is empty.

## Relationship with Aoi

This repository was split out from the [Aoi](https://github.com/myon-bioinformatics/Aoi) subproject [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics).
The parent is Aoi (Aoi's parent is [myon-bioinformatics](https://github.com/myon-bioinformatics/myon-bioinformatics)). It is registered in Aoi's [`child-heads.json`](https://github.com/myon-bioinformatics/Aoi/blob/main/child-heads.json), and its tree equals Aoi's `sakanalytics/` at registration time (including `.github/`, `pyproject.toml`, `uv.lock`, `conftest.py`, `.gitignore`, and this README). It syncs with `git subtree` ("Syncing with Aoi" below; the full procedure is in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md)).
This README starts from the same file as Aoi's `sakanalytics/README.md`. Links to documents and data inside Aoi are written as GitHub URLs so they open from either place.

### Source hashes

`aoi_paths.py` lives in only one place, Aoi's top level (not in this repository). CLIs take `--cycle-dir`, and tests take only `AOI_ROOT`.

`analysis_sha256` of `proposition_seed_audit.py` is compared with Aoi's `seed-evaluation.json` and `source-divergence.json`. Tests compare only against the checked-out Aoi copy and its sidecar. A hash that differs from the record is not let through by a local declaration. With `SOURCE_HASH_CHECK=report` (pull_request), mismatches warn and continue; anything else, including unset, fails. Push to main and schedule fail. Generated artifacts have not been regenerated.

NPB-specific assumptions (number of teams, rounding, and head-to-head columns in annual tables, the CS rules preset `npb_rules()`, and the 2022 verification `season_verify_2022.py`) live in Aoi's `aoi_npb.py` and `scripts/`, and are received here as `AuditRules` and `Rules`.

### Syncing with Aoi

This repository is a subtree of Aoi's `sakanalytics/`. No files are excluded, and the tree of Aoi's `sakanalytics/` equals this repository's tree. Inside Aoi, `sakanalytics/.github/` does not run (GitHub reads only the repository root's `.github/`), and `sakanalytics/conftest.py` checks `AOI_ROOT` the same way under Aoi's pytest.

- The history was split out, preserving history, from `sakanalytics/` in Aoi `0a1751a60ac64708d679f22950aa2b14cf688efd` (main, the merge commit of #57) (main `67c8781b0e606ab41f56f717c2a84efa67b98533`; the tree at split time, `a54fc414f1959f7619619c0ae9398ff2fe8fbcbb`, equals Aoi's `sakanalytics/`).
- This history is not connected to Aoi's history, so a join is added to Aoi once. A squash commit with this repository's main commit in `git-subtree-split:` (tree equal to this repository) becomes the second parent of a merge that doesn't change Aoi's tree. After the join, `git subtree` starts from it.
- The join must remain as the second parent. Aoi PRs containing a join are merged with a merge commit, not squashed (squashing drops the second parent and `git subtree pull` and `split` stop).
- The `git-subtree-split:` commit must be on this repository's main. When squash-merging a PR here changes main's sha, a join with the same tree is re-added in Aoi.

Child → Aoi (on a branch made from Aoi's main):

```bash
git subtree pull --prefix=sakanalytics https://github.com/myon-bioinformatics/SakAnalytics.git main --squash
test "$(git rev-parse HEAD:sakanalytics)" = "$(git rev-parse FETCH_HEAD^{tree})"   # when Aoi has no unsynced changes
```

Aoi → child (on Aoi's main):

```bash
git fetch https://github.com/myon-bioinformatics/SakAnalytics.git main   # bring the split's starting commit local
git subtree split --prefix=sakanalytics -b sync/sakanalytics
test "$(git rev-parse sync/sakanalytics^{tree})" = "$(git rev-parse HEAD:sakanalytics)"
git push https://github.com/myon-bioinformatics/SakAnalytics.git sync/sakanalytics:refs/heads/<new-branch>
```

- Open a PR to this repository from the pushed branch. After merging, do the "child → Aoi" pull in Aoi to reattach Aoi's starting point to this repository's main (squash merges don't keep the split commits on main).
- Aoi's `scripts/check_child_heads.py --fail-on-diff` compares the tree of the sha registered in Aoi's `child-heads.json` with Aoi's `sakanalytics/`.

## Related subprojects

Each subproject of the parent [Aoi](https://github.com/myon-bioinformatics/Aoi) is its own repository. They are listed with their location in Aoi (subtree). The list and registration details are in Aoi's [docs/child-repositories.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/child-repositories.md).

| Repository | Location in Aoi | Role |
|---|---|---|
| [BlueProbe](https://github.com/myon-bioinformatics/BlueProbe) | [`blueprobe/`](https://github.com/myon-bioinformatics/Aoi/tree/main/blueprobe) | Observation and extraction (reads saved HTML/CSS/DOM and records what is there) |
| [QueRyu](https://github.com/myon-bioinformatics/QueRyu) | [`queryu/`](https://github.com/myon-bioinformatics/Aoi/tree/main/queryu) | Fetching and building observation datasets (caches with provenance) |
| **SakAnalytics** (this repository) | [`sakanalytics/`](https://github.com/myon-bioinformatics/Aoi/tree/main/sakanalytics) | Metrics and statistics from observation data (team × season metrics, outlook for remaining games) |
| [PythDRagoras](https://github.com/myon-bioinformatics/PythDRagoras) | [`pythdragoras/`](https://github.com/myon-bioinformatics/Aoi/tree/main/pythdragoras) | Verifying explanations (propositions, counterexamples, objections) |
| [NagoyAction](https://github.com/myon-bioinformatics/NagoyAction) | [`nagoyaction/`](https://github.com/myon-bioinformatics/Aoi/tree/main/nagoyaction) | Pipeline execution and automation (the same definition locally and on GitHub Actions) |
| [DRAgoWing](https://github.com/myon-bioinformatics/DRAgoWing) | [`dragowing/`](https://github.com/myon-bioinformatics/Aoi/tree/main/dragowing) | Figures and reports (Plotly.js HTML, the four-forms table) |

## License

MIT License ([LICENSE](LICENSE)). Same contents as Aoi's `LICENSE`.

---

# Research usage and column details (Chunichi / NPB)

The following covers usage in Aoi's research cycle (c001: Chunichi and NPB data) and details of the columns built from research. Paths in the command examples (`sakanalytics/…`, `cycles/…`, `data/…`) are locations from Aoi's root.

```bash
uv run python sakanalytics/sakanalytics.py --games data/observations/npb_calendar/games.jsonl \
  --config cycles/c001-chunichi/analysis.toml --out cycles/c001-chunichi/outputs/season.jsonl
```

## Advantages, errors, and columns built from research (R32–R34, R39)

All are values compared with other teams in the same year and league, per game. Columns for reading by amount rather than rank.
Upper and lower opponents are decided by **final standings** (an argument made knowing the results; Groups Defined By The Final Outcome in [docs/propositions.md](https://github.com/myon-bioinformatics/Aoi/blob/main/docs/propositions.md)).

| Column | Contents | Formula | Notes |
|---|---|---|---|
| `rf_adv` | Scoring advantage (more positive = scored more) | runs/game − mean runs/game of other teams | Same quantity as `rf_def_total` |
| `ra_adv` | Runs-allowed advantage (more positive = held down more) | mean runs allowed/game of other teams − runs allowed/game | |
| `run_balance` | Balance | `rf_adv + ra_adv` | If positive, the scoring shortfall was covered by runs allowed |
| `short_share` | Share (0–1) | shortfall ÷ (shortfall + advantage). shortfall = max(0, −`rf_adv`), advantage = `ra_adv` | Doesn't diverge near a zero divisor. 1 if it can't be offset, 0 if no shortfall and positive advantage, empty if neither |
| `rf_adv_z` / `ra_adv_z` | advantage ÷ standard deviation of advantages over all units | | The yardstick is the spread between teams. Moves slightly as years are added |
| `rf_zone` / `ra_zone` | 3 bins of the z above | z ≥ 1 → 1, z ≤ −1 → −1, between → 0 | Too wide in R33. The error-based bins (below) take precedence |
| `rf_sd_g` / `ra_sd_g` | Standard deviation of per-game runs scored/allowed | | Built from per-game values (at the measure stage) |
| `rf_adv_se` / `ra_adv_se` | Error of the advantage | √(own sd² ÷ games + Σ other teams' sd² ÷ games ÷ number of other teams²) | Each team's games are treated as independent |
| `rf_zone_se` / `ra_zone_se` | 3 bins by error | advantage ≥ error → 1, ≤ −error → −1, between → 0 | 0 means "indistinguishable from the mean" |
| `rf_adv_t` / `ra_adv_t` | How many times the error the advantage is (continuous) | `rf_adv / rf_adv_se`, `ra_adv / ra_adv_se` | `*_zone_se` is the same quantity cut at \|t\| ≥ 1 |
| `run_balance_t` | How many times the error the balance is | `run_balance / √(rf_adv_se² + ra_adv_se²)` | Errors of runs scored and allowed are treated as independent |
| `adv_shape_se` | Shape (9 possible strings) | `"<scoring bin>/<runs-allowed bin>"`, each `-1`, `0`, `+1` | e.g. `-1/+1` = clearly short on scoring, clearly ahead on runs allowed |
| `bat_routes` | Number of batting routes (0–2) | [`bat_d_bb_pa` ≥ 0] + [`bat_d_iso` ≥ 0] | One each if walks+HBP/PA or ISO is at or above other teams' mean. Empty if either is empty |
| `vs_top_minus_lower` | Winning pct vs upper opponents − winning pct vs lower opponents | `vs_top_wpct − vs_lower_wpct` | Upper = final 1st and 2nd, lower = 4th–6th. Decided by final standings, so it is partly arithmetically linked to whether a team is A |

## The A line (R46, R50)

| Column | Contents | Formula | Notes |
|---|---|---|---|
| `lg_lead_gap` / `lg_gap34` / `lg_rest_sd` | Winning pct gaps 1st − 2nd and 3rd − 4th, and std dev of winning pct excluding 1st | The k-th value of winning pct sorted descending | Not used for comparisons between leagues (user's policy) |
| `lg_line` | The A line for that year and league | (3rd's winning pct + 4th's winning pct) ÷ 2 | |
| `line_gap_pythag` | Distance of the run-differential expected winning pct from the A line | `pythag_fixed − lg_line` | Split by the identity winning pct − A line = `line_gap_pythag` + `resid_fixed` (wins beyond the run differential) |
| `lg_rank_at_500` | Which rank a .500 winning pct corresponds to (another way to draw the line) | Sort winning pct descending and linearly interpolate the rank between the 2 teams straddling .500 | Smaller than 3.5 means .500 sits toward the top. Empty if all teams are on one side of .500 |
| `lg_break_after` / `lg_break_gap` | The k where the largest gap in winning pct (where the data splits naturally) is "between k-th and (k+1)-th", and that gap | Maximum difference between neighbors in winning pct sorted descending | A line that doesn't use human-chosen cut points. On equal gaps, the upper side |
| `lg_tier` / `lg_tier_of_3rd` | Of the 3 clusters split by the 2 largest gaps (1, 2, 3 from the top), own cluster and 3rd place's cluster | 2 cut points in descending order of neighbor gaps | If in the same cluster as 3rd, the team was in a group close to 3rd in winning pct even if below the A line |
| `lg_bar` | The height to clear (R56) | The (teams ÷ 2)-th of the other teams' winning pct in the same year and league, sorted descending (3rd for 6 teams) | An external height determined by other teams only. Exceeding it puts a team in the upper half (ties excluded). The sign of winning pct − lg_bar agrees arithmetically with A/B |
| `lg_bar_pythag` / `pbar_gap` | That year's height to clear, seen from run differential (R73) | The (teams ÷ 2)-th of other teams' run-differential expected winning pct (`pythag_fixed`), sorted descending. `pbar_gap` = own run-differential expected winning pct − that | Not compared with a fixed .500 (the height changes between years with a runaway 1st and close years). Negative means it falls short at face value of the run differential |
| `mix_lo` / `mix_hi` / `mix_zone` | The band where A and B mix (R53), and whether the team is below, in, or above it (−1, 0, +1) | Over all units of other years, excluding own year (and years in the settings' `[[exclude]]`), the lowest A winning pct (mix_lo) and highest B winning pct (mix_hi) | Leave-one-year-out, so the line isn't set with that year's data. Leagues are pooled. Exactly at an edge is in (0). Empty if other years have no A or no B |
| `live_mix_lo` / `live_mix_hi` / `live_mix_zone` | The same band drawn with winning pct over only games that matter for A/B (`live_wpct`) (R58) | `add_mix_zone(col="live_wpct", prefix="live_mix")` | The band with games that don't matter (after it was decided) removed |
| `rf_mix_*` / `bal_mix_*` / `vsl_mix_*` / `sim_mix_*` (`_lo`, `_hi`, `_zone`) | The same band drawn with scoring advantage (`rf_adv`), balance (`run_balance`), winning pct vs lower opponents (`vs_lower_wpct`), and A probability from the distribution (`sim_p_upper`, R67) (R66) | `add_mix_zone(col=..., prefix=...)`, leave-one-year-out | Lines of metric values, not ranks. −1 is worse than any A in other years |
| `rf_adv_bgap` / `run_balance_bgap` / `vs_lower_wpct_bgap` and `rfg_mix_*` / `balg_mix_*` / `vslg_mix_*` | A metric's difference from that year's height (the last value of the other teams' upper half), and bands drawn with that difference (R74) | `add_bar_gaps` → `add_mix_zone` | Not compared with fixed 0 or .500. Carries the difference between runaway and close years |
| `rf_state2` / `ra_state2` | Two-line state of scoring advantage and runs-allowed advantage (`A`, `AB`, `B`, R67) | Sort the same year and league's values descending and split at the midpoint of 2nd and 3rd and of 4th and 5th (`add_state2`) | Lines of values, not ranks. Empty for league-years with a team lacking a value |
| `fld_fpct` / `fld_e_g` / `fld_dp_g` / `fld_pb_g` / `fld_a_po` and `fld_d_*` | Team fielding rates (`--fielding`): fielding pct, errors/game, double plays/game, passed balls/game, assists/putouts, and the difference from other teams' mean in the same year and league | `fielding_join`. Stops if games, chances, or fielding pct don't reconcile | Negative `fld_d_e_g` means fewer errors than other teams. Raw counts are not output |
| `ls_cov` / `ls_e_g` / `ls_opp_e_g` / `ls_e_net_g` / `ls_e_net_close` / `ls_e_net_win` / `ls_e_net_loss` / `ls_e_net_q4` | Errors from per-game line scores (`--linescore`): share of games with a line score, own and opponent errors/game, and (own − opponent)/game over all games, 1-run games, wins, losses, and the last segment | `linescore_join`. Joined by date and team; stops if R doesn't match the schedule's score | Filled only for fetched years (empty for years with `ls_cov` = 0). Negative means fewer errors than the opponent |
| `rank_fixed_x` / `rank_fixed_left` / `rank_fixed` | The position of the day the final rank became mathematically certain (0 = opening day, 1 = last day), games left that day, and that rank (R57) | The day the best and worst possible ranks agree, from upper/lower bounds on winning pct assuming all remaining games won/lost, at the end of each day | Conservative since it ignores head-to-head (may come late but never early). Empty if tied to the end |
| `live_g` / `live_wpct` / `live_rd_g` | Games that matter for A/B (up to and including the day it was decided whether the team is in or out): count, winning pct, and run differential per game (R57) | Cut at the `clinch_in_x` or `clinch_out_x` day. All games if never decided | The cut is the same conservative date as R26 |
| `dead_g` / `dead_wpct` / `dead_rd_g` | Games after the decided day (games that don't matter for A/B) | The rest of the above | If none, `dead_g` = 0 and the others are empty |
| `h2_live_g` / `h2_live_wpct` | Of the second half (the latter half of own games), the count and winning pct of games that matter for A/B (R63) | The boundary is games ÷ 2 rounded down. Games that matter use the same cut as `live_*` | Separates whether a second-half drop happened in games after it was decided |
| `h1_rd_g` / `h1_wl_vs_upper` / `h1_wl_vs_lower` and the same for `h2_live_*` | For the first half (all games) and only the second half's games that matter: run differential per game, and wins − losses vs the same league's upper half and lower half (R64) | Upper/lower by final winning pct (ties to the upper side) | Interleague opponents are not counted |
| `lock_g` / `lock_x` | In the standings, the games played (N) and the date position on the day the team's side (upper half or not) became the same as at the end and no longer changed (R60) | Ordering by winning pct at the end of each day. Upper side if (number of teams above in winning pct + 1) ≤ teams ÷ 2 (ties to the upper side) | Not mathematical certainty (`clinch_*`), but when the actual standings settled |
| `lg_set_lock_x` | The position of the day the league's upper-half membership became the same as at the end and no longer changed (R60) | Same as above | One value per league |
| `q_wl_1`–`q_wl_4` / `lone_down_n` | Wins − losses in each of 4 segments of own games in order played, and the number of segments where only this team in the league had a losing record (R60) | Boundaries are games × q ÷ 4 rounded down | A record of "only this team declined during a period". No meaning is sought in it by itself; it is material for propositions |
| `pre_lock_wpct` / `post_lock_g` / `post_lock_wpct` | Winning pct up to (and including) the day the team settled on its final side in the standings, and games and winning pct after (R61) | Cut at `lock_g` | Whether it kept fighting the same way after settling, or went back to even |
| `q4_g` / `q4_rd_g` / `q4_one_run_net` / `q4_wl_vs_upper` / `q4_wl_vs_lower` | For the 4th segment (the last 1/4 of own games, boundary games × 3 ÷ 4 rounded down): games, run differential per game, wins − losses in 1-run games, and wins − losses vs the same league's upper/lower half (R62) | Upper/lower by final standings (assumption) | Interleague opponents count as neither upper nor lower |

## Reference values for paths to B (R45)

`path_offense`, `path_defense`, `path_convert`, `path_collapse` (whether each applies), and `b_paths`, joining those that apply with `+` (e.g. `offense+convert`; `none` if none apply). These are **reference values not used for judgement (proposition exit codes)**, and the rules are fixed to those decided in prior research (not changed after seeing values). They are also attached to A units (read as: entered A despite matching a path).

| Path | Rule | Source |
|---|---|---|
| `offense` scoring shortfall | `rf_zone_se = −1` (scoring advantage negative beyond the error) | R35, R40 |
| `defense` worse runs allowed | `ra_zone_se = −1` | R40, R44 |
| `convert` can't turn run differential into wins | `wins_vs_pythag < −2` or `alloc_z_strat < −1` | R38, R44 |
| `collapse` second-half collapse | `course_fade ≥ 3` and `course_rf_d < 0` and `course_ra_d > 0` and `half2_vs_pythag < −2` | R43, R44 |

If the source column is empty, that path is empty. If no path can be determined, `b_paths` is empty.

Every column only "measures" and does not judge good or bad. Which research created each and why is in `R31`–`R39` and `R45` under `cycles/c001-chunichi/from-cycle-001/research/` (research on the cycle-001/chunichi branch side; numbered separately from the canonical `research/`).

## Annual team tables and synthetic leagues

`annual_audit.py` audits official annual stats for integer fields, published digits of rates, common columns between tables, and agreement with existing season tables.
`synthetic_league.py` fixes the whole league's annual stats first, checks the head-to-head capacity with integer max flow, and then expands into game results.
The main target is 2013–2026. The default is 14 years of 3 conditions × 1 set each, and it passes if the annual stats and game totals match for all 14 years.
Covering past years or increasing the number generated is not required. Years before 2013 are kept for reference, separate from regular analysis, calibration, and pass judgement.
It can build examples with the same runs scored/allowed but different win/loss allocation. Generated examples are not added to measured counts.
Procedure, generation families, and completion conditions are in [c001's fetch and synthetic verification record](https://github.com/myon-bioinformatics/Aoi/blob/main/cycles/c001-chunichi/annual-history-synthetic.md).

## Experiments on conditional generation, ability budgets, and scoring scales

`league_laboratory.py` runs an experiment that fixes runs scored/allowed and fills in hidden wins/losses, an experiment that allocates ability under the same point budget,
and an experiment that measures the same integer scores in 6 kinds of analysis units. It checks with annual stats first and expands only representative examples into games.
It keeps ungeneratable examples, pass/fail of recommended conditions, fixed/new FP/FN, and rank changes between scales as material for the next propositions.

```bash
python -S sakanalytics/league_laboratory.py
```

Settings are in [league-laboratory.toml](https://github.com/myon-bioinformatics/Aoi/blob/main/cycles/c001-chunichi/league-laboratory.toml),
and observation and interpretation in [R29](https://github.com/myon-bioinformatics/Aoi/blob/main/cycles/c001-chunichi/research/R29-league-laboratory.md).
This is exploration under the synthetic model's assumptions; existing propositions, pass conditions, and measured scores are not changed.

## Common evaluation axes for all propositions and seed sensitivity

PythDRagoras attaches Precision / Recall / F1 / Accuracy /
Balanced Accuracy / MCC to every proposition and each evaluated form. Zero denominators, constant predictions, etc. are left as `None` with a reason and are not used for formal judgement.
Propositions without synthetic input also have seed evaluation fields, `None` when unevaluated. It is not limited to particular re-evaluation candidates.

```bash
python sakanalytics/proposition_seed_audit.py --cycle-dir cycles/c001-chunichi
# only when also regenerating the annual-stats evidence under the same conditions:
python sakanalytics/proposition_seed_audit.py --cycle-dir cycles/c001-chunichi --generate-plans
```

It uses the existing 3 series of synthetic annual stats, and ability budget seeds 0–9, 2023–2026, all 28 allocations, and decay 0/0.4.
The evidence is in `cycles/c001-chunichi/outputs/exploratory/proposition-evaluation/`.
The regular c001 pipeline also reads the diagnostics with `--seed-evaluation` and lists all propositions in `outputs/index.md`.
Seed variation is measured only within groups with the same year, proposition definition, and generation conditions, kept separate from the effects of changing conditions.
Synthetic input covers 13 propositions; propositions lacking needed columns or a mapping to real teams stay unevaluated.
