# FAOSTAT QI — Food / crops / cereals production indices

## Panel
- File: `faostat_food_production_index_qi_panel.csv`
- Rows: 53421
- ISO3: 184
- Years: 1961–2024
- Element: Gross Production Index Number (2014-2016 = 100), code 432
- Items: Food (2054), Crops (2041), Livestock (2044), Agriculture (2051), Cereals primary (1717)

## Counts by indicator
                                                          n  iso3    y0    y1
indicator                                                                    
agriculture_gross_production_index_2014_2016_100      10863   184  1961  2024
cereals_primary_gross_production_index_2014_2016_100  10003   172  1961  2024
crops_gross_production_index_2014_2016_100            10863   184  1961  2024
food_gross_production_index_2014_2016_100             10863   184  1961  2024
livestock_gross_production_index_2014_2016_100        10829   183  1961  2024

## Source
- FAOSTAT domain **QI** (Production Indices)
- Bulk: https://bulks-faostat.fao.org/production/Production_Indices_E_All_Data_(Normalized).zip
- Raw: `raw/fao_qi/` (zip also under `raw/fao_ppi/`)

## Notes
- **Volume** production indices — not consumer or producer prices.
- FAOSTAT PP **PPI (5539)** already lives inside `faostat_producer_prices_staples.csv` — not re-extracted.
- Distinct from `wdi_food_production_index_panel` by multi-item QI split (Food/Crops/Livestock/Agriculture/Cereals).
- Regional aggregates dropped via iso3 map. No FX.
- Retrieved: 2026-10-24 (Asia/Tokyo)
