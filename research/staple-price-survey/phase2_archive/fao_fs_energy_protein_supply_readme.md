# FAOSTAT FS — dietary energy supply (kcal) + average protein supply

**Retrieved:** 2026-10-25 Asia/Tokyo · Aoi non-CPI resume

## What
Open continuous **supply-level** companions from FAOSTAT Suite of Food Security Indicators (**FS**), useful beside Engel food-share ratios (not CPI; not SOFI prevalence):

| variable | item | unit | coverage |
|---|---:|---|---|
| `fs_dietary_energy_supply_kcal_pou` | 22000 | kcal/cap/day | 3,760 / 157 ISO3 / end-years 2002–2025 |
| `fs_avg_protein_supply_g` | 21013 | g/cap/day | 3,732 / 185 ISO3 / 2002–2023 |
| `fs_avg_animal_protein_supply_g` | 21014 | g/cap/day | 3,732 / 185 ISO3 / 2002–2023 |

## Files
- Panel: `fao_fs_energy_protein_supply_panel.csv` (**11,224** rows; **185** ISO3)
- Raw: `raw/engel_global_ref/Food_Security_Data_E_All_Data_Normalized.zip`

## Year convention
Range labels → **`year` = end-year**; original kept as `year_label`. Frequency `annual_3y_avg_end_year`.

## Notes
- Distinct from `sofi_food_insecurity_panel.csv` (PoU/FIES **prevalence**).
- Distinct from `fao_fbs_kcal_supply_panel.csv` / FBSH kcal (Food Balances element 664).
- Complements `fao_fs_cereal_root_tuber_energy_share_panel.csv` (21012 share %).
- **Japan:** protein items present end-years **2002–2009** only in this bulk; DES kcal (22000) **no JPN** rows here.
- **CHN**=mainland. No FX. No fill.
