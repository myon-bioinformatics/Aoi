# Source npb_calendar: npb.jp's HTML structure by year

Even if the published information is the same across years, the DOM structure and the tags used may have changed.
This file records which page of which year was checked for what, **separating observed facts from unconfirmed points**.
Gaps are not filled by guessing (xprobe: Inference presented as measurement; Aoi: Separate Facts From Explanations).

## Sources

| Period | URL | Unit | Status |
|---|---|---|---|
| 2012–2025 | `https://npb.jp/bis/{year}/calendar/index_{MM}.html` | 1 page = 1 month, all 12 teams | Adopted |
| 2016– | `https://npb.jp/games/{year}/schedule_{MM}_detail.html` | 1 page = 1 month | Not adopted (404 for 2012–2015) |

Back numbers under `games/` exist only from 2016 (confirmed 2026-10-03).
So everything was unified on `bis/{year}/calendar/`, which exists from 2012.

## Parsing contract

1. Only official game links whose path **fully matches** `/bis/{year}/games/s{year}{MMDD}{serial}.html` are targeted. If the path's year and the first 4 digits of the game ID don't match, it is excluded.
2. After normalizing the link text, it must **fully match** `{home abbreviation} {runs} - {runs} {visitor abbreviation}`.
   - Normalization: replace NUL with U+FFFD, apply NFKC, and collapse consecutive whitespace into one.
   - Abbreviations are limited to the 12 teams' single characters (巨 ヤ デ 中 神 広 ソ 日 オ 楽 西 ロ).
   - Runs are limited to half-width 0–99.
   - Characters treated as dashes: `-` `‐` `‑` `‒` `–` `—` `−`
3. The team written first is home. The score is in "home − visitor" order.
4. **Non-official tournaments are separated by heading.** CS, the Japan Series, the All-Star Game, and the Asia Series also appear as the same `/bis/{year}/games/` links and can be on the same day as official games (e.g. 2013-10-12). They can't be separated by path or date.
   - On the page, each day's box (`class="stvsteam"`) contains a tournament heading (`class="tescheaten"`), and the games after it belong to that tournament.
   - Headings are normalized, then compared by full match with the 6 known ones (`CS ファーストS`, `CS ファイナルS`, `クライマックスS` (Pacific 2020), `日本シリーズ`, `オールスター`, `アジアシリーズ`).
   - Unknown headings go into `unknown` (neither accepted nor silently discarded).
5. What is dropped is not silently discarded but reported as counts.

| Category | Condition | Handling |
|---|---|---|
| `games` | Game link and score form | Accepted |
| `cancelled` | Game link and `* - *`, `中止` (cancelled), or `ノーゲーム` (no game) | Count only |
| `non_regular` | Score form but not a game link | Count only |
| `non_regular:<heading>` | Game link, but under a non-official tournament heading | Count per heading |
| `unknown` | A game link matching none of the above, or an unknown heading | Keep count and source text. **Suspect a notation change** |

This oversight in categorization (headings weren't checked before) was found by PR #3 (GPT's research R001) running against real pages for 2013–2025.
There, 276 were excluded (All-Star 25, CS First Stage 63, CS Final Stage 102, Japan Series 75, Asia Series 9, Climax Series 2),
and the remaining 11,028 games matched the official annual stats for 156 team-years × 6 items. When run on real data, compare against these counts.
Contamination is also caught by the check against known game counts (below), so the pipeline stops before measuring if the check fails (`--strict`).

When a new notation is found, add a case to `blueprobe/tests/cases/npb_score_text.jsonl` before widening the regex.

## Confirmation status by year

The method of confirmation was "reading the rendered result with WebFetch", not the raw DOM.
The raw DOM is cached in `data/raw/npb_calendar/` during the first bulk fetch, then summarized into `cycles/c001-chunichi/outputs/observed.md` by the pipeline's `inspect` step (no network access).

| Year | Page checked | Observed facts | Unconfirmed |
|---|---|---|---|
| 2012 | `calendar/index_04.html` | March–April are on one page. Game links are of the form `s2012040100187.html`. Text is `巨 4 - 2 ヤ`. Cancellations are `ヤ * - * 神` | Parent elements in the DOM, May–November |
| 2012 | `calendar/index_11.html` | The Japan Series and Asia Series appear in the form `日本シリーズ[日 2 - 10 巨]` | Whether there are official game links |
| 2012 | `games/schedule_03,04_detail.html` | 404 | — |
| 2013 | None | — | Everything |
| 2014–2019, 2021–2023 | `calendar/index_06.html` for each year | The page exists. All Chunichi game links are of the form `/bis/{year}/games/s{year}{MMDD}{5 digits}.html`, with text `{abbr} {runs} - {runs} {abbr}`. Interleague games (西, ロ, ソ, 楽, 日, オ) use the same form | Parent elements in the DOM, months other than June |
| 2020 | `calendar/index_07.html` | Same form as above. Links to monthly pages exist only for June–November, not March–May (opening postponed) | Parent elements in the DOM |
| 2024 | `calendar/index_04.html` | Game links are of the form `s2024040201097.html`. From `中 4 - 3 巨` (Vantelin Dome) and `広 0 - 1 中` (Mazda), the first team was confirmed as home | Parent elements in the DOM |
| 2024 | `calendar/index_10.html` | Official games have links. CS appears as `CS ファーストS[神 1 - 3 デ]` and the Japan Series as `日本シリーズ[デ 3 - 5 ソ]`, without official game links | hrefs on the CS and Japan Series side |
| 2024 | `games/schedule_04_detail.html` | Ties are `2 - 2`, cancellations `中止`. Score links are `/scores/2024/0402/d-g-01/` | — |
| 2025 | `calendar/index_06.html` | Same form as above | Parent elements in the DOM, months other than June |

The 2014–2025 checks were done on 2026-10-03, one page per year.

Dates are taken from the game link URL (`s{year}{MMDD}…`). In WebFetch's summaries, there were cases where the calendar date and the URL date disagreed (June 2023). Dates are not inferred from cell position.

## Expected game counts (known values for judging without querying npb.jp)

Official games per team. Cancelled games are made up, so if nothing is missed every team matches this value.
`npb_calendar.check()` checks against this table, and the `observe` and `inspect` steps display and record it.

| Year | Games |
|---|---|
| 2012–2014 | 144 |
| 2015–2019 | 143 |
| 2020 | 120 (shortened season due to the postponed opening; the Central League held no CS) |
| 2021–2025 | 143 |

## Origin of test fixtures

`blueprobe/tests/fixtures/npb_calendar_sample.html` was **synthesized** from the WebFetch observations above (April and October 2024); it is not raw HTML.
Once raw HTML is fetched, add one page per representative month to the fixtures and move structural checks there (markdown: DOM_FIRST_WITH_THIN_CORPUS).

## Record contract (observed and derived values)

Each line of `games.jsonl` holds the source text and the result of reading it side by side.

| Kind | Column | Contents |
|---|---|---|
| Observed | `raw_text` | The link text itself (before normalization) |
| Observed | `href`, `source_url` | The game link and the page it appeared on |
| Derived | `key` | Game ID (from the URL) |
| Derived | `date` | Date (from the game ID, not from cell position) |
| Derived | `home`, `away`, `hs`, `as` | Abbreviations and runs as read |
| Derived | `normalized` | Whether normalization changed the text (comparable with `raw_text`) |

The normalization (NUL → U+FFFD, NFKC, collapsing whitespace) is recorded in the dataset's `.manifest.json`.
