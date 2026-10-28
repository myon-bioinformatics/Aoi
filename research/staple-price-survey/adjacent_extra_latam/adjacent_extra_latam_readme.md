# adjacent_extra_latam — LatAm food CPI gap pack

Retrieved: 2026-10-24 Asia/Tokyo

## Scope

Close LatAm food CPI gaps left by `adjacent_extra/` for Big Mac universe countries:
**GTM, HND, NIC, PER, URY**.

Existing adjacent_extra already covered ARG, BRA, CHL, COL, CRI, MEX (not re-downloaded).

Also pulls bread/cereals and rice CPI where open NSO bulk publishes them.

## Hard rules

No FX conversion; no unit homogenization; no gap-filling.
Columns: `country,date,year,variable,value,unit,source,note,estimated_value`.
`estimated_value` is always `false`.

## Sources

| ISO3 | Agency | Coverage | Variables |
|------|--------|----------|-----------|
| GTM | INE Guatemala CKAN Empalme División + product DB | Div01 food monthly; product rice/pan/maíz/tortilla (2025–) | `cpi_food_nso`, `cpi_rice_nso`, `cpi_bread_nso`, `cpi_maize_nso`, `cpi_tortilla_nso` |
| HND | BCH IPC por división Base Dic.2025=100 | Food Div monthly 1991-01–2026-09 | `cpi_food_nso` |
| NIC | INIDE Cuadros IPC Jul-2026 (2-2-06) + BCN Serie_Indice INac | Food 2001–2026-07; pan/cereales + arroz Dec.2009–Jul.2019 | `cpi_food_nso`, `cpi_bread_cereals_nso`, `cpi_rice_nso` |
| PER | BCRP PN39445PM | Lima Metropolitana food & beverages Ene.1992–Sep.2026 | `cpi_food_nso` (**regional Lima**) |
| URY | INE IPC división País + Cuadro 2.0 detail | Div01 from 2010-12; 0111 + arroz from 2022-10 | `cpi_food_nso`, `cpi_bread_cereals_nso`, `cpi_rice_nso` |

## Gaps closed

Food CPI closed: GTM, HND, NIC, PER, URY
Still missing food: (none)

## Row counts

See `_build_stats.json` (n_rows=1842).

## Rebuild

```bash
python3 /workspace/staple-price-survey/adjacent_extra_latam/build_adjacent_extra_latam.py
```
