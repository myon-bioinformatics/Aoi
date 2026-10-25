# adjacent_ilo — ILO food CPI (parallel to FAO B)

Retrieved: 2026-10-24 Asia/Tokyo

## Purpose

Parallel **Food and non-alcoholic beverages** CPI from ILOSTAT beside FAOSTAT `fao_cpi_food` (adjacent family B). Does **not** replace or delete FAO rows. Variable names are `ilo_cpi_*` so sources stay separable.

## Hard rules

- No foreign-exchange conversion.
- No unit/pack homogenization (units as published).
- No gap-filling / interpolation / invented values.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value` (estimated_value empty).

## Universe

56 ISO3 from `countries_iso3.txt` (includes EUZ).

## Source

- ILOSTAT SDMX dataflow `ILO:DF_CPI_XCPI_COI_RT(1.0)` — *CPI: National consumer price index, base year 2017 = 100 by COICOP*
- Measure: `CPI_XCPI_RT`
- COICOP class: `COI_COICOP_CP01` = Food and non-alcoholic beverages
- REST base: `https://sdmx.ilo.org/rest/data/ILO,DF_CPI_XCPI_COI_RT,1.0/{REF_AREA}.{FREQ}.CPI_XCPI_RT.COI_COICOP_CP01`
- Bulk `.csv.gz` / rplumber indicator files returned empty (0-byte) on 2026-10-24; SDMX CSV used instead.
- Raw batch extracts: `raw/batch_{M|A|Q}_*.csv` (+ DSD JSON).

## Variables

| variable | frequency | unit | notes |
|----------|-----------|------|-------|
| `ilo_cpi_food` | monthly | index 2017=100 | date = YYYY-MM-01 |
| `ilo_cpi_food_annual` | annual | index 2017=100 | date = YYYY-01-01 (calendar year as published) |

Quarterly SDMX pulls were downloaded into `raw/` for audit but **not** melted into the vertical file (redundant with monthly).

### Bread / cereals

ILO `CL_COI` for this dataflow is **1-digit COICOP only** (CP01…CP12 + general CP01T12). There is **no** bread-and-cereals (CP011) series. Documented in notes on every row and in `adjacent_ilo_missing.md`.

## Overlap with FAO B (`fao_cpi_food`)

| | FAO food CPI | ILO food CPI |
|--|--------------|--------------|
| Base year | 2015=100 | 2017=100 |
| Universe hit | 54 / 56 | 44 / 56 |
| FAO-miss (EUZ, TWN) | missing | **also missing** (ILO does not fill these holes) |
| Countries with both | 44 | 44 |
| FAO only (no ILO food) | ARE, CHN, GTM, IDN, JPN, PER, PHL, ROU, URY, VEN | — |
| ILO only (no FAO food) | — | none in this universe |

Row-level notes flag `overlap_fao_cpi_food=same_month` when a monthly ILO observation shares YYYY-MM with FAO B for that country.

Several ILO-miss countries still publish **general** CPI (`COI_COICOP_CP01T12`) in the same dataflow; those general series were **not** included (food-only brief).

## Coverage

- Rows: **17794**
- Countries with any ILO food row: **44 / 56**
- `ilo_cpi_food` (monthly): 16356
- `ilo_cpi_food_annual`: 1438

## Rebuild

```bash
python3 /workspace/staple-price-survey/adjacent_ilo/build_adjacent_ilo.py
```

Requires network for SDMX refetch (or reuse existing `raw/batch_*.csv`).

## Mirror

`/workspace/aoi-phase2/staple-price-survey/adjacent_ilo/`
