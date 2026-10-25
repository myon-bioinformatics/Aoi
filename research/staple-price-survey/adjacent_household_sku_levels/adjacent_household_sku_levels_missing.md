# adjacent_household_sku_levels — missing / blocked / deferred

Retrieved: 2026-10-25 Asia/Tokyo

## Already landed elsewhere (not duplicated into this #118 pack)

| ISO3 | Status |
|------|--------|
| JPN | **Aoi panel** — RPS everyday clothing/household + oil/sugar/coffee. Season2 does not re-emit into `adjacent_household_sku_levels`. |
| GBR | **Aoi panel** — ONS avg retail household/clothing. |
| USA | **Aoi panel** — BLS APU ground coffee only among everyday products; BLS average-price list is food/energy-heavy (no toilet paper/detergent APU secured). |

## Closed in this pack (vertical CSV)

SGP, MYS, IRL, QAT, **FIN**, **AUT**, **NLD** — see readme.

## SKU family gaps (relative to lane list)

| Family | In this pack | Notes |
|--------|--------------|-------|
| coffee / tea | SGP, MYS, IRL, QAT, FIN, AUT, NLD | Strongest family |
| soap / detergent | SGP, MYS, QAT, FIN | FIN is the dense EUZ detergent set |
| toilet paper | SGP, FIN | MYS no stable TP SKU in selected PriceCatcher codes |
| tissue / napkins | MYS (1 month Kleenex); FIN sanitary towels + kitchen towel | Sparse tissue; kitchen towel = paper towel SKU |
| towels (textile) | — | Bath/hand towels not in SGP/MYS/QAT/IRL/FIN/AUT/NLD tables; GBR/JPN in Aoi panels |
| underwear | — | Not in these NSO tables; JPN/GBR gender SKUs in Aoi panels only |

## Probed / exhausted (no absolute household SKU bulk loaded)

| ISO3 | Status |
|------|--------|
| EUZ / Eurostat | Prior staple lane: no ongoing absolute retail product LCU table (`prc_fpmt_m` indices only). Not re-dug for household. |
| IRL (beyond tea) | CPM04/08/12 absolute national averages are food/drink-heavy; household cleaning/paper not in those item lists. CPM13 hits are COICOP **index** categories, not LCU levels. |
| AUT (beyond coffee/tea) | Preisradar `products.json` scanned: coffee beans/pads/instant + tea bags only among lane families (no TP/detergent/towel/underwear product IDs). |
| NLD (beyond coffee/tea) | CBS 80345eng is food-only (Beer…Tea); no detergent/TP. |
| FIN (post-2018) | StatFin Passiivi 011 average commodity prices end 2018; no continuous replacement table secured this turn. |
| HKG | MDS Table 5.8 path used for rice staples; no household named-retail extract. |
| NZL | Stats NZ open data gateway 502; figure.nz search 404; FPI selected prices historically food-focused — no household absolute secured. |
| ARE/BHR/KWT/OMN | Prior staple lane exhausted for open absolute retail bulk; not re-forced. |
| CAN/DNK/NOR/AUS/CHE | Prior TLS/CPI-only notes; Aoi `hi_staple_levels_alt` / dead-ends — no forced household dig. |
| TWN | NDC e-invoice path for food staples; 22933 household listing 404 this turn — not forced. |

## Intentionally not collected

- Numbeo / Starbucks / Coke / IKEA / UBS / USB/DRAM (Aoi lane)
- Broad CPI / HICP indices
- Rewrites of Big Mac, `adjacent_hi_staple_levels`, `adjacent_euz_proxy_staple_levels`, hours packs
- FX unify, unit unify, DIY hours, inventing estimates
