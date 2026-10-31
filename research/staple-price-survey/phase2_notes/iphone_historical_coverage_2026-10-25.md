# iPhone series — historical / multi-model x-country coverage

Date: **2026-10-25 Asia/Tokyo**. Easy open paths only.

## Panels landed

| File | Rows | ISO3 | Models | Observation span | USD |
|---|---:|---:|---|---|---|
| `iphone_models_xcountry_panel.csv` | **1195** | **44** | 5s–18 / Air / SE | 2013 … 2026-09-17 | mix (source or bundled FX) |
| `iphone_pre_x_deutsche_bank_panel.csv` | 106 | 35 | 5s, 6, 6s, 7 | 2015-04 / 2017-05 | yes (survey USD) |
| `iphone_se_paulcollas_aos_panel.csv` | 24 | 24 | SE (gen unlabeled) | ~2021–2022 | yes (bundled FX) |
| `iphone_15_burgerparity_panel.csv` *(rank 1)* | 30 | 30 | iPhone 15 | reference snapshot | yes |
| `iphone_14_zenodo_aos_2022_panel.csv` | 518 | 37 | 14 family | 2022-11-20 | yes via Zenodo FX |
| `iphone_current_models_burgerparity_aos_panel.csv` | 117 | 9 | 17, 18 Pro, Air | 2026-09-17 | **none** (local only) |
| `iphone_launch_msrp_5country_panel.csv` | 400 | 5 | X–16 families | launch 2017–2024 | USA rows only |

## Sources (pre-X extension, this pass)

1. **Deutsche Bank 2015** *Random Walk / Mapping the World's Prices* PDF (FT Alphaville CDN) — iPhone **5s** 16GB + **6** 16GB; 20 countries; USD published.
2. **Deutsche Bank 2017** via PocketNow reprint — iPhone **7** 128GB; 33 countries; USD published.
3. **iPhone 6s** — derived from the 2017 table's **Relative to iPhone 6s** column (`usd_7 / rel`). Same published table; not inventing FX.
4. **PaulCollas ApplePrices** — iPhone SE (generation unlabeled; likely 2nd/3rd) with bundled FX CSV.

## Coverage by generation (long panel)

| model_year | Models present | Main source(s) |
|---:|---|---|
| 2013 | iPhone 5s | DB 2015 survey |
| 2014 | iPhone 6 | DB 2015 survey |
| 2015 | iPhone 6s | DB 2017 derived |
| 2016 | iPhone 7 | DB 2017 survey |
| 2017 | iPhone X / 8 not in multi-country easy path | gist launch (X only) |
| 2018 | XR, XS, XS Max | gist launch |
| 2019 | 11 family | gist launch |
| 2020 | 12 family (+ SE unlabeled) | gist + PaulCollas SE |
| 2021 | 13 family | gist launch |
| 2022 | 14 family | Zenodo AOS + gist |
| 2023 | 15 family | Burger Parity + gist |
| 2024 | 16 family | gist launch |
| 2025 | iPhone 17 | Burger Parity AOS |
| 2026 | 18 Pro / Pro Max / Air | Burger Parity AOS |

## Dispersion (pre-X USD CV)

| Model | n ISO3 | CV |
|---|---:|---:|
| iPhone 5s (16GB) | 20 | 0.189 |
| iPhone 6 (16GB) | 20 | 0.156 |
| iPhone 6s (128GB, derived) | 33 | 0.098 |
| iPhone 7 (128GB) | 33 | **0.086** |
| iPhone SE (PaulCollas) | 24 | 0.079 |

iPhone 7 / 6s survey CVs are **tighter than** the iPhone 15 Burger Parity screen (~0.19) and competitive with Starbucks/Netflix ranks.

## SKIP / blocked

| Item | Why |
|---|---|
| iPhone 8 multi-country absolute | No easy open CSV/full reprint found this pass |
| Continuous weekly iPhone USD history | Login-gated |
| Burger Parity older product slugs | Only latest / iphone-15 style refs |
| Archive.org Apple regional pages | Forced dig; skipped |
| EveryMac global MSRP scrape | HTML multi-page grind; skipped |
| Invented FX | Policy |
| Netflix / Big Mac historical | **Season2** |
| World Price Index Apple API | Needs API key signup — not used |
| Mac mini in Zenodo package | Not present under `category=mac` |

## Raw files

`raw/numeraire_hist_2026-10-25/` — prior Zenodo / gist / Burger Parity.
`raw/apple_extend_2026-10-25/` — DB PDF + PocketNow HTML + PaulCollas CSVs + `build_summary.json`.
