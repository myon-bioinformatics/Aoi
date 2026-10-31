# FAO GIEWS FPMA — international staple / food benchmark prices

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi companion collect

## What
**International** FPMA Tool V4 price series (export/import benchmarks) — **distinct** from `fpma_domestic_staple_prices_panel.csv` (domestic LCU retail/wholesale).

Curated to **food-related monthly** series only (grains, rice, oils/seeds, dairy, meat, tea, sugar, bananas, fish meal/oil, etc.). Excluded: crude oil, fertilizers (DAP/TSP/urea), jute/sisal.

## Files
- Panel: `fpma_international_staple_prices_panel.csv` (~26,513 rows, 79 series)
- Raw: `raw/fpma_intl/` (`fpma_international_series_meta.json` 90 series catalog; `fpma_intl_selected_meta.json`; `fpma_intl_prices.json`)
- Tool: https://fpma.fao.org/giews/fpmat4/global/

## API
- Meta: `.../FpmaSerieInternational/`
- Prices: `.../FpmaSeriePrice/?uuid__in=<uuid>&periodicity=monthly`

## Coverage
- Span: **1989-01 – 2026-09** (varies by series)
- Currencies: as published (mostly USD; a few EUR) — **no FX fills**
- Units: heterogeneous (`tonne`, `Kg`, `Box (18.14 kg)`, …) — not unit-harmonized

## Notes
- Field stored: `price_value` only. FAO `price_value_dollar` / `price_value_real` not written.
- Not Season2 Big Mac / domestic FPMA vertical. Overlap with Pink Sheet commodities is expected (different source channel); keep both with source tags.
