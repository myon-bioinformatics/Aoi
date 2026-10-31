# Eurostat HICP — transport / motor cars & motor cycles (annual index)

## Panel
- File: `eurostat_hicp_motor_vehicles_panel.csv`
- Rows: 3,421
- ISO3: 38
- Span: 1996–2025 (annual)
- Measures: CP07, CP071, CP0711, CP0712 annual average index (2015=100)

## Source
- Eurostat `prc_hicp_aind` (subset from bulk `raw/broaden_2026-10-25/prc_hicp_aind.tsv.gz` → `raw/durables_xcountry_2026-10-25/prc_hicp_aind_durables.tsv`)
- Retrieved: 2026-10-25 Asia/Tokyo

## Notes
- Annual average HICP index (INX_A_AVG), 2015=100. CP07 transport + CP071 purchase of vehicles + CP0711 motor cars + CP0712 motor cycles — personal transport durables. Indices, not MSRP levels. Aggregates skipped. No FX.
- Price **indices**, not absolute € retail levels. Aggregates skipped. No FX.
- Aoi index/COL durables lane (electronics/appliances/vehicles); not Season2 NSO named-retail SKUs.
