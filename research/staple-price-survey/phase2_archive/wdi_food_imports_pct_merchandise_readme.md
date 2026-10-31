# WDI — Food imports (% of merchandise imports)

## Panel
- File: `wdi_food_imports_pct_merchandise_panel.csv`
- Rows: 8116
- ISO3: 199
- Years: 1962–2025
- Indicator: TM.VAL.FOOD.ZS.UN

## Source
- World Bank WDI API: `https://api.worldbank.org/v2/country/all/indicator/TM.VAL.FOOD.ZS.UN?format=json&per_page=20000`
- Raw: `raw/wdi_food_imports/TM.VAL.FOOD.ZS.UN.json` (WDI lastupdated 2026-10-08)
- Aggregates (WLD/regions/income groups) excluded
- No FX

## Notes
- Engel-adjacent **trade/import-dependence** companion (share of merchandise imports that are food). Distinct from FAOSTAT Food CPI packs, WDI food production index, WDI cereal yield, and FAO QI.
- FAOSTAT Trade Indices (domain TI) returned HTTP 521 from fenixservices this turn — not used; this WDI series is the open substitute path.

- Retrieved: 2026-10-25 (Asia/Tokyo)
