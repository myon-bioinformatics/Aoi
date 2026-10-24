# missing — adjacent_food_share_by_income

## Hits: 25 ISO3 · 437 rows

See `readme.md` coverage tables and `_coverage_by_country.csv`.

Hits: ARG, BRA, CHL, COL, CRI, CZE, DNK, EUZ, GBR, GTM, HND, HUN, IDN, IND, MEX, NIC, NOR, PER, PHL, POL, ROU, SWE, THA, TUR, URY

### By source

| source | countries |
|--------|-----------|
| Eurostat HBS_STR_T223 | CZE, DNK, EUZ, GBR, HUN, NOR, POL, ROU, SWE, TUR |
| CEPALSTAT indicator 5725 | ARG, BRA, CHL, COL, CRI, GTM, HND, MEX, NIC, PER, URY |
| ONS Family Spending workbook 2 Table A8 | GBR (deciles) |
| Defra Family Food (GOV.UK CSV) | GBR (q1/q3/q5) |
| MOSPI HCES 2022-23 Table A6 + A2 | IND |
| NSO Thailand SES 2561 summary PDF | THA (q1/q5 only) |
| BPS Susenas via Kompas (bps.go.id 403) | IDN |
| PSA FIES 2023 Table 7 (bettergov OpenSTAT mirror) | PHL |

## Priority status (Asia + ZAF)

| ISO3 | status | probe notes |
|------|--------|-------------|
| IND | **HIT** 15 rows | MOSPI HCES 2022-23 Excel Table A6 (Food:Total by 12 MPCE fractiles) + Table A2 household weights → national q1–q5 and d1–d10; rural fractile series validated vs published ~54.2…34.4 |
| THA | **HIT** 2 rows (partial) | NSO catalog SES_* CSVs lack food×income share (SES_41_05 is income distribution, not Engel). SES 2561 summary PDF publishes only q1=48.1 / q5=27.2 for food+bev+tobacco (2018). q2–q4 not in open summary |
| IDN | **HIT** 10 rows (secondary) | `bps.go.id` publication PDFs Cloudflare/403; Wayback CDX timed out (000). Kompas 2026-10-06 quotes full BPS Susenas March 2025 & March 2026 q1–q5 food shares — loaded with secondary-citation note |
| PHL | **HIT** 15 rows | PSA / OpenSTAT direct 403 earlier; **bettergov.ph** OpenSTAT mirror API served FIES 2023 Table 7 (food+non-alc % by decile) curl-open |
| ZAF | **MISS** (exhausted curl) | Stats SA P0100 PDF paths 403 or empty HTML; Wayback CDX empty/timeout; DataFirst catalog HTML only (no open bulk IES food×quintile table without browser/login). No WB/ADB open quintile food-share series found |

## Other Big Mac misses (excl. Aoi skip)

ARE, AUS, AZE, BHR, CAN, CHE, CHN, EGY, HKG, ISR, JOR, KWT, LBN, LKA, MDA, MYS, NZL, OMN, PAK, QAT, RUS, SAU, SGP, UKR, USA, VEN, VNM, ZAF

No open HBS/FIES quintile×food share table loaded for these this run. National-mean Engel / ICP aggregate food shares intentionally **not** used as quintile proxies (no gap-fill).

## Intentional skip

| ISO3 | note |
|------|------|
| JPN | Season2 Japan Engel quintiles |
| KOR | Aoi Korea food-share-by-income |
| TWN | Aoi Taiwan food-share-by-income |

## Probes not loaded / not reused as Engel

- THA `SES_41_05.csv` — income distribution by quintile, **not** food expenditure share (do not treat as Engel)
- INEGI ENIGH micro/tabulados direct: 403 (CEPALSTAT 5725 covers MEX 2018)
- IBGE SIDRA POF: CEPALSTAT 5725 used for BRA
- BLS CE / FPMA / Pink Sheet / CoAHD / producer prices / eating-out: out of scope
- Aoi CPI / housing / FPO companions: not touched
