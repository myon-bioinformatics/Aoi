# iPhone models — multi-country long panel (historical + current)

- **Panel:** `iphone_models_xcountry_panel.csv`
- **What:** Long rows of iPhone **model × storage × country** absolute prices from easy open sources (launch MSRP, Apple Online Store scrapes, Burger Parity reference, Deutsche Bank price surveys).
- **Coverage (2026-10-25 update):** **1195** rows; **44 ISO3**; models **iPhone 5s → 18 Pro / Air** (plus SE); years **2013–2026**.
- **Pre-X addition:** Deutsche Bank 2015/2017 surveys (5s/6/6s/7) + PaulCollas SE — see `iphone_pre_x_deutsche_bank_panel.csv` and notes.
- **USD policy:** only when source publishes USD or bundles FX in the same package; otherwise `usd_price` null.
