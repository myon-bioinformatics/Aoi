# npb_team_fielding: team fielding stats

## Source

`https://npb.jp/bis/{year}/stats/tmf_c.html` (Central League), `tmf_p.html` (Pacific League). 1 page = 1 year, 1 league, 6 teams. 28 pages for 2012–2025. Team records (within the policy of not using individual records).

## Confirmed shape

The 2025 and 2018 Central League pages were checked with WebFetch (2026-10-05). WebFetch converts the page to prose, so spaces and line breaks inside cells aren't visible accurately.

| Heading | Column |
|---|---|
| チーム (team) | (team name) |
| 守備率 (fielding pct) | `fpct` |
| 試合 (games) | `g` |
| 守備機会 (total chances) | `tc` |
| 刺殺 (putouts) | `po` |
| 補殺 (assists) | `a` |
| 失策 (errors) | `e` |
| 併殺 (double plays; spans 2 columns, lower row `参加` "participated" and `球団` "team") | `dp_part`, `dp` |
| 捕逸 (passed balls) | `pb` |

In 2018, as with batting, there are spaces inside heading words and two-character team names (`失 策`, `中 日`).

### Other notations seen on real pages (preview_fielding, all 28 pages)

In the first preview, the table couldn't be read on any of the 28 pages, and it stopped on unknown notations (it didn't silently skip them):

- 2012–2024: `守機備会` (a cell with `守備／機会` set in two lines reads in this order once spaces are removed) → mapped to `tc`
- 2025: `併殺・参加`, `併殺・球団` (separate cells rather than a spanning heading) → mapped to `dp_part`, `dp`
- The 2012–2024 `併殺` (a heading spanning 2 columns plus a lower row) was readable from the first run

## Parsing contract

Same as batting ([npb_team_batting.md](npb_team_batting.md)). In addition, if a heading spans 2 or more columns horizontally, the next row is read as the lower headings and compared by the name joined after the parent's name (`併殺参加`). If the lower row can't be read, it goes into unknown and column positions aren't guessed.

## Handling in the pipeline

Initially the shape was checked with `preview_fielding` (without `--strict`). In the second run, all 12 teams × 14 years (2012–2025) were readable and unknown notations reached 0, so it switched to `inspect_fielding` (`--strict`) and passes to SakAnalytics' `fielding_join`. Cross-check: games match the calendar-derived values, total chances = putouts + assists + errors, and recomputed fielding pct matches the page's value at the displayed digits. Stops if they don't match.

`outputs/season.jsonl` contains only rates (`fld_fpct`, `fld_e_g`, `fld_dp_g`, `fld_pb_g`, `fld_a_po`) and differences from other teams (`fld_d_*`), not the raw counts.
