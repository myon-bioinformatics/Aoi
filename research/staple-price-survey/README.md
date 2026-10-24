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
| engel* | 556 |
| `household_consumption_total_lcu` | 1,344 |
| `population_total` | 1,404 |
| `bigmac_local_price` | 2,056 |
| **Total** | **66,517** |

### Coverage (of 56 Big Mac countries)

- Staples (A): 40 countries (WFP/FPMA + USA BLS + Japan e-Stat)
- Engel (B): 53 (USDA ERS 2021–2025; Japan included; food includes nonalcoholic beverages; at-home). Longer Japan household-survey series kept as a separate variable (`engel_share_food_national_hh_survey`, 2000–2025; 2024–2025 come from the Statistics Bureau annual summaries, see [`staple_survey_readme.md`](staple_survey_readme.md)).
- Household LCU / population (C): 54 each (World Bank `NE.CON.PRVT.CN`, `SP.POP.TOTL`)

High-income staples often missing from WFP/FPMA: ARE, AUS, BHR, CAN, CHE, DNK, EUZ, HKG, KWT, MYS, NOR, NZL, OMN, QAT, SGP, TWN. See [`staple_survey_missing.md`](staple_survey_missing.md).

## Adjacent HI staple price levels

See [`adjacent_hi_staple_levels/`](adjacent_hi_staple_levels/) for absolute NSO retail staple prices (HKG/MYS/NZL/SGP). CPI indices are elsewhere; Eurostat had no absolute LCU food-product bulk.

## Adjacent extra LatAm CPI fill

See [`adjacent_extra_latam/`](adjacent_extra_latam/) for GTM/HND/NIC/PER/URY national (or Lima) food CPI and bread/rice components where published.

## Adjacent ILO food CPI

See [`adjacent_ilo/`](adjacent_ilo/) for ILOSTAT food CPI (2017=100) as a parallel source to FAO food CPI. Does not close EUZ/TWN gaps.

## Adjacent A–F fill-in

See [`adjacent/`](adjacent/) for ICP food/bread-cereals PLI & shares, FAO food CPI, Japan income-quintile Engel, FAO FBSH historical Bennett, PIP poverty/welfare reference, and OECD/Eurostat longer food-share series.

## Adjacent extra (national food CPI)

See [`adjacent_extra/`](adjacent_extra/) for national food / bread-cereals CPI covering high-income Big Mac gap countries and selected LatAm NSOs (Japan CPI is maintained on the Aoi phase2 Japan lane, not here).

## Reinforcement (Engel-adjacent reference)

See [`reinforcement/`](reinforcement/) for Bennett starchy-staple calorie shares, Working–Leser materials (quintile food shares / published income elasticities), and Orshansky-type poverty multipliers kept as a separate normative reference. Do not mix Orshansky into Engel E.

## Row key

In `staple_survey_vertical.csv`, `country + date + variable + source` is **not** unique: FPMA/WFP rows that differ only in market or price type share it (4,030 such keys). `unit` and `note` carry that difference, so identify a row by `country, date, variable, source, unit, note`. Do not drop "duplicates" on the shorter key.

## Rules for downstream use

This folder is **data only**. Do not splice USDA Engel with Japan national Engel without documenting the definition break. Do not convert currencies or pack sizes when forming \(b\).

Path note: files live under `research/staple-price-survey/` (not `data/`), because the repository `.gitignore` ignores `data/`.

### Update 2026-10-24 (Asia/Tokyo) — QAT + TWN absolute levels

- Pack `adjacent_hi_staple_levels` now includes **QAT** (NPC/data.gov.qa annual averages, 2017–2023) and **TWN** (NDC e-invoice midpoints + Taipei potato).
- Still in pack: HKG, MYS, NZL, SGP. Active-lane exhausted/blocked: ARE, BHR, KWT, OMN, EUZ.
- AUS/CAN/CHE/DNK/NOR remain on Aoi `hi_staple_levels_alt` (do not double-take).

### Update 2026-10-24 (Asia/Tokyo) — EUZ-proxy absolute staple levels

- New pack `adjacent_euz_proxy_staple_levels`: national absolute retail/unit-value staples as **country ISO3 proxies** for the euro-area (EUZ) Big Mac gap (no fake EUZ aggregate).
- Hits: **FRA** (INSEE prix moyens), **IRL** (CSO NAP), **NLD** (CBS), **ESP** (INE valor unitario) — 4601 rows, ~1992–2026-09.
- Exhausted this turn for open absolute bulk: DEU, ITA, SWE deepen, BEL/AUT; FIN/PRT not pursued beyond priority.
