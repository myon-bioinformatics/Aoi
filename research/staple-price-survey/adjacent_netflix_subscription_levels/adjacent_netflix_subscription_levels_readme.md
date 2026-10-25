# adjacent_netflix_subscription_levels — Netflix list prices (tompec history)

Retrieved: 2026-10-25 Asia/Tokyo

## Hard rules

- Absolute subscription list prices in **local currency as published** (not CPI indices).
- No FX conversion; source `price_usd` is **not** loaded.
- No gap-fill of null plans; `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Country universe = Big Mac ISO3 (`countries_iso3.txt`).

## What

Historical panel of Netflix plan list prices from [tompec/netflix-prices](https://github.com/tompec/netflix-prices) (CC-BY-4.0), clone commit `efa54e3` (2026-09-28).

Primary easy raw (box): `/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/tompec-netflix-prices/data/*.json`  
(`latest.json` ignored — duplicate of newest dated snapshot.)

**Variables** (prefix `netflix:`):

| variable | plan |
|----------|------|
| `netflix:mobile` | Mobile |
| `netflix:basic_with_ads` | Basic with ads |
| `netflix:basic` | Basic |
| `netflix:standard_with_ads` | Standard with ads |
| `netflix:standard` | Standard ← primary numéraire-candidate plan |
| `netflix:premium` | Premium |

Unit: `{ISO4217} per monthly subscription`.

## Coverage (this pack)

| Metric | Value |
|--------|------:|
| Rows | **5029** |
| ISO3 | **53** / 56 Big Mac |
| Snapshots | **30** (2023-01-07 … 2026-09-28) |
| `netflix:standard` | 1590 rows / 53 ISO3 |
| `netflix:premium` | 1590 |
| `netflix:basic` | 1371 |
| `netflix:mobile` | 261 |
| `netflix:standard_with_ads` | 210 |
| `netflix:basic_with_ads` | 7 |

**Big Mac ISO3 with no tompec country series:** CHN, EUZ, RUS.

- **EUZ**: Netflix prices by member state, not euro-area aggregate — not invented here. Individual DE/FR/ES/… exist upstream but sit outside the Big Mac ISO3 list (Big Mac uses `EUZ`).
- **CHN / RUS**: absent from tompec country list this clone.

## Burger Parity snapshot cross-check (not history)

`prices_all.csv` (`product_slug=netflix`, 30 countries) is a **single cross-section** reference (same family as Aoi `netflix_standard_burgerparity_panel.csv`). It is **not** used as a time series and **no values are copied** into this panel.

Cross-check of Burger Parity standard LCU vs any tompec standard observation (see `_crosscheck_burgerparity.json`):

- Exact LCU+currency match on ≥1 tompec date: **10** ISO3 (IDN, BRA, JPN, KOR, POL, CAN, AUS, MEX, GBR, USA).
- Near (no exact): **12** — expected when observation dates / plan definitions diverge.
- Outside Big Mac universe (ESP, ITA, PRT, FRA, DEU, IRL, NLD, …): documented, not loaded.
- CHN: in Big Mac list but no tompec series.

## Not collected / left alone

| Asset | Why |
|-------|-----|
| Aoi `netflix_standard_burgerparity_panel.csv` | Aoi lane — Burger Parity snapshot only; do not overwrite |
| iPhone CSVs in `numeraire_hist_2026-10-25/` | Aoi durables lane — **leave alone** |
| Spotify / other Burger Parity products | Out of scope this pack |
| Source `price_usd` | Published FX companion — skipped (no FX lane) |

## Files

- `adjacent_netflix_subscription_levels_vertical.csv` (+ `.gz`)
- `build_netflix_subscription_levels.py`
- `_build_stats.json`
- `_crosscheck_burgerparity.json`
- `raw/SOURCE.md` — provenance (full JSON kept on box under aoi-phase2, not vendored here)
- `adjacent_netflix_subscription_levels_missing.md`

## Status (2026-10-25 Asia/Tokyo)

- Historical tompec → Season2 vertical panel landed.
- Schema header verified; all `estimated_value` empty; csv/gz match; **0** duplicate keys.
- Attribution: [thomas.io](https://www.thomas.io) / tompec/netflix-prices, CC-BY-4.0.
