# Panel pack-weight rule — GohanTrust Aoki

Date: 2026-10-24 (Asia/Tokyo)

## Decision (myon, 2026-10-24)
Bag weight (historically locked at **5 kg**) is a **scale placeholder**.  
10 kg historical retail prices are acceptable via a coefficient. Prefer pulling all available years. If a more standard pack series exists, that is fine too — but do not silently mix units in `P_yen`.

## Locked conversion (main panel)
- Panel column semantics: `P_yen` = price for **`q_kg` kg** of the chosen pack.
- Continuity choice: keep **`q_kg = 5.0`** for all rows (including years whose raw e-Stat unit is 10 kg).
- When e-Stat item **1002** unit is **10Kg**:
  - `P_yen = price_10kg / 2`  (5 kg–equivalent)
  - `q_kg = 5.0` (unchanged)
  - Record in `source_notes`: `P_unit=10kg_halved_to_5kg_eq` (and the raw 10 kg annual mean).
- Do **not** store unscaled 10 kg prices in `P_yen` next to 5 kg pouch years.

## Years using the conversion
| year | raw unit (item 1002) | conversion |
|------|----------------------|------------|
| 1999 | 10Kg | /2 → 5kg-eq |
| 2000 | 10Kg | /2 → 5kg-eq |
| 2001 | 10Kg | /2 → 5kg-eq |
| 2002– | 1袋 (5kg pouch) | none (already 5 kg) |

## Optional long series (not switched)
- Tokyo-ku **うるち米(複数原料米)** / item ~1003 on bukkanavi.jp has a long history (10kg → 5kg pouch). Different item / city scope than panel item **1002** (単一品種・コシヒカリ以外・全国市平均). Kept as a side option only; main panel stays on item 1002.

## Related files
- `gohantrust_panel_aoki.csv`
- `rice_monthly_pre2005.csv` (stores **raw** unit prices; unit column distinguishes 10Kg vs 5kg pouch)
- `report_panel_extend_pack_scale_2026-10-24.md`

---

## Amendment 2026-10-24 — overlap ratio + series split (t162u)

Empirical check: `pack_unit_ratio_overlap.md` (+ CSVs).

### 1. Measured R = P_10kg / P_5kg
- item **1002**: no same-year dual unit (break at 2002-01 per f2taisyo.pdf).
- Proxy: sibling items **1003/1005**, footnote **a)** cities publish raw 10kg while other cities are 5kg pouch.
  - 2002: R_mean ≈ **2.009** (1003), **2.025** (1005) → ÷2 kept as splice **convention** (equal ¥/kg not confirmed; see t163u).
  - 2003–2004: R_mean ≈ **1.87–1.93** (n10=2 only; city confounding possible).
  - Monthly proxy n=48: median R ≈ **1.99**, mean ≈ **1.96**.
- **Conversion rule kept as convention:** `P_yen = price_10kg / 2` for connected rows (not a confirmed equal-unit-price result).
- **But:** do not treat 1999–2001 as the same continuous 5kg series for judgment.

### 2. Always split n in reports
| label | years | n | `series` tag |
|-------|-------|---|--------------|
| **5kg continuous** | 2002–2025 | **24** | `5kg_continuous` |
| **Connected (pack-scale)** | 1999–2025 | **27** | full file; early years `connected_packscale` |

Breaks on connected early years: P=10kg÷2; E 1999=農林漁家除く; A=NHK bunken 政治意識月例（明示）。Never lead with bare “n=27” as homogeneous.

### 3. K instability (numbers only, 1999–2001)
| year | A | (100−A) | K | K_alt |
|------|---|--------|---|-------|
| 1999 | 70.38 | 29.62 | 69.79 | 15.95 |
| 2000 | 56.95 | 43.05 | 46.71 | 14.06 |
| 2001 | 83.20 | 16.80 | 116.07 | 16.69 |

Primary K spans ~47–116; K_alt stays ~14–17. Same (100−A) denominator shrinkage as prior extend when A is high.

### 4. Judgment windows locked
Prior judgments stay on declared windows **2005 / 2010 / 2015+**.  
Do **not** rewrite `claude_adoption_judgment_2026-10-24.md`.  
Any use of 1999–2001 = **sensitivity analysis, separate row**, under pre-declared rules only.

### Related (this amendment)
- `pack_unit_ratio_overlap.md`
- `pack_unit_ratio_overlap.csv` / `_annual.csv` / `_footnote_cities.csv`
- `gohantrust_panel_aoki.csv` (`series` column)
- `gohantrust_panel_aoki_5kg_continuous.csv`

---

## Amendment 2026-10-24 — R range + wording (t163u)

Does **not** change the locked conversion (`P_yen = price_10kg / 2`) or judgment windows.

### Wording (required)
- **÷2 は接続の約束事として残してよいが、等単価が確認できたとは言えない。**
- Report: **÷2 は約束事で、実測は 1.81〜2.03、等単価は未確認。**
- Do **not** write 「÷2 が成立した」 / 「等単価が確認できた」。

### R recorded range
| case | R |
|------|---|
| Default annual (outliers excluded from P5, not in P10) | 1.872–2.025 (mean 1.959) |
| Outliers on 10kg side: 徳島(2003)=**1.898**, 富山(2004)=**1.813** | verified from `pack_unit_ratio_overlap_annual.csv` + `pack_unit_ratio_outliers.csv` |
| **Report span** | **1.81〜2.03** |

### Definition facts
- 2002 R ≈ 2.01–2.03 is from **sibling items 1003/1005** (footnote a), **not** measured on panel item **1002**.
- 2002-01 brand/spec change: splice YoY **+1.4%** mixes price change and brand change.
- Measured years are 2002–2004; applying to 1999–2001 is **extrapolation**. 10kg side = 2–3 cities only.

### Series split (unchanged)
- Main: **5kg continuous n=24 (2002–2025)**
- Sensitivity only: **1999–2001 n=3** (`connected_packscale`)

### Sensitivity pre-declaration only (not run)
See `pack_ratio_sensitivity_prelock_2026-10-24.md`:
- Level: R ∈ {1.8, 1.9, 2.0, 2.05} as **one family** in m.
- YoY: exclude/flag 2002 splice YoY; **no R grid**.
- Windows **2005 / 2010 / 2015+** and adoption judgment unchanged.
