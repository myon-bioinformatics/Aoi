# Japan RPS — everyday clothing & household named SKUs

- **Panel:** `japan_rps_everyday_clothing_household_panel.csv`
- **What:** City-mean yen prices for named RPS SKUs: electricity, city gas, propane, water; towel; tissue; toilet paper; dish/laundry detergent; men's undershirt/briefs; bra; women's panties/T-shirt; socks; sanitary napkin; hand soap; shampoo; toothpaste; body soap.
- **Source:** e-Stat 小売物価統計調査（動向編）第１表 (prefectural capitals & cities ≥150k).
- **Raw handoff:** `/workspace/aoi-phase2/raw/specific_products_2026-10-25/japan_rps/` (multi-year `yYYYY_*.xlsx` / probe bins; 2017–2025 downloads; panel extracts 2020–2025).
- **Coverage:** JPN; monthly 2020–2025; 21 variables; 1482 rows.
- **Crowd-sourced:** No (official NSO).
- **Caveats:** SKU specs change over time (see `sku_spec`). 2017–2019 files on disk but older sheet layout not parsed. Propane missing some early years. **Further NSO named-retail household SKU collection stopped — Season2 #118 owns that lane.** Gendered SKUs are variables only (no gender analysis in this readme).
- **Retrieved:** 2026-10-25 (Asia/Tokyo).
