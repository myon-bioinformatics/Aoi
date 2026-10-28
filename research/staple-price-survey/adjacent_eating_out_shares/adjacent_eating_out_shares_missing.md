# missing — adjacent_eating_out_shares

## Hits: 55 ISO3 · 1626 rows

See `readme.md` coverage table and `_coverage_by_country.csv`.

### By source (CP11 / 1111000 share)

| source | countries |
|--------|-----------|
| Eurostat NAMA_10_CO3_P3 | CHE, CZE, DNK, EUZ, HUN, NOR, POL, ROU, SWE, TUR |
| OECD DF_TABLE5 (gap-fill) | AUS, CAN, CHL, COL, CRI, GBR, IDN, ISR, MEX, NZL, RUS |
| OECD DF_TABLE5A_T500 (gap-fill) | JPN, KOR |
| World Bank ICP source=90/78 (gap-fill) | ARE, ARG, AZE, BHR, BRA, CHN, EGY, GTM, HKG, HND, IND, JOR, KWT, LBN, LKA, MDA, MYS, NIC, OMN, PAK, PER, PHL, QAT, SAU, SGP, THA, TWN, UKR, URY, VEN, VNM, ZAF |

EUZ geo used: **EA20**.

ICP new rows this pass: **91** shares + **91** levels.

## Misses (fillable)

None among Big Mac ISO3 after ICP gap-fill.

## Intentional skip

| ISO3 | note |
|------|------|
| USA | USDA FES shares + Aoi `bls_us_cpi_fah_fafh_panel` already cover FAH/FAFH; not duplicated here |

## Partial ICP coverage notes

| ISO3 | note |
|------|------|
| VEN | Only 2011 benchmark (ICP 2017 API source=78); no 2017/2021 in source=90 |
| ARG | 2017+2021 (source=90); no 2011 PCAP.PP pair |
| GTM | 2011+2021; 2017 null in source=90 |
| LBN | 2017+2021; 2011 null in source=78 |

## Probes not loaded

| source | reason |
|--------|--------|
| CEPALSTAT ind. 2500 | Same ICP PPP per-capita headings; denominator is AIC not HFCE — would duplicate |
| ADB KIDB / data.adb.org | Cloudflare 403 this run |
| UNSD SNAAMA / UNdata | No open COICOP CP11 HFCE detail in probed endpoints |

## Not in scope

- HICP / CPI CP11 **price indexes**
- Aoi Japan 外食 HH survey (separate Engel panels)
- ITA browser absolute staples
