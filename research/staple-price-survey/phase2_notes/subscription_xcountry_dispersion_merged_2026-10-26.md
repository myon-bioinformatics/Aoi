# Cross-country subscription price dispersion — MERGED — 2026-10-26

**Lane:** Aoi phase-2 off-main curiosity (myon).  
**Ask:** Classify absolute USD cross-country CV vs Netflix; record a core set; gather continuous/date×country panels like Netflix where easy; prep Aoi upload packs.  
**Baseline:** Burger Parity Netflix Standard, **n=30, CV ≈ 0.233**, p90/p10 ≈ 1.93 (`netflix_standard_burgerparity_panel.csv`).  
**Slices merged:**  
- Music + SaaS: `notes/subscription_xcountry_dispersion_2026-10-26.md`  
- SVOD Season2: `notes/subscription_xcountry_svod_season2_2026-10-26.md`  
**Rule:** free/easy tables only; FX as published by source; not PPP; no invented FX.

Summary CSV: `raw/subscription_xcountry/dispersion_merged_summary.csv`  
Upload prep: `raw/subscription_xcountry/UPLOAD_PACK.md`

---

## Buckets vs BP Netflix ~0.23

### Tighter / Netflix-like (CV ≲ 0.30)

| Service | Plan | n | CV | p90/p10 | Slice | Source |
|---------|------|--:|---:|--------:|-------|--------|
| iCloud+ | 50 GB | 18 | 0.169 | 1.53 | music/SaaS | PriceByCountry |
| Paramount+ | Starting Monthly | 24 | 0.220 | 1.65 | SVOD | Subscription Land |
| **Netflix** | **Standard (baseline)** | **30** | **0.233** | **1.93** | — | Burger Parity |
| Max / HBO Max | Premium | 34 | 0.279 | 1.95 | SVOD | PriceByCountry |

### Mildly higher (~0.30–0.40)

| Service | Plan | n | CV | p90/p10 | Slice | Source |
|---------|------|--:|---:|--------:|-------|--------|
| Disney+ | Premium | 39 | 0.318 | 2.01 | SVOD | PriceByCountry |
| Microsoft 365 | Individual monthly | 37 | 0.327 | 2.85 | music/SaaS | PriceByCountry |
| Apple TV+ | default table | 102 | 0.340 | 1.86 | music/SaaS | subscriptionscompare |
| Google One | 100 GB | 44 | 0.343 | 2.83 | music/SaaS | PriceByCountry |

### Clearly higher (CV ≳ 0.40) — music + bundled Prime stand out

| Service | Plan | n | CV | p90/p10 | Slice | Source |
|---------|------|--:|---:|--------:|-------|--------|
| Adobe CC | Individual | 46 | 0.420 | 3.33 | music/SaaS | geopriced |
| Spotify | BP same-30 as Netflix | 30 | 0.497 | 5.65 | music/SaaS | Burger Parity |
| Apple Music | Individual | 44 | 0.570 | 5.77 | music/SaaS | PriceByCountry |
| Dropbox | default | 17 | 0.573 | 10.13 | music/SaaS | subscriptionscompare |
| Amazon Prime | **membership** (not Video) | 20 | 0.576 | 3.46 | SVOD | PriceByCountry |
| YouTube Premium | Premium / Individual | 43 | 0.615 | 8.06 | music/SaaS | PriceByCountry |
| Spotify | PBC Individual | 50 | 0.636 | 7.17 | music/SaaS | PriceByCountry |

### SKIP

Apple One (no easy ≥8-country table); YouTube Music (use Premium); Hulu; Peacock; Prime Video standalone (SL FX DQ); WPI/Statista/Cable paywalls; BigMacIndex Spotify CSV (login-gated — not used).

---

## Recorded core set (myon)

For Big-Mac-tolerance comparison and Aoi upload. User「Apple Plus」= **Apple TV+** (Apple One remains SKIP).

