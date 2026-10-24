# adjacent_hi_staple_levels — absolute staple retail prices (HI Big Mac gaps)

Retrieved: 2026-10-24 Asia/Tokyo

## Hard rules

- Absolute retail average prices in **local currency as published** (not CPI / HICP indices).
- No foreign-exchange conversion.
- No unit/pack homogenization (pack size kept in `variable` and/or `unit`).
- No gap-filling / interpolation.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value` (`estimated_value` empty).

## Gap universe (16)

ARE, AUS, BHR, CAN, CHE, DNK, EUZ, HKG, KWT, MYS, NOR, NZL, OMN, QAT, SGP, TWN  
(+ SWE probed; USA BLS and Japan rice already in main/Aoi — skipped).

## Coverage (gap-16 with ≥1 absolute staple series)

| ISO3 | Series | Source | Span (approx.) |
|------|--------|--------|----------------|
| **HKG** | `staple_price:rice_long_grain_kg`, `staple_price:rice_short_grain_kg` | HK C&SD Monthly Digest of Statistics Table 5.8 | annual + monthly through 2026-06 |
| **MYS** | rice_10kg, wheat_flour_kg, potato_kg, bread_400g, maize_flour_400g | DOSM PriceCatcher (monthly mean across premises) | 2022-01–2026-09 |
| **NZL** | rice_kg, wheat_flour_1_5kg, potato_kg, bread_700g, wheatmeal_bread_700g, pasta_500g | Stats NZ FPI weighted average retail (via figure.nz) | ~2006–2026 |
| **SGP** | rice_5kg, bread_400g | SingStat M213761 Average Retail Prices of Selected Items | 2015-01 onward |

**Hit: 4 / 16** (HKG, MYS, NZL, SGP). See `missing.md` for the other 12 and Eurostat.

## Files

- `adjacent_hi_staple_levels_vertical.csv` (+ `.gz`)
- `build_hi_staple_levels.py`
- `_build_stats.json`
- `raw/` — SingStat JSON, DOSM months + lookup (~3GB), HK MDS PDFs/txt, NZ figure.nz CSV, Eurostat probes
- Mirror: `/workspace/aoi-phase2/staple-price-survey/adjacent_hi_staple_levels/` (light raw; full DOSM only in primary path)

## Eurostat (attempted)

Open bulk for **absolute** retail food product prices was **not found**.  
`prc_fpmt_m` (Food Price Monitoring Tool) downloads successfully but units are only `I25` (index) / `RCH_*` (rates) for HICP/PPI/ACPI/IPI stages — **not LCU levels**.  
`prc_fsc_*` codes 404 on the SDMX API; HICP annual (`prc_hicp_aind`) is index/rates only.  
Agricultural absolute prices (`apri_ap`) are farm-gate, not retail — excluded (Aoi already has FAOSTAT producer prices).

## Notes on secured series

- **MYS**: PriceCatcher is premise-level; pack uses monthly **mean** of positive prices for fixed SKUs chosen by observation count (Faiza Emas rice 10 kg, Cap Sauh wheat flour 1 kg, China import potato 1 kg, Gardenia sandwich bread 400 g, maize flour 400 g). Not a CPI.
- **NZL**: figure.nz republishes Stats NZ “selected monthly weighted average prices”; values kept as NZD per published pack.
- **HKG**: rice only from Table 5.8 ($/kg); parser keeps the first YM block (rice) so later product blocks in the same extract cannot overwrite. Other food columns not extracted.
- **SGP**: Premium Thai Rice per 5 kg; Wholemeal Bread per 400 g.
