# Subscription “Engel” shares — inventory (2026-10-26 Asia/Tokyo)

**Ask:** like food Engel coefficient — how much households/individuals spend on subscriptions (absolute monthly/annual and/or share of income or total consumption), from official/trusted free sources.

**Context:** Cross-country *price/CV* dig closed; Aoi #128 holds price levels. This dig is about **expenditure / budget shares**, not list prices.

**Landed under:** `/workspace/aoi-phase2/raw/subscription_engel/`  
**No GitHub PR** (parent decides upload).

---

## Bottom line (numbers)

| Source | Geo | Period | What | Absolute | Share | Label caveats |
|--------|-----|--------|------|----------|-------|---------------|
| **BLS CE Table 2500** | USA | **2024** | Rental, streaming & downloading **videos** | **$185.02 / CU / year** (~$15.4/mo) | **0.24% of total expenditures**; **0.18% of income before taxes** | Mean across **all** CUs; **36.8%** reporting. Closest official SVOD-like line. |
| BLS CE Table 2500 | USA | 2024 | Streaming & downloading **audio** | **$34.59 / CU / year** (~$2.9/mo) | **0.044% of spend**; **0.033% of income** | 18.3% reporting. Music streaming + downloads. |
| BLS CE (sum of two lines) | USA | 2024 | Video + audio streaming-like | **$219.61 / CU / year** (~$18.3/mo) | **~0.28% of spend**; **~0.21% of income** | Still tiny vs food Engel (~food 12–15% in US CE). |
| BLS CE Table 2500 | USA | 2024 | Cable & satellite TV services | **$454 / CU / year** | **0.58% of spend** | Traditional pay-TV; 33.5% reporting. |
| BLS CE | USA | 2024 | Entertainment (broad) | **$3,609 / CU / year** | **4.6% of spend**; **3.5% of income** | Pets, admissions, AV gear, etc. — **not** subscriptions-only. |
| **Eurostat HBS cult_pcs_hbs** | **EU27** | **2020** | TV/radio licence fees, **subscriptions**, hire of cultural equipment | **153 PPS / household / year** | **0.57% of total consumption**; **20.9% of culture spend** | Explicitly includes streaming/cable/pay-TV per Eurostat culture article. Best EU “fees & subs” money share. |
| Eurostat HBS | EU27 | 2020 | All cultural goods & services | 731 PPS | **2.7% of total consumption** | Broader culture basket (books, equipment, admissions…). |
| Eurostat NAMA `nama_10_co3_p3` | EU27 | 2022 | CP094 recreational & cultural **services** | — | **3.0% of HFCE** | Broader than fees/subs; multi-country annual panel. |
| Eurostat NAMA | EU27 | 2022 | CP09 recreation & culture | — | **8.4% of HFCE** | Very broad (holidays, pets, gear…). |
| Eurostat `isoc_ec_ibgs` | EU27 | **2025** | Paid film/series/sports streaming sub | — | **33% of internet users** (prevalence) | **Not expenditure**. Music streaming paid sub: **23%**. |
| MIC 家計消費状況調査 | Japan (2+ person hh) | 2024 | ダウンロード版の音楽・映像、アプリなど (net shopping) | **¥269 / month** | — | Internet-shopping channel only; **not** full SVOD billings. |
| StatCan (HFCE via Plus article) | Canada | 2024 | Cable, satellite & other program distribution **incl. streaming** | **CAD 11.3 bn** national aggregate | — | Mixes cable + streaming; not per-household share in free extract. |

**Rough conditional means (illustrative, not published):** US video line ÷ 36.8% reporting ≈ **~$500/year (~$42/mo)** among reporters; audio ÷ 18.3% ≈ **~$190/year (~$16/mo)**. Use with care (reporting ≠ unique paid SVOD count).

---

## Available series (detail)

### 1) USA — BLS Consumer Expenditure Survey (best SVOD/music **dollars**) — **RECOMMENDED #1**

- **Files:** `bls_ce_streaming_audio_panel.csv`, `bls_ce_detailed_means_2024.xlsx`, `bls_ce_entertainment_shares_panel.csv`
- **Coverage:** USA; streaming line items published in detailed means for **2024** (historical 2013–2023 xlsx returned 403 this run; entertainment/AV aggregates via API/FRED back to 1980s).
- **Measures:** Absolute USD/year per consumer unit; share of total expenditures; share of income before taxes; percent reporting; SE/RSE.
- **URLs:**
  - https://www.bls.gov/cex/tables/top-line-means.htm (Table 2500 / detailed means)
  - https://www.bls.gov/cex/ (CE homepage)
  - API series used for aggregates: `CXUENTRTAINLB0101M`, `CXUTVAUDIOLB0101M`, `CXUTOTALEXPLB0101M`, `CXUINCBEFTXLB0101M`
