# Defra UK Agricultural Price Indices (farmgate)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
United Kingdom **Agricultural Price Indices** (API) — monthly indexes for farm output (crops, livestock, milk, eggs, etc.) and selected food-related inputs. Farmgate / producer side — **not** retail CPI.

## Files
- Panel: `defra_uk_agri_price_index_panel.csv` (~9,472 rows, 64 categories)
- Raw: `raw/defra/API_20260924.csv`
- Landing: https://www.gov.uk/government/statistics/agricultural-price-indices

## Coverage
**2014-01 – 2026-07** as published in the Sept 2026 vintage CSV.

## Notes
- Includes all `output` categories plus food-keyword `input` categories (e.g. animal feedingstuffs). Energy/fertilizer-only inputs may still appear if labeled under output aggregates — filter via `api_category` as needed.
- Index base per Defra release notes in the statistical publication. No FX.
