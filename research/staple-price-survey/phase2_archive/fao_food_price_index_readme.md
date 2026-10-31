# FAO Food Price Index / Cereal Price Index (global)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin batch 2

## What
Monthly **global** FAO Food Price Index and sub-indices (Meat, Dairy, Cereals, Oils, Sugar).  
**Not** country-level FAO consumer CPI (Season2 lane).

## Files
- Panel: `fao_food_price_index_panel.csv` (vertical tidy)
- Raw: `raw/fao_fpi/food_price_indices_data.csv`
- Source: https://www.fao.org/worldfoodsituation/foodpricesindex/
- Raw CSV URL (wfs-library): used at retrieval; FAO FFPI page documents monthly updates

## Coverage
- Geography: WORLD
- Frequency: monthly
- Span: **1990-01 – 2026-09**
- Series: `fao_food_price_index`, `fao_meat_price_index`, `fao_dairy_price_index`, `fao_cereal_price_index`, `fao_oils_price_index`, `fao_sugar_price_index`
- Unit: index **2014–2016 = 100**
- Rows: 2,646

## Rules
No FX. No gap-fill. Distinct from Season2 FAO country CPI food/cereals.
