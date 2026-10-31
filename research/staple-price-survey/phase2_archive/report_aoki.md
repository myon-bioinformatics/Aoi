# GohanTrust panel — Aoki rate (青木率) version

**Retrieval / rebuild date:** 2026-10-24 (Asia/Tokyo)

## 0. Definition (Wikipedia「青木の法則」)

Source: https://ja.wikipedia.org/wiki/青木の法則

- **青木率** \(A\) ＝ **内閣支持率（%）** ＋ **与党第一党の政党支持率（%）**
- 第一法則: \(A < 50\) で政権が倒れる／運営が厳しくなる、という経験則
- 第二法則: 国政選挙で「与党第一党の現有議席 × 直近の青木率 ≈ 獲得議席」

このパネルで使うのは **青木率そのもの**（第一法則側の定義）。第二法則の議席予測は扱わない。

2015–2025 の期間、与党第一党は一貫して **自由民主党（LDP）** なので、政党支持率は NHK の自民党支持率を用いる。

## 1. Identity

**Primary (as written, with Aoki rate in place of ψ):**

\[ P = K \cdot q \cdot (100 - A) \cdot E \]

\[ K_t = P_t / \bigl(q \cdot (100 - A_t) \cdot E_t\bigr) \]

**Exploratory alternate** (keeps the political factor positive when \(A\) is in \((100, 200)\)):

\[ P = K_{\mathrm{alt}} \cdot q \cdot (200 - A) \cdot E \]

Primary is **not** silently rewritten when \(A \ge 100\): those years get `K = NA` under the primary form. The alternate is labeled and stored in `K_alt` for every year.

## 2. The (100 − A) problem

- **Annual** \(A \ge 100\): **0 / 11** years (2015–2025). None in this window.
- **Monthly** paired \(A \ge 100\): **1 / 130** months.
  - Only hit: **2020-09** (菅内閣発足直後) cabinet 62% + LDP 40.8% = **102.8**. Annual mean for 2020 is still 80.08, so primary \(K\) for 2020 remains defined.
- Conclusion: for 2015–2025 annual means, primary \((100-A)\) does not go non-positive, but the monthly breach shows the form is **fragile** under high-support cabinets. Do not treat 100 as a deep constant; it was inherited from the cabinet-only draft where ψ ≤ 100 by construction.

## 3. Sources

| Series | Definition | Source | Notes |
|---|---|---|---|
| **P** | 国内産うるち米（単一原料米）5kg、コシヒカリを除く、全国平均小売価格（円） | 総務省 小売物価統計（動向編）; monthly re-tab https://www.jpmarket-conditions.com/1002/ ; e-Stat / https://www.stat.go.jp/data/kouri/doukou/3.htm | Same as prior cabinet-only panel. Annual = mean of 12 months. |
| **q** | kg | Fixed **5** | P is yen per 5 kg bag. |
| **E** | エンゲル係数（食料／消費支出）、二人以上世帯、小数 | 総務省 家計調査 | Same as prior panel (e.g. 2025: 28.6% → 0.286). |
| **cabinet ψ** | NHK「内閣を支持する」% | NHK 世論調査; archive used previously https://ai.jfsc.jp/research/yato-tsuikyu-japan/data/appendixH_approval.csv ; UI https://news.web.nhk/senkyo/shijiritsu/ | Paired with LDP months only. |
| **ruling party** | NHK 自民党支持率 % | **Priority:** (1) NHK放送文化研究所 政治意識月例調査 https://www.nhk.or.jp/bunken/research/yoron/political/YYYY.html for 2016–2019 (+2020-01..03); (2) moshisen.com NHK re-tabulation https://moshisen.com/polling for 2015 and gaps through 2022-05; (3) chart-read values already in `/workspace/aoi-phase2/nhk_approval.csv` for 2022-06 onward (±0.5pt). | Missing months excluded, not imputed. 2019-10 cancelled in bunken → left missing (moshisen’s 2019-10 cell discarded). |
| **Aoki A** | cabinet + LDP, then annual mean of **paired** months | Computed | \(A_t = \overline{\mathrm{cab}_m + \mathrm{LDP}_m}\) over months where both exist. |

ChatGPT ~1-year-old numbers were **not** used.

Monthly audit file: `/workspace/aoi-phase2/nhk_ldp_monthly_aoki.csv`

## 4. Panel

Path: `/workspace/aoi-phase2/gohantrust_panel_aoki.csv`

