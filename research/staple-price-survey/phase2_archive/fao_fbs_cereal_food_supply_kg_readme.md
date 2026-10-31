# FAOSTAT FBS — cereal food supply quantity (kg/capita/year)

**Retrieved:** 2026-10-25 Asia/Tokyo · Aoi non-CPI supply companions

## What
Annual **food supply quantity** for **Cereals – Excluding Beer** from FAOSTAT domain **FBS** (2010–):

| variable | item | element | unit |
|---|---:|---:|---|
| `fbs_cereal_food_supply_kg_cap_yr` | 2905 | **645** Food supply quantity (kg/capita/yr) | kg/capita/year |

Structural companion beside kcal levels / cereal energy share (not a price series).

## Files
- Panel: `fao_fbs_cereal_food_supply_kg_panel.csv` (**2,392** rows; **176** ISO3; **2010–2023**)
- Raw: `raw/faostat_fbs/FoodBalanceSheets_E_All_Data_Normalized.zip`

## Notes
- **Japan absent** from this FBS 2010– bulk (same limitation as FBS kcal panel).
- Distinct from `fao_fbs_kcal_supply_panel.csv` (el **664** kcal) and `fao_fbs_cereal_energy_share_panel.csv` (2905/2901 %).
- **CHN**=mainland (aggregate *China* dropped). No FX. No fill.
