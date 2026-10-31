# INE Spain food CPI (ECOICOP ver.2) index panel

**File:** `ine_spain_food_cpi_panel.csv`  
**ISO3:** ESP  
**Source:** INE (Instituto Nacional de Estadística) IPC — ECOICOP ver.2 national indices.  
**Tables:** 79181 groups, 79183 subgroups, 79184 subclasses (CSV via jaxiT3 / Tempus3).  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: **11,268**
- Series: **68** (food 01* + restaurants/hotels 11*; Índice only)
- Levels: {'subclass': np.int64(9486), 'subgroup': np.int64(1188), 'group': np.int64(594)}
- Span: **2002-01-01 – 2026-09-01** (monthly)
- Unit: index, **2025=100** (ECOICOP ver.2 rebase; ~100 in 2025)

## Why landed
Eurostat HICP in aoi-phase2 is one `hicp_food_cp011_i15` for ESP (~360 rows). National ECOICOP ver.2 tree (groups→subclasses) is richer.

## Notes
- Missing Índice cells (`.` / blank in source for late-introduced subclasses) dropped — no fabricate.
- Season2 `adjacent_euz_proxy_staple_levels` holds ESP **absolute retail** levels; this panel is **CPI indexes only**.
- Variation rates (mensual/anual/YTD) dropped — index levels only.
- Older ECOICOP class tables (50903/50904, through 2025M12) kept in `raw/ine_es/` but not spliced into this 2025-base panel.
- No FX. Raw: `raw/ine_es/79181.csv`, `79183.csv`, `79184.csv` (+ Tempus3 JSON `79183_json.json`).

## Columns
iso3, country, series, series_label, coicop, level, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
