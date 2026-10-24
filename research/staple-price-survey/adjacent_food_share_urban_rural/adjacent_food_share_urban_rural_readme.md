# adjacent_food_share_urban_rural

Urban vs rural (or municipal / non-municipal) food expenditure shares of household consumption — Engel companion for Big Mac ISO3 coverage.

## Schema
`country,date,year,variable,value,unit,source,note,estimated_value`

Variables: `engel_share:food_urban`, `engel_share:food_rural`.

## Coverage (build 2026-10-25 Asia/Tokyo)
- **467 rows / 86 ISO3**, years **1988–2025**
- ISO3: ARM AUS AUT AZE BEL BGD BGR BOL BRA BWA CHN CIV COL CRI CYP CZE DEU DNK DOM DZA ECU EGY ESP EST ETH EUZ FIN FJI FRA GBR GEO GRC GTM HND HRV HUN IDN IND IRL IRN ITA JOR KEN KHM LAO LKA LTU LUX LVA MAR MDA MEX MLI MLT MMR MOZ MYS NAM NGA NIC NLD NOR OMN PAK PER PHL POL PRT PRY ROU RUS RWA SLV SVK SVN SWE THA TUN TZA UGA UKR URY USA VNM ZAF ZMB
- `estimated_value` empty on all rows

## Sources
| Source | Rows | Notes |
|---|---:|---|
| Eurostat HBS_STR_T226 | 277 | CP01; PM÷10→%; DEG1=cities→urban; DEG3=rural |
| CEPALSTAT indicator 5725 | 26 | Urban/Rural; **Total quintile** only |
| MOSPI HCES Statement 3 | 12 | India (incl. 2023-24) |
| Azerbaijan SSC HBS via banker.az | 2 | Azerbaijan H1 2023 |
| BLS CE Table 1721 | 8 | USA |
| BPS Susenas 2020–2023 (Kompas/CNBC→BPS) | 6 | IDN |
| NSO Thailand SES 2021 Table 6 | 2 | THA municipal/non-municipal |
| PSA FIES via Bairagi PLOS ONE 2022 | 10 | PHL |
| DOSM HES Report 2024 | 2 | MYS F&B 14.4 / 23.0 |
| PBS Pakistan HIES Table 3.7.A/B | 8 | PAK Food & Non-Alc urban/rural 2011-12…2018-19 |
| DCS Sri Lanka HIES 2016 Table 8 + 2019 Table 10 | 4 | LKA Urban/Rural food ratio |
| Rosstat HBS R_1-5 (via Roschart) | 4 | RUS Q3 2022–2023 |
| CAPMAS HIECS 2019/2020 (ERF 3948) | 2 | EGY Urban 28.63 / Rural 36.39 |
| HCP Morocco ENCDM/ENNVM | 6 | MAR Alimentation urban/rural 2001/2007/2014 |
| DANE Colombia ENPH 2016-2017 | 2 | COL cabeceras 14.0 / rural disperso 31.2 |
| INEGI ENIGH 2020/2022/2024 | 6 | MEX alimentos+bebidas+tabaco urban/rural |

## Deliberate misses / skips
CAN (StatCan SSL); ARG urban-only ENGHo; CHL INE EPF urban capitals only; CHE/TUR not in T226; URY/PAN/ARG/CHL CEPAL National-only for area; HKG/SGP city-state; SAU/ARE national/regional only; PAK **HIT** (HIES 2011-12…2018-19); EGY CAPMAS primary not pinned; VNM/ZAF/AUS/CHN appended earlier;  Aoi skips: JPN/KOR/TWN, AUS/NZL HES; UK ONS LCFS national (GBR here = Eurostat T226).

See `missing.md`.
