# Cross-country SVOD price dispersion (video peers) — Season2 — 2026-10-26

**Lane:** Aoi phase-2 off-main curiosity (myon OK via Aoi origin).  
**Scope this note:** SVOD video peers only — Disney+, Amazon Prime / Prime Video, Max/HBO Max, Paramount+, Hulu, Peacock.  
**Sibling note (music + SaaS):** `notes/subscription_xcountry_dispersion_2026-10-26.md` — parent merges.  
**Rule:** free/easy multi-country absolute named-plan prices only; no invented FX; PPP/CPI not used.

---

## Method

- **Metric:** CV = sample std / mean of **USD** monthly list prices for one named plan; also **p90/p10**.
- **Threshold vs Netflix baseline (~0.23):**
  - **Tighter:** CV &lt; ~0.15
  - **Netflix-like:** CV roughly **0.15–0.30**
  - **Higher:** CV clearly &gt; ~0.30
  - **SKIP:** &lt;8 comparable countries, no clean free table, or data-quality fail
- **Primary FX / sources:**
  - **PriceByCountry** embedded country→USD maps; site converts at **ExchangeRate-API rates dated 2026-10-17** (methodology). Tax treatment **not** normalised. Plan “last read” dates vary by product page.
  - **Subscription Land** Paramount+ / Prime Video: local billing currency kept; **USD = page `exchangedPrice`** in Next.js RSC payload. **FX provider not named** on SL methodology (“converts … into your selected comparison currency”) — documented, not invented.
  - **Android Authority** Disney+ Mar 2025: USD as published in article table (secondary / mixed-tier caveat).
- **Caveats:** Country-set composition moves CV a lot (adding cheap EM markets raises CV). Ads vs ad-free / Premium vs Standard mismatch. Annual vs monthly. Membership bundles (Prime) ≠ standalone video. Not PPP-adjusted. Observation dates differ across sources.

Tidy panels: `/workspace/aoi-phase2/raw/subscription_xcountry/`  
Summary CSV: `raw/subscription_xcountry/svod_season2_dispersion_summary.csv`

---

## Netflix baseline (restated; not re-scraped)

| Source | Plan | n | median USD | **CV** | p90/p10 | Notes |
|--------|------|--:|----------:|-------:|--------:|-------|
| **Burger Parity** (landed panel) | **Standard** | **30** | 11.85 | **0.233** | 1.93 | Stable-xcountry screen 2026-10-25; `burger_netflix.csv` / `netflix_standard_burgerparity_panel.csv` |
| PriceByCountry (context only) | Standard | 50 | ~12.5 | 0.398 | 2.73 | Wider EM set → higher CV; **not** the bucket baseline |
| Aoi #118 hist pack tip `17e5c1e` | adjacent_netflix_subscription_levels | — | — | — | — | Time-series companion; **CV baseline for buckets = BP cross-section ~0.23**, not a CV recomputed from the full monthly hist panel |

**Baseline used for buckets below: Burger Parity Netflix Standard CV ≈ 0.23 (n=30).**

---

## Classification — SVOD video peers (this slice)

Ranked by CV (primary row). Buckets vs **BP Netflix CV ≈ 0.23**.

