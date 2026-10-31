# USDA ERS Food Expenditure Series (USA) — FAH / FAFH

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin batch 2

## What
United States **Food Expenditure Series** shares and monthly sales — **distinct** from Season2/USDA-ERS **international** at-home food share of consumer expenditure (Euromonitor-based country panel).

Variable names are prefixed `usa_fes_*` / `usa_fes_archive_*` so they never collide with `engel_food_athome_share_pct`.

## Files
- Panel: `usda_fes_usa_food_expenditure_panel.csv`
- Raw: `raw/usda_fes/`
- Landing: https://www.ers.usda.gov/data-products/food-expenditure-series

## Coverage
| Block | Variables (examples) | Span |
|---|---|---|
| Current normalized (annual) | `usa_fes_fah_share_of_dpi_hh_pct`, `usa_fes_fafh_share_of_dpi_hh_pct`, `usa_fes_total_food_share_of_dpi_hh_pct`, FAH/FAFH shares of food (hh + all purchasers) | **1997–2025** (file years through latest ERS release) |
| Current monthly sales | `usa_fes_fah_sales_nominal_mil_usd`, `usa_fes_fafh_*`, `usa_fes_fah_share_of_monthly_food_sales_pct` | **~1997 – 2026-08** |
| Archived normalized | `usa_fes_archive_*_share_of_dpi_hh_pct` (FAH/FAFH/total) | **1929–2014** (previous methodology — **do not splice** to current without a break note) |

## Notes
- Current constant-dollar columns in raw use 2025=100 (June 2026 revision); share/%DPI series used in panel are unitless percents.
- Monthly sales exclude furnished/donated/home-produced (ERS documentation).
- No FX.
