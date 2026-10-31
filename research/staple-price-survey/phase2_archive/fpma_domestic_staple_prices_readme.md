# FAO GIEWS FPMA — domestic staple price companion (curated)

Built: 2026-10-24 (Asia/Tokyo).

## File
- `fpma_domestic_staple_prices_panel.csv` — **~24.9k** monthly rows, **107** series, **33** ISO3, **1991-01–2026-10**.
- Raw meta: `raw/fpma/fpma_domestic_series_meta.json` (full catalog ~4843 domestic series), `fpma_picked_series_meta.json`, `fpma_selected_series.json`.

## What this is / is not
- **Is:** Open FPMA Tool V4 API pull of domestic **local-currency** staple levels (rice / wheat / maize / bread / flour family), one top-scoring series per (country × commodity × price_type), max 6 series/country.
- **Is not:** Season2’s full Big Mac-universe FPMA/WFP vertical; not FAO country CPI; not ICP. **Skipped** Season2 absolute-level lanes: ARE/BHR/KWT/OMN/QAT/TWN/EUZ.
- **Not in FPMA (for these staple keywords):** AUS, CAN, CHE, DNK, NOR, SGP, HKG, NZL, MYS, USA — documented gap (use NSO / BLS instead).

## API (reachable from box)
- Meta: `https://fpma.fao.org/giews/v4/global/price_module/api/v1/FpmaSerieDomestic/`
- Prices: `.../FpmaSeriePrice/?uuid__in=<uuid>&periodicity=monthly` → `{results:[{uuid,datapoints:[...]}]}`
- Stored field: `price_value` in local currency only. FAO `price_value_dollar` / `price_value_real` **not** written (no FX / no deflator fills).

## Scoring for market pick
Prefer national average → capital → average market type; retail over wholesale; longer monthly history.

## Units
Heterogeneous (`Kg`, `5 kg`, `20 kg`, `tonne`, …) — **not** unit-harmonized (project rule). Compare within series only.
