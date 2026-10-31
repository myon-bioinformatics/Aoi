# Mac (Air / Pro / iMac) — Zenodo Apple Online Store scrape (~2022-11)

- **Panel:** `mac_zenodo_aos_2022_panel.csv`
- **What:** Apple Online Store listed prices for **MacBook Air (M1/M2), MacBook Pro (13/14/16), iMac 24-inch** across ~36 ISO3. Color/SKU variants collapsed to median per country×model.
- **Rows / ISO3:** 216 / 36
- **Source:** Zenodo *Iphone-Ipad-Mac-Prices* (Poy & Tortosa 2022), CC-BY-4.0. DOI: https://doi.org/10.5281/zenodo.7344067
- **USD:** via `world_currencies.csv` bundled in the same Zenodo package (Numbeo FX scrape) — not invented outside source.
- **Date:** treated as **2022-11-20** (Zenodo publish 2022-11-21; same package as iPhone 14 scrape).
- **Dispersion (CV USD):** MacBook Air M1 ≈ 0.171; Air M2 ≈ 0.165; Pro 14 ≈ 0.173; iMac 24 ≈ 0.166.
- **Missing in this scrape:** Mac mini / Mac Studio rows were not present under `category=mac` in the Zenodo file.
- **Raw:** `raw/numeraire_hist_2026-10-25/zenodo_preus_mac_ipad_iphone.csv`
