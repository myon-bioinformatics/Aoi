# Panel extend coverage pre-2002 — pack-scale pass

Date: 2026-10-24 (Asia/Tokyo)

## Goal
Append older annual years after myon approved 10kg→5kg scale conversion. No FX. No new form bake-off / adoption rewrite.

## Pack rule
See `panel_pack_weight_rule_2026-10-24.md`: `P_yen = price_10kg / 2`, `q_kg=5.0`, note `P_unit=10kg_halved_to_5kg_eq`.

## Coverage 1998–2004

| year | P | E | cab | ruling | status | n_mo_pol | P_yen (5kg-eq) | E | flags |
|------|---|---|-----|--------|--------|----------|----------------|---|-------|
| 1998 | N | Y* | Y | Y | partial | 8 | — | 0.238 | no e-Stat item1002 annual; E=excl_farm break |
| 1999 | Y* | Y* | Y | Y | complete_with_flags | 12 | 2449.6 | 0.237 | P 10kg/2; E excl_farm break |
| 2000 | Y* | Y | Y | Y | complete_with_flags | 11 | 2342.8 | 0.233 | P 10kg/2; gap 2000-06 |
| 2001 | Y* | Y | Y | Y | complete_with_flags | 11 | 2261.9 | 0.232 | P 10kg/2; gap 2001-07; 7 mo A≥100 |
| 2002 | Y | Y | Y | Y | complete | 12 | 2293.3 | 0.233 | unchanged |
| 2003 | Y | Y | Y | Y | complete | 12 | 2365.0 | 0.232 | unchanged |
| 2004 | Y | Y | Y | Y | complete | 12 | 2610.1 | 0.230 | unchanged |

\* = used under documented conversion / definition break.

## Bottlenecks remaining
1. **1998 P**: e-Stat 小売物価 年次 item1002 file set starts **1999** (`statInfId=000000680001`). No 1998 annual in the same series. Monthly 1998 national city tables not confirmed in this pass.
2. **Pre-1998 politics**: NHK bunken monthly starts **1998-04**. 「くらしと政治」面接法 (1976–1998-03) is a method break — do not silent-splice; keep as Partial alternate only.
3. **Pre-1999 E**: only 農林漁家除く long series (a18-1). 1999 row uses it with break flag; 2000+ stay on 含む series.
4. Optional side series: Tokyo-ku 複数原料米 (bukkanavi) — different item/scope; not merged into main `P_yen`.

## Panel
- Backup: `gohantrust_panel_aoki_packscale_backup.csv` (n=24, 2002–2025)
- Now: **connected n=27 (1999–2025)**; main continuous = **5kg n=24 (2002–2025)** (`series` column). See `pack_unit_ratio_overlap.md`.
- 2002–2025 values: preserved

## Sources
- Rice 1999: e-Stat `statInfId=000000680001` → `raw/rice_annual_1999.xls`
- Rice 2000–01: existing `raw/rice_annual_2000.xls`, `2001.xls`
- E 1998–99: https://www.stat.go.jp/data/kakei/longtime/zuhyou/a18-1.xls (Food/CE)
- E 2000+: existing `engel_annual_extended.csv` (二人以上・含む)
- NHK: `nhk_political_monthly_1998_2004.csv`
