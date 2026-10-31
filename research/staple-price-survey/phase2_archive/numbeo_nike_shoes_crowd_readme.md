# Numbeo — Nike running shoes (crowd-sourced snapshot, numéraire candidate)

- **Panel:** `numbeo_nike_shoes_crowd_panel.csv`
- **What:** Country median USD prices for **Nike Running Shoes (Mid-Range)** (Numbeo itemId 64).
- **Source:** Focused extract from already-landed `numbeo_clothing_utilities_markets_crowd_panel.csv` (same public HTML snapshot).
- **URL:** https://www.numbeo.com/cost-of-living/country_price_rankings?itemId=64
- **Coverage:** 102 ISO3; snapshot 2026-10-25 (not a time series).
- **Cross-country dispersion (USD display):** n=102; median=94.560; **CV=0.2457**; **p90/p10=1.812**; min=39.160; max=172.440.
- **Why landed (focused):** Among Numbeo branded durables/apparel, Nike mid-range shoes show **low** cross-country dispersion — useful Big Mac–like companion (globally branded tradable good). Full clothing basket remains in the parent panel.
- **Caveats:** **CROWD-SOURCED**. Model mix ("mid-range") is contributor-defined. Historical bulk/API paywalled.
- **Lane:** Aoi Numbeo/COL; not Season2 NSO named-retail.
- **Retrieved:** 2026-10-25 (Asia/Tokyo box).
