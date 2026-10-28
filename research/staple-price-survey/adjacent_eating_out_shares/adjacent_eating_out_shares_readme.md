# adjacent_eating_out_shares — restaurants/hotels & food-away HFCE shares

Retrieved: **2026-10-24 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**1626 vertical rows** · **55 / 56** Big Mac ISO3 with at least one series · year span shares **1995–2025**.

Companion to Engel / at-home food shares. **Not CPI / HICP indexes.**

| variable | rows | unit | definition |
|----------|-----:|------|------------|
| `hh_consumption_share:restaurants_hotels` | 671 | percent_of_hfce | COICOP CP11 / ICP 1111000 restaurants **and** hotels ÷ HFCE |
| `engel_share:food_away_from_home` | 284 | percent_of_hfce | COICOP **CP111 catering services** ÷ HFCE (closer to FAFH; excludes hotels) |
| `hh_consumption_level:restaurants_hotels` | 671 | million_eur / million_lcu_* / billion_lcu | CP11 / ICP 1111000 expenditure level |

Schema: `country,date,year,variable,value,unit,source,note,estimated_value` (ISO3; `date=YYYY-01-01`; `estimated_value` empty (no gap-fill); OECD/ICP shares are ratios of published levels).

## Sources (priority)

1. **Eurostat** `NAMA_10_CO3_P3` unit `PC_TOT` (published shares) + `CP_MEUR` levels — COICOP 1999. EUZ mapped from **EA20**.
2. **OECD** `DSD_NAMAIN10@DF_TABLE5` (COICOP 1999 T0117) for Big Mac countries **without** Eurostat CP11 share — share = CP11 / `_T` HFCE in current-price national currency.
3. **OECD** `DSD_NAMAIN10@DF_TABLE5A_T500` (COICOP 2018 T0500) for remaining gaps (**JPN**, **KOR**).
4. **World Bank ICP** API `sources/90` (2017, 2021) and `sources/78` (2011) for remaining Big Mac misses — share = `100 * PCAP.PP(1111000) / PCAP.PP(9100000)`; levels from Classification `CN` (LCU billions). Formula recorded in each row `note`.

Eurostat preferred over OECD when both exist; OECD/Eurostat preferred over ICP (ICP only gap-fills prior misses). **USA skipped** (USDA FES + Aoi BLS FAH/FAFH already cover). HICP CP11 price indexes not used.

CEPALSTAT indicator 2500 mirrors ICP PPP per-capita headings (AIC denominator) — not loaded separately (would duplicate ICP). ADB Key Indicators / data.adb.org blocked (Cloudflare) this run. UNSD SNAAMA lacks COICOP CP11 detail in open pulls.

## Coverage (hits)

### Eurostat / OECD (annual NA)

| ISO3 | CP11 share rows (years) | source | CP111/FAFH rows | level rows |
|------|-------------------------|--------|-----------------|------------|
| AUS | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 30 |
| CAN | 31 (1995-2025) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 31 |
| CHE | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 0 | 28 |
| CHL | 7 (2018-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 7 |
| COL | 20 (2005-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 20 |
| CRI | 27 (1995-2021) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 27 |
| CZE | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| DNK | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| EUZ | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| GBR | 31 (1995-2025) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 31 |
| HUN | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| IDN | 6 (2010-2015) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 6 |
| ISR | 29 (1995-2023) | OECD DSD_NAMAIN10@DF_TABLE5 | 30 (1995-2024) | 29 |
| JPN | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5A_T500 | 30 (1995-2024) | 30 |
| KOR | 31 (1995-2025) | OECD DSD_NAMAIN10@DF_TABLE5A_T500 | 0 | 31 |
| MEX | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 30 |
| NOR | 29 (1995-2023) | Eurostat NAMA_10_CO3_P3 | 27 (1995-2021) | 29 |
| NZL | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 30 |
| POL | 29 (1995-2023) | Eurostat NAMA_10_CO3_P3 | 29 (1995-2023) | 29 |
| ROU | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| RUS | 9 (2011-2019) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 | 9 |
| SWE | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| TUR | 15 (2009-2023) | Eurostat NAMA_10_CO3_P3 | 0 | 15 |

### World Bank ICP gap-fill (benchmark years)

| ISO3 | share rows (years) | sources | level rows (CN billion LCU) |
|------|--------------------|---------|-----------------------------|
| ARE | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| ARG | 2 (2017-2021) | World Bank ICP 2021 API source=90 | 2 |
| AZE | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| BHR | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| BRA | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| CHN | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| EGY | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| GTM | 2 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 2 |
| HKG | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| HND | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| IND | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| JOR | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| KWT | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| LBN | 2 (2017-2021) | World Bank ICP 2021 API source=90 | 2 |
| LKA | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| MDA | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| MYS | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| NIC | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| OMN | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| PAK | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| PER | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| PHL | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| QAT | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| SAU | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| SGP | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| THA | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| TWN | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| UKR | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| URY | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| VEN | 1 (2011) | World Bank ICP 2017 API source=78 | 1 |
| VNM | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |
| ZAF | 3 (2011-2021) | World Bank ICP 2017 API source=78; World Bank ICP 2021 API source=90 | 3 |

## Intentional skips / remaining misses

- **USA** — do not duplicate USDA FES / Aoi BLS FAH–FAFH.
- **No remaining fillable Big Mac misses** after ICP gap-fill (VEN only 2011 benchmark in source=78; ARG/GTM/LBN lack some benchmark years).

## Files

- `adjacent_eating_out_shares_vertical.csv` (+ `.gz`)
- `readme.md`, `missing.md`, `_build_stats.json`, `_coverage_by_country.csv`
- `raw/eurostat/` — SDMX-CSV pulls
- `raw/oecd/` — OECD SDMX CSV + structure
- `raw/wb/` — ICP API JSON (`icp90_*.json`, `icp78_*.json`)
- `raw/cepal/` — probe only (indicator 2500; not loaded)

## URLs

- https://ec.europa.eu/eurostat/databrowser/product/page/nama_10_co3_p3
- https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/NAMA_10_CO3_P3/A.PC_TOT.CP11.?format=SDMX-CSV&startPeriod=1995
- https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5/A..S14.S1.P31DC._Z._Z.CP11.XDC.V..?startPeriod=1995&format=csvfilewithlabels
- https://api.worldbank.org/v2/sources/90/country/all/series/1111000?format=json&per_page=20000
- https://api.worldbank.org/v2/sources/90/country/all/series/9100000?format=json&per_page=20000
- https://api.worldbank.org/v2/sources/78/country/all/series/1111000?format=json&per_page=20000
- https://data-explorer.oecd.org/

## Definition caveats

- CP11 / ICP 1111000 ≠ Japan 家計調査「外食」 ≠ USDA food-at-home; includes **hotels**.
- Use `engel_share:food_away_from_home` (CP111) when comparing to FAFH / 外食 (Eurostat/OECD only so far).
- Eurostat levels are **million EUR** even for non-euro geos; OECD levels are national currency millions; ICP `CN` levels are **billions LCU**.
- ICP rows are **benchmark years** (2011/2017/2021), not annual national accounts.
- ICP share formula (in `note`): `100 * PCAP.PP(1111000) / PCAP.PP(9100000)` — HFCE base, not AIC (`AICZS`).
- No FX conversion; no unit homogenization across sources.

## Mirror

`/workspace/aoi-phase2/staple-price-survey/adjacent_eating_out_shares/`

## Explicit non-touches

Aoi food CPI panels, `hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS, CoAHD, producer prices, Japan numeraire/food-service, ITA browser staple probe.
