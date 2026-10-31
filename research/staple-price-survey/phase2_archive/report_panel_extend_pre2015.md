# Panel extend pre-2015 — GohanTrust Aoki

Date (Asia/Tokyo): 2026-10-24

## Goal
Extend `gohantrust_panel_aoki.csv` backward with real annual data. No imputation. Definitions unchanged.

## Definitions (unchanged)
- **P**: 国内産うるち米（単一原料米）5kg、コシヒカリ以外、全国 = mean of city monthly means, then annual mean of months. e-Stat item **1002**.
- **q**: 5.0 kg
- **E**: エンゲル係数 fraction、二人以上の世帯・全国. 2015 = 0.250 matches prior panel.
- **Aoki A**: cabinet ψ + ruling first-party support, paired months only.
- **Ruling first**: LDP through 2009-08; DPJ 2009-09–2012-12; LDP from 2013-01 (Abe from 2012-12-26; Dec-2012 survey still Noda → DPJ).
- **K** = P / (q·(100−A)·E); **K_alt** with (200−A).
- Dual NHK surveys: prefer **緊急** on cabinet-change months (2008-09 Asō, 2009-09 Hatoyama).

## Coverage 2005–2014 (year × series)

| year | P(1002) | E | cabinet | ruling | complete | ruling_first | n_mo_pol | P_yen | E |
|------|---------|---|--------|--------|----------|--------------|----------|-------|---|
| 2005 | Y | Y | Y | Y | Y | LDP | 12 | 2224.2 | 0.22899999999999998 |
| 2006 | Y | Y | Y | Y | Y | LDP | 12 | 2138.7 | 0.231 |
| 2007 | Y | Y | Y | Y | Y | LDP | 12 | 2104.0 | 0.23 |
| 2008 | Y | Y | Y | Y | Y | LDP | 12 | 2078.3 | 0.23199999999999998 |
| 2009 | Y | Y | Y | Y | Y | LDP | 12 | 2090.4 | 0.23399999999999999 |
| 2010 | Y | Y | Y | Y | Y | DPJ | 12 | 1996.7 | 0.233 |
| 2011 | Y | Y | Y | Y | Y | DPJ | 11 | 1896.3 | 0.23600000000000002 |
| 2012 | Y | Y | Y | Y | Y | DPJ | 12 | 2082.7 | 0.235 |
| 2013 | Y | Y | Y | Y | Y | LDP | 12 | 2157.5 | 0.23600000000000002 |
| 2014 | Y | Y | Y | Y | Y | LDP | 12 | 2006.5 | 0.24 |

**Complete years newly added:** [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014] (n=10)
**Partial years:** none in 2005–2014.

## Spot-checks
- 2015 P e-Stat method = 1833.1 (panel 1833.1) → exact match.
- 2015 E 全国 = 0.25 (panel 0.25) → exact match.
- 2015–2025 panel rows preserved.

## A ≥ 100 checks (new years)

| year | Aoki_A annual | months A≥100 | n_months |
|------|---------------|--------------|----------|
| 2005 | 85.75 | 3 | 12 |
| 2006 | 89.47 | 1 | 12 |
| 2007 | 76.12 | 0 | 12 |
| 2008 | 67.83 | 0 | 12 |
| 2009 | 69.63 | 3 | 12 |
| 2010 | 69.83 | 1 | 12 |
| 2011 | 52.15 | 0 | 11 |
| 2012 | 44.17 | 0 | 12 |
| 2013 | 100.87 | 7 | 12 |
| 2014 | 89.5 | 0 | 12 |

## K summary for new years

