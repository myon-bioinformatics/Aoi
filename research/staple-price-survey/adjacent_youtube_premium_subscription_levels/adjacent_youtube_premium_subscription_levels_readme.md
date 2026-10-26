# adjacent_youtube_premium_subscription_levels

Retrieved: 2026-10-26 Asia/Tokyo

## Hard rules (mirror Netflix adjacent pack)

- Absolute subscription list prices in **local currency as published**.
- Source `price_usd` / USD-only mirrors are **not** loaded into `value` (may appear in `note` as `source_price_usd=`).
- No invented FX. `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.

## What

| Field | Value |
|-------|-------|
| Variable | `youtube_premium:individual` |
| Plan | YouTube Premium Individual |
| Vertical LCU rows | **154** |
| ISO3 | **58** |
| Distinct dates | **4** (2026-03-13, 2026-04-10, 2026-07-13, 2026-10-26) |
| Hist companion | `raw/youtube_premium_levels.csv` |

## Sources (easy free)

- Subscription Land country tables + Wayback snapshots (local + exchangedPrice; FX provider unnamed)
- PriceByCountry Oct-2026 panels (USD via ExchangeRate-API 2026-10-17; LCU when `local_display` ISO4217-prefixed)

## Netflix pack

Do **not** rebuild. Point to `adjacent_netflix_subscription_levels` (Aoi #118 tip `17e5c1e`).

## Files

- `adjacent_youtube_premium_subscription_levels_vertical.csv` (+ `.gz`)
- `adjacent_youtube_premium_subscription_levels_readme.md` / `adjacent_youtube_premium_subscription_levels_missing.md`
- `raw/youtube_premium_levels.csv`
