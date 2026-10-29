# adjacent_apple_tv_plus_levels

Retrieved: 2026-10-26 Asia/Tokyo

## Hard rules (mirror Netflix adjacent pack)

- Absolute subscription list prices in **local currency as published**.
- Source `price_usd` / USD-only mirrors are **not** loaded into `value` (may appear in `note` as `source_price_usd=`).
- No invented FX. `estimated_value` empty.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value`.

## What

| Field | Value |
|-------|-------|
| Variable | `apple_tv_plus:monthly` |
| Plan | Apple TV+ Monthly |
| Vertical LCU rows | **378** |
| ISO3 | **118** |
| Distinct dates | **4** (2026-01-13, 2026-03-13, 2026-06-06, 2026-10-26) |
| Hist companion | `raw/apple_tv_plus_levels.csv` |

## Sources (easy free)

- Subscription Land country tables + Wayback snapshots (local + exchangedPrice; FX provider unnamed)
- PriceByCountry Oct-2026 panels (USD via ExchangeRate-API 2026-10-17; LCU when `local_display` ISO4217-prefixed)

## Netflix pack

Do **not** rebuild. Point to `adjacent_netflix_subscription_levels` (Aoi #118 tip `17e5c1e`).

## Files

- `adjacent_apple_tv_plus_levels_vertical.csv` (+ `.gz`)
- `adjacent_apple_tv_plus_levels_readme.md` / `adjacent_apple_tv_plus_levels_missing.md`
- `raw/apple_tv_plus_levels.csv`

## Observation contract

See [subscription_contract.md](../subscription_contract.md). `source` is a required series dimension; the observation key is `(country, date, variable, source)`. Cross-source values are separate observations, not independent countries or additive prices. These are reported third-party prices, not verified checkout quotes.
