# ELSTAT Greece food HICP (COICOP 2018) index panel

**File:** `elstat_greece_food_cpi_panel.csv`  
**ISO3:** GRC  
**Source:** Hellenic Statistical Authority (ELSTAT) — Harmonised Index of Consumer Prices, COICOP 2018, published on **data.gov.gr**.  
**Resource:** `hicp-indices_1996-2025-coicop18.csv`  
**URL:** `https://data.gov.gr/dataset/enarmonismenos-deiktis-timon-katanaloti-endtk` (resource download above)  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **17,974**
- Series: **94** with ≥1 observation (COICOP **01*** + **11***; codes with all-blank history omitted)
- Levels: {'division': 722, 'group': 1444, 'class': 6498, 'subclass': 8113, 'item': 1197}
- Span: **1995-12-01 – 2025-12-01** (monthly)
- Unit: index as published (HICP; comma-decimal in source)

## Why landed
Eurostat HICP pack in aoi-phase2 is one `hicp_food_cp011_i15` for GRC. This ELSTAT file is a full COICOP 2018 tree (deep subclasses) for food and catering/accommodation.

## Notes
- This is **ELSTAT’s HICP release**, not a re-pull of Eurostat SDMX and not the national CPI (ΔΤΚ) workbook from statistics.gr — national CPI Excel links on DKT87 were not bulk-parsed this turn.
- Empty cells (series not yet in basket) dropped — no fabricate.
- Labels left in Greek as in source; `coicop` / `series` are code-based.
- Season2 absolute EUZ-proxy / eating-out shares not duplicated here.
- Raw: `raw/elstat_gr/hicp-indices_1996-2025-coicop18.csv`.
