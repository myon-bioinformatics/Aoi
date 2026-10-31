# INSEE France food CPI (COICOP) index panel

**File:** `insee_france_food_cpi_panel.csv`  
**ISO3:** FRA  
**Source:** INSEE BDM SDMX dataflow `IPC-2025` (Consumer Price Index, base 2025).  
**API:** `https://bdm.insee.fr/series/sdmx/data/IPC-2025`  
**Retrieved:** 2026-10-24 (Asia/Tokyo)

## Coverage
- Rows: 32,874
- Series: 90 COICOP food (01*) + restaurants (11*) subgroups
- Span: 1996-01-01 – 2026-09-01 (monthly)
- Unit: index, 2025=100 (`BASIND=2025`)
- Filter: `REF_AREA=FE` (France entière), `MENAGES_IPC=ENSEMBLE`, `NATURE=INDICE`

## Notes
- Eurostat HICP in aoi-phase2 is one `hicp_food_cp011_i15` for FRA (1996–2025); this national COICOP tree is richer → landed.
- Season2 `adjacent_euz_proxy_staple_levels` holds FRA **absolute retail** levels; this panel is **CPI indexes only**.
- No FX conversion. Raw: `raw/insee_fr/IPC-2025_M_all.xml` (SDMX StructureSpecificData).

## Columns
iso3, country, series, series_label, coicop, ref_area, forme_vente, idbank, frequency, year, month, date, value, unit, source, source_url, source_file, notes, retrieved
