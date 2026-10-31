# Aoi phase-2 Engel/staple companion — collect status

**Date:** 2026-10-25 (Asia/Tokyo)  
**Root:** `/workspace/aoi-phase2/`  
**Rule:** no fabricate · no FX fills · sources documented · Season2 lanes left alone

## Density
- **Tidy panels:** 89 `*_panel.csv` (+ Japan core `engel_food_panel_*` / `engel_annual_*` not matching `*_panel.csv` suffix)
- **Inventory:** `engel_companion_inventory_2026-10-24.md`
- **Gaps QC:** `engel_companion_gaps_2026-10-25.md`

## Major families (filename heuristic counts)
| family | panels |
|--------|-------:|
| Japan RPS / CPI / food-service | 8 |
| FAO Food CPI packs | 5 |
| FAO other (QI/PP/FBS/FBSH/FS/TI/FPI) | 6 |
| WDI / WB | 3 |
| USDA / BLS / ERS / NASS | 6 |
| National food CPI indexes | 23 |
| National HES food shares | 11 |
| HI / domestic staple levels | 5 |
| Pink / IMF / intl benchmarks | 5 |
| Other companions | 17 |

## Japan core
- 二人以上: annual + monthly 用途 (`engel_food_panel_annual` / `_monthly`)
- 単身: annual 用途 yearbook stitch (`engel_food_panel_single_annual`; 2001–2024)
- 総世帯: **not built** — no 用途 continuous longtime; skip documented
- RPS yen levels: rice · numeraire · extras · oil/sugar/coffee · miso/shoyu
- CPI midclass food+外食; food-service activity

## Global / supply / trade companions (selected)
- FAO Food CPI packs (~163 ISO3)
- FAOSTAT QI production; PP staples; **FBS/FBSH kcal levels + cereal energy shares**; **FS 21012** cereal+roots energy share; **FS DES kcal + protein**
- FAOSTAT TI food trade value indexes
- WDI food production · cereal yield · food imports % merchandise
- USDA FES / FPO / PSD / NASS; BLS FAH/FAFH + staple retail
- Pink Sheet / FPMA / IMF; CoAHD; SOFI; shrinkflation

## National CPI + HES (selected)
- Many EU/Nordic/Asia national food **CPI indexes**; national HES food-share panels
- HI absolute retail: Aoi `hi_staple_levels_alt` AUS+CHE only; CAN/DNK/NOR miss (Season2 + avoid)

## Remaining blocked (do not grind)
Avoid-list NSOs · TI API 521 (bulk OK) · ERS FAH-cost 404 · 総世帯 用途 longtime absent · KOSIS SSL · Season2-owned verticals · FBS Japan 2010– gap

## Recommendation
**Stop net-new CPI/HES collect.** Calorie/Bennett/supply lane from local FAO raw is now panelfied. Prefer QC and Season2 handoff over thickening indexes.

## Latest landings (2026-10-25 non-CPI resume)
1. `fao_fbs_kcal_supply_panel.csv` — 11960 / 176 / 2010–2023 (JPN absent)
2. `fao_fs_cereal_root_tuber_energy_share_panel.csv` — 3732 / 185 / 2002–2023
3. `fao_fbsh_kcal_supply_panel.csv` — 24702 / 172 / 1961–2013 (JPN yes; +2907)
4. `fao_fs_energy_protein_supply_panel.csv` — 11224 / 185 / 2002–2025


## Supply companions resume (2026-10-25 Asia/Tokyo, post calorie/Bennett QC)
- **QC:** `engel_companion_qc_resume_2026-10-25.md` — PASS on prior 4 panels; disk matches gaps addendum.
- **Landed:**
  1. `fao_fs_avg_fat_supply_panel.csv` — 3732 / 185 / 2002–2023 (FS 21061)
  2. `fao_fbs_animal_kcal_share_panel.csv` — 2392 / 176 / 2010–2023 (100×2941/2901)
  3. `fao_fbs_cereal_food_supply_kg_panel.csv` — 2392 / 176 / 2010–2023 (el 645 / 2905)
- **SKIP:** FBSH animal share (no 2941); extra WDI food (no unused local raw).
- Panel count: **92**. CPI/HES / avoid-list / Season2 untouched.
