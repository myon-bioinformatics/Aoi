# adjacent_subscription_engel_shares

This pack holds Engel-like subscription and AV-content spending data: household spending levels and their share of total spending or income. It also includes the share of internet users who pay for a subscription. It sits next to the `adjacent_*_levels` subscription price packs.

- **Schema (vertical):** `country,date,year,variable,value,unit,source,note,estimated_value`. `date` is the year-end placeholder `YYYY-12-31`.
- **Values are kept as published:** USD, PPS, JPY or CAD, or percent. No FX conversion is applied, and `estimated_value` is always empty.
- **Build:** `python3 build_subscription_engel_shares.py`. It uses only the standard library, reads the tidy panels in `raw/`, and writes `*_vertical.csv`, `*_vertical.csv.gz` (gzip mtime=0) and `_build_stats.json`.

## Sources
| prefix | source | coverage |
|---|---|---|
| `bls_ce:` | US BLS Consumer Expenditure Survey: Table 2500 detailed means for 2024, and the CXU API series for 1984–2024 | USA |
| `eurostat_hbs:` | Eurostat `cult_pcs_hbs` (HBS) CP09423_09424: licence fees, subscriptions and hire | EU, 2010/2015/2020 |
| `eurostat_nama:` | Eurostat `nama_10_co3_p3` CP094 and CP09 as a percent of HFCE | Europe, 2006– |
| `eurostat_isoc:` | Eurostat `isoc_ec_ibgs`: share paying for streaming (**prevalence, not spending**) | EU, 2024–2025 |
| `mic_joukyou:` | Japan MIC 家計消費状況調査 2024 概況: digital content bought through internet shopping | JPN, 2023–2024 |
| `statcan:` | Statistics Canada Plus (2025-07-02): cable/satellite/streaming aggregate | CAN, in CAD billions |

## Headline figures
- USA 2024: rental, streaming and downloading of videos is $185.02 per consumer unit per year, about 0.24% of spending. Adding audio gives about 0.28%.
- EU27 2020: fees and subscriptions are about 0.57% of total consumption.
- CP094 is about 3% of HFCE, but it is a much broader category.
- EU 2025: 32.7% of internet users pay for video streaming and 23.0% pay for music.
- JPN 2024: downloaded music, video and apps come to ¥269 per month for households of two or more.

`raw/headline_subscription_engel_snapshot.csv` mixes units and is kept for reference only. The phase-2 note is in `raw/subscription_engel_shares_2026-10-26.md`.
