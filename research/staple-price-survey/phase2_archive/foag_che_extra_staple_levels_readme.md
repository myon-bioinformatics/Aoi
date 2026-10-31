# FOAG Switzerland — extra staple retail levels (beyond bread/flour)

## Panel
- File: `foag_che_extra_staple_levels_panel.csv`
- Also appended into `hi_staple_levels_alt_panel.csv` (CHE extension)
- Rows: 2233
- ISO3: CHE
- Items: milk, eggs, potato, sunflower_oil, butter
- Span: 2000-01 … 2026-09
- Currency: CHF (no FX)

## Selection (one series per item)
| item | series | unit | n | span |
|------|--------|------|--:|------|
| milk | Whole milk UHT (Vollmilch UHT) | CHF per Litres | 570 | 2000-01–2026-09 |
| eggs | Raw eggs, CH, all production systems, weighted average | CHF per piece | 81 | 2020-01–2026-09 |
| potato | Waxy potatoes green line (Festkochend: Linie grün) | CHF per kg | 992 | 2006-02–2026-09 |
| sunflower_oil | Sunflower oil, non-organic, CH | CHF per Litres | 20 | 2020-01–2026-04 |
| butter | Premium butter (Vorzugsbutter) | CHF per kg | 570 | 2000-01–2026-09 |

## Source
- FOAG Lindas cubes (consumer / consumption prices):
  - MilkDairyProducts/Consumption_Price_Month
  - Eggs/Consumption_Price_Month
  - FruitsVegetablesPotatoes/Consumption_Price_Month
  - Oilseeds/Consumption_Price_Month
- SPARQL via https://lindas.admin.ch/query
- Raw: `raw/hi_staple_levels_alt/foag_*_month_raw.csv`, `foag_che_extra_staples_raw.csv`

## Notes
- Eggs cube prices are published in **Centime** (Rappen); panel stores **CHF per piece** (= centimes/100). Milk/potato/oil/butter cubes are native CHF.
- Distinct from prior CHE bread + wheat_flour in `hi_staple_levels_alt`.
- Distinct from `swiss_bfs_food_cpi_panel` (indexes) and BFS HABE food **shares**.
- Full FOAG cubes hold many SKUs; this companion keeps five staple series only.
- Retrieved: 2026-10-24 (Asia/Tokyo)
