# FAOSTAT Food Balances (2010–) — food supply kcal/cap/day levels

**Retrieved:** 2026-10-25 Asia/Tokyo · Aoi non-CPI resume

## What
Annual **kcal/capita/day** levels from FAOSTAT domain **FBS** (Food Balances 2010–), element **664** Food supply (kcal/capita/day):

| variable | item | label |
|---|---:|---|
| `fbs_kcal_cap_day_total` | 2901 | Grand Total |
| `fbs_kcal_cap_day_cereals_excl_beer` | 2905 | Cereals – Excluding Beer |
| `fbs_kcal_cap_day_starchy_roots` | 2907 | Starchy Roots |
| `fbs_kcal_cap_day_vegetal_products` | 2903 | Vegetal Products |
| `fbs_kcal_cap_day_animal_products` | 2941 | Animal Products |

## Files
- Panel: `fao_fbs_kcal_supply_panel.csv` (**11,960** rows; **176** ISO3; years **2010–2023**)
- Raw: `raw/engel_global_ref/FoodBalanceSheets_E_All_Data_Normalized.zip` (+ `faostat_area_iso3_map.csv`)

## Notes
- **Japan absent** from this FBS 2010– bulk (0 JPN rows) — documented; not invented. Prefer FBSH kcal / FS 21012 / OWID staple-energy for Japan structure.
- Distinct from `fao_fbs_cereal_energy_share_panel.csv` (share + only 2901/2905). This panel is **levels-first** and adds 2907/2903/2941.
- **CHN** = *China, mainland* (aggregate *China* area dropped to avoid ISO3 collision).
- No FX. No interpolation. Regional aggregates / invalid ISO3 dropped.
- Bulk URL: `https://bulks-faostat.fao.org/production/FoodBalanceSheets_E_All_Data_(Normalized).zip`
