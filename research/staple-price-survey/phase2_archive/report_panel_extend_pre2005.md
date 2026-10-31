# Panel extend pre-2005 — GohanTrust Aoki

Date: 2026-10-24 (Asia/Tokyo)

## Goal
Extend `gohantrust_panel_aoki.csv` further back with real annual data under identical definitions. No imputation.

## Result
- **Complete years added:** 2002, 2003, 2004
- **Partial (not added):** 1998–2001 (see coverage memo)
- **Panel n:** 24 (2002–2025)
- **2005–2025:** unchanged

## Definitions
Unchanged from `report_panel_extend_pre2015.md`.

## New rows

| year | P | cabinet_ψ | ruling | A | E | K | K_alt | n_mo |
|------|---|-----------|--------|---|---|---|-------|------|
| 2002 | 2293.3 | 53.75 | 27.48 | 81.23 | 0.233 | 104.8747 | 16.5740 | 12 |
| 2003 | 2365.0 | 54.58 | 30.33 | 84.91 | 0.232 | 135.1089 | 17.7148 | 12 |
| 2004 | 2610.1 | 49.08 | 31.25 | 80.33 | 0.230 | 115.3865 | 18.9659 | 12 |

## Spot-checks
- Re-parse 2005 item1002 → P=2224.2 (panel match).
- NHK bunken 2005 cabinet/LDP parse matches `nhk_political_monthly_2005_2014.csv` exactly.
- 2005 panel row byte-equal on all columns after append.

## Why not 2000–2001
Item 1002 unit was **10Kg** (not 5kg pouch). Politics + E are available; status=Partial. No silent conversion.

## Why not 1998–1999
P and E missing under same definitions. NHK bunken monthly exists from 1998-04 (Partial politics only).

## Notes
- 2004-07 NHK 名簿→RDD method change (documented; values used as published).
- YoY / rolling / adoption **not** re-run (out of scope this pass).
- Full scout detail: `panel_extend_coverage_pre2005.md`


---

**Superseded for 1999–2001:** see `report_panel_extend_pack_scale_2026-10-24.md` (pack-scale append; panel n=27).
