# missing — adjacent_food_share_by_income

## Hits: 21 ISO3 · 395 rows

See `readme.md` coverage tables and `_coverage_by_country.csv`.

Hits: ARG, BRA, CHL, COL, CRI, CZE, DNK, EUZ, GBR, GTM, HND, HUN, MEX, NIC, NOR, PER, POL, ROU, SWE, TUR, URY

### By source

| source | countries |
|--------|-----------|
| Eurostat HBS_STR_T223 | CZE, DNK, EUZ, GBR, HUN, NOR, POL, ROU, SWE, TUR |
| CEPALSTAT indicator 5725 | ARG, BRA, CHL, COL, CRI, GTM, HND, MEX, NIC, PER, URY |
| ONS Family Spending workbook 2 Table A8 | GBR (deciles) |
| Defra Family Food (GOV.UK CSV) | GBR (q1/q3/q5) |

## Priority misses

| ISO3 | probe notes |
|------|-------------|
| ZAF | Stats SA IES / P0100 PDF and isibalo paths 403 or empty; Wayback CDX empty this run |
| IND | MOSPI HCES PDFs give national food share; Table A6 (fractile×food) Excel URLs 404; third-party GitHub HCES microdata repo not a published food×quintile table |
| THA | NSO SES tables open but no food×income-quintile expenditure share table found (income-distribution tables only) |
| IDN | BPS / related open paths Cloudflare/403 this run |
| PHL | bettergov / OpenStat PX Cloudflare-blocked this run |

## Other Big Mac misses (excl. Aoi skip)

ARE, AUS, AZE, BHR, CAN, CHE, CHN, EGY, HKG, IDN, IND, ISR, JOR, KWT, LBN, LKA, MDA, MYS, NZL, OMN, PAK, PHL, QAT, RUS, SAU, SGP, THA, UKR, USA, VEN, VNM, ZAF

No open HBS/FIES quintile×food share table loaded for these this run. National-mean Engel / ICP aggregate food shares intentionally **not** used as quintile proxies (no gap-fill).

## Intentional skip

| ISO3 | note |
|------|------|
| JPN | Season2 Japan Engel quintiles |
| KOR | Aoi Korea food-share-by-income |
| TWN | Aoi Taiwan food-share-by-income |

## Probes not loaded

- INEGI ENIGH micro/tabulados direct: 403 from this egress (CEPALSTAT 5725 covers MEX 2018)
- IBGE SIDRA POF class descriptors fetched; CEPALSTAT 5725 used for BRA instead of rebuilding from SIDRA
- BLS CE / FPMA / Pink Sheet / CoAHD / producer prices / eating-out: out of scope for this pack
