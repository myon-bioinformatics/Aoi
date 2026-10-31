# World Bank WDI — Food production index

## Panel
- File: `wdi_food_production_index_panel.csv`
- Rows: 11,516
- ISO3: 197 countries (region/income aggregates excluded)
- Span: 1961–2024 (annual)
- Indicator: AG.PRD.FOOD.XD — Food production index (2014–2016 = 100)

## Source
- World Bank World Development Indicators API
- https://data.worldbank.org/indicator/AG.PRD.FOOD.XD
- Raw: `raw/wdi_food_production/AG.PRD.FOOD.XD.json`
- WDI lastupdated: 2026-10-08
- Retrieved: 2026-10-24 (Asia/Tokyo)

## Distinct from
- FAOSTAT FBS/FBSH cereal energy shares (dietary energy, not production index)
- FAOSTAT producer prices / PSD grains (commodity stocks/production levels)
- National food CPI packs (prices, not output)

## Notes
- Engel-adjacent supply companion — food output volume index, not expenditure share.
- No FX. Null observations dropped. Aggregates (WLD, regions, income groups) excluded.
