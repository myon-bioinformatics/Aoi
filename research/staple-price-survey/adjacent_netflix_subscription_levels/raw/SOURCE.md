# Raw provenance — Netflix subscription levels

## 1. tompec/netflix-prices (2023-01-07 … 2026-09-28)

- Upstream: https://github.com/tompec/netflix-prices
- Clone commit: `efa54e3700976d2821d5f9379df0c9deedb4a5d0` (2026-09-28)
- Box path: `/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/tompec-netflix-prices`
- Snapshots: 30 dated JSON under `data/`; `latest.json` ignored.
- License: Creative Commons Attribution 4.0.

## 2. fromabroad.org (2020-03-10)

- Article: https://fromabroad.org/netflix/a-study-on-the-netflix-price-differences-between-countries-and-how-to-get-netflix-70-cheaper/
- Dated: 2020-03-10 (COVID-era demand start).
- Curated extract in-pack: `fromabroad_2020-03-10_lcu_curated.csv` (20 ISO3, unambiguous native LCU only).
- Box HTML archive: `/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/netflix_pre2023/fromabroad_2020-03-10.html`
- Skipped: TR/EG EUR-mislabeled, EC ARS-mislabeled, TH incomplete, euro-area (BM→EUZ).

## 3. Comparitech Dec-2021 via Kaggle apoorvgupta25 (2021-12-28)

- Dataset: https://www.kaggle.com/datasets/apoorvgupta25/netflix-prices
- In-pack: `apoorvgupta25_Netflix_Prices_Dec2021.csv`
- Box zip: `/workspace/aoi-phase2/raw/numeraire_hist_2026-10-25/netflix_pre2023/apoorvgupta25_netflix-prices.zip`
- Rows kept: 171 / 54 ISO3 (currency matched to tompec billing currency; RUS/RUB added).
- USD-only prasertk Dec-2021 mirror **not** used (no FX lane).

## Not used / left alone

- Aoi `netflix_standard_burgerparity_panel.csv` / `prices_all.csv` — snapshot only.
- iPhone CSVs in numeraire_hist — leave alone.
- 2022: no easy open full LCU cross-section found.
- Pre-2020: out of owner scope (~2020+).
