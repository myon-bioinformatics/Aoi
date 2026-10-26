# adjacent_youtube_premium_subscription_levels — missing / thin coverage

- Distinct dates with LCU rows: **4** (2026-03-13, 2026-04-10, 2026-07-13, 2026-10-26)
- ISO3 with ≥1 LCU row: **57**
- Hist raw rows (all sources, incl. USD-only): 188
- Vertical LCU rows: 149

## Status: multi-date (thin vs Netflix)
- Coverage is months-scale from Subscription Land Wayback, not 2020–2026 dense like Netflix tompec.
- Small Wayback captures (JS shell only) yielded 0 price rows and were skipped.
- SL CURRENT pages (2026-10-26) often embed only `initialPrices` (~24 cheapest) — full-table dates preferred from earlier Wayback; PBC Oct-2026 added where local ISO4217-prefixed.


## Quarantine (2026-10-26)

Five unverified observations are excluded from vertical CSV/gzip and preserved verbatim in `raw/quarantined_vertical.csv`; original raw files are unchanged. MEX: 15.99 MXN on 2026-07-13 and 2026-10-26. DOM: 8.49 DOP on 2026-04-10, 2026-07-13 and 2026-10-26. No replacement price or currency is inferred.

Mexico first-party distributor terms https://www.movistar.com.mx/tyc/youtube-premium (checked 2026-10-26) state MXN 159 monthly, inconsistent with 15.99; this does not establish the historical direct checkout price. YouTube availability help https://support.google.com/youtube/answer/6307365 confirms Dominican Republic availability but does not verify its price/currency. DOM remains unresolved pending dated official billing evidence.
