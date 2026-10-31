# Cross-country subscription price dispersion (music + SaaS slice) — 2026-10-26

**Lane:** Aoi phase-2 off-main curiosity (myon).  
**Scope this note:** music streaming + SaaS / non-video cloud (Spotify, Apple Music, YouTube Premium, Microsoft 365, Google One, iCloud+, Adobe CC, Dropbox; Apple TV+ as easy video-adjacent).  
**SVOD peers** (Disney+, Amazon Prime, Max/HBO, Paramount+, Hulu/Peacock) → **Season2 note (pending merge)** — not expanded here.  
**Rule:** free/easy multi-country absolute plan prices only; no invented FX; PPP not used.

---

## Method

- **Metric:** CV = sample std / mean of **USD** monthly list prices for one named plan; also **p90/p10**.
- **Threshold vs Netflix baseline (~0.23):**
  - **Tighter:** CV &lt; 0.15
  - **Netflix-like:** CV roughly **0.15–0.30**
  - **Higher:** CV &gt; 0.30
  - **SKIP:** &lt;8 countries or no easy free table
- **Primary FX / sources:**
  - PriceByCountry embedded country→USD maps; site converts at **ExchangeRate-API rates dated 2026-10-17** (methodology page). Tax treatment **not** normalised.
  - Burger Parity reference CSV: USD **as published** (no FX fill by us).
  - Geonode Spotify blog: USD via **open.er-api.com ~2026-10-07**.
  - geopriced Adobe: USD as published (site cites **ECB**); Individual monthly from page RSC payload.
  - subscriptionscompare Dropbox / Apple TV+: USD as published (FX less transparent — secondary).
- **Caveats:** Country-set composition moves CV a lot (adding low-income EM markets raises CV for almost everyone, including Netflix). Plan mismatch / ads / tax / annual vs monthly. Not PPP-adjusted.

Tidy panels (optional): `/workspace/aoi-phase2/raw/subscription_xcountry/`  
Summary CSV: `raw/subscription_xcountry/music_saas_dispersion_summary.csv`

---

## Netflix baseline (restated)

| Source | Plan | n | median USD | **CV** | p90/p10 | Date / notes |
|--------|------|--:|----------:|-------:|--------:|--------------|
| **Burger Parity** (landed panel) | **Standard** | **30** | 11.85 | **0.233** | 1.93 | Snapshot used in stable-xcountry screen 2026-10-25; `netflix_standard_burgerparity_panel.csv` |
| PriceByCountry (context only) | Standard | 50 | ~12.5 | 0.398 | 2.73 | Read ~2026-10-17; includes cheaper EM (e.g. PK ~$2.89) → higher CV |

**Baseline used for buckets below: Burger Parity Netflix Standard CV ≈ 0.23 (n=30).**  
Season2 Aoi #118 long panel (tip `17e5c1e`) is the time-series companion pack; this note’s CV baseline is the **absolute USD cross-section** already used in the durables screen, not a CV recomputed from the full #118 monthly panel.

---

## Classification — music + SaaS (this slice)

Ranked by CV (primary PriceByCountry row where available). Buckets vs **BP Netflix CV 0.23**.

