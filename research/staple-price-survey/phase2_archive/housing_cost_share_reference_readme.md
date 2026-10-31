# Housing-cost share reference panel (NOT Engel core)

**File:** `housing_cost_share_reference_panel.csv`  
**Role:** **Reference-only** housing / housing+energy expenditure shares for comparison beside Engel/food work. **Not** an Engel form; **not** Japan 住居費.

**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **2,162**
- Series:
  - `eurostat_cp04_housing_utilities_share_hfce_pct` — 952 rows; Eurostat `NAMA_10_CO3_P3` COICOP1999 **CP04** % of HFCE; geos: 41 (nationals + EA/EU aggregates); span **2000–2025**
  - `oecd_ahd_hc1_1_2_housing_energy_share_hfce_pct` — 1,210 rows; OECD Affordable Housing Database **HC1.1.2**; geos: 44; span **1995–2024**

## Why landed
`engel_global_ref_panel_stub.csv` already carried OECD HC1.1.2 for ~21 countries and **truncated** Eurostat CP04 to Big Mac∩EU. `eurostat_eating_out_panel.csv` extracted full CP11 from the same Eurostat raw — this panel is the **CP04 twin** (full Europe) plus OECD housing share for non-EU OECD members. Continuous multi-country housing reference without claiming Season2 food-share lanes.

## Notes
- Eurostat CP04 includes **imputed rentals** and utilities — not cash rent alone.
- OECD HC1.1.2 is housing+water+fuels % HFCE; **rent burden** (HC1.2 % disposable income) not included here (different concept; still in raw `oecd_HC1_2_*.xlsx` if present).
- Eurostat and OECD series kept **separate** (do not splice).
- No FX, no fabricate. Label every use as **reference-not-Engel-core**.
- Raw: shared under `raw/engel_global_ref/` (symlinked from `raw/housing_ref/`).
