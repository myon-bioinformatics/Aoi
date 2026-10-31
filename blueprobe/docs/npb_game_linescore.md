# npb_game_linescore: per-game line scores (R H E)

## Source

The game links in the schedule (`npb_calendar`) observations, `https://npb.jp/bis/{year}/games/s{game ID}.html`. One page per game. Only team records are read (policy of not reading individual records).

## Confirmed shape

One 2024 game was checked with WebFetch (2026-10-05). The line score has 2 rows (visitor, home); two-character team names are written with a space between (`中 日`), and Giants is `読売` (Yomiuri). The last 3 cells are R (runs), H (hits), E (errors). Errors per inning, or which player made them, are not on the page.

## Volume and fetching

About 860 pages per year. At 3-second intervals per page, about 45 minutes. All 14 years would be about 12,000 pages and about 10 hours, so as decided with the user, only 2025 is fetched first (`linescore_years` in `pipeline.toml`). Years are expanded after the shape and cross-checks pass.

## First fetch (2026-10-05, 2025, 858 pages)

- The 858 pages were fetched once and saved (858 HTTP requests; after that, reread from the saved pages)
- Only 84 games were readable. In addition, player stat rows (pitcher name rows, etc.) were put into unknown en masse as "line-score-shaped but with an unknown team name" (32,370)
- Player rows are not read by policy, so it was fixed not to put them into unknown either. For unreadable pages, only the position of the team name cell and the number of cells per row are kept in counts to check the shape

## Rereads (from saved pages, without going to the source)

| Run | Games read | Clue | Fix |
|---|---|---|---|
| 1 | 84 | 32,370 player rows in unknown | Don't read or keep player rows |
| 2 | 84 | 404 pages with one team name row, 370 with none | Keep the leading name of line-score-shaped rows as candidates |
| 3 | 84 | 北海道日本ハム, 千葉ロッテ, 埼玉西武, 広島東洋, 東京ヤクルト | Add as observed official names |
| 4 | 460 | 東北楽天, 横浜DeNA, 福岡ソフトバンク | Add likewise |
| 5 | **858 (all games)** | 0 unknown | Switch to `--strict` and go to measure |

In line scores, team names were written as abbreviations with a space between for two-character teams (`中日`, `読売`, `阪神`), and as official names for the others (`広島東洋`, `横浜DeNA`, etc.).

## Parsing contract

1. Rows whose last 3 cells are integers are treated as line score rows, and the team name in the first cell (spaces removed) is compared by full match with known notations (`読売` is the Giants)
2. Player rows (pitching and batting stats) are not read, and are put in neither unknown nor counts (individual records are not handled). For unreadable pages, only shape clues (position of the team name cell, number of cells per row) are kept in counts
3. If a page doesn't have exactly 2 rows (2 teams) starting with a team name and ending with R, H, E, that page isn't read
4. Cross-check (to be done in SakAnalytics): R must match the runs in the schedule observations

## Handling in the pipeline

Initially the shape was checked with `preview_linescore` (without `--strict`); once all games were readable it switched to `inspect_linescore` (`--strict`) and passed to `linescore_join`.