| Bucket | Service | Plan | n | CV | p90/p10 | Source |
|--------|---------|------|--:|---:|--------:|--------|
| **Tighter / lower end of Netflix-like** | **iCloud+** | 50 GB | 18 | **0.169** | 1.53 | [PriceByCountry](https://pricebycountry.com/icloud-plus/) |
| **Netflix-like** | *(none other in this slice on full PBC samples)* | | | | | |
| **Mildly higher** | Microsoft 365 | Individual monthly | 37 | **0.327** | 2.85 | [PriceByCountry](https://pricebycountry.com/microsoft-365/) |
| **Mildly higher** | Google One | 100 GB | 44 | **0.343** | 2.83 | [PriceByCountry](https://pricebycountry.com/google-one/) |
| **Mildly higher** | Apple TV+ *(video-adjacent)* | default table plan | 102 | **0.340** | 1.86 | [subscriptionscompare](https://subscriptionscompare.com/apple-tv-plus-price-by-country) |
| **Higher** | Adobe Creative Cloud | Individual monthly | 46 | **0.420** | 3.33 | [geopriced](https://geopriced.com/service/adobe-cc) |
| **Higher** | Spotify | (Burger Parity, same ~30-set as Netflix) | 30 | **0.497** | 5.65 | [Burger Parity](https://burgerparity.com/data/prices.csv?product=spotify) |
| **Higher** | Apple Music | Individual | 44 | **0.570** | 5.77 | [PriceByCountry](https://pricebycountry.com/streaming-prices/apple-music/) |
| **Higher** | Dropbox | default plan on page | 17 | **0.573** | 10.13 | [subscriptionscompare](https://subscriptionscompare.com/dropbox-price-by-country) |
| **Higher** | YouTube Premium | Premium / Individual | 43 | **0.615** | 8.06 | [PriceByCountry](https://pricebycountry.com/streaming-prices/youtube/) |
| **Higher** | Spotify | Premium Individual | 50 | **0.636** | 7.17 | [PriceByCountry](https://pricebycountry.com/streaming-prices/spotify/) |
| **Higher** (check) | Spotify | Individual | 20 | **0.619** | 10.28 | [Geonode Oct 2026](https://geonode.com/blog/spotify-premium-prices-by-country) |

### Plain-language take for myon

1. **Music streamers look clearly more dispersed than Netflix** on absolute USD: Spotify / YouTube Premium / Apple Music CVs roughly **0.5–0.64** (≈2–3× the BP Netflix ~0.23). Same story on the Burger Parity 30-country set (Spotify **0.50** vs Netflix **0.23**).
2. **Cloud storage SaaS is mixed:** **iCloud+ 50GB is the only “tight / Netflix-like” name** in this slice (CV **0.17**). **Google One** and **Microsoft 365** sit **mildly above** Netflix (~0.33–0.34) on broad samples.
3. **Adobe CC Individual** (~**0.42**) and **Dropbox** (~**0.57**, smaller n) are **higher** than Netflix — regional pricing exists, but music is still the stand-out high-dispersion group.
4. **Apple TV+** (~**0.34**, third-party table) is mildly higher than Netflix; **Apple One** had no easy free multi-country table → SKIP.

---

## SKIP (this slice)

| Item | Why |
|------|-----|
| **Apple One** | No easy free ≥8-country absolute MSRP table (PriceByCountry / geopriced 404; no quick roundup used). |
| **YouTube Music** | No separate easy table; **YouTube Premium** used (often bundles Music). |
| **Adobe / Dropbox on PriceByCountry** | No product pages; Adobe via geopriced, Dropbox via subscriptionscompare. |
| **World Price Index JSON API** | Bearer API key required — skipped (auth). HTML hub not used as primary panel. |
| **Cable.co.uk-style paid digs / Statista paywall** | Not free-easy. |

---

## SVOD peers → Season2 note (pending merge)

Parent handed SVOD video peers to Season2. **Do not treat the following as final classification** — placeholder until Season2’s note lands and parent merges.

Incidental PriceByCountry pulls already on disk (not expanded after scope split):

| Service | Plan (PBC chart plan) | n | CV | p90/p10 | Rough vs BP Netflix 0.23 |
|---------|----------------------|--:|---:|--------:|--------------------------|
| HBO Max | (chart plan) | 34 | 0.279 | 1.95 | Netflix-like |
| Hulu | Standard (With Ads) | 10 | 0.295 | 1.59 | Netflix-like (thin n) |
| Disney+ | Premium | 39 | 0.318 | 2.01 | Mildly higher |
| Amazon Prime | Prime membership | 20 | 0.576 | 3.46 | Higher |
| Crunchyroll | Mega Fan | 16 | 0.584 | 8.91 | Higher |

Raw HTML/panels may exist under `raw/subscription_xcountry/pbc2_*.html` for Season2 reuse.

---

## Top sources

1. https://pricebycountry.com/streaming-prices/ (+ `/microsoft-365/`, `/google-one/`, `/icloud-plus/`) — methodology FX: ExchangeRate-API **2026-10-17**
2. https://burgerparity.com/data/prices.csv?product=netflix (and `product=spotify`)
3. https://geonode.com/blog/spotify-premium-prices-by-country
4. https://geopriced.com/service/adobe-cc
5. https://subscriptionscompare.com/dropbox-price-by-country , `/apple-tv-plus-price-by-country`

---

## Files

- Note: `notes/subscription_xcountry_dispersion_2026-10-26.md` (this file)
- Summary: `raw/subscription_xcountry/music_saas_dispersion_summary.csv`
- Panels: `raw/subscription_xcountry/panel_pbc_*.csv`, `panel_geopriced_adobe_cc.csv`, `panel_subcmp_*.csv`, `burger_spotify.csv`
- Netflix landed baseline: `netflix_standard_burgerparity_panel.csv`

Retrieved: 2026-10-26 (Asia/Tokyo box).
