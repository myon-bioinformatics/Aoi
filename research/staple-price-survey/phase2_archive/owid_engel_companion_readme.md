# OWID Engel / Bennett companions (tidy vertical)

**Retrieved:** 2026-10-24 Asia/Tokyo · Aoi origin batch 2

## Files
| Panel | Variable | Coverage | Notes |
|---|---|---|---|
| `owid_staple_energy_share_panel.csv` | `owid_staple_energy_share_cereals_roots_tubers_pct` | **2001–2021**, 191 ISO3, 3709 rows | Non-null staple share ends **2021** (same as stub). Raw grapher has later years with GDP-only / NaN calorie share — not fabricated. |
| `owid_food_expenditure_share_panel.csv` | `owid_food_athome_share_consumer_expenditure_pct` | **2017–2023**, 104 ISO3, 727 rows | Full OWID entities; stub `engel_food_athome_share_pct` remains Big Mac–scoped subset. |

## Stub
`engel_global_ref_panel_stub.csv` **not rewritten** — no newer non-null staple years beyond 2021; food share already through 2023 in stub.

## Sources
- https://ourworldindata.org/grapher/share-of-energy-from-cereals-roots-and-tubers-vs-gdp-per-capita
- https://ourworldindata.org/grapher/share-of-consumer-expenditure-spent-on-food
Raw copies under `raw/engel_global_ref/`.
