# npb_schedule_current: this season's schedule and results (season in progress)

## Source

`https://npb.jp/games/{year}/schedule_{month}_detail.html` (March–November). 1 page = 1 month, games of all 12 teams.

Past years' schedules (`npb_calendar`, `/bis/{year}/calendar/index_{month}.html`) haven't been created yet for this season. For 2026 all 9 pages were 404 (pipeline run on 2026-10-06).

## Confirmed shape

September 2026 was checked with WebFetch (2026-10-06). WebFetch converts the page to prose, so the tag order isn't visible. What was visible:

- 1 game = `巨人 [4 - 3](https://npb.jp/scores/2026/0901/g-db-20/) DeNA`. The link text is only the score
- Link target `/scores/{year}/{MMDD}/{home}-{visitor}-{number}/`. The first code matched the team written first (home) (all 6 games)
- Codes: g, s, db, d, t, c (Central), h, f, b, e, l, m (Pacific). The same codes as `npb_calendar`'s records

Teams are read from the URL codes, not from the team names in the text. The record shape (other than key) is the same as `npb_calendar`, so SakAnalytics can read the two joined (list both in `--games`; it stops if the same key appears).

## Not accepted

| Category | Contents |
|---|---|
| `scheduled:<month>` | A game link without a result (no digits, or `- （球場）18:00` "- (stadium) 18:00") |
| `cancelled` | `中止` (cancelled), `ノーゲーム` (no game) |
| `non_regular` | Score form but not a game link |
| `non_regular:オールスター` | Code is cl or pl (All-Star) |
| unknown | Unknown team codes, or digits that aren't in score form (in-progress scores, etc.) |

Whether CS and the Japan Series appear in the same link form is unconfirmed. `check()` returns ok=False if a team has more than 143 games, a team has 2 games on the same day, or a pairing exceeds the official count (25 within a league, 3 interleague). Since the season is in progress, falling short of 143 is normal.

### Notations seen on real pages (preview_2026, 2026-10-06)

First preview: 9 pages, 854 games accepted, 41 cancelled, 20 unknown. The 12 teams' game counts were 140–143 (7 teams had finished 143). Chunichi was 60–81–2, matching the external report (C26).
The 20 unknowns were of two forms (added as observed notations, then switched to `--strict`):

- Games before results: link text of the form `- （ZOZOマリン）18:00` (with spaces and line breaks) → `scheduled:<month>`
- All-Star: link target codes `cl-pl` and `pl-cl` → `non_regular:オールスター`

## Usage commitments

- Used only for the 2026 provisional figures (R74). Not included in the main body (2013–2025)
- R18: brought into the main body after all teams finish 143 games. At that time, a person checks the pages after the official games (CS may appear)
- For pages of a season in progress, QueRyu checks for updates (If-Modified-Since). Provenance stays in the ledger (`outputs/fetched/npb_schedule_current.jsonl`)
- First check the shape with preview (without `--strict`). Switch to `--strict` after seeing the real pages' notation