| Rank | Bucket | Service | Plan | n | CV | p90/p10 | Source |
|-----:|--------|---------|------|--:|---:|--------:|--------|
| 1 | **Netflix-like** | **Paramount+** | Starting Monthly (Subscription Land international label) | **24** | **0.220** | 1.65 | [Subscription Land](https://subscriptionland.com/services/paramount_plus/starting_monthly/USD) |
| 2 | **Netflix-like** | **Max / HBO Max** | Premium (PBC chart plan) | **34** | **0.279** | 1.95 | [PriceByCountry](https://pricebycountry.com/streaming-prices/hbo-max/) |
| 3 | **Higher** | **Disney+** | Premium (PBC chart plan) | **39** | **0.318** | 2.01 | [PriceByCountry](https://pricebycountry.com/streaming-prices/disney-plus/) |
| 4 | **Higher** | **Amazon Prime** *(membership)* | Prime monthly membership (**not** standalone Prime Video) | **20** | **0.576** | 3.46 | [PriceByCountry](https://pricebycountry.com/streaming-prices/amazon-prime/) |
| — | **SKIP** | Hulu | — | — | — | — | See SKIP |
| — | **SKIP** | Peacock | — | — | — | — | See SKIP |
| — | **SKIP** (DQ) | Amazon Prime Video standalone | SL monthly | 24 | (0.49 raw) | — | See SKIP / caveat |

### Plain-language take for merge

1. **Paramount+ Starting Monthly (~CV 0.22)** and **Max Premium (~0.28)** sit in the **Netflix-like** band vs the BP Netflix ~0.23 baseline — similar absolute USD dispersion on these easy tables.
2. **Disney+ Premium (~0.32)** is **mildly higher** than Netflix on the PBC 39-country set (just over the ~0.30 line). A secondary Android Authority Mar 2025 mixed-tier USD table (n=47) gives CV **~0.34** — same bucket, **not** a strict same-tier check (US row is With Ads Dual).
3. **Amazon Prime membership (~0.58)** is **clearly higher** dispersion — and it is a **bundled membership** (shipping + video + other perks), not a clean SVOD peer. Treat as “Prime membership,” not “Prime Video.”
4. **Standalone Prime Video**, **Hulu**, and **Peacock** lack a clean ≥8-country comparable free table after easy paths → **SKIP** (details below).
5. No service in this slice cleared the **tighter (&lt;0.15)** bar on a trusted panel.

---

## Per-service detail

### Paramount+ — Netflix-like (CV 0.220, n=24)

- **Plan:** Subscription Land “Starting Monthly” (international label; may map to Basic/Essential/with-ads entry tiers that differ by market — not audited country-by-country).
- **USD:** `exchangedPrice` from page RSC; local price+currency retained in panel.
- **FX:** Provider **unnamed** on [SL methodology](https://subscriptionland.com/methodology); do not invent. Page header “Prices verified June 17” (2026 context). Retrieved **2026-10-26**.
- **Panel:** `panel_subscriptionland_paramount_plus_starting_monthly.csv`
- Official Paramount help pages only listed a thin AU/CA-style set → SL used as the easy multi-country table.

### Max / HBO Max — Netflix-like (CV 0.279, n=34)

- **Plan:** PriceByCountry **Premium** (chart plan; page also prices Standard).
- **USD / FX:** PBC published USD; ExchangeRate-API table **2026-10-17**.
- **Observation:** Product page “prices last read **2026-07-27**” (stale vs later US list moves possible — e.g. US Premium list has moved in App Store tables; panel still used as published).
- **Panel:** `panel_pbc_hbo-max.csv`

### Disney+ — higher (CV 0.318, n=39)

- **Plan:** PriceByCountry **Premium** (charts also show Standard / Standard with Ads / Basic).
- **USD / FX:** PBC; ExchangeRate-API **2026-10-17**; prices last read **2026-10-17**.
- **Panel:** `panel_pbc_disney-plus.csv`
- **Secondary (not primary bucket):** Android Authority Mar 2025 USD roundup, n=47, CV **0.339**, p90/p10 **2.58** — mixed tiers (US With Ads Dual $7.99). Panel: `panel_androidauthority_disney_plus_mar2025_mixed_usd.csv`. Source: https://www.androidauthority.com/disney-plus-price-increase-3530231/

### Amazon Prime membership — higher (CV 0.576, n=20)

- **Plan:** PBC **Prime** monthly membership (page: “2 plans priced; charts show Prime”). **Clarify:** this is **Prime membership**, not standalone Prime Video.
- **USD / FX:** PBC; ExchangeRate-API **2026-10-17**; prices last read **2026-10-17**.
- **Panel:** `panel_pbc_amazon-prime.csv`
- Egypt $0.54 … US $14.99 on this table → wide right/left tails typical of regional membership pricing.

---

## SKIP

| Item | Why |
|------|-----|
| **Hulu** | Subscription Land explicitly **1 country (US)** for With Ads / No Ads. PBC shows a 10-country “Standard (With Ads)” table (CV≈0.30 if taken literally) but footprint conflicts with SL’s US-only framing and known Hulu geographic limits → **not trusted** as comparable multi-country SVOD. |
| **Peacock** | Consumer Peacock is **US (+ territories)**; international availability is largely via **Sky / partner bundles**, not an easy free standalone multi-country MSRP table. |
| **Amazon Prime Video (standalone)** | SL monthly table has n=24 and raw CV≈0.49, but **JM / UY** convert to absurd USD (~$0.04 / ~$0.15) — likely currency/label errors. Even dropping usd&lt;$1 leaves CV≈0.32 on n=21, still not clean enough for classification. Panel kept for audit only: `panel_subscriptionland_amazon_prime_video_monthly.csv`. **Primary Amazon line = Prime membership (above).** |
| **World Price Index JSON API** | Bearer key required — skipped. |
| **Paid digs / Statista / hard scrapes** | Out of scope (easy free only). |
| **Official Paramount country help alone** | Too thin (AU/CA-style) for ≥8 without SL. |

---

## Ranked one-liner table (for Aoi origin merge)

| Service | n | CV | p90/p10 | Plan | Bucket | Source |
|---------|--:|---:|--------:|------|--------|--------|
| Paramount+ | 24 | 0.220 | 1.65 | Starting Monthly (SL) | Netflix-like | subscriptionland.com …/paramount_plus/starting_monthly/USD |
| Max / HBO Max | 34 | 0.279 | 1.95 | Premium | Netflix-like | pricebycountry.com/streaming-prices/hbo-max/ |
| Disney+ | 39 | 0.318 | 2.01 | Premium | higher | pricebycountry.com/streaming-prices/disney-plus/ |
| Amazon Prime (membership) | 20 | 0.576 | 3.46 | Prime monthly membership | higher | pricebycountry.com/streaming-prices/amazon-prime/ |
| Hulu | — | — | — | — | SKIP | US-centric; PBC multi-country untrusted |
| Peacock | — | — | — | — | SKIP | US / partner-bundle only |
| Prime Video standalone | — | — | — | — | SKIP (DQ) | SL table FX integrity fail |

---

## Files

- Note: `notes/subscription_xcountry_svod_season2_2026-10-26.md` (this file)
- Summary: `raw/subscription_xcountry/svod_season2_dispersion_summary.csv`
- Panels: `panel_pbc_disney-plus.csv`, `panel_pbc_hbo-max.csv`, `panel_pbc_amazon-prime.csv`, `panel_subscriptionland_paramount_plus_starting_monthly.csv`, `panel_androidauthority_disney_plus_mar2025_mixed_usd.csv`, `panel_subscriptionland_amazon_prime_video_monthly.csv` (audit/SKIP)
- Netflix baseline: `raw/subscription_xcountry/burger_netflix.csv` (and durable panel sibling)

Retrieved: **2026-10-26 Asia/Tokyo** (box).
