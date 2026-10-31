# World Bank WDI — Cereal yield (kg per hectare)

## Panel
- File: `wdi_cereal_yield_panel.csv`
- Rows: 10632
- ISO3: 184 countries (region/income aggregates excluded)
- Span: 1961–2024 (annual)
- Indicator: AG.YLD.CREL.KG — Cereal yield (kg per hectare)

## Source
- World Bank World Development Indicators API
- https://data.worldbank.org/indicator/AG.YLD.CREL.KG
- Raw: `raw/wdi_cereal_yield/AG.YLD.CREL.KG.json`
- WDI lastupdated: 2026-10-08
- Retrieved: 2026-10-25 (Asia/Tokyo)

## Distinct from
- `wdi_food_production_index_panel.csv` (AG.PRD.FOOD.XD volume index)
- `faostat_food_production_index_qi_panel.csv` (QI gross production indexes)
- FAOSTAT FBS/FBSH cereal energy shares (dietary energy, not yield)
- USDA PSD grains (production/stocks levels)

## Notes
- Engel-adjacent supply/productivity companion — cereal land productivity, not prices or expenditure shares.
- No FX. Null observations dropped. Aggregates excluded.
