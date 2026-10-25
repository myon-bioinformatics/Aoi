# adjacent_household_sku_levels — missing / blocked / deferred

Retrieved: 2026-10-25 Asia/Tokyo

## Already landed elsewhere (not duplicated into this #118 pack)

| ISO3 | Status |
|------|--------|
| JPN | **Aoi panel** — RPS everyday clothing/household + oil/sugar/coffee. Season2 does not re-emit into `adjacent_household_sku_levels`. |
| GBR | **Aoi panel** — ONS avg retail household/clothing. |
| USA | **Aoi panel** — BLS APU ground coffee only among everyday products; BLS average-price list is food/energy-heavy (no toilet paper/detergent APU secured). |

## Closed in this pack (vertical CSV)

SGP, MYS, IRL, QAT, FIN, AUT, NLD, FRA, **ARG**, **NZL** — see readme.

## SKU family gaps (relative to lane list)

| Family | In this pack | Notes |
|--------|--------------|-------|
| coffee / tea | SGP, MYS, IRL, QAT, FIN, AUT, NLD, FRA, ARG, NZL | Strongest family |
| soap / detergent | SGP, MYS, QAT, FIN, ARG (soap bars + shampoo; detergent API empty) | FIN is the dense EUZ detergent set |
| toilet paper | SGP, FIN | MYS no stable TP SKU in selected PriceCatcher codes; ARG TP not in Precios catalog hit |
| tissue / napkins | MYS (1 month Kleenex); FIN sanitary towels + kitchen towel | Sparse tissue; kitchen towel = paper towel SKU |
| towels (textile) | — | Bath/hand towels not in SGP/MYS/QAT/IRL/FIN/AUT/NLD/ARG/NZL tables; GBR/JPN in Aoi panels |
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
| ARE/BHR/KWT/OMN | Prior staple lane exhausted for open absolute retail bulk; not re-forced. |
| CAN/DNK/NOR/AUS/CHE | Prior TLS/CPI-only notes; Aoi `hi_staple_levels_alt` / dead-ends — no forced household dig. |
| TWN | NDC e-invoice path for food staples; 22933 household listing 404 this turn — not forced. |

## Probed densify turns (2026-10-25 Asia/Tokyo)

| ISO3 | Status |
|------|--------|
| FRA | **HIT** (earlier) — INSEE BDM ground coffee 250g (2 idbanks) monthly through 2019-12. |
| ARG | **HIT** — INDEC IPC-GBA Precios (Pesos) via datos.gob.ar: coffee_ground, shampoo, soap_bar_toilet_125g, soap_bar_laundry_pan (491 rows). Detergente líquido / lavandina / jabón en polvo IDs catalogued with claimed last_value but API returns 0 observations — not loaded / not gap-filled. |
| NZL | **HIT** — Stats NZ FPI selected prices via figure.nz table BbCZ4OW1Nk3LzCX5: instant coffee 100g, ground coffee 200g, tea bags 100, herbal tea bags 25 (820 rows). Food basket only — no detergent/TP. Takeaway cups skipped. |
| CAN | StatCan table **18-10-0245-01** right absolute path; **TLS EOF** — not forced. |
| KOR | 참가격 / data.go.kr — **TLS fail** — not forced. |
| DEU | Destatis Preismonitor is **% change vs 2020**, not LCU absolute. |
| SWE | SCB open tables are CPI **indices** only for coffee/tea/detergent/TP. |
| ESP | INE — no named absolute household SKU table; HBS *valor unitario* food only. |
| THA | MOC agricultural / CPI indexes; no open named household absolute bulk. |
| BEL | Statbel — no absolute named household table secured. |
| PRT | Observatório agroalimentar food-chain only; no detergent/TP absolute open bulk. |
| DNK/NOR/AUS/ITA/HKG/ZAF/IDN/PHL | Prior probes: CPI/index or food-only / TLS-403; no new absolute household SKU bulk. |
| Textile towels / underwear | Still absent outside Aoi JPN/GBR panels. |

**Densify note:** open paths remaining for BM ISO3 after ARG+NZL are thin; stop when further easy probes yield no absolute bulk.