- **Label:** Questionnaire separates subscription music vs streaming video (Netflix/Disney+/etc. examples in info booklet). Published line is slightly broader (“rental, streaming, and downloading videos”).
- **Gap:** Multi-year **item-level** panel not landed (BLS blocked older xlsx); series IDs for item-level not confirmed via public API mnemonics.

### 2) EU — Eurostat HBS culture fees & subscriptions (best EU **money share**) — **RECOMMENDED #2**

- **Files:** `eurostat_hbs_fees_share_of_total_panel.csv`, `eurostat_hbs_fees_subscriptions_panel.csv`, `eurostat_cult_pcs_hbs_panel.csv`
- **Coverage:** EU countries (+ some others); HBS waves **2010 / 2015 / 2020** (not annual).
- **Measures:** Mean PPS; fees as % of total consumption; fees as % of culture; culture as % of total.
- **URL / dataset:** `cult_pcs_hbs` — https://ec.europa.eu/eurostat/databrowser/product/page/cult_pcs_hbs  
  Article: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Culture_statistics_-_household_expenditure_on_culture
- **Label:** COICOP `CP09423` / `CP09423_09424` — “Television and radio licence fees, subscriptions, hire of equipment…”. Eurostat text: includes **TV on demand, cable/paid TV, and various streaming services**.
- **Country spread (2020 fees % of total spend):** DK ~1.24%, FR ~0.91%, DE ~0.79%, EU27 ~0.57%, PL ~0.64%, NL ~0.17%, ES ~0.04% (licence/subscription regimes differ a lot).

### 3) EU — Eurostat NAMA HFCE COICOP shares (annual multi-country, broader) — **RECOMMENDED #3**

- **Files:** `eurostat_cp094_share_hfce_panel.csv`, `eurostat_cp09_share_hfce_panel.csv`, `eurostat_cp094_eurhab_panel.csv`, `eurostat_cp094_meur_panel.csv`
- **Coverage:** EU/EA + members; ~last 20 years annual (varies by geo).
- **Measures:** % of HFCE; EUR per capita; million EUR.
- **Dataset:** `nama_10_co3_p3` — CP094 recreational & cultural services; CP09 recreation & culture.
- **Label:** **Broader** than subscriptions (sports services, cultural services, hire, etc.). Companion to existing `eurostat_nama_engel_like_shares_panel.csv` (CP09 already there).
- **COICOP 2018 note:** Code `CP08392` “Subscriptions to audiovisual streaming services…” exists in classification; **HFCE money series at that grain not published yet** in NAMA (HICP transition mentioned from 2026). Future unlock.

### 4) EU — Paid subscription **prevalence** (not spend) — **RECOMMENDED #4 (adoption companion)**

- **File:** `eurostat_paid_subscription_prevalence_panel.csv`
- **Coverage:** EU countries; ~2020–2025 (indicator-dependent).
- **Measures:** % of internet users (last 3 months) with paid film/series/sports / music / gaming streaming subscription.
- **Dataset:** `isoc_ec_ibgs` (`I_BFLMS2`, `I_BMUSS2`, `I_BGAMSS`)
- **Article:** https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Culture_statistics_-_use_of_ICT_for_cultural_purposes  
  EU 2025: **33%** film/series/sports paid sub; **23%** music; **6%** gaming (of internet users).
