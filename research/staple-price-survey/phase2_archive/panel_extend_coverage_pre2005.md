# Panel extend coverage pre-2005 — GohanTrust Aoki

> **Update 2026-10-24 (pack-scale):** myon approved 10kg→5kg-eq. Years **1999–2001** appended.
>
> **Series split (t162u):** always report **5kg continuous n=24 (2002–2025)** separately from **connected series n=27 (1999–2025)**. Column `series` on `gohantrust_panel_aoki.csv`. Overlap ratio: `pack_unit_ratio_overlap.md` (R≈2 at 2002 proxy; ÷2 kept; early years = sensitivity). Judgment windows unchanged. See `panel_pack_weight_rule_2026-10-24.md`, `report_panel_extend_pack_scale_2026-10-24.md`.
>
> Text below is the earlier same-definition scout (kept for history).


Date: 2026-10-24 (Asia/Tokyo)

## Goal
Scout real annual data before 2005 under the **same definitions** as `report_panel_extend_pre2015.md`. No imputation. No FX. No form bake-off. No new adoption run.

## Definitions (unchanged; reference)
- **P**: e-Stat item **1002** 国内産うるち米（単一原料米／単一品種）5kg、コシヒカリ以外、全国 = mean of city-monthly means, then annual mean of months.
- **q**: 5.0 kg
- **E**: エンゲル係数 fraction、二人以上の世帯・全国（現行シリーズ「二人以上の世帯（2000年～）」）.
- **Aoki A**: cabinet ψ + ruling first-party support, paired months only (NHK bunken 政治意識月例調査).
- **Ruling first**: LDP for all months in 1998–2004 (Hashimoto / Obuchi / Mori / Koizumi LDP cabinets).
- **K** = P / (q·(100−A)·E); **K_alt** with (200−A).
- Dual NHK surveys: prefer 緊急 on cabinet-change months (none needed in 2002–2004; Koizumi continuous).

## Coverage year × series (1998–2004)

| year | P(1002,5kg) | E | cabinet | ruling | status | ruling_first | n_mo_pol | P_yen | E | P unit |
|------|-------------|---|--------|--------|--------|--------------|----------|-------|---|--------|
| 1998 | N | N | Y | Y | partial | LDP | 8 |  |  | nan |
| 1999 | N | N | Y | Y | partial | LDP | 12 |  |  | nan |
| 2000 | N | Y | Y | Y | partial | LDP | 11 | 4685.6 | 0.233 | 10Kg |
| 2001 | N | Y | Y | Y | partial | LDP | 11 | 4523.8 | 0.23199999999999998 | 10Kg |
| 2002 | Y | Y | Y | Y | complete | LDP | 12 | 2293.3 | 0.233 | １袋･1pouch |
| 2003 | Y | Y | Y | Y | complete | LDP | 12 | 2365.0 | 0.23199999999999998 | 1袋･1pouch |
| 2004 | Y | Y | Y | Y | complete | LDP | 12 | 2610.1 | 0.23 | 1袋･1pouch |

### Status summary
- **Complete (appended to panel):** 2002, 2003, 2004 (n=3)
- **Partial (not appended):** 1998, 1999, 2000, 2001
- **Blocked for same-definition annual panel before 1998:** NHK monthly starts 1998-04; P item1002 annual files from 2000; E 二人以上（2000年～） from 2000.

## Bottlenecks by series

### P (rice item 1002)
- e-Stat 小売物価統計 年次「1001うるち米」～「1081もち」 files exist for **2000–** (statInfIds: 2000=`000000680049` … 2004=`000000680267`; 2005=`000000680322` matches prior extend).
- **Definition break 2000–2001:** unit = **10Kg**; spec = 国内産・精米・単一品種・コシヒカリを除く (no 5kg pouch / 産地・産年同一 wording).
- **Same definition from 2002:** unit = 1袋; spec includes 袋入り（５kg入り）・産地・産年が同一のもの・コシヒカリを除く — continuous with 2005 panel method. Recomputed 2005 P = **2224.2** (exact match to panel).
- Do **not** halve 10kg prices to fake 5kg without an explicit user-approved definition change.
- Pre-2000: item 1002 not in the same e-Stat annual file set used here. Older undifferentiated / different-pack rice exists in 10-year books etc., but that is a different series.