| # | Service | CV (primary) | Bucket | Snapshot source (one-liner) | Hist depth (easy free) |
|--:|---------|-------------:|--------|-----------------------------|------------------------|
| 1 | **Netflix** | 0.233 (BP n=30) | baseline | Burger Parity Standard | **POINTER** to Aoi #118 `adjacent_netflix_subscription_levels` tip `17e5c1e` — 32 dates × 54 ISO3 (2020-03…2026-09); do not rebuild |
| 2 | **iCloud+** | 0.169 (PBC 50GB n=18) | tighter / Netflix-like | PriceByCountry 50GB | **5 dates** LCU vertical (Apple Support Wayback 2024-07/09/11 + SL 2026-05 + Support/PBC 2026-10) ≈88 ISO3 |
| 3 | **Microsoft 365** | 0.327 (PBC Individual n=37) | mildly higher | PriceByCountry | **SNAPSHOT-ONLY** — no SL page; PBC Wayback CDX empty; vertical LCU thin (12 ISO3 with parseable local) |
| 4 | **Google One** | 0.343 (PBC 100GB n=44) | mildly higher | PriceByCountry | **2 dates** (SL 2026-05 + PBC/SL 2026-10) ≈130 ISO3 |
| 5 | **Apple TV+** | 0.340 (subcmp n=102) | mildly higher | subscriptionscompare | **4 dates** SL Wayback/current (2026-01…2026-10) ≈118 ISO3 |
| 6 | **Spotify** | 0.497 BP / 0.636 PBC | higher (music) | BP + PriceByCountry | **3 dates** SL full-table Wayback (2025-11, 2026-02) + PBC 2026-10 ≈157 ISO3 LCU |
| 7 | **Apple Music** | 0.570 (PBC n=44) | higher (music) | PriceByCountry | **3 dates** SL (2025-11, 2026-03) + PBC 2026-10 ≈121 ISO3 |
| 8 | **YouTube Premium** | 0.615 (PBC n=43) | higher (music) | PriceByCountry | **4 dates** SL (2026-03…2026-10) ≈58 ISO3 |

Music CVs ~0.5–0.64 are kept for Big-Mac-tolerance discussion even though clearly above Netflix.

---

## Caveats

1. **Country-set width moves CV** — PBC Netflix n=50 → CV~0.40 vs BP n=30 → 0.23; buckets use BP baseline for like-for-like with Spotify BP.
2. **FX** — PBC uses ExchangeRate-API **2026-10-17**; SL `exchangedPrice` FX provider **unnamed**; Apple Support LCU with USD only when billing currency is USD (no invented FX). Tax not normalised.
3. **Prime membership ≠ Prime Video** — high-CV Amazon line is bundled membership.
4. **Hist ≠ Netflix density** — music/SaaS packs are months-scale SL Wayback + a few Apple Support dates, not 2020–2026 tompec-density. Small Wayback captures (JS shell, ~35–50 KB) yielded 0 rows.
5. **SL CURRENT (2026-10-26)** often embeds only `initialPrices` (~24 cheapest countries); prefer earlier full-table Wayback + PBC Oct cross-section.
6. **Observation dates differ** across sources; plan tiers (ads/Premium) may mismatch.

---

## Continuous / hist files

| Path | Role |
|------|------|
| `raw/subscription_xcountry/hist/*_levels.csv` | Long panels: date, iso3/iso2, plan, local_price, currency, price_usd (as published), source |
| `raw/subscription_xcountry/hist/netflix_levels_POINTER.md` | Points at Season2 #118 pack |
| `*_xcountry_hist_panel.csv` (aoi-phase2 root) | Friendly copies when ≥2 distinct dates (all core except M365) |
| `raw/subscription_xcountry/upload_packs/adjacent_*` | Aoi-ready packs (vertical LCU schema mirroring Netflix) |

---

## Plain take

1. **Video SVOD peers** (Paramount+, Max) land near Netflix; Disney+ just above.  
2. **Music streaming** is the high-dispersion cluster (~0.5–0.64) — kept in the recorded set for Big-Mac tolerance.  
3. **Cloud SaaS** splits: iCloud+ tight; Google One / M365 mild; Adobe / Dropbox higher.  
4. **Continuous data** for the recorded set is **partial**: Netflix already dense; iCloud/Spotify/Apple Music/YouTube/Apple TV+/Google One have multi-date LCU panels (thin vs Netflix); **M365 snapshot-only**.

Retrieved: **2026-10-26 Asia/Tokyo** (box).
