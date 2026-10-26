# adjacent_spotify_subscription_levels — missing / thin coverage

- Distinct dates with LCU rows: **3** (2025-11-14, 2026-02-18, 2026-10-26)
- ISO3 with ≥1 LCU row: **157**
- Hist raw rows (all sources, incl. USD-only): 442
- Vertical LCU rows: 350

## Status: multi-date (thin vs Netflix)
- Coverage is months-scale from Subscription Land Wayback, not 2020–2026 dense like Netflix tompec.
- Small Wayback captures (JS shell only) yielded 0 price rows and were skipped.
- SL CURRENT pages (2026-10-26) often embed only `initialPrices` (~24 cheapest) — full-table dates preferred from earlier Wayback; PBC Oct-2026 added where local ISO4217-prefixed.