| year | P_yen | q | cabinet | LDP | Aoki A | E | K (primary) | K_alt (200−A) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2015 | 1833.1 | 5.0 | 46.42 | 36.86 | 83.27 | 0.25 | 87.6819 | 12.5635 |
| 2016 | 1912.5 | 5.0 | 49.17 | 38.14 | 87.31 | 0.258 | 116.8135 | 13.1559 |
| 2017 | 2033.4 | 5.0 | 47.17 | 36.25 | 83.42 | 0.257 | 95.4219 | 13.5732 |
| 2018 | 2157.8 | 5.0 | 42.17 | 36.49 | 78.66 | 0.257 | 78.6828 | 13.8388 |
| 2019 | 2151.4 | 5.0 | 46.0 | 36.17 | 82.17 | 0.257 | 93.9146 | 14.2093 |
| 2020 | 2163.1 | 5.0 | 44.08 | 35.99 | 80.08 | 0.275 | 78.9543 | 13.1179 |
| 2021 | 2096.8 | 5.0 | 39.83 | 36.19 | 76.02 | 0.272 | 64.3072 | 12.4361 |
| 2022 | 1995.8 | 5.0 | 48.58 | 38.32 | 86.91 | 0.266 | 114.6226 | 13.2689 |
| 2023 | 2069.1 | 5.0 | 36.33 | 35.5 | 71.83 | 0.278 | 52.8483 | 11.6143 |
| 2024 | 2686.9 | 5.0 | 28.08 | 29.58 | 57.67 | 0.283 | 44.8552 | 13.341 |
| 2025 | 4599.7 | 5.0 | 42.18 | 29.23 | 71.41 | 0.286 | 112.5034 | 25.014 |

## 5. K summary (primary)

| Stat | Value |
|---|---:|
| n (years with A<100) | 11 |
| mean | **85.51** |
| min | **44.86** (2024) |
| max | **116.81** (2016) |
| Aoki annual mean / min / max | 78.07 / 57.67 / 87.31 |

**Reading:** With A ≈ 58–87, \((100-A)\) is only ≈ 13–42 (vs ≈ 50–72 when using cabinet alone). Primary \(K\) therefore jumps to a **much higher level** (mean ≈ 85 vs ≈ 30 in the cabinet-only panel) and is **more volatile** (≈45–117). The free scale is absorbing the fact that Aoki rate is a larger number shoved into a form built for a 0–100 single rate. `K_alt` (200−A) sits in a tighter band ≈ 11–25 (mean ≈ 14.2), which is numerically closer to the old K scale — but that is an **exploratory rescaling**, not the Wikipedia definition.

## 6. Out-of-sample (same design as cabinet-only)

- Train 2015–2021 → \(\hat K = 87.9680\)
- Test 2022–2025
- Model: \(\hat P_t = \hat K \cdot 5 \cdot (100 - A_t) \cdot E_t\)
- Naive: \(\hat P_t = P_{t-1}\)

| year | actual P | model \(\hat P\) | naive | \|e\| model | \|e\| naive |
|---:|---:|---:|---:|---:|---:|
| 2022 | 1995.8 | 1531.7 | 2096.8 | 464 | 101 |
| 2023 | 2069.1 | 3444.1 | 1995.8 | 1375 | 73 |
| 2024 | 2686.9 | 5269.4 | 2069.1 | 2583 | 618 |
| 2025 | 4599.7 | 3596.6 | 2686.9 | 1003 | 1913 |

**MAE (yen, 2022–2025):** Aoki primary model **1356** vs naive last-year **676**.

## 7. Comparison vs previous cabinet-only panel

| | Cabinet-only (ψ) | Aoki rate (A) |
|---|---:|---:|
| K mean | 30.44 | 85.51 |
| K min–max | 23.38–55.63 | 44.86–116.81 |
| OOS MAE model | 740 | 1356 |
| OOS MAE naive | 676 | 676 |

**One line:** Switching ψ → Aoki rate makes fixed-K price forecasts **worse** on this OOS window (MAE 1356 vs 740), and still loses to last-year naive (676). Definitional correctness (青木率) and forecast usefulness are separate; Aoki is the right political variable for the user’s intent, but the inherited \((100 - \cdot)\) shell does not earn its keep yet.

## 8. Caveats

1. K remains a free scale coefficient with no external unit.
2. (100−A) is a draft leftover; Aoki rates routinely sit near 70–90 and can exceed 100 in single months.
3. LDP series mixes bunken (best), moshisen re-tab (good for 2015 / mid-2020–2022-05), and chart-reads for 2022-06+ (±0.5pt).
4. Annual A uses only months with **both** cabinet and LDP (2019-10 and 2025-10 excluded).
5. ChatGPT old figures untrusted.

## 9. Files

- `/workspace/aoi-phase2/gohantrust_panel_aoki.csv` — annual panel
- `/workspace/aoi-phase2/nhk_ldp_monthly_aoki.csv` — monthly cabinet/LDP/A with source tags
- `/workspace/aoi-phase2/_summary_aoki.json` — machine summary
- `/workspace/aoi-phase2/report_aoki.md` — this report
- Prior cabinet-only: `gohantrust_panel.csv`, `report.md`
