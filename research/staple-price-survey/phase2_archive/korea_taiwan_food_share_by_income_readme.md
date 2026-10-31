# Korea / Taiwan — food expenditure share by income quintile (Working–Leser materials)

**Retrieved:** 2026-10-24 Asia/Tokyo

## What
Annual household **food / consumption shares by disposable-income quintile** for Working–Leser–style work. Values stay in **source currency (NT$)** — **no FX**.

## Files
- Panel: `korea_taiwan_food_share_by_income_panel.csv`
- Raw Excels: `raw/korea_taiwan_wl/twROC*_77.xls`, `tw20*_table6_77.xls`

## Coverage (what landed)

| country | status | span | notes |
|---|---|---|---|
| **Taiwan (TWN)** | **in panel** | **2001–2025** (food row continuous; see definition break) | DGBAS FIES Table 6 — five equal divisions by disposable income |
| **Korea (KOR)** | **not in panel** | — | **BLOCKER:** `kostat.go.kr` / `mods.go.kr` / `data.go.kr` / `korea.kr` all fail from this box with `SSL: UNEXPECTED_EOF_WHILE_READING`. No alternate open file URL obtained. Season2 may pull via another egress if needed. |

### Taiwan detail
- **Income groups:** `average`, `q1`…`q5` (household count quintiles by disposable income).
- **Share:** `food_expenditure_nt$ / consumption_expenditure_nt$` (and optional `food_plus_dining_share_of_consumption` when dining row present).
- **Food definition break:**
  - ~**2001–2008:** row `食品費` / `Food` (`food_definition=food_fee_legacy`) — not identical to COICOP food+non-alc.
  - **2009–2025:** `食品及非酒精飲料` / Food and non-alcoholic beverages (`food_non_alc_coicop`).
- **Dining label:** `餐廳及旅館` through ~2023; **2024–2025** `餐廳及住宿` / Restaurants and accommodation services (still mapped to `restaurants_hotels_nt$`).
- Sources: Chinese archive `ws.dgbas.gov.tw/win/fies/doc/result/{ROC}/a11/77.xls` (ROC 90–110); English report Upload `…/77.xls` for calendar 2022–2025.

## Korea blocker (do not retry blindly)
Attempted: `boardDownload.es` on kostat, mods.go.kr press pages, data.go.kr fileData, korea.kr briefing. Same TLS EOF from box Python/`curl -k`. Needs browser/other network or user-supplied xlsx.

## Do-not (Season2 lanes)
Eurostat average food product prices; Season2 high-income NSO retail *levels*; LatAm/ILO/ICP bulk — not collected here.

## KOR — blocker (mirror search, 2026-10-24 JST)
KOR rows NOT added; no numbers invented. kosis.kr / kostat.go.kr / mods / data.go.kr unreachable from box (TLS/connection closed).
Mirrors tried:
- OECD SDMX `OECD.SDD.NAD,DSD_EGDNA_CONS_INC@DF_CONS_INC` (household consumption in NA by income quintile). KOR present 2018–2022 but **only totals** (P31NC _T, P41, D63, P33X34; KRW, XDC and XDC_HH). **No COICOP CP01/CP11 breakdown for KOR** (CP01 exists only for other countries). Raw: `raw/korea_taiwan_wl/oecd_egdna_cons_inc_all.csv`.
- OECD dataflow catalogue scan (EGDNA CONS_HHT / CONS_MSI / SOCDEM): household-type/income-source splits, same KOR coverage limits.
- WB / UN / Eurostat: no KOR income-quintile food expenditure published.
Next options: user-side download of KOSIS 가계동향조사 소득5분위별 가구당 가계수지 (DT_1L9U001 etc.) from a non-box network, then drop into raw/.
