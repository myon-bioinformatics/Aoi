# Report — panel extend with pack-scale (10kg→5kg-eq)

Date: 2026-10-24 (Asia/Tokyo)

## Decision applied
myon: 5 kg bag weight is a placeholder scale; 10 kg history OK via coefficient.  
Locked rule: `panel_pack_weight_rule_2026-10-24.md` — `P_yen = price_10kg / 2`, `q_kg=5.0`.

## Years added to `gohantrust_panel_aoki.csv`

| year | P_yen (5kg-eq) | raw 10kg | A | E | K | K_alt | n_mo_pol | notes |
|------|----------------|----------|---|---|---|-------|----------|-------|
| 1999 | 2449.6 | 4899.2 | 70.38 | 0.237* | 69.7898 | 15.9479 | 12 | E=農林漁家除く break |
| 2000 | 2342.8 | 4685.6 | 56.95 | 0.233 | 46.7128 | 14.0579 | 11 | gap 2000-06 |
| 2001 | 2261.9 | 4523.8 | 83.20 | 0.232 | 116.0663 | 16.6945 | 11 | gap 2001-07; 7 mo A≥100 |

\* E for 1999 from a18-1 Food/CE (農林漁家除く). Sensitivity: same Food/CE on 2000 excl-farm also rounds to 23.3%, matching the panel’s 含む series for 2000 — level break at 1999/2000 is small in this window but still flagged.

## Panel state
- **Connected file n = 27**, years **1999–2025** (not homogeneous — see Amendment / split: **5kg continuous n=24** for 2002–2025)
- Backup before this pass: `gohantrust_panel_aoki_packscale_backup.csv`
- **2002–2025 rows unchanged** (byte-equal on all columns)

## Spot-checks
1. Re-parse e-Stat 2000 item1002 → annual 10kg mean **4685.64** matches `rice_monthly_pre2005.csv` (existing).
2. Continuity P 5kg-eq: 1999 **2449.6** → 2000 **2342.8** (−4.4%) → 2001 **2261.9** (−3.5%) → 2002 pouch **2293.3** (+1.4%). No unit cliff after /2.
3. 2002 panel row unchanged vs pre-append backup.
4. A≥100: 1999=0, 2000=0, 2001=**7** monthly (Koizumi surge); annual A=83.20 < 100 so primary K defined.

## Not added
- **1998**: NHK (n=8 from Apr) + E excl_farm available; **P missing** (no item1002 annual on e-Stat for 1998). Status=partial.
- Pre-1998: politics method break (くらしと政治); no silent splice.

## Optional series (not switched)
Tokyo-ku うるち米(複数原料米) long retail series (bukkanavi / older 小売物価) — different item and geography. Documented as option only; main panel remains e-Stat item **1002** national city mean.

## Out of scope this pass
- No YoY / rolling / adoption re-run (per brief).
- No monthly seasonality work.

## Files
- `panel_pack_weight_rule_2026-10-24.md`
- `panel_extend_coverage_pre2002.md` / `.csv` (and refreshed `panel_extend_coverage_pre2005.csv`)
- `gohantrust_panel_aoki.csv` (connected n=27; `series` tags; continuous view n=24)
- `gohantrust_panel_aoki_packscale_backup.csv`
- `rice_monthly_pre2005.csv` (1999 prepended, raw 10kg)
- `engel_annual_extended.csv` (1998–1999 excl_farm rows)
- `engel_annual_excl_farm_computed.csv`
- `raw/rice_annual_1999.xls` (+ `.xlsx`)
- `raw/engel_excl_farm_a18-1.xls` (+ `.xlsx`)
- `_summary_pack_scale.json`
- this report

---

## Amendment 2026-10-24 — four points (t162u / Claude)

### Panel state (split n — do not lead with bare n=27)

| series | years | n | role |
|--------|-------|---|------|
| **5kg continuous** (`series=5kg_continuous`) | 2002–2025 | **24** | Main continuous panel; judgment reference |
| **Connected pack-scale** (full file; early `connected_packscale`) | 1999–2025 | **27** | Includes 10kg÷2 years; sensitivity only |

Column `series` added to `gohantrust_panel_aoki.csv` (rows kept). Views: `gohantrust_panel_aoki_5kg_continuous.csv`, `gohantrust_panel_aoki_connected.csv`. Backup: `gohantrust_panel_aoki_pre_series_tag_backup.csv`.

Breaks on 1999–2001 (flagged, not hidden):
- **P:** e-Stat item1002 unit 10Kg → `P_yen = raw/2` (`P_unit=10kg_halved_to_5kg_eq`)
- **E 1999:** 農林漁家除く (vs 2000+ 含む)
- **A:** NHK bunken 政治意識月例（`source_notes` に `NHK=bunken`）

