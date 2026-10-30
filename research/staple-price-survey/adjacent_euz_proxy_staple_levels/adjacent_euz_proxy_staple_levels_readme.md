# adjacent_euz_proxy_staple_levels — EA NSO absolute staple retail (EUZ gap proxies)

Retrieved: 2026-10-25 Asia/Tokyo (hygiene sync at tip after e731537)

Sibling pack to `adjacent_hi_staple_levels`. These are **national** absolute average retail / unit-value staple prices used as **country ISO3 proxies for the euro-area (EUZ) Big Mac gap**. There is **no fake EUZ aggregate row**.

## Hard rules

- Absolute prices in **local currency as published** (EUR / historical IEP for Ireland CPM08).
- No FX conversion; no unit/pack homogenization; no gap-fill.
- Vertical schema: `country,date,year,variable,value,unit,source,note,estimated_value` (`estimated_value` empty).
- Every EA-country `note` states the series is a **national proxy for the EUZ gap**, not a euro-area aggregate.
- Never HICP/CPI indices; never PPP/PLI.

## Coverage (tip hygiene)

**Total rows: 14911** across **8** ISO3 proxies (AUT, DEU, ESP, FIN, FRA, IRL, NLD, PRT).

| ISO3 | Rows | Series (examples) | Source | Span (approx.) |
|------|------|-------------------|--------|----------------|
| **FRA** | 4769 | baguette/parisian bread, potato ware/new, pasta; + milk/butter/oils/sugar/chicken/pork/beef rumsteak | INSEE BDM Prix moyens (SDMX) | ~1992–2026-09 (some stopped) |
| **IRL** | 4565 | bread/flour/potato/spaghetti; + milk/eggs/butter/sugar/beef/pork/chicken (CPM12) | CSO PxStat CPM08/CPM04/CPM12 NAP | 1997–2026-09 |
| **FIN** | 3615 | rice/flour/breads/pasta/potato; + milk/eggs/butter/oil/sugar/beef/pork/chicken | StatFin Passiivi **011** | 2002–2018 |
| **AUT** | 675 | rice/flour/breads/pasta/potato; + milk/eggs/butter/olive oil/sugar/pork/beef | Statistik Austria Preisradar meanData | 2023-01–2026-09 |
| **PRT** | 606 | rice avg/carolino, wheat flour, spaghetti, potato, bread bolas carcaça (unit) | Observatório de Preços Consumo | ~2019–2026 4-week |
| **ESP** | 328 | rice/bread/flour/pasta/potato; + milk/eggs/butter/oils/sugar/beef/pork/poultry (HBS unit values) | INE jaxiT3 **25169** + **73844** | 2006–2025 |
| **NLD** | 246 | bread/rice/potato; + milk/eggs/butter/cheese/margarine/pork/stewing steak/sugar | CBS 80345eng + maatwerk potato | 1999–2018; potato to 2025 |
| **DEU** | 107 | rye/wheat/multigrain/wholemeal breads, wheat flour 405, potato (LEH) | BMEL-Statistik 5050850 + 5051000 | 2000; 2009–2024 |

## Exhaustion (easy densify STOP)

- **PRT / DEU**: no easy milk/eggs/meat/oil/sugar beyond cereal/potato already loaded (Observatório ajax; BMEL open 505 tables).
- **ITA / SWE / BEL**: still CPI/HICP-only — not forced.
- World Bank ICP public = PPP/PLI/expenditure only (sibling `adjacent_icp_food_prices/`).
- See `missing.md`.

## Hygiene (2026-10-25 Asia/Tokyo)

- Schema header verified; all `estimated_value` empty; csv/gz match; **0** duplicate `(country,date,variable)` keys.
- Coverage table row counts synced to tip (prior readme still showed pre-densify totals).
- No new country digs; no Aoi JPN/UK towel re-panel.

## Notes

- **FRA**: Metropolitan France average consumer prices; annual series as `*_annual` so they do not overwrite monthly. Stopped milk/butter/oil/sugar series retained as published absolute history.
- **IRL**: CPM08 IEP through 2001-11; CPM04/CPM12 EUR.
- **ESP**: *Valor unitario* = EPF expenditure/quantity — absolute EUR, **not** a CPI store quote.
- **FIN**: Passiivi 011 ends 2018; current StatFin `khi` is index/fuel-only for food.
- **PRT**: Consumo stage absolute EUR; bread is EUR per unit as published.
- **AUT**: Preisradar scanner *Durchschnittspreise* (mean); index companions in JSON not loaded.
- **Out of scope**: Aoi lanes; CAN/KOR TLS retries; BEL redo; household SKUs (sibling pack).

## Files

- `adjacent_euz_proxy_staple_levels_vertical.csv` (+ `.gz`)
- `build_euz_proxy_staple_levels.py` / densify append scripts (`append_staple_food_densify_s2.py`, `append_staple_food_densify_s3.py`)
- `raw/insee/`, `raw/cso/`, `raw/cbs/`, `raw/ine/`, `raw/statfin/`, `raw/ine_pt/`, `raw/statistik_at/`, probes
- `adjacent_euz_proxy_staple_levels_missing.md`
