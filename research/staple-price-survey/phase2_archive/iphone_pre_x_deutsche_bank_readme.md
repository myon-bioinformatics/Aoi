# iPhone pre-X — Deutsche Bank Mapping the World's Prices

- **Panel:** `iphone_pre_x_deutsche_bank_panel.csv`
- **What:** Multi-country **USD** absolute prices for **iPhone 5s / 6 / 6s / 7** (pre-iPhone X window).
- **Rows / ISO3:** 106 / 35
- **Sources (easy open):**
  1. Deutsche Bank *The Random Walk: Mapping the World's Prices 2015* (FT Alphaville PDF) — Fig.12 iPhone 5s 16GB; Fig.13 iPhone 6 16GB; 20 countries; observation ≈ 2015-04-14.
  2. Deutsche Bank *Mapping the World's Prices 2017* as reprinted by PocketNow — iPhone 7 128GB; 33 countries; observation ≈ 2017-05. US figure includes NYC sales tax (source commentary).
  3. **iPhone 6s 128GB** derived from the same 2017 table's published **Relative to iPhone 6s** column: `usd_6s = usd_7 / (rel_to_6s)`. Not external/invented FX.
- **Dispersion (CV of USD across ISO3):** 5s ≈ 0.189; 6 ≈ 0.156; 6s ≈ 0.098; 7 ≈ 0.086.
- **SKIP:** iPhone 8 continuous multi-country table (no easy open CSV/reprint found); EveryMac HTML grind; archive.org Apple regional pages.
- **Raw:** `raw/apple_extend_2026-10-25/`
- **Also folded into:** `iphone_models_xcountry_panel.csv`
