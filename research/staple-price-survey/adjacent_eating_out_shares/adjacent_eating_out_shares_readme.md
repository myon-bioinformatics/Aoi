# adjacent_eating_out_shares — restaurants/hotels & food-away HFCE shares

Retrieved: **2026-10-24 Asia/Tokyo** · Season2 adjacent for Aoi #118

## Result

**1444 vertical rows** · **23 / 56** Big Mac ISO3 with at least one series · year span shares **1995–2025**.

Companion to Engel / at-home food shares. **Not CPI / HICP indexes.**

| variable | rows | unit | definition |
|----------|-----:|------|------------|
| `hh_consumption_share:restaurants_hotels` | 580 | percent_of_hfce | COICOP CP11 restaurants **and** hotels/accommodation ÷ HFCE |
| `engel_share:food_away_from_home` | 284 | percent_of_hfce | COICOP **CP111 catering services** ÷ HFCE (closer to FAFH; excludes hotels) |
| `hh_consumption_level:restaurants_hotels` | 580 | million_eur or million_lcu_* | CP11 expenditure level (Eurostat CP_MEUR or OECD XDC) |

Schema: `country,date,year,variable,value,unit,source,note,estimated_value` (ISO3; `date=YYYY-01-01`; `estimated_value` empty (no gap-fill); OECD shares are exact ratios of published levels).

## Sources (priority)

1. **Eurostat** `NAMA_10_CO3_P3` unit `PC_TOT` (published shares) + `CP_MEUR` levels — COICOP 1999. EUZ mapped from **EA20**.
2. **OECD** `DSD_NAMAIN10@DF_TABLE5` (COICOP 1999 T0117) for Big Mac countries **without** Eurostat CP11 share — share = CP11 / `_T` HFCE in current-price national currency.
3. **OECD** `DSD_NAMAIN10@DF_TABLE5A_T500` (COICOP 2018 T0500) for remaining gaps (**JPN**, **KOR**).

Eurostat preferred over OECD when both exist. **USA skipped** (USDA FES + Aoi BLS FAH/FAFH already cover). HICP CP11 price indexes not used. ITA absolute staple retail exhausted separately (indices/city-only); not part of this pack.

## Coverage (hits)

| ISO3 | CP11 share rows (years) | source | CP111/FAFH rows | level rows |
|------|-------------------------|--------|-----------------|------------|
| AUS | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 30 |
| CAN | 31 (1995-2025) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 31 |
| CHE | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 0 (nan) | 28 |
| CHL | 7 (2018-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 7 |
| COL | 20 (2005-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 20 |
| CRI | 27 (1995-2021) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 27 |
| CZE | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| DNK | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| EUZ | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| GBR | 31 (1995-2025) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 31 |
| HUN | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| IDN | 6 (2010-2015) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 6 |
| ISR | 29 (1995-2023) | OECD DSD_NAMAIN10@DF_TABLE5 | 30 (1995-2024) | 29 |
| JPN | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5A_T500 | 30 (1995-2024) | 30 |
| KOR | 31 (1995-2025) | OECD DSD_NAMAIN10@DF_TABLE5A_T500 | 0 (nan) | 31 |
| MEX | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 30 |
| NOR | 29 (1995-2023) | Eurostat NAMA_10_CO3_P3 | 27 (1995-2021) | 29 |
| NZL | 30 (1995-2024) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 30 |
| POL | 29 (1995-2023) | Eurostat NAMA_10_CO3_P3 | 29 (1995-2023) | 29 |
| ROU | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| RUS | 9 (2011-2019) | OECD DSD_NAMAIN10@DF_TABLE5 | 0 (nan) | 9 |
| SWE | 28 (1995-2022) | Eurostat NAMA_10_CO3_P3 | 28 (1995-2022) | 28 |
| TUR | 15 (2009-2023) | Eurostat NAMA_10_CO3_P3 | 0 (nan) | 15 |

## Intentional skips / misses

- **USA** — do not duplicate USDA FES / Aoi BLS FAH–FAFH.
- **33 Big Mac ISO3** with no open Eurostat/OECD CP11 HFCE series in these pulls (see `missing.md`): mostly MENA, LatAm beyond OECD coverage, South/SE Asia, Africa.

## Files

- `adjacent_eating_out_shares_vertical.csv` (+ `.gz`)
- `readme.md`, `missing.md`, `_build_stats.json`, `_coverage_by_country.csv`
- `raw/eurostat/` — SDMX-CSV pulls
- `raw/oecd/` — OECD SDMX CSV + structure

## URLs

- https://ec.europa.eu/eurostat/databrowser/product/page/nama_10_co3_p3
- https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/NAMA_10_CO3_P3/A.PC_TOT.CP11.?format=SDMX-CSV&startPeriod=1995
- https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/NAMA_10_CO3_P3/A.PC_TOT.CP111.?format=SDMX-CSV&startPeriod=1995
- https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5/A..S14.S1.P31DC._Z._Z.CP11.XDC.V..?startPeriod=1995&format=csvfilewithlabels
- https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE5A_T500/A..S14.S1.P31DC._Z._Z.CP11.XDC.V..?startPeriod=1995&format=csvfilewithlabels
- https://data-explorer.oecd.org/

## Definition caveats

- CP11 ≠ Japan 家計調査「外食」 ≠ USDA food-at-home; CP11 includes **hotels**.
- Use `engel_share:food_away_from_home` (CP111) when comparing to FAFH / 外食.
- Eurostat levels are **million EUR** even for non-euro geos; OECD levels are national currency millions.
- No FX conversion; no unit homogenization across sources.

## Mirror

`/workspace/aoi-phase2/staple-price-survey/adjacent_eating_out_shares/`

## Explicit non-touches

Aoi food CPI panels, `hi_staple_levels_alt`, BLS, FPMA, Pink Sheet, UK ONS, CoAHD, producer prices, Japan numeraire/food-service, ITA browser staple probe.