- **Use:** Combine with price packs (#128) for rough implied spend; do **not** treat as Engel share.

### 5) Japan — 家計消費状況調査 (partial absolute)

- **Files:** `japan_joukyou_2024.pdf`, `japan_joukyou_digital_content_panel.csv`
- **Coverage:** Japan, two-or-more-person households; 2023–2024 in extract.
- **Measures:** Yen/month via **net shopping** — 「ダウンロード版の音楽・映像、アプリなど」¥269 (2024).
- **URL:** https://www.stat.go.jp/data/joukyou/2024ar/gaikyou/pdf/gkall.pdf
- **Gap:** 家計調査本体に独立の「動画配信サブスク」品目は見当たらず。受信料・教養娯楽サービス寄せは別掘りが必要。Share of income/消費支出は未接続。

### 6) Canada — StatCan HFCE aggregate

- **File:** `statcan_cable_streaming_aggregate_panel.csv` (from free Plus article; zip download TLS-failed this run)
- **Coverage:** Canada national; 2004–2024 sparse points.
- **Measures:** CAD billions — cable/satellite/other program distribution **including streaming** (2024: 11.3 bn).
- **URL:** https://www.statcan.gc.ca/o1/en/plus/8248-medium-cheaper-message-pricier  
  Table 36-10-0107 (full CSV blocked here).
- **Also:** CPI “video and audio subscription services” price index (+21% 2019→2024) — prices, not Engel share.

---

## SKIP / weak / not landed

| Item | Reason |
|------|--------|
| Statista-only subscription spend tables | Paywalled; skip per brief |
| Deloitte Digital Media Trends ($69/mo SVOD households, US survey) | Useful context but **commercial survey**, not NSO; keep as secondary cite only |
| Ofcom Media Nations 2026 PDF | Download 403 from box; site claims adoption (e.g. ~70% households ≥1 SVoD) and sector revenues — revisit via browser if needed |
| ONS Family Spending streaming line | Workbook URL 404 this run; ONS notes TV/streaming currently inside recreation & culture; COICOP18 streaming detail from LCF July 2026 / outputs later |
| Hulu/Peacock/US-only SVOD HES lines outside BLS | Covered by BLS video line |
| OECD Digital Economy Outlook free chapters | No clear country table of household subscription **$ / % income** found |
| FCC | No household Engel-like subscription share table found |
| Pure SaaS (M365/Adobe) household spend shares | No free NSO multi-country series found |
| Eurostat CP08392 streaming HFCE $ | Classification yes; published money panel **not yet** |

---

## What exists vs missing

**Exists (usable now):**
1. USA official **absolute + % of spend/income** for streaming-like video & audio (2024).
2. EU official **fees/subscriptions money share** of total consumption (HBS 2020) + annual broader CP094/CP09 shares.
3. EU official **paid-sub prevalence** (2024–2025).
4. JP partial absolute via net-shopping digital content.
5. CA national aggregate cable+streaming.

**Missing (true Engel analogue multi-country annual for SVOD-only):**
- Harmonized **SVOD-only % of disposable income** across OECD/EU annual panel.
- Japan full household survey SVOD line + income share.
- UK ONS streaming £ line (until COICOP18).
- Multi-year US item-level CE panel (need unblock/download or PUMD).

---

## Best 2–4 series for myon’s use

1. **BLS CE streaming video (+ audio) dollars & shares** — closest “how much do households pay” for Netflix-class + Spotify-class; pair with Aoi #128 US prices.  
2. **Eurostat HBS fees/subscriptions % of total consumption** — best cross-EU money share including streaming; Engel-like but **broader** (licence + cable).  
3. **Eurostat NAMA CP094 % of HFCE** — annual multi-country companion to food Engel NAMA packs (accept broader label).  
4. **Eurostat isoc_ec_ibgs paid-sub prevalence** — adoption layer to combine with price packs; not a spend share.

**Optional add-on:** Japan joukyou digital-content ¥ (absolute only); StatCan aggregate if per-household/share can be derived later from Table 36-10-0107 + household counts.

---

## Suggested next step

1. **If Engel-style chart is the goal:** plot USA BLS video+audio share of spend (~0.28%) next to food Engel (~12%+) and EU HBS fees share (~0.6%) — documents that subscription “Engel” is **orders of magnitude smaller** than food.  
2. **If multi-year USA streaming needed:** retry BLS detailed means 2013–2023 via browser / `download.bls.gov` when unblocked, or CE PUMD.  
3. **If Japan share needed:** link joukyou ¥ to 家計調査 消費支出 total (or 勤労者世帯実収入) for a JP share proxy; dig 受信料 / 教養娯楽サービス in 家計調査品目.  
4. **Upload:** only if parent wants — quality is inventory + tidy panels, not Netflix-adjacent continuous price pack. Hold PR unless asked.

---

## File index

```
raw/subscription_engel/
  README.md
  headline_subscription_engel_snapshot.csv
  bls_ce_detailed_means_2024.xlsx
  bls_ce_streaming_audio_panel.csv
  bls_ce_entertainment_av_panel.csv
  bls_ce_entertainment_shares_panel.csv
  eurostat_cp09_share_hfce_panel.csv
  eurostat_cp094_*_panel.csv
  eurostat_cult_pcs_hbs_panel.csv
  eurostat_hbs_fees_subscriptions_panel.csv
  eurostat_hbs_fees_share_of_total_panel.csv
  eurostat_paid_subscription_prevalence_panel.csv
  japan_joukyou_2024.pdf|.txt
  japan_joukyou_digital_content_panel.csv
  statcan_cable_streaming_aggregate_panel.csv
  fred_CXUENTRTAINLB0101M.csv
  fred_CXUTVAUDIOLB0101M.csv
```

Retrieved: 2026-10-26 (Asia/Tokyo). No invent; mixed units flagged.
