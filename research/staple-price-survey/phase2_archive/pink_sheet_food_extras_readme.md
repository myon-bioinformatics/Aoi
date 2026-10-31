# World Bank Pink Sheet — food extras (beyond existing panels)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
Additional **food** commodities from the on-disk Pink Sheet monthly workbook, **not** already promoted in:
`pink_sheet_coffee_sugar_panel.csv`, `pink_sheet_wheat_maize_panel.csv`, `pink_sheet_vegetable_oils_panel.csv`, `rice_international_price_panel.csv`.

## Series
Cocoa; Tea (avg 3 auctions, Colombo, Kolkata, Mombasa); Groundnuts; Fish meal; Soybean meal; Barley; Sorghum; Banana (Europe, US); Orange; Beef; Chicken; Lamb; Shrimps (Mexican).

## Files
- Panel: `pink_sheet_food_extras_panel.csv` (~12,392 rows, 17 series)
- Raw copy: `raw/pink_sheet_extras/CMO-Historical-Data-Monthly.xlsx` (same vintage as `raw/rice_intl/`)
- Landing: https://www.worldbank.org/en/research/commodity-markets

## Coverage
**1960-01 – 2026-09** (series start dates differ; missing months omitted — Pink `…` cells dropped).

## Notes
- Nominal USD as published. No FX. No fabricated fills.
- Pink Sheet labels with `**` footnote markers cleaned in `label` only.
