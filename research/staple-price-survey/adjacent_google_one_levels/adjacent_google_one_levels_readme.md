# adjacent_google_one_levels

Retrieved: 2026-10-26 Asia/Tokyo

## Hard rules (mirror Netflix adjacent pack)

- Absolute subscription list prices in **local currency as published**.
- Source `price_usd` / USD-only mirrors are **not** loaded into `value` (may appear in `note` as `source_price_usd=`).
- No invented FX. `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.

## What

| Field | Value |
|-------|-------|
| Variable | `google_one:100gb` |
| Plan | Google One 100 GB |
| Vertical LCU rows | **165** |
| ISO3 | **130** |
| Distinct dates | **2** (2026-05-09, 2026-10-26) |
| Hist companion | `raw/google_one_levels.csv` |

## Sources (easy free)

- Subscription Land country tables + Wayback snapshots (local + exchangedPrice; FX provider unnamed)
- PriceByCountry Oct-2026 panels (USD via ExchangeRate-API 2026-10-17; LCU when `local_display` ISO4217-prefixed)

## Netflix pack

Do **not** rebuild. Point to `adjacent_netflix_subscription_levels` (Aoi #118 tip `17e5c1e`).

## Files

- `adjacent_google_one_levels_vertical.csv` (+ `.gz`)
- `adjacent_google_one_levels_readme.md` / `adjacent_google_one_levels_missing.md`
- `raw/google_one_levels.csv`
