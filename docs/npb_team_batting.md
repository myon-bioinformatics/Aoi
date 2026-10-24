# npb_team_batting: team batting stats

## Source

`https://npb.jp/bis/{year}/stats/tmb_c.html` (Central League), `tmb_p.html` (Pacific League). 1 page = 1 year, 1 league, 6 teams. 28 pages for 2012–2025.

## Confirmed shape

First, the headings and one row were checked with WebFetch (2026-10-04). WebFetch converts the page to prose, so spaces inside cells weren't visible.
Then, checking the actually fetched pages (28 pages, 2012–2025) with `--strict` showed that **2012–2024 headings had spaces inside words** (`打 率`, `試 合`). 2025 has none.
Because of this, the 2012–2024 tables couldn't be read and it stopped before measuring. Headings were fixed to be compared after removing spaces.
The second check after the fix showed that **in 2012–2024, two-character team names are also written with a space between the characters** (`中 日`, `巨 人`, `広 島`, `阪 神`, `楽 天`, `西 武`).
Names of 3 or more characters (`ヤクルト`, `DeNA`, `ソフトバンク`, etc.) have no space. For team names, only the form of two characters with one space between is closed up when reading.

| Year | League | Headings | Difference |
|---|---|---|---|
| 2012 | Pacific | チーム, 打率, 試合, 打席, 打数, 得点, 安打, 二塁打, 三塁打, 本塁打, 塁打, 打点, 盗塁, 盗塁刺, 犠打, 犠飛, 四球, 故意四, 死球, 三振, 併殺打, 長打率, 出塁率 | `故意四` (intentional walks) |
| 2018 | Central | Same as above | `故意四` |
| 2024 | Central | Same as above | `故意四球` |

Team names use the same notation as `npb_calendar.TEAM_NAME` (`中日`, `DeNA`, `ロッテ`, etc.).

## Parsing contract

1. The row whose first cell is `チーム` (team) is the heading row. Headings are normalized, spaces inside words removed, then compared by full match with known names. Alternative notations (`故意四球` / `故意四`) map to the same column
2. Rows with the same number of cells as the headings are read as one team each. Team names must fully match a known notation. Only the two-characters-with-a-space form (`中 日`) is closed up before comparison. Values must fully match an integer (0–99999) or a rate (the `.256` form)
3. Unknown headings, unknown team names, teams from the other league, and values of the wrong shape go into `unknown`. If there is an unknown heading, that table isn't read (column positions aren't guessed)
4. Cross-check (SakAnalytics' `batting_join`): games and runs must match the calendar-derived values, and recomputed batting average, slugging, and on-base percentage must match the page's values at the displayed digits. Stops if they don't match

## Handling data

Source pages and per-team-per-year observations (at-bats, home runs, etc.) are kept only in `data/`, not in git.
`outputs/season.jsonl` contains only rates computed here (`bat_*`) and differences from other teams' mean in the same year and league (`bat_d_*`).
