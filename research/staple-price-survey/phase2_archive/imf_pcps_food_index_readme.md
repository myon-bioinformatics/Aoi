# IMF Primary Commodity Prices — Food index (via FRED)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin batch 2

## What
IMF **PCPS** global food commodity price index (`PFOOD`), monthly, index **2016 = 100**.  
Downloaded via FRED series **PFOODINDEXM** (IMF is the source).

Distinct from FAO FFPI (different basket/base) and from Season2 country CPI.

## Files
- Panel: `imf_pcps_food_index_panel.csv`
- Raw: `raw/imf_pcps/PFOODINDEXM_fred.csv`
- FRED: https://fred.stlouisfed.org/series/PFOODINDEXM
- IMF PCPS: https://data.imf.org/en/datasets/IMF.RES:PCPS

## Coverage
- Geography: WORLD (`iso3=WLD`)
- Span: **1992-01 – 2026-09** (417 months)
- Variable: `imf_pcps_food_index_2016eq100`
- No FX.

## Scout leftovers
Direct IMF ExternalData / SDMX CSV from this box hit TLS/403 timeouts; FRED mirror used. Cereal-only IMF sub-index not pulled this round.
