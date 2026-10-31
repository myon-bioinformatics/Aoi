# SOFI / FAO food insecurity panel (PoU + FIES)

Date: **2026-10-24 Asia/Tokyo**. Catalog tag: **Aoi origin batch SOFI/EastEU**.

| Field | Detail |
|---|---|
| Panel | `sofi_food_insecurity_panel.csv` |
| Raw | `raw/sofi_fs/Food_Security_Data_E_All_Data_(Normalized).zip` (+ extracted CSV) |
| Source | FAOSTAT domain **FS** — Suite of Food Security Indicators (July 2026 SOFI-aligned release) |
| Bulk URL | https://bulks-faostat.fao.org/production/Food_Security_Data_E_All_Data_(Normalized).zip |
| Landing | https://www.fao.org/faostat/en/#data/FS |
| Distinct from | `coa_healthy_diet_panel.csv` (CAHD affordability / diet cost) — this file is **prevalence** (PoU, FIES), not cost |

## What is kept

Core **total-population** series only (no sex / urban–rural / age splits):

| indicator | FAO Item Code | Notes |
|---|---|---|
| `pou_pct_annual` | 210040 | Annual PoU % — **regions/World only** in this bulk (no country annual) |
| `pou_pct_3y_avg` | 210041 | 3-year-average PoU % — **main country continuous panel** |
| `n_undernourished_million_*` | 210010 / 210011 | Counts (million) |
| `fies_mod_sev_pct_annual` | 210090 | Annual FIES moderate+severe % — regions/World only |
| `fies_mod_sev_pct_3y_avg` | 210091 | 3y FIES mod+sev % — main country panel |
| `fies_sev_pct_*` | 210400 / 210401 | Severe FIES % |
| `n_fies_*_million_*` | 210070/071/080/081 | FIES headcounts (million) |

`year` for 3-year averages is the **window end year** (`year_label` keeps `2000-2002` etc.; `year_kind=3y_window_end`).

## Coverage (this pull)

- Rows: **~18.9k** (countries + regional aggregates)
- Country ISO3 mapped: **~184** (after fixing BDI/PLW/SGP/SOM/SSD/SDN missing from the local FAO area map)
- Country years: **2002–2025** (PoU 3y); FIES 3y mostly **2016–2025**
- PoU 3y country: **~166 ISO3**; FIES mod+sev 3y: **~153 ISO3**; FIES sev 3y: **~151 ISO3**
- Censored FAO tokens (`<2.5`, `<0.5`, …): kept as rows with **`value` null**, `value_raw` as published, flag `censored_<…>` — **not** filled with 2.5

## Columns

`iso3, area, area_code, year, year_label, year_kind, indicator, indicator_label, item_code, value, value_raw, unit, flag, is_aggregate, source, source_url, note, retrieval_date`

## Rules / blockers

- **No FX. No fabricated fills** for censored prevalence.
- Country-level **annual** PoU/FIES prevalence is **not in** the FS normalized bulk (only aggregates) — use `*_3y_avg` for country×year work.
- Sex/geography FIES splits exist in raw ItemCodes but were **not** tidied here (can extend).
- Confidence-interval Element rows dropped (Value only).
- Singapore / several fragile states were absent from `faostat_area_iso3_map.csv` and patched by hand (see note).

## Companion

- CoAHD cost/affordability: `coa_healthy_diet_panel.csv`
- Bennett energy share (FS 21012) already in engel global ref / OWID tidies — not duplicated here
