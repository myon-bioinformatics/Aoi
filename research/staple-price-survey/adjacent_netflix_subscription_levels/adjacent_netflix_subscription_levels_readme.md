# adjacent_netflix_subscription_levels — Netflix list prices (2020+)

Retrieved: 2026-10-25 Asia/Tokyo

## Hard rules

- Absolute subscription list prices in **local currency as published** (not CPI indices).
- No FX conversion; source `price_usd` / USD-only mirrors are **not** loaded.
- No gap-fill of null plans; `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.
- Country universe = Big Mac ISO3 (`countries_iso3.txt`).

## What

Historical panel of Netflix plan list prices from three open LCU sources:

1. **tompec/netflix-prices** (CC-BY-4.0) — dated JSON 2023-01-07 … 2026-09-28
2. **fromabroad.org** — 2020-03-10 LCU table (curated native-currency rows)
3. **Comparitech Dec-2021** via Kaggle `apoorvgupta25/netflix-prices` — dated 2021-12-28

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
| Rows | **5261** |
| ISO3 | **54** / 56 Big Mac |
| Earliest date | **2020-03-10** |
| Latest date | **2026-09-28** |
| Distinct dates | **32** |
| tompec snapshots | 30 (2023-01-07 … 2026-09-28) |
| fromabroad 2020-03-10 | 61 rows / 20 ISO3 |
| Comparitech 2021-12-28 | 171 rows / 54 ISO3 |
| `netflix:standard` | 1664 |
| `netflix:premium` | 1664 |
| `netflix:basic` | 1445 |
| `netflix:mobile` | 271 |

**Big Mac ISO3 with no series at all:** CHN, EUZ.

- **EUZ**: Netflix prices by member state — not invented as euro-area aggregate.
- **CHN**: absent from open LCU tables used here.
- **RUS**: added from Comparitech Dec-2021 (RUB); absent from tompec / fromabroad curated set.

## Thin gaps

| Window | Status |
|--------|--------|
| Before 2020 | Out of scope (owner: ~2020+ COVID-era) |
| 2020 | Partial — fromabroad curated 20 BM ISO3 (native LCU only) |
| 2021 | Good BM overlap — Comparitech Dec-2021 via Kaggle (~50 ISO3 currency-matched) |
| 2022 | **Thin** — no easy open full multi-country LCU cross-section (USD-only mirrors skipped) |
| 2023-01 … 2026-09 | Dense — tompec dated JSON |

## Burger Parity snapshot cross-check (not history)

`prices_all.csv` is a **single cross-section** reference. **No values copied** into this panel.
See `_crosscheck_burgerparity.json`.

## Not collected / left alone

| Asset | Why |
|-------|-----|
| Aoi `netflix_standard_burgerparity_panel.csv` | Aoi lane — leave alone |
| iPhone CSVs in `numeraire_hist_2026-10-25/` | Aoi durables — **leave alone** |
| prasertk / danwaters gist (USD-only) | No FX lane |
| Netflix account / login walls | Not scraped |

## Files

- `adjacent_netflix_subscription_levels_vertical.csv` (+ `.gz`)
- `build_netflix_subscription_levels.py`
- `_build_stats.json` / `_crosscheck_burgerparity.json`
- `raw/SOURCE.md`, `raw/fromabroad_2020-03-10_lcu_curated.csv`, `raw/apoorvgupta25_Netflix_Prices_Dec2021.csv`
- `adjacent_netflix_subscription_levels_missing.md`
