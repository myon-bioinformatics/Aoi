# Eurostat HICP — household furnishings & non-durable goods (annual index)

## Panel
- File: `eurostat_hicp_household_furnishings_panel.csv`
- Rows: 2,997
- ISO3: 37
- Span: 1996–2025 (annual)
- Measures: CP05, CP056, CP0561 annual average index (2015=100)

## Source
- Eurostat `prc_hicp_aind` (extracted from existing bulk `raw/broaden_2026-10-25/prc_hicp_aind.tsv.gz`)
- Retrieved: 2026-10-25 Asia/Tokyo

## Notes
- Price **indices**, not absolute € retail levels. CP0561 ≈ non-durable household goods (cleaning products etc.) — useful synthetic-country household ref without NSO named-retail digs.
- Complements `eurostat_hicp_clothing_housing_panel` (CP03/031/04/041). Aggregates skipped. No FX.
- Aoi index/COL lane; Season2 owns NSO named-retail household SKUs.
