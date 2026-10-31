# Eurostat HICP — household appliances (durables) (annual index)

## Panel
- File: `eurostat_hicp_household_appliances_panel.csv`
- Rows: 1,446
- ISO3: 37
- Span: 1996–2025 (annual)
- Measures: CP053, CP0531 annual average index (2015=100)

## Source
- Eurostat `prc_hicp_aind` (subset from bulk `raw/broaden_2026-10-25/prc_hicp_aind.tsv.gz` → `raw/durables_xcountry_2026-10-25/prc_hicp_aind_durables.tsv`)
- Retrieved: 2026-10-25 Asia/Tokyo

## Notes
- Annual average HICP index (INX_A_AVG), 2015=100. CP053 household appliances + CP0531 major appliances — durable goods price indices for cross-country appliance inflation (not named-retail SKU levels). Complements eurostat_hicp_household_furnishings (CP05 aggregate). Aggregates skipped. No FX.
- Price **indices**, not absolute € retail levels. Aggregates skipped. No FX.
- Aoi index/COL durables lane (electronics/appliances/vehicles); not Season2 NSO named-retail SKUs.
