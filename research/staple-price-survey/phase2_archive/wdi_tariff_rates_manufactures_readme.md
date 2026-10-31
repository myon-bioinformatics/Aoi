# WDI — Tariff rates (manufactures / all products / primary)

## Panel
- File: `wdi_tariff_rates_manufactures_panel.csv`
- Rows: 30230
- ISO3: 189
- Years: 1988–2022
- Indicators (8):
  - `TM.TAX.MANF.SM.AR.ZS` / `WM.AR` — applied simple/weighted mean, **manufactured** products (%)
  - `TM.TAX.MANF.SM.FN.ZS` — MFN simple mean, manufactured (%)
  - `TM.TAX.MRCH.SM.AR.ZS` / `WM.AR` / `SM.FN.ZS` — all products
  - `TM.TAX.TCOM.SM.AR.ZS` / `WM.AR` — **primary products** (WDI code TCOM)

## Source
- World Bank WDI API (underlying: WITS / UNCTAD TRAINS / WTO IDB)
- Raw: `raw/wdi_tariffs/*.json` (lastupdated 2026-10-08)
- Aggregates excluded

## Caveats
- These are **tariff rates (%)**, not prices or unit values.
- Country×year coverage is naturally sparse (notification lag).
- Manufactured = SITC Rev.3 sections 5–8 excluding division 68.
- No FX.

- Retrieved: 2026-10-25 (Asia/Tokyo)
