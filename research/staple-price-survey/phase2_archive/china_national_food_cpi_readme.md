# China national food CPI panel (Aoi origin)

Date: **2026-10-24 Asia/Tokyo**. Vertical tidy panel. **No FX. No fabricated fills.**

File: `/workspace/aoi-phase2/china_national_food_cpi_panel.csv`  
Raw: `/workspace/aoi-phase2/raw/china_cpi/`

## Why this panel

Asia emerging CPI panel (`asia_national_food_cpi_panel.csv`) intentionally omitted **CHN**. Continuous open series for China food CPI are collected here from **OECD SDMX / FRED mirrors of OECD MEI** and **ADB KIDB (NBS)**. Season2 FAO country-CPI bulk is **not** mirrored.

## Series (read definitions carefully)

| series | what | freq | n | start | end | unit / base |
|---|---|---:|---:|---|---|---|
| `food_cpi_index_oecd_cp01` | **Primary** CP01 food+non-alc beverages **index level** | monthly | 405 | 1993-01 | 2026-09 | index, **2015=100** |
| `food_cpi_yoy_pct_from_oecd_index` | YoY % **derived** from OECD IX | monthly | 393 | 1994-01 | 2026-09 | percent_yoy |
| `food_cpi_index_fred_oecd_mirror` | Same CP01 IX via FRED (lags OECD end) | monthly | 388 | 1993-01 | 2025-04 | index, 2015=100 |
| `food_cpi_yoy_pct_fred_oecd_quarterly` | Official OECD YoY % (quarterly) | quarterly | 125 | 1994-Q1 | 2025-Q1 | percent_yoy |
| `food_cpi_prevyear100_adb_nbs` | NBS via ADB; **previous year = 100** | annual | 26 | 2000 | 2025 | index_prev_year_100 |
| `food_cpi_yoy_pct_adb_nbs_annual` | ADB prev-year index − 100 | annual | 26 | 2000 | 2025 | percent_yoy |
| `food_incl_restaurants_cpi_index_fred` | **Broader** food **including restaurants** | monthly | 305 | 1993-01 | 2018-05 | index (source base) |

**Rows total:** 1668

### Index level vs YoY — do not confuse

1. **`food_cpi_index_oecd_cp01` / FRED mirror** = fixed-base **index levels** (2015=100). Use for continuous level / relative path.  
2. **`food_cpi_yoy_pct_*`** = year-over-year **percent** changes.  
3. **`food_cpi_prevyear100_adb_nbs`** looks like an “index” but **BASE_YEAR = previous year** (NBS/ADB convention). A value of `103.4` means **+3.4% vs prior year**, not a 2015-based level. **Never splice** onto the OECD 2015=100 series.  
4. ADB footnote: **from 2016 onward the ADB/NBS food series excludes non-alcoholic beverages** (definition break vs 2000–2015). OECD CP01 continues to include non-alc beverages.

### Cereals / grain

COICOP **CP011** (bread & cereals) was **not** available for CHN on OECD `DSD_PRICES@DF_PRICES_ALL` in this pull (`NoResultsFound` / 404). Not fabricated.

## Columns

`iso3, series, series_label, frequency, year, month, date, value, unit, base_year, source, source_url, note, retrieval_date`

## Raw files

| file | role |
|---|---|
| `raw/china_cpi/oecd_chn_cp01_ix.csv` | OECD SDMX monthly CP01 IX (longest end: 2026-09) |
| `raw/china_cpi/fred_CHNCP010000IXOBM.csv` | FRED mirror of OECD monthly IX |
| `raw/china_cpi/fred_CHNCP010000GYQ.csv` | FRED OECD quarterly YoY % |
| `raw/china_cpi/adb_chn_food.csv` | ADB annual PCPI_CP_01_IX PRC (prev year=100) |
| `raw/china_cpi/fred_CPGDFD01CNM661N.csv` | Food including restaurants (broader; ends 2018) |
| `raw/china_cpi/fred_CPALTT01CNM659N.csv` | All-items YoY (kept raw only; **not** in panel — not food) |
| `raw/china_cpi/fred_CHNPIEATI01GYM.csv` | Industrial PPI YoY (raw only; **not** food CPI) |
| `raw/china_cpi/fred_CHNCPALTT01IXNBM.csv` | All-items CPI index (raw only) |

## Blockers

- Direct OECD **GY** (monthly YoY) SDMX key returned 403/404 this pull — monthly YoY in panel is **derived from IX** and labeled as such; quarterly official YoY kept via FRED.  
- NBS English monthly site / `data.stats.gov.cn` not bulk-downloaded (session/Chinese UI); ADB+OECD already carry NBS-national food CPI.  
- IMF CPI portal TLS/404 from this box (same as Asia panel note) — unused.  
- Season2 FAO country food CPI bulk intentionally **not** mirrored.

## Rules

No FX conversion. No gap-filling. Provenance on every row. Prefer `food_cpi_index_oecd_cp01` for continuous monthly index work.
