# adjacent_hi_staple_levels — absolute staple retail prices (HI Big Mac gaps)

Retrieved: 2026-10-25 Asia/Tokyo (hygiene sync at tip after e731537)

## Hard rules

- Absolute retail average prices in **local currency as published** (not CPI / HICP indices).
- No foreign-exchange conversion.
- No unit/pack homogenization (pack size kept in `variable` and/or `unit`).
- No gap-filling / interpolation.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value` (`estimated_value` empty).

## Lane scope (this pack)

**Active lane (this bot):** ARE, BHR, KWT, OMN, QAT, TWN, EUZ (+ keep HKG, MYS, NZL, SGP).

**Handed to Aoi** (`hi_staple_levels_alt`): AUS, CAN, CHE, DNK, NOR.

Original gap-16 universe still listed in `missing.md` for cross-lane tracking.

## Coverage (tip hygiene)

**Total rows: 3691** across **6** ISO3 (HKG, MYS, NZL, QAT, SGP, TWN).

| ISO3 | Rows | Series (examples) | Source | Span (approx.) |
|------|------|-------------------|--------|----------------|
| **HKG** | 190 | rice_long_grain_kg, rice_short_grain_kg | HK C&SD MDS Table 5.8 | ~2016–2026-04 |
| **MYS** | 230 | rice_10kg, wheat_flour_kg, potato_kg, bread_400g, maize_flour_400g | DOSM PriceCatcher monthly premise mean | 2022-01–2026-09 |
| **NZL** | 1512 | rice_kg, wheat_flour_1_5kg, potato_kg, bread_700g (to 2014-08), bread_600g_cheapest, wheatmeal_bread_700g, pasta_500g | Stats NZ FPI via figure.nz | ~2006–2026-06 |
| **SGP** | 1551 | rice_5kg, bread_400g, instant_noodles_5pack, lean_pork/ribeye/chicken chilled, fresh_milk_l, hen_eggs_10, cooking_oil_2kg, potato_kg, white_sugar_2kg | SingStat M213761 | 2015-01–2026-09 |
| **QAT** | 85 | bread/Lebanese bread, flours, rice 5kg, potato; + milk/eggs/sugar/corn oil/chicken/mutton densify | PSA/NPC annual average consumer prices | 2017–2023 annual |
| **TWN** | 123 | rice_3kg, wheat_flour_kg, white_toast_loaf, potato_catty | NDC e-invoice midpoints; Taipei potato 元/台斤 | ~2022–2025 |

**Active-lane exhausted/blocked (not forced):** ARE, BHR, KWT, OMN, EUZ (EUZ staples live in sibling `adjacent_euz_proxy_staple_levels`). See `missing.md`.

## Hygiene (2026-10-25 Asia/Tokyo)

- Schema header verified: `country,date,year,variable,value,unit,source,note,estimated_value`; all `estimated_value` empty; csv/gz row counts match.
- **NZL** `staple_price:bread_700g` key clash fixed: figure.nz had two white-loaf measures under one variable — **700 g weighted average** (99 months, 2006-06–2014-08) kept as `bread_700g`; **600 g cheapest-brand** (241 months) re-labelled `bread_600g_cheapest` (unit NZD per 600 g). No invented fills; no other ISO3 changed.
- No new country digs this hygiene pass.

## Files

- `adjacent_hi_staple_levels_vertical.csv` (+ `.gz`)
- `build_hi_staple_levels.py` / densify append scripts
- `raw/` — SingStat, DOSM, HK MDS, figure.nz white-bread extract, Qatar CSV, NDC/Taipei, probes
- `adjacent_hi_staple_levels_missing.md`

## Notes

- **MYS**: PriceCatcher premise-level monthly mean; not a CPI.
- **NZL**: figure.nz republishes Stats NZ selected monthly weighted average prices; pack sizes kept as published (700 g vs 600 g cheapest are distinct variables after hygiene).
- **SGP**: densify append added milk/eggs/meat/oil/sugar/potato/noodles on top of rice/bread.
- **QAT**: Annual QAR averages; densify s3 added milk/eggs/sugar/oil/chicken/mutton from already-downloaded NPC CSV.
- **TWN**: NDC e-invoice midpoint monthly; Taipei potato in 元 per 台斤. MOA RicepriceData TLS-blocked (not used).
