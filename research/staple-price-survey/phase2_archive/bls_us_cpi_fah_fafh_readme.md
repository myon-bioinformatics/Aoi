# BLS USA CPI-U Food at home / Food away from home

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
U.S. city-average **CPI-U index levels** (not seasonally adjusted) for Food, Food at home (FAH), Food away from home (FAFH), and All items — plus two **documented derived ratios** of indexes (FAH/Food, FAFH/Food).

**Distinct from** `usda_fes_usa_food_expenditure_panel.csv` (expenditure shares / sales) and `bls_us_staple_retail_panel.csv` (absolute average prices for rice/bread/flour/milk).

## Files
- Panel: `bls_us_cpi_fah_fafh_panel.csv` (~4,296 rows)
- Raw API JSON decade chunks: `raw/bls_cpi_fah_fafh/api_YYYY_YYYY.json`
- API: https://api.bls.gov/publicAPI/v1/timeseries/data/
- Landing: https://www.bls.gov/cpi/

## Series
| series_id | series | unit | span |
|---|---|---|---|
| CUUR0000SAF11 | cpi_u_food_at_home_nsa | index 1982-84=100 | 1967-01 – 2026-09 |
| CUUR0000SEFV | cpi_u_food_away_from_home_nsa | index 1982-84=100 | 1967-01 – 2026-09 |
| CUUR0000SAF1 | cpi_u_food_nsa | index 1982-84=100 | 1967-01 – 2026-09 |
| CUUR0000SA0 | cpi_u_all_items_nsa | index 1982-84=100 | 1967-01 – 2026-09 |
| DERIVED_FAH_OVER_FOOD | ratio_fah_to_food_index | ratio of indexes | same overlap |
| DERIVED_FAFH_OVER_FOOD | ratio_fafh_to_food_index | ratio of indexes | same overlap |

## Notes
- `download.bls.gov` flat files returned **403** on this box; used Public API v1 decade chunks instead.
- Derived ratios are **not** expenditure shares — use USDA FES for FAH/FAFH % of DPI / food sales.
- Missing months omitted. No FX. No seasonal adjustment.
