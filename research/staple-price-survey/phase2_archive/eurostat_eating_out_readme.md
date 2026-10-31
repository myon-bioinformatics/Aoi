# Eurostat eating-out / restaurants panel (Aoi origin batch)

Date: **2026-10-24 Asia/Tokyo**.  
File: `eurostat_eating_out_panel.csv`  
Raw (shared with engel_global_ref): `raw/engel_global_ref/eurostat_nama_co3_pc_tot_food_housing_rest.csv`

## What this is

Annual **COICOP 1999 CP11 — Restaurants and hotels** as **% of household final consumption expenditure (HFCE)**, Eurostat `NAMA_10_CO3_P3`, unit `PC_TOT`, 2000–2025 where reported.

**Distinct from** Season2 Eurostat **HBS quintile food shares** (Working–Leser materials). This is national-accounts consumption purpose, not HBS.

## Coverage

- **36** ISO3 countries (+ Eurostat aggregates kept as EA*/EU* codes)
- **952** country×year rows (non-missing only)
- Years: **2000–2025** (country-gappy; many end 2023/2024)

API used for raw pull:  
`https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/NAMA_10_CO3_P3/A.PC_TOT.CP01+CP04+CP11+TOTAL.?format=SDMX-CSV&startPeriod=2000`

## Caveats

- CP11 = restaurants **and hotels** — not Japan 家計調査「外食」 alone.
- Domestic HFCE concept.
- Stub `engel_global_ref_panel_stub.csv` still filters Eurostat rows to Big Mac∩EU (~9 geos); **this file is the fuller Europe panel**.

## Relation to prior stub

Catalog previously noted only 9 Big Mac∩Eurostat countries for CP11. This panel **replaces that as the primary eating-out deliverable** without poorly duplicating Season2 HBS.
