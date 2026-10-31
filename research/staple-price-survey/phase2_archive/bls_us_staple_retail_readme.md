# BLS USA staple retail average prices (promoted)

Built: 2026-10-24 (Asia/Tokyo).

## File
- `bls_us_staple_retail_panel.csv` — tidy top-level promote of USA city-average **absolute** retail prices for rice / bread / flour / milk.
- Full numeraire set (also coffee + sugar) remains at `raw/numeraire/bls_average_price_panel.csv`.

## Series (U.S. city average, NSA)
| series_id | series | unit | span (obs) |
|---|---|---|---|
| APU0000701312 | Rice, white, long grain, uncooked | USD per lb | 1980–2026 (535) |
| APU0000702111 | Bread, white, pan | USD per lb | 1980–2026 (560) |
| APU0000701111 | Flour, white, all purpose | USD per lb | 1980–2026 (559) **added this turn** |
| APU0000709112 | Milk, fresh, whole, fortified | USD per gal | 1995–2026 (374) |

## Source / method
- BLS Public API v2 `timeseries/data` (POST), decade chunks (bulk `download.bls.gov` historically 403).
- Factsheet: https://www.bls.gov/cpi/factsheets/average-prices.htm
- Missing months omitted (not filled). No FX. No seasonal adjustment.

## Notes
- Average prices are levels, not CPI indexes — BLS warns they are better for level comparisons than percent change over long spans.
- Flour was missing from the earlier raw panel; re-fetched all four staples + coffee/sugar into raw, then promoted staples only.
