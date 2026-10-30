# adjacent_ilo — missing / limits

Retrieved: 2026-10-24 Asia/Tokyo

## Universe gaps (no `ilo_cpi_food` / `ilo_cpi_food_annual`)

12 / 56 ISO3 have **no** ILO Food (CP01) index in `DF_CPI_XCPI_COI_RT`:

| ISO3 | Notes |
|------|-------|
| EUZ | Not in ILO `CL_AREA`. No euro-area aggregate food CPI in this dataflow (EU27 `X92` exists as a region code but was **not** mapped to EUZ). |
| TWN | In `CL_AREA` as Taiwan, China, but **no** CP01 and **no** general CP01T12 observations returned. |
| ARE, CHN, GTM, IDN, JPN, PER, PHL, ROU, URY, VEN | General CPI (CP01T12) often present; **Food CP01 absent** in SDMX for M/A/Q. FAO B still covers these ten. |

## FAO-miss fill-in result

Target holes from adjacent B: **EUZ, TWN**.

- ILO food CPI covers **0 / 2** of them.
- Conclusion: ILO is a useful **parallel** source (2017=100, often longer national history) but **not** a filler for the FAO EUZ/TWN gaps.

## Bread / cereals

Not published in ILO `CL_COI` for this dataflow (1-digit COICOP only). No `ilo_cpi_bread_cereals` variable.

## Intentionally not collected

- Asia emerging / Africa / MENA NSO CPI lanes (other agents)
- Japan e-Stat CPI / household survey lanes (Aoi)
- CoAHD, SOFI undernourishment/FIES, OWID, LatAm NSO, Pink Sheet, FFPI
- ILO general CPI (CP01T12), YoY/MoM % change measures (`CPI_NCYR_RT`, `CPI_NCPD_RT`), country weights
- FX conversion, rebasing to 2015, splicing FAO↔ILO, gap-fill

## Other limits

- Index base is **2017=100** as published; not rebased to FAO’s 2015=100.
- National source breaks / repository notes (often IMF) left in `note` (`SOURCE=…`, `NOTE_SOURCE=…`).
- Quarterly raw batches kept under `raw/` but omitted from vertical output.
