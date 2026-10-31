# Africa / MENA national food CPI panel (Aoi origin batch Africa/MENA)

Date: **2026-10-24 Asia/Tokyo**. Vertical tidy panel. **No FX. No fabricated fills. No rebase.**

File: `/workspace/aoi-phase2/africa_mena_national_food_cpi_panel.csv`  
Raw: `/workspace/aoi-phase2/raw/africa_mena_cpi/`

## Scope

Target staple / Big-Mac–relevant Africa & MENA (non–Season2 high-income list):  
**EGY, ZAF, NGA, KEN, MAR, TUN, TUR, ISR, SAU** (ARE/BHR skipped).

Season2 owns FAO country food/cereals CPI bulk and high-income national CPI — this panel uses **IMF CPI food component (PCPIF_IX) via DBnomics** and **OECD national CP01** where IMF food levels are empty. Not a FAO CPI duplicate.

## Coverage (this pull)

| iso3 | series | freq | n | start | end |
|---|---|---|---:|---|---|
| EGY | `food_cpi_index_imf_pcpif` | monthly | 186 | 2010-01-01 | 2025-06-01 |
| ZAF | `food_cpi_index_oecd_cp01` | monthly | 660 | 1970-01-01 | 2024-12-01 |
| NGA | `food_cpi_index_imf_pcpif` | monthly | 240 | 2005-01-01 | 2024-12-01 |
| KEN | `food_cpi_index_imf_pcpif` | monthly | 192 | 2009-02-01 | 2025-01-01 |
| MAR | `food_cpi_index_imf_pcpif` | monthly | 222 | 2007-01-01 | 2025-06-01 |
| TUN | `food_cpi_index_imf_pcpif` | monthly | 247 | 2005-01-01 | 2025-07-01 |
| TUR | `food_cpi_index_imf_pcpif` | monthly | 751 | 1963-01-01 | 2025-07-01 |
| TUR | `food_cpi_index_oecd_cp01` | monthly | 672 | 1970-01-01 | 2025-12-01 |
| ISR | `food_cpi_index_imf_pcpif` | monthly | 667 | 1970-01-01 | 2025-07-01 |
| ISR | `food_cpi_index_oecd_cp01` | monthly | 681 | 1970-01-01 | 2026-09-01 |
| SAU | `food_cpi_index_imf_pcpif` | monthly | 174 | 2011-01-01 | 2025-06-01 |
| SAU | `food_cpi_index_oecd_cp01` | monthly | 175 | 2011-01-01 | 2025-07-01 |

**Rows total:** 4867

### By country (primary continuous series)

| iso3 | Best continuous food CPI here |
|---|---|
| **EGY** | IMF PCPIF_IX monthly 2010-01–2025-06 |
| **ZAF** | OECD CP01 monthly 1970-01–2024-12 (IMF PCPIF_IX on DBnomics is all `NA`) |
| **NGA** | IMF PCPIF_IX monthly 2005-01–2024-12 |
| **KEN** | IMF PCPIF_IX monthly 2009-02–2025-01 |
| **MAR** | IMF PCPIF_IX monthly 2007-01–2025-06 |
| **TUN** | IMF PCPIF_IX monthly 2005-01–2025-07 |
| **TUR** | IMF PCPIF_IX (long) + OECD CP01 parallel |
| **ISR** | IMF PCPIF_IX + OECD CP01 (OECD extends to 2026-09) |
| **SAU** | IMF PCPIF_IX + OECD CP01 |

## Columns

`iso3, series, series_label, frequency, year, month, date, value, unit, base_year, source, source_url, note, retrieval_date`

## Source URLs

- IMF CPI (food = `PCPIF_IX`) via DBnomics: `https://api.db.nomics.world/v22/series/IMF/CPI/M.{ISO2}.PCPIF_IX?observations=1`  
  (ISO2: EG/ZA/NG/KE/MA/TN/TR/IL/SA). Upstream: IMF.STA CPI dataset.
- OECD SDMX: `DSD_PRICES@DF_PRICES_ALL` national monthly CP01 index for TUR+ISR+ZAF+SAU  
  `https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/TUR+ISR+ZAF+SAU.M.N.CPI.IX.CP01.N._Z?startPeriod=1970&format=csvfilewithlabels`

## Blockers / gaps

- **IMF SDMX API** (`api.imf.org`) returned **503** from this box — used DBnomics mirror instead.
- **IMF ZAF PCPIF_IX**: series present but all observation values `NA` on DBnomics (indexed 2025-08-31); ZAF filled from OECD CP01.
- **National NSO bulk** (Stats SA zip redirect loop; CAPMAS/CBE/NBS/KNBS/HCP page-by-page) not scraped this pass.
- **ILOSTAT** bulk `CPI_NCPI_COI_IN` URL **404**.
- Indices **not rebased** to a common base; do not splice IMF onto OECD without documenting breaks.
- Season2 FAO country CPI lane intentionally **not** mirrored.

## Companion

Eurostat HICP food (CP011) long panel (EU + TR etc., distinct from eating-out CP11 shares):  
`eurostat_hicp_food_panel.csv` + `eurostat_hicp_food_readme.md`

## Rules

No FX conversion. No gap-filling. Provenance on every row. Catalog tag: **Aoi origin batch Africa/MENA**.
