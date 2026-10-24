# missing — adjacent_eating_out_shares

## Hits: 23 ISO3 · 1444 rows

See `readme.md` coverage table and `_coverage_by_country.csv`.

### By source (CP11 share)

| source | countries |
|--------|-----------|
| Eurostat NAMA_10_CO3_P3 | CHE, CZE, DNK, EUZ, HUN, NOR, POL, ROU, SWE, TUR |
| OECD DF_TABLE5 (gap-fill) | AUS, CAN, CHL, COL, CRI, GBR, IDN, ISR, MEX, NZL, RUS |
| OECD DF_TABLE5A_T500 (gap-fill) | JPN, KOR |

EUZ geo used: **EA20**.

## Misses (33)

ARE, ARG, AZE, BHR, BRA, CHN, EGY, GTM, HKG, HND, IND, JOR, KWT, LBN, LKA, MDA, MYS, NIC, OMN, PAK, PER, PHL, QAT, SAU, SGP, THA, TWN, UKR, URY, USA, VEN, VNM, ZAF

### Notes on selected misses

| ISO3 | note |
|------|------|
| USA | Intentional skip — USDA FES shares + Aoi `bls_us_cpi_fah_fafh_panel` already cover FAH/FAFH; not duplicated here |
| BRA, HKG | OECD HFCE total present in some pulls; **no CP11** expenditure series in DF_TABLE5/T5A extracts |
| CHN, IND, TWN, SGP, THA, MYS, VNM, PHL, PAK, LKA, … | No Eurostat; not in OECD COICOP CP11 extract |
| ARE/BHR/KWT/OMN/QAT/SAU/JOR/EGY/… | No open NA COICOP CP11 share in these APIs |
| ARG/URY/PER/GTM/HND/NIC/VEN/ZAF/… | Same |

## Not in scope

- HICP / CPI CP11 **price indexes**
- Aoi Japan 外食 HH survey (separate Engel panels)
- ITA browser absolute staples
