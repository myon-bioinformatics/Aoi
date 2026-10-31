# MacBook Air + iMac 24 — PaulCollas ApplePrices scrape

- **Panel:** `mac_paulcollas_aos_panel.csv`
- **What:** Base **MacBook Air** and **24-inch iMac** listed prices for 24 countries (local currency).
- **Rows / ISO3:** 48 / 24
- **Source:** https://github.com/PaulCollas/apache-spark `ApplePrices.csv` (EFREI Spark coursework scrape of Apple country sites).
- **USD:** `CurrencyConversion.csv` bundled in the same repo (`Dollar_To_Curr_Ratio`).
- **Date:** not published; co-listed models (iPhone 12/13) imply ~2021–2022.
- **Dispersion (CV USD):** MacBook Air ≈ 0.092; iMac 24-inch ≈ 0.093 (tighter than Zenodo — smaller country set, fewer high-tax outliers).
- **Companion:** `iphone_se_paulcollas_aos_panel.csv` (iPhone SE, 24 ISO3, CV≈0.079) — generation not labeled (likely SE 2nd/3rd, not 2016 1st-gen); folded into long iPhone panel with that caveat.
- **Raw:** `raw/apple_extend_2026-10-25/`
