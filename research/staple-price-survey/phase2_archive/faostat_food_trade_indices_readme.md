# FAOSTAT Trade Indices — food import/export value indexes

## Panel
- File: `faostat_food_trade_indices_panel.csv`
- Rows: 197280
- ISO3: 184
- Years: 1961–2024
- Elements: Import Value Index (462), Export Value Index (492); 2014-2016=100
- Items (aggregates): Food Excluding Fish; Crops and livestock products; Cereals and Preparations; Cereals; Fruit and Vegetables; Meat and Meat Preparations; Dairy Products and Eggs; Sugar and Honey; Vegetable Oil and Fat; Other food

## Source
- FAOSTAT domain TI bulk (API fenixservices returned **HTTP 521** this turn — retried once; still 521)
- Bulk URL: `https://bulks-faostat.fao.org/production/Trade_Indices_E_All_Data_(Normalized).zip`
- Raw: `raw/faostat_ti/`
- Country areas only (M49→ISO3 ∩ QI allowlist). No FX.

## Notes
- Distinct from `wdi_food_imports_pct_merchandise_panel` (share of merchandise imports) — this is a **value index** of food trade.
- Distinct from FAO Food CPI packs and FAO QI production indexes.

## Counts by item×element
```
item                          element                             
Cereals                       Export Value Index (2014-2016 = 100)     7929
                              Import Value Index (2014-2016 = 100)    10790
Cereals and Preparations      Export Value Index (2014-2016 = 100)     8891
                              Import Value Index (2014-2016 = 100)    10833
Crops and livestock products  Export Value Index (2014-2016 = 100)    10708
                              Import Value Index (2014-2016 = 100)    10868
Dairy Products and Eggs       Export Value Index (2014-2016 = 100)     7572
                              Import Value Index (2014-2016 = 100)    10700
Food Excluding Fish           Export Value Index (2014-2016 = 100)    10683
                              Import Value Index (2014-2016 = 100)    10868
Fruit and Vegetables          Export Value Index (2014-2016 = 100)     9973
                              Import Value Index (2014-2016 = 100)    10616
Meat and Meat Preparations    Export Value Index (2014-2016 = 100)     7793
                              Import Value Index (2014-2016 = 100)    10364
Other food                    Export Value Index (2014-2016 = 100)    10166
                              Import Value Index (2014-2016 = 100)    10664
Sugar and Honey               Export Value Index (2014-2016 = 100)     8315
                              Import Value Index (2014-2016 = 100)    10760
Vegetable Oil and Fat         Export Value Index (2014-2016 = 100)     8243
                              Import Value Index (2014-2016 = 100)    10544
```

- Retrieved: 2026-10-25 (Asia/Tokyo)