| year | P | A | E | K | K_alt | ruling_first |
|------|---|---|---|---|-------|--------------|
| 2005 | 2224.2 | 85.75 | 0.22899999999999998 | 136.3181 | 17.0025 | LDP |
| 2006 | 2138.7 | 89.47 | 0.231 | 175.8488 | 16.7528 | LDP |
| 2007 | 2104.0 | 76.12 | 0.23 | 76.615 | 14.7689 | LDP |
| 2008 | 2078.3 | 67.83 | 0.23199999999999998 | 55.6928 | 13.5556 | LDP |
| 2009 | 2090.4 | 69.63 | 0.23399999999999999 | 58.83 | 13.7046 | LDP |
| 2010 | 1996.7 | 69.83 | 0.233 | 56.8083 | 13.1667 | DPJ |
| 2011 | 1896.3 | 52.15 | 0.23600000000000002 | 33.5848 | 10.8694 | DPJ |
| 2012 | 2082.7 | 44.17 | 0.235 | 31.7484 | 11.3746 | DPJ |
| 2013 | 2157.5 | 100.87 | 0.23600000000000002 | -2101.5975 | 18.4444 | LDP |
| 2014 | 2006.5 | 89.5 | 0.24 | 159.246 | 15.132 | LDP |

## Sources
- Rice: e-Stat 小売物価統計 年次 item 1002 (statInfIds 2005=000000680322 … 2015=000031406934).
- Engel: e-Stat 家計調査 long-time 二人以上・全国 (`raw/engel_eStat_rehost.csv`).
- NHK: bunken https://www.nhk.or.jp/bunken/yoron/political/YYYY.html (2005–2014).
- moshisen used only to confirm 緊急 preference.

## DPJ vs LDP
- 2005–2008: LDP all months.
- 2009: Jan–Aug LDP; Sep–Dec DPJ (Sep=緊急). Annual `ruling_first` = month-count majority (LDP 8 vs DPJ 4); monthly A still uses correct party.
- 2010–2012: DPJ. 2011-03 omitted (震災).
- 2013–2014: LDP.

## Definition notes
- Item 1002 continuous 2005–2015 — no definition break; no undifferentiated-rice side table.
- YoY/rolling **not** re-run.

## Files written
- `gohantrust_panel_aoki.csv`
- `gohantrust_panel_aoki_pre_extend_backup.csv`
- `rice_monthly_extended.csv`
- `engel_annual_extended.csv`
- `nhk_ldp_monthly_aoki.csv`
- `nhk_political_monthly_2005_2014.csv`
- `panel_extend_coverage_2005_2014.csv`
- `_summary_aoki.json`
- `report_panel_extend_pre2015.md`

## Panel head / tail

```
{'year': 2005, 'P_yen': 2224.2, 'cabinet_psi': 50.42, 'ruling_party': 35.33, 'Aoki_A': 85.75, 'E': 0.22899999999999998, 'K': 136.3181, 'ruling_first': 'LDP'}
{'year': 2006, 'P_yen': 2138.7, 'cabinet_psi': 50.83, 'ruling_party': 38.64, 'Aoki_A': 89.47, 'E': 0.231, 'K': 175.8488, 'ruling_first': 'LDP'}
{'year': 2007, 'P_yen': 2104.0, 'cabinet_psi': 44.25, 'ruling_party': 31.88, 'Aoki_A': 76.12, 'E': 0.23, 'K': 76.615, 'ruling_first': 'LDP'}
...
{'year': 2023, 'P_yen': 2069.1, 'cabinet_psi': 36.33, 'ruling_party': 35.5, 'Aoki_A': 71.83, 'E': 0.278, 'K': 52.8483, 'ruling_first': 'LDP'}
{'year': 2024, 'P_yen': 2686.9, 'cabinet_psi': 28.08, 'ruling_party': 29.58, 'Aoki_A': 57.67, 'E': 0.283, 'K': 44.8552, 'ruling_first': 'LDP'}
{'year': 2025, 'P_yen': 4599.7, 'cabinet_psi': 42.18, 'ruling_party': 29.23, 'Aoki_A': 71.41, 'E': 0.286, 'K': 112.5034, 'ruling_first': 'LDP'}
```

**Full panel n = 21 years (2005–2025).**

## Blockers
- None for stretch target 2005–2014. All series from e-Stat / NHK bunken.
- 2011-03 NHK missing (documented); annual uses n=11.
