# adjacent_household_sku_levels — missing / blocked / deferred

Retrieved: 2026-10-25 Asia/Tokyo

## Already landed elsewhere (not duplicated into this #118 pack)

| ISO3 | Status |
|------|--------|
| JPN | **Aoi panel** — RPS everyday clothing/household + oil/sugar/coffee. Season2 does not re-emit into `adjacent_household_sku_levels`. |
| GBR | **Aoi panel** — ONS avg retail household/clothing. |
| USA | **Aoi panel** — BLS APU ground coffee only among everyday products; BLS average-price list is food/energy-heavy (no toilet paper/detergent APU secured). |

## Closed this turn (in vertical CSV)

SGP, MYS, IRL, QAT — see readme.

## SKU family gaps (relative to lane list)

| Family | In this pack | Notes |
|--------|--------------|-------|
| coffee / tea | SGP, MYS, IRL, QAT | Strongest family here |
| soap / detergent | SGP, MYS, QAT | |
| toilet paper | SGP | MYS no stable toilet-paper SKU in selected PriceCatcher codes |
| tissue / napkins | MYS (1 month Kleenex only) | Sparse; JPN/GBR covered in Aoi panels |
| towels | — | Not in SGP M213761 / MYS selection / QAT / IRL CPM; GBR/JPN in Aoi panels |
| underwear | — | Not in these NSO tables; JPN/GBR gender SKUs in Aoi panels only |

## Probed / exhausted (no absolute household SKU bulk loaded)

| ISO3 | Status |
|------|--------|
| EUZ / Eurostat | Prior staple lane: no ongoing absolute retail product LCU table (`prc_fpmt_m` indices only). Not re-dug for household. |
| IRL (beyond tea) | CPM04/08/12 absolute national averages are food/drink-heavy; household cleaning/paper not in those item lists. CPM13 hits are COICOP **index** categories, not LCU levels. |
| HKG | MDS Table 5.8 path used for rice staples; no household named-retail extract this turn. |
| NZL | Stats NZ / figure.nz household absolute not secured this turn (API key / search empty); FPI selected prices historically food-focused. |
| ARE/BHR/KWT/OMN | Prior staple lane exhausted for open absolute retail bulk; not re-forced. |
| CAN/DNK/NOR/AUS/CHE | Prior TLS/CPI-only notes; Aoi `hi_staple_levels_alt` / dead-ends — no forced household dig. |
| TWN | NDC e-invoice used for food staples; household SKUs not pulled this turn. |

## Intentionally not collected

- Numbeo / Starbucks / Coke / IKEA / UBS / USB/DRAM (Aoi lane)
- Broad CPI / HICP indices
- Rewrites of Big Mac, `adjacent_hi_staple_levels`, `adjacent_euz_proxy_staple_levels`, hours packs
- FX unify, unit unify, DIY hours, inventing estimates

## Raw packaging

- IRL: `raw/cso/irl_tea_bags.csv` extract only (full CPM12 JSON-stat not vendored).
- MYS: monthly means only (full PriceCatcher month CSVs not vendored).
