# adjacent_icloud_plus_levels — missing / thin coverage

- Distinct dates with LCU rows: **5** (2024-07-15, 2024-09-11, 2024-11-10, 2026-05-09, 2026-10-26)
- ISO3 with ≥1 LCU row: **88**
- Hist raw rows (all sources, incl. USD-only): 450
- Vertical LCU rows: 285

## Status: multi-date (thin vs Netflix)
- Coverage is months-scale from Subscription Land Wayback (+ Apple Support for iCloud), not 2020–2026 dense like Netflix tompec.
- Small Wayback captures (JS shell only) yielded 0 price rows and were skipped.
- SL CURRENT pages (2026-10-26) often embed only `initialPrices` (~24 cheapest) — full-table dates preferred from earlier Wayback; PBC Oct-2026 added where local ISO4217-prefixed.

## iCloud+ sources
- Apple Support official tables (CURRENT + Wayback p/b markup where parseable).
- Subscription Land 50GB.
- PriceByCountry 50GB (n=18).

