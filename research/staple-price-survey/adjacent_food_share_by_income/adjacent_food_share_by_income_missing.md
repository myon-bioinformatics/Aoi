# missing — adjacent_food_share_by_income

## Hits: 27 ISO3 · 554 rows

See `readme.md` coverage tables and `_coverage_by_country.csv`.

Hits: ARG, BRA, CAN, CHL, COL, CRI, CZE, DNK, EUZ, GBR, GTM, HND, HUN, IDN, IND, MEX, NIC, NOR, PER, PHL, POL, ROU, SWE, THA, TUR, URY, USA

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
| BLS CE opub Tables 2/3 | USA (food + food_at_home; quintiles + deciles) |
| StatCan SHS Table 11-10-0223-01 via The Daily | CAN (food-total % of current consumption; quintiles) |

## Priority status (Asia + ZAF + NA)

| ISO3 | status | probe notes |
|------|--------|-------------|
| IND | **HIT** 15 rows | MOSPI HCES 2022-23 Excel Table A6 + Table A2 → national q1–q5 and d1–d10 |
| THA | **HIT** 2 rows (partial) | SES 2561 summary PDF q1/q5 only |
| IDN | **HIT** 10 rows (secondary) | BPS via Kompas; bps.go.id 403 |
| PHL | **HIT** 15 rows | bettergov OpenSTAT FIES 2023 Table 7 |
| USA | **HIT** 110 rows | BLS CE Table 2/3 Food and Food at home ÷ avg annual expenditures; WebFetch (curl download.bls.gov 403 Akamai) |
| CAN | **HIT** 7 rows | StatCan Daily published shares; CSV zip HTTP 000 from this egress — full Table 11-10-0223-01 not densified |
| ZAF | **MISS** (exhausted curl) | Stats SA / DataFirst / Wayback no open bulk IES food×quintile |

## Other Big Mac misses (excl. Aoi skip)

ARE, AUS, AZE, BHR, CHE, CHN, EGY, HKG, ISR, JOR, KWT, LBN, LKA, MDA, MYS, NZL, OMN, PAK, QAT, RUS, SAU, SGP, UKR, VEN, VNM, ZAF

No open HBS/FIES quintile×food share table loaded for these this run. National-mean Engel / ICP aggregate food shares intentionally **not** used as quintile proxies (no gap-fill). NZL Aoi HES panel is national-all-households only.

## Intentional skip

| ISO3 | note |
|------|------|
| JPN | Season2 Japan Engel quintiles |
| KOR | Aoi Korea food-share-by-income |
| TWN | Aoi Taiwan food-share-by-income |
| AUS | Aoi ABS HES food-share panel — do not duplicate into this pack |

## Probes not loaded / not reused as Engel

- THA `SES_41_05.csv` — income distribution by quintile, **not** food expenditure share
- INEGI ENIGH micro/tabulados direct: 403 (CEPALSTAT 5725 covers MEX 2018)
- IBGE SIDRA POF: CEPALSTAT 5725 used for BRA
- BLS staple retail levels / FAH·FAFH **indexes** / FPMA / Pink Sheet / CoAHD / producer prices / eating-out: out of scope (BLS **CE expenditure shares** are in-scope and loaded)
- Aoi CPI / housing / FPO companions: not touched
- StatCan `11100223-eng.zip`: blocked from this egress (use Daily shares instead)
