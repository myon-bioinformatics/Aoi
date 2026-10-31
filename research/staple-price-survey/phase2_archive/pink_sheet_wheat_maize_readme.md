# World Bank Pink Sheet — wheat & maize (international staples)

**Retrieved:** 2026-10-24 Asia/Tokyo · extracted from existing CMO workbook (same file as rice / coffee-sugar companions)

## What
Tidy monthly companion for **maize** and **wheat** (US SRW + US HRW) from the World Bank Pink Sheet (CMO Historical Data Monthly).

Rice stays in `rice_international_price_panel.csv`; coffee/sugar in `pink_sheet_coffee_sugar_panel.csv` — not duplicated here.

## Files
- Panel: `pink_sheet_wheat_maize_panel.csv` (**2175** rows)
- Original workbook: `raw/rice_intl/CMO-Historical-Data-Monthly.xlsx` (Updated on October 02, 2026)

## Coverage
| variable | span | n |
|---|---|---|
| `pink_sheet_maize_usd_per_mt` | 1960–2026 | 801 |
| `pink_sheet_wheat_us_srw_usd_per_mt` | 1979–2026 | 573 |
| `pink_sheet_wheat_us_hrw_usd_per_mt` | 1960–2026 | 801 |

- Unit/currency as published (nominal USD / mt). **No FX conversion.** Missing months omitted (not filled).
- Spec notes (Description sheet): Maize = U.S. No.2 yellow, FOB Gulf; Wheat US HRW / SRW as published (** markers for series revisions — see Pink Sheet Description).
