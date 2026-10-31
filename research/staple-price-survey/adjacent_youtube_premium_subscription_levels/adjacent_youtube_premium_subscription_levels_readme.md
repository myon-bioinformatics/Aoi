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
| Vertical LCU rows | **149** |
| ISO3 | **57** |
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

## Observation contract

See [subscription_contract.md](../subscription_contract.md). `source` is a required series dimension; the observation key is `(country, date, variable, source)`. Cross-source values are separate observations, not independent countries or additive prices. These are reported third-party prices, not verified checkout quotes.

## Quarantine (2026-10-26)

Five unverified observations are excluded from vertical CSV/gzip and preserved verbatim in `raw/quarantined_vertical.csv`; original raw files are unchanged. MEX: 15.99 MXN on 2026-07-13 and 2026-10-26. DOM: 8.49 DOP on 2026-04-10, 2026-07-13 and 2026-10-26. No replacement price or currency is inferred.

Mexico first-party distributor terms https://www.movistar.com.mx/tyc/youtube-premium (checked 2026-10-26) state MXN 159 monthly, inconsistent with 15.99; this does not establish the historical direct checkout price. YouTube availability help https://support.google.com/youtube/answer/6307365 confirms Dominican Republic availability but does not verify its price/currency. DOM remains unresolved pending dated official billing evidence.
