# Numbeo — new compact/mid-size car prices (crowd-sourced snapshot)

## Panel
- File: `numbeo_new_car_crowd_panel.csv`
- Rows: 204
- ISO3: 102
- Span: snapshot 2026-10-25 (not a time series)
- Measures: Volkswagen Golf 1.5 equiv. (itemId 25); Toyota Corolla Sedan 1.6 equiv. (itemId 206); USD

## Source
- Numbeo public `country_price_rankings` HTML
- Raw: `raw/durables_xcountry_2026-10-25/numbeo/item_25.html`, `item_206.html`
- Retrieved: 2026-10-25 Asia/Tokyo

## Notes
- **CROWD-SOURCED** COL absolute prices (USD as displayed). Not official NSO MSRP.
- Historical Numbeo bulk/API is paywalled — this is a current cross-section only.
- Complements continuous Eurostat HICP CP0711 / OECD CPI CP07 motor-vehicle **indices**.
- Aoi branded/COL lane; not Season2 NSO named-retail household SKUs. No FX fills beyond Numbeo's displayed USD.
