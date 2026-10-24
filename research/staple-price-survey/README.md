# Staple price survey（青いプロジェクト第2弾）

Retrieved: **2026-10-24 Asia/Tokyo**

International staple prices, food-expenditure shares (Engel), and household consumption in local currency, aligned to Big Mac countries for analyses that treat staple cost as a Big Mac multiple \(b\) (local currency only; no FX).

## Files

| File | Role |
|------|------|
| [`staple_survey_vertical.csv`](staple_survey_vertical.csv) (~26 MB) | Full vertical panel (UTF-8) |
| [`staple_survey_vertical.csv.gz`](staple_survey_vertical.csv.gz) | Same, gzip |
| [`staple_survey_B_C_bigmac.csv`](staple_survey_B_C_bigmac.csv) | Engel + household consumption + population + Big Mac only |
| [`bigmac_vertical.csv`](bigmac_vertical.csv) | Country universe (user-supplied Big Mac prices) |
| [`countries_iso3.txt`](countries_iso3.txt) | 56 ISO3 codes (includes `EUZ`) |
| [`staple_survey_readme.md`](staple_survey_readme.md) | Provenance detail |
| [`staple_survey_missing.md`](staple_survey_missing.md) | Gaps and reasons |

## Schema

`country,date,year,variable,value,unit,source,note[,estimated_value]`

- `country`: ISO3 (same as `bigmac_vertical.csv`)
- `year`: join key
- **No FX conversion. No unit homogenization. No gap-filling.** Estimates would go only in `estimated_value` (empty in this build).

### Variable families (row counts)

| Family | Rows |
|--------|------|
| `staple_price:*` | 61,157 |
| engel* | 554 |
| `household_consumption_total_lcu` | 1,344 |
| `population_total` | 1,404 |
| `bigmac_local_price` | 2,056 |
| **Total** | **66,515** |

### Coverage (of 56 Big Mac countries)

- Staples (A): 40 countries (WFP/FPMA + USA BLS + Japan e-Stat)
- Engel (B): 53 (USDA ERS 2021–2025; Japan included; food includes nonalcoholic beverages; at-home). Longer Japan household-survey series kept as a separate variable.
- Household LCU / population (C): 54 each (World Bank `NE.CON.PRVT.CN`, `SP.POP.TOTL`)

High-income staples often missing from WFP/FPMA: ARE, AUS, BHR, CAN, CHE, DNK, EUZ, HKG, KWT, MYS, NOR, NZL, OMN, QAT, SGP, TWN. See [`staple_survey_missing.md`](staple_survey_missing.md).

## Rules for downstream use

This folder is **data only**. Do not splice USDA Engel with Japan national Engel without documenting the definition break. Do not convert currencies or pack sizes when forming \(b\).

Path note: files live under `research/staple-price-survey/` (not `data/`), because the repository `.gitignore` ignores `data/`.
