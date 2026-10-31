# Engel companion QC — resume after calorie/Bennett wave

**Date:** 2026-10-25 (Asia/Tokyo)  
**Root:** `/workspace/aoi-phase2/`  
**Scope:** light integrity on 4 calorie/Bennett panels + disk vs gaps addendum; then 3 supply companions landed same turn.

## A. Four panels from prior calorie/Bennett wave

| file | header | data rows | ISO3 | year span | value col all-null? | verdict |
|------|:------:|----------:|-----:|-----------|:-------------------:|---------|
| `fao_fbs_kcal_supply_panel.csv` | OK | 11960 | 176 | 2010–2023 | no | **PASS** |
| `fao_fs_cereal_root_tuber_energy_share_panel.csv` | OK | 3732 | 185 | 2002–2023 | no | **PASS** |
| `fao_fbsh_kcal_supply_panel.csv` | OK | 24702 | 172 | 1961–2013 | no | **PASS** |
| `fao_fs_energy_protein_supply_panel.csv` | OK | 11224 | 185 | 2002–2025 | no | **PASS** |

- iso3: all length-3 uppercase alpha; **0** bad codes on the four.
- year: within 1950–2030; **0** bad years.
- Soft note (not failure): FBS kcal / animal-share / cereal-kg lanes **lack JPN** (documented bulk gap).

### Disk vs gaps addendum
Gaps doc claimed the four filenames + row/ISO3/span above; disk counts **match** (11960 / 3732 / 24702 / 11224). Pre-landing panel glob was **89**; after this turn’s three new panels → **92**.

## B. New panels this turn (post-QC probes)

| file | rows | ISO3 | span | note |
|------|-----:|-----:|------|------|
| `fao_fs_avg_fat_supply_panel.csv` | 3732 | 185 | 2002–2023 | FS **21061**; 3y→end-year |
| `fao_fbs_animal_kcal_share_panel.csv` | 2392 | 176 | 2010–2023 | 100×kcal(2941)/kcal(2901); both required |
| `fao_fbs_cereal_food_supply_kg_panel.csv` | 2392 | 176 | 2010–2023 | FBS el **645** item 2905 |

Light checks on new three: header OK; ≥1 row; iso3/year sane; value nonempty; animal share ∈ (0,100].

## C. Skips
| probe | result |
|-------|--------|
| FBSH animal kcal share | **SKIP** — FBSH panel items 2901/2905/2907 only; no 2941 |
| New WDI food indicator | **SKIP** — no local unused WDI food raw; existing three WDI food panels already land |
| CPI/HES / avoid-list / Season2 | **not touched** |

## Verdict
**PASS** on calorie/Bennett four; three open supply companions landed; no invented failures.

## Method
UTF-8 `csv.reader` / DictReader; no downloads for QC; fat+kg from existing local FAO bulks; animal share derived only.