### Overlap ratio (priority #1)

Full write-up: **`pack_unit_ratio_overlap.md`**.

- item 1002: **no** same-year 10kg+5kg overlap (銘柄改正 2002-01).
- Proxy R (items 1003/1005, footnote a)=10kg cities vs 5kg cities):
  - 2002 R ≈ **2.01–2.03** (sibling 1003/1005 only) → ÷2 kept as **convention**; equal ¥/kg **not** confirmed (see t163u amendment)
  - annual mean R ≈ **1.96**; monthly median ≈ **1.99**
- Recommendation: keep ÷2 as documented conversion for connected rows; **sideline 1999–2001 from main continuous judgment panel** (separate `series` tag). Continuity % at 2001→2002 (+1.4%) still mixes true price change with any residual unit-splice error — do not read as pure price change.

statInfIds used: 1999=`000000680001`, 2000=`000000680049`, 2001=`000000680102`, 2002=`000000680157`, 2003=`000000680212`, 2004=`000000680267`.

### K (1999–2001) — numbers only

| year | K | K_alt | note |
|------|---|-------|------|
| 1999 | 69.79 | 15.95 | |
| 2000 | 46.71 | 14.06 | |
| 2001 | 116.07 | 16.69 | A=83.2 → (100−A)=16.8 |

Primary K ~47–116; K_alt ~14–17 stable. Same primary-shell instability seen on earlier extend.

### Judgment lock

- Windows unchanged: **2005 / 2010 / 2015+** (pre-declared).
- `claude_adoption_judgment_2026-10-24.md` conclusions **not rewritten**.
- No adoption re-run in this amendment. 1999–2001 use = sensitivity separate row only, if ever run under pre-declared rules.

### Files added/updated this amendment
- `pack_unit_ratio_overlap.md` + `pack_unit_ratio_overlap.csv` + `_annual.csv` + `_footnote_cities.csv` + `_outliers.csv`
- `panel_pack_weight_rule_2026-10-24.md` (amendment section)
- `gohantrust_panel_aoki.csv` (`series` column)
- this report (amendment section)

---

## Amendment 2026-10-24 — pack ratio wording (t163u / Claude)

**No judgment rewrite. No R-grid run. Windows 2005 / 2010 / 2015+ unchanged.**

### Conclusion wording
**÷2 は接続の約束事として残してよいが、等単価が確認できたとは言えない。**  
報告: **÷2 は約束事で、実測は 1.81〜2.03、等単価は未確認。**

### Series (unchanged split)
| series | years | n | role |
|--------|-------|---|------|
| **5kg continuous** | 2002–2025 | **24** | Main / judgment reference |
| Connected early years | 1999–2001 | **3** | Sensitivity only (`connected_packscale`) |

### R facts folded in
1. **Range 1.81〜2.03:** default annual 1.872–2.025 (mean 1.959); with outliers 徳島(2003) / 富山(2004) on 10kg side → R **1.898** / **1.813** (verified from annual + outliers CSV).
2. **2002 R is sibling 1003/1005, not item 1002.** 2002-01 銘柄改正 is a definition fact at the splice; +1.4% mixes price and brand change.
3. Caveats: R declines 2.01→1.93→1.87 over 2002–2004; 10kg side only 2–3 cities (津・松江 etc.); measured years extrapolated to 1999–2001.
4. Implications table (no grid run):

| R | splice-year K scale (vs ÷2) | 2001→2002 YoY |
|---|---|---|
| 1.8 | +11.1% | −8.8% |
| 1.9 | +5.3% | −3.7% |
| 2.0 | 0% | +1.4% |
| 2.05 | −2.4% | +3.9% |

- **YoY:** constant R cancels inside 1999–2001; only the 2002 splice point matters → exclude/flag, no R grid.
- **Level:** K for 1999–2001 shifts by 2/R; mean K ~1–2% (~20–40円) — larger than legacy aoff 2020–21 win margins (6–19円), so level year-wins can flip inside R uncertainty.

### Pre-declaration only
`pack_ratio_sensitivity_prelock_2026-10-24.md` — level R family {1.8, 1.9, 2.0, 2.05} as one family in m; YoY flag/exclude splice; **not executed**.

### Primary write-up
`pack_unit_ratio_overlap.md`  
City-level verification paths: `pack_unit_ratio_footnote_cities.csv`, `pack_unit_ratio_outliers.csv`, `raw/rice_annual_2002.xls`–`2004.xls` (+ `raw/xlsx_probe/`).