### E (Engel)
- Current panel series `engel_annual_extended.csv` = 二人以上の世帯（2000年～）・全国, already covers **2000–2004**.
- Pre-2000: official long series exist (e.g. 家計調査 long-time / 年報), but **1999年以前は農林漁家世帯を除く** vs **2000年以降は含む** (stat.go.jp research note). That is a definition break vs the panel’s 2000～ series. Keep as Partial/blocked unless the user accepts the break.
- Source used: `raw/engel_eStat_rehost.csv` / https://www.stat.go.jp/data/kakei/longtime/index.htm

### Politics (NHK bunken monthly)
- Earliest bunken page: **1998-04** — https://www.nhk.or.jp/bunken/yoron/political/1998.html (月例開始; history: 1998 電話法・名簿法).
- Pages confirmed present: 1998–2004 (and onward). HTML saved under `raw/bunken_YYYY.html`.
- Gaps on published annual tables (cabinet blank / omitted): 1998-07; 2000-06; 2001-07 (参院選月). 2002–2004: full 12 paired months.
- **2004-07 method change:** 名簿法 → 固定RDD（追跡法）. Same bunken series; possible level shift — noted, not adjusted.
- Pre-1998 alternate (different method — do **not** switch without flagging):
  - NHK「くらしと政治」面接法（1976～1998-03）: https://www.nhk.or.jp/bunken/yoron/nhk/history.html
  - Other media RDD/面接 (朝日・毎日等): method ≠ bunken monthly; not used.

NHK is **not** the binding bottleneck for 2002–2004 (all complete). For 2000–2001, **P unit (10kg)** is the binding blocker under same definitions. For 1998–1999, **P + E** both missing under same definitions.

## Panel update
- Backup: `gohantrust_panel_aoki_pre2005_backup.csv`
- Appended rows: **2002, 2003, 2004** only.
- 2005–2025 rows: **unchanged** (spot-checked).
- Full panel now **n=24** (2002–2025).

### New years K summary

| year | P | A | E | K | K_alt | ruling_first | n_mo | months A≥100 |
|------|---|---|---|---|-------|--------------|------|--------------|
| 2002 | 2293.3 | 81.23 | 0.233 | 104.8747 | 16.5740 | LDP | 12 | 1 (Jan A=112.7) |
| 2003 | 2365.0 | 84.91 | 0.232 | 135.1089 | 17.7148 | LDP | 12 | 0 |
| 2004 | 2610.1 | 80.33 | 0.230 | 115.3865 | 18.9659 | LDP | 12 | 0 |

### Continuity at 2005
- Method: same item 1002, same city-mean→month-mean, same NHK bunken, same E series.
- Levels: P 2004=2610.1 → 2005=2224.2 (harvest/price path; not a unit break). A 80.33 → 85.75. E 0.230 → 0.229.

## Sources
- Rice XLS: e-Stat file-download statInfId 2000=`000000680049`, 2001=`000000680102`, 2002=`000000680157`, 2003=`000000680212`, 2004=`000000680267` (table「1001うるち米」～「1081もち」).
- Engel: e-Stat 家計調査 long-time 二人以上・全国 (`raw/engel_eStat_rehost.csv`).
- NHK: https://www.nhk.or.jp/bunken/yoron/political/YYYY.html (1998–2004).
- NHK history (月例開始 / くらしと政治): https://www.nhk.or.jp/bunken/yoron/nhk/history.html
- Engel pre-2000口径注: https://www.stat.go.jp/training/2kenkyu/pdf/rn/2-rn-005.pdf

## Next fetch steps (if going further back)
1. **Do not** append 2000–2001 until user decides whether to (a) keep 10kg as a separate side series, or (b) accept a documented unit break / conversion rule.
2. Pre-2000 E: pull 家計調査 long-time 農林漁家除く series only if user accepts 1999/2000口径切れ; otherwise stop at 2000.
3. Pre-2000 P: search older 小売物価 10年報 / 指定銘柄米 — expect different item codes; flag before any merge.
4. Pre-1998-04 politics: 「くらしと政治」面接法 only as Partial alternate; never silent-substitute for bunken monthly.
5. No monthly panel / seasonality work in this pass (user prioritized older **years**).

## Files written
- `panel_extend_coverage_pre2005.md` (this file)
- `panel_extend_coverage_pre2005.csv`
- `rice_monthly_pre2005.csv` (2000–2005 with unit/spec)
- `rice_monthly_extended.csv` (now includes 2002–2004)
- `nhk_political_monthly_1998_2004.csv`
- `nhk_ldp_monthly_aoki.csv` (prepended 1998–2004)
- `gohantrust_panel_aoki.csv` (n=24)
- `gohantrust_panel_aoki_pre2005_backup.csv`
- `_summary_pre2005.json`
- `report_panel_extend_pre2005.md`
