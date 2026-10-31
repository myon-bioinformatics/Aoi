# WDI — Trade structure (manufactures / high-tech / ores-metals)

## Panel
- File: `wdi_trade_structure_manuf_tech_metals_panel.csv`
- Rows: 18897
- ISO3: 199
- Years: 1962–2025
- Indicators (3):
  - `TX.VAL.TECH.MF.ZS` — High-technology exports (% of manufactured exports)
  - `TM.VAL.MANF.ZS.UN` — Manufactures imports (% of merchandise imports)
  - `TM.VAL.MMTL.ZS.UN` — Ores and metals imports (% of merchandise imports)

## Source
- World Bank WDI API; raw `raw/wdi_tariffs/*.json`
- Aggregates excluded; no FX

## Caveats
- Trade **structure shares**, not tariff rates and not unit prices. Complements tariff-rate panel for tariff/trade context on parts & manufactures.

- Retrieved: 2026-10-25 (Asia/Tokyo)
