# Numéraire core set (ranks 1–5)

Date: **2026-10-25 Asia/Tokyo**. User chose the small usable set from
`notes/stable_xcountry_durables_2026-10-25.md` ranks **1–5**.

| Rank | Series | Owner | Panel path | Rows | ISO3 | Span / kind |
|---:|---|---|---|---:|---:|---|
| 1 | iPhone 15 (Burger Parity) | Aoi | `iphone_15_burgerparity_panel.csv` | 30 | 30 | single reference snapshot |
| 2 | Starbucks Tall Latte (Burger Parity) | Aoi | `starbucks_latte_burgerparity_panel.csv` | 30 | 30 | single reference snapshot |
| 3 | Netflix standard (Burger Parity) | Aoi (snapshot) | `netflix_standard_burgerparity_panel.csv` | 30 | 30 | single reference snapshot |
| 4 | Big Mac | **Season2** | *(not duplicated here)* | — | — | Season2 absolute / densify lane |
| 5 | Numbeo Nike mid-range shoes | Aoi | `numbeo_nike_shoes_crowd_panel.csv` | 102 | 102 | crowd snapshot 2026-10-25 |

## Confirmed on disk (1, 2, 3, 5)

All four Aoi panels exist under `/workspace/aoi-phase2/` with matching `*_readme.md`.

## Rank 4 — Season2

Big Mac absolute packs / densify remain **Season2-owned**. Aoi must not fetch or
duplicate Big Mac panels.

## Historical extensions (this pass)

### iPhone series (Aoi)

Long multi-model panel + companions (see `notes/iphone_historical_coverage_2026-10-25.md`):

| Panel | What |
|---|---|
| `iphone_models_xcountry_panel.csv` | **Long** union: iPhone X–18 / Air; 42 ISO3; launch + AOS + reference |
| `iphone_14_zenodo_aos_2022_panel.csv` | Apple Online Store scrape ~2022-11 (Zenodo CC-BY-4.0); USD via bundled FX |
| `iphone_current_models_burgerparity_aos_panel.csv` | 2026-09-17 Apple Store listed (17 / 18 Pro / Air); **local only** (no USD in source) |
| `iphone_launch_msrp_5country_panel.csv` | Launch MSRP iPhone X–16 for PAK/IND/CHN/USA/ARE |

Existing rank-1 snapshot `iphone_15_burgerparity_panel.csv` kept as the canonical 1×30 numéraire cross-section.

### Netflix plans historical

**Season2 owns** Netflix plan historical backfill (Basic / Standard / Premium over time).
Aoi keeps only the rank-3 **standard** Burger Parity snapshot; no new Netflix historical
panels in this pass.

## Policy reminders

- No invented FX (USD only when source publishes USD or bundles FX in the same package).
- Crowd / archive / reference labeled in panel `notes` and readmes.
- No NSO digs; no Big Mac duplication.

## Later extension (same day) — pre-X iPhone + Mac

- Pre-X iPhone (5s/6/6s/7) + SE: see `notes/iphone_historical_coverage_2026-10-25.md`; long panel now **1195** rows / **44** ISO3 / years **2013–2026**.
- MacBook Air/Pro + iMac: see `notes/apple_mac_xcountry_2026-10-25.md` (`mac_zenodo_aos_2022_panel.csv`, `mac_paulcollas_aos_panel.csv`).
- Netflix historical / Big Mac still **Season2**.
