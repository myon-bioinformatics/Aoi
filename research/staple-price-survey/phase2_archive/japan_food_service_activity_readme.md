# Japan food-service activity index (METI ITA, 2020基準)

Date: 2026-10-24 Asia/Tokyo. File: `japan_food_service_activity_panel.csv` — **1932 rows**, vertical tidy.

Source: 経産省 第３次産業活動指数 https://www.meti.go.jp/statistics/tyo/sanzi/result-2.html
2020基準（2019-2020年平均=100.0）. Excel files were **browser-downloaded** after curl got HTTP 403; raw in `raw/japan_food_service/`.

| File | Content | Span | Rows |
|---|---|---|---|
| b2020_komj.xlsx | 月次 業種別原指数 (seasonal_adj=0) | 2018-01–2026-08 | 728 |
| b2020_ksmj.xlsx | 月次 季調済指数 (seasonal_adj=1) | 2018-01–2026-08 | 728 |
| b2020_koqj.xlsx | 四半期 原指数 | 2018-Q1–2026-Q2 | 238 |
| b2020_ksqj.xlsx | 四半期 季調済 | 2018-Q1–2026-Q2 | 238 |

Monthly is primary. Quarterly rows: date=YYYY-Qn, month column = quarter number; CY/FY annual columns skipped.

Series (weight /10000): JM00000I 宿泊業、飲食サービス業 342.4; DJB0000I 飲食店、飲食サービス業 280.3; DJBA100I 食堂、レストラン、専門店 120.8; DJBA200I パブレストラン、居酒屋 45.2; DJBA300I 喫茶店 12.8; DJBA400I ファーストフード店 16.2; DJBB000I 飲食サービス業（持ち帰り・配達含む）85.3.
No sub-rows under DJBB exist in the Excel (持ち帰り・配達 not separately published here).

Not included: linked long series `b2020_ITA_linkj.xlsx` (1988–) is downloaded but not parsed this round. Values are as published; no rebasing/fill.

## Pre-2018 extension (linked series, b2020_ITA_linkj.xlsx)
- Added 720 monthly rows (2003-01–2017-12, original + SA) for **DJB0000I** (2015 code DKB0000I, link coef 1.154) and **JM00000I** (link coef 1.153). Linkj starts 1988-01 for some series but these two are blank before 2003-01.
- DJBA100I/DJBA200I/DJBA300I/DJBA400I/DJBB000I are **not in linkj** → still start 2018-01. No 持ち帰り・配達 subrow in linkj.
- Overlap 2018-01–2024-12: linkj and komj/ksmj identical (max abs diff 0.0); existing komj/ksmj rows kept. Column `source_file` added.
- 利用上の注意 caveats: linked index = past base-year indices (5 years each) chained with link coefficients, **reference only**; series with differing source data across bases or below threshold are not linked; users linking unlinked series must mind continuity breaks.
