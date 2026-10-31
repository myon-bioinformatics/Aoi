# Eastern Europe / Big-Mac-gap national food CPI panel

Date: **2026-10-24 Asia/Tokyo**. Catalog tag: **Aoi origin batch SOFI/EastEU**.

| Field | Detail |
|---|---|
| Panel | `easteu_national_food_cpi_panel.csv` |
| Raw | `raw/easteu_cpi/` (DBnomics IMF JSON + OECD CP01 CSV) |
| Rows | **4382** |
| ISO3 | **BGR, CZE, HUN, POL, ROU, RUS, SRB, UKR** (HRV skipped — no length value-add vs HICP) |

## Why a separate file (vs `eurostat_hicp_food_panel.csv`)

Eurostat HICP CP011 already covers POL/CZE/HUN/ROU/BGR/HRV/SRB from the mid-1990s/2000s. This panel keeps **only series with clear value-add**:

| iso3 | series | start–end | Value-add vs HICP |
|---|---|---|---|
| **UKR** | IMF PCPIF_IX | 2005-01–2025-07 | **Missing from HICP** |
| **RUS** | IMF PCPIF_IX | 2004-01–2022-02 | **Missing from HICP** (stops 2022-02 on DBnomics) |
| **SRB** | IMF PCPIF_IX | 2007-01–2025-07 | Non-EU national parallel to HICP |
| **HUN** | IMF PCPIF + OECD CP01 | **1980-01**–2025 | Pre-HICP (HICP from 2000-12) |
| **CZE** | IMF PCPIF + OECD CP01 | **1994-01**–2025 | Pre-HICP (HICP from 1999-12) |
| **POL** | IMF PCPIF + OECD CP01 | **1995-01**–2025 | Pre-/parallel HICP (HICP from 1996-01) |
| **BGR** | IMF PCPIF + OECD CP01 | 1995-01–2025 | Parallel / slight pre-HICP |
| **ROU** | IMF **PCPIHAF_IX** (harmonized food) | 1996-01–2025-07 | National PCPIF_IX empty; HAF from 1996 vs HICP from 2000-12 |

**HRV**: HICP from 1998-01 and OECD CP01 from 1998-01 — **not included** (no clear pre-1996 / length gain).

## Columns

`iso3, series, series_label, frequency, year, month, date, value, unit, base_year, source, source_url, note, retrieval_date, value_add_vs_hicp`

## Sources

- IMF CPI food (`PCPIF_IX`) / Romania harmonized food (`PCPIHAF_IX`) via DBnomics:  
  `https://api.db.nomics.world/v22/series/IMF/CPI/M.{ISO2}.PCPIF_IX?observations=1`  
  (PL/CZ/HU/BG/RS/UA/RU; RO uses `PCPIHAF_IX`)
- OECD SDMX national monthly CP01:  
  `DSD_PRICES@DF_PRICES_ALL` for POL+CZE+HUN+BGR  
  `https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/POL+CZE+HUN+BGR.M.N.CPI.IX.CP01.N._Z?startPeriod=1970&format=csvfilewithlabels`

## Blockers / gaps

- **IMF SDMX** (`api.imf.org`) unreliable from this box historically → DBnomics mirror used (same pattern as Africa/MENA batch).
- **ROU IMF PCPIF_IX**: series exists but all observations `NA`; used **PCPIHAF_IX** instead.
- **ROU / SRB**: not in OECD CP01 pull (`NoRecordsFound` for ROU alone).
- **RUS**: ends **2022-02** on DBnomics; no post-2022 food CPI in this pull.
- **HRV**: intentionally omitted (no value-add vs existing HICP).
- Indices **not rebased**; do not splice IMF onto OECD/HICP without documenting breaks.
- Season2 FAO country CPI / high-income national CPI / LatAm / ILO lanes **not** mirrored.

## Rules

No FX. No gap-filling. Provenance + `value_add_vs_hicp` on every row. Companion HICP aggregate food panel remains `eurostat_hicp_food_panel.csv`.
