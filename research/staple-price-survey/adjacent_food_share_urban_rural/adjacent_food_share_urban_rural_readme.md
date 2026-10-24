# adjacent_food_share_urban_rural

Urban vs rural (or municipal / non-municipal) food expenditure shares of household consumption — Engel companion for Big Mac ISO3 coverage.

## Schema
`country,date,year,variable,value,unit,source,note,estimated_value`

Variables: `engel_share:food_urban`, `engel_share:food_rural`.

## Coverage (build 2026-10-24 Asia/Tokyo)
- **343 rows / 50 ISO3**, years **1988–2024**
- ISO3: AUT BEL BGR BOL BRA COL CRI CYP CZE DEU DNK DOM ECU ESP EST EUZ FIN FRA GBR GRC GTM HND HRV HUN IDN IND IRL ITA LTU LUX LVA MEX MLT MYS NIC NLD NOR PER PHL POL PRT PRY ROU RUS SLV SVK SVN SWE THA USA
- `estimated_value` empty on all rows

## Sources
| Source | Rows | Notes |
|---|---:|---|
| Eurostat HBS_STR_T226 | 277 | CP01; PM÷10→%; DEG1=cities→urban; DEG3=rural |
| CEPALSTAT indicator 5725 | 26 | Urban/Rural; **Total quintile** only |
| MOSPI HCES Statement 3 | 10 | India |
| BLS CE Table 1721 | 8 | USA |
| BPS Susenas 2022–2023 (CNBC/Kompas→BPS) | 4 | IDN |
| NSO Thailand SES 2021 Table 6 | 2 | THA municipal/non-municipal |
| PSA FIES via Bairagi PLOS ONE 2022 | 10 | PHL |
| DOSM HES Report 2024 | 2 | MYS F&B 14.4 / 23.0 |
| Rosstat HBS R_1-5 (via Roschart) | 4 | RUS Q3 2022–2023 |

## Deliberate misses / skips
CAN (StatCan SSL); ARG urban-only ENGHo; CHL INE EPF urban capitals only; CHE/TUR not in T226; URY/PAN/ARG/CHL CEPAL National-only for area; HKG/SGP city-state; SAU/ARE national/regional only; PAK HIES writeup lacks urban/rural food÷total; EGY CAPMAS primary not pinned; VNM GSO blocked; **ZAF left to sibling Stats SA lane**. Aoi skips: JPN/KOR/TWN, AUS/NZL HES; UK ONS LCFS national (GBR here = Eurostat T226).

See `missing.md`.
