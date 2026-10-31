# Asia national food / cereals CPI panel (Aoi origin)

Date: **2026-10-24 Asia/Tokyo**. Vertical tidy panel. **No FX. No fabricated fills.**

File: `/workspace/aoi-phase2/asia_national_food_cpi_panel.csv`  
Raw: `/workspace/aoi-phase2/raw/asia_food_cpi/`

## Scope

Target Big-Mac / staple-relevant Asia emerging (+ KOR): **IDN, THA, PHL, VNM, IND, KOR, MYS**.

Season2 owns FAO country food/cereals CPI and high-income national CPI lanes — this panel uses **ADB KIDB national CPI mirrors**, **OECD national CPI mirrors** (where published), and **DOSM Malaysia open data**. Not a FAO CPI duplicate.

## Coverage (this pull)

| iso3 | series | freq | n | start | end |
|---|---|---|---:|---|---|
| IDN | `food_cpi_index_adb_pcpi_cp01` | annual | 26 | 2000-01-01 | 2025-01-01 |
| IND | `food_cpi_index_adb_pcpi_cp01` | annual | 13 | 2013-01-01 | 2025-01-01 |
| IND | `food_cpi_index_oecd_cp01` | monthly | 77 | 2013-01-01 | 2019-05-01 |
| IND | `food_cpi_yoy_oecd_cp01` | monthly | 65 | 2014-01-01 | 2019-05-01 |
| KOR | `food_cpi_index_adb_pcpi_cp01` | annual | 26 | 2000-01-01 | 2025-01-01 |
| KOR | `food_cpi_index_oecd_cp01` | monthly | 441 | 1990-01-01 | 2026-09-01 |
| KOR | `food_cpi_yoy_oecd_cp01` | monthly | 441 | 1990-01-01 | 2026-09-01 |
| MYS | `food_cpi_index_adb_pcpi_cp01` | annual | 26 | 2000-01-01 | 2025-01-01 |
| MYS | `food_cpi_index_dosm_div01` | monthly | 561 | 1980-01-01 | 2026-09-01 |
| PHL | `food_cpi_index_adb_pcpi_cp01` | annual | 26 | 2000-01-01 | 2025-01-01 |
| THA | `food_cpi_index_adb_pcpi_cp01` | annual | 26 | 2000-01-01 | 2025-01-01 |
| VNM | `food_cpi_index_adb_pcpi_cp01` | annual | 26 | 2000-01-01 | 2025-01-01 |

**Rows total:** 1754

### By country (what continuous series we got)

| iso3 | Best continuous food CPI here |
|---|---|
| **IDN** | ADB annual `PCPI_CP_01_IX` 2000–2025 |
| **THA** | ADB annual `PCPI_CP_01_IX` 2000–2025 |
| **PHL** | ADB annual `PCPI_CP_01_IX` 2000–2025 |
| **VNM** | ADB annual `PCPI_CP_01_IX` 2000–2025 |
| **IND** | ADB annual 2013–2025 + OECD monthly index/YoY (shorter monthly window) |
| **KOR** | OECD monthly index + YoY 1990-01–2026-09 + ADB annual 2000–2025 |
| **MYS** | DOSM monthly division 01 1980-01–2026-09 + ADB annual 2000–2025 |

Cereals / bread subdivision (COICOP CP011) was **not** available on the OECD keys tried (`NoResultsFound`). ADB food series is CP01 (food & non-alcoholic beverages), not cereals-only.

## Columns

`iso3, series, series_label, frequency, year, month, date, value, unit, base_year, source, source_url, note, retrieval_date`

## Source URLs

- ADB KIDB DF_PRI: `https://kidb.adb.org/api` (dataflow `ADB,DF_PRI`, indicator `PCPI_CP_01_IX`; economy codes INO/PHI/VIE/MAL map to IDN/PHL/VNM/MYS)
- OECD SDMX: `DSD_PRICES@DF_PRICES_ALL` (index) and `DSD_PRICES@DF_PRICES_N_CP01` (YoY)
- DOSM: `https://api.data.gov.my/data-catalogue?id=cpi_headline` (division `01`)

## Blockers / gaps

- **IMF CPI SDMX** (`dataservices.imf.org`) TLS EOF / portal 404 from this box — not used.
- **National NSO bulk** (BPS/BOT/PSA/GSO/KOSIS) often Cloudflare/403 from cloud egress — not scraped.
- **Monthly food CPI** continuous for IDN/THA/PHL/VNM not obtained here (annual ADB only). MYS monthly via DOSM; KOR monthly via OECD.
- Indices are **not rebased to a common base**; `base_year` left as published when present. Do not splice ADB annual onto OECD monthly without documenting breaks.
- Season2 FAO country CPI lane intentionally **not** mirrored.

## Rules

No FX conversion. No gap-filling. Provenance on every row.
