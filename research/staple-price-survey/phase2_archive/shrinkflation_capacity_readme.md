# Shrinkflation capacity panel (いつの間にか容量が減っている商品wiki)

Source: [https://shrinkflation.info/](https://shrinkflation.info/) — volunteer / AI-assisted wiki that tracks **content shrinkage** (grams, pack counts, ml), not an official retail price index.

## What this is

- Local dump of **capacity / grams / pack-quantity** time points for Japanese packaged goods.
- The useful “index” idea (e.g. カントリーマアム) is **how pack size shrank over event years**, not 小売物価統計の銘柄価格.
- Built for engel / snack-numeraire research as a **Japan local companion** (alongside Big Mac etc.). **Not global.**

## Files

| File | Description |
|---|---|
| `shrinkflation_capacity_panel.csv` | Vertical panel (all kept products) |
| `shrinkflation_capacity_products.csv` | One row per product (year span, n_rows, units) |
| `country_maam_shrinkflation_series.csv` | Earlier Country Ma'am–only tidy series (still valid) |
| `shrinkflation_capacity_index_panel.csv` | Derived capacity index (100=base); see `shrinkflation_capacity_index_readme.md` |
| `shrinkflation_capacity_index_annual_median.csv` | Sparse annual median cross-section of indexes |
| `raw/shrinkflation/pages/` | Downloaded wiki HTML |
| `raw/shrinkflation/panel_build_summary.json` | Build stats |
| `raw/shrinkflation/skipped_pages.json` | Edit-only / too-few / empty skips |

## Panel columns

`product_slug, product_name, manufacturer, date, year, capacity_value, capacity_unit, pack_note, price_yen_ex_tax, source_url, note, category, wiki_page`

- `capacity_unit`: `g` | `count` | `ml`
- `price_yen_ex_tax`: nullable; wiki list price when present (税抜/税別 preferred). **Capacity is the signal.**
- Undated first rows (wiki blank 年月) keep `date`/`year` empty and are tagged in parsing as baseline.

## Coverage (this build)

- **Products kept:** 508
- **Rows:** 2485
- **Year span:** 1973–2026 (event dates; sparse, not monthly)
- **Units:** {'g': 1970, 'count': 170, 'ml': 345}
- **Products by wiki category:** {'菓子': 312, '加工食品': 88, '日用品': 26, '飲料': 19, '冷凍食品': 13, 'インスタント食品': 46, 'チョコレート': 1, 'LION(ライオン)': 2, '外食・その他': 1}

Inclusion rule: parsed capacity table with **≥3 observations** (including undated baseline rows). Pages that are edit-only stubs, have no capacity table, or only price changes with blank 容量 are skipped.

## Notable inclusions / skips

- **Included:** カントリーマアム (12 pts, 1992–2024), カルビー ポテトチップス, キットカットミニ, うまい棒, たけのこの里 / きのこの山, じゃがりこ サラダ, 雪見だいふく, フルグラ, plus hundreds of sweets / snacks / drinks / cup-noodle–adjacent / dairy / household pages that met the row threshold.
- **Skipped examples:** ホームパイ / チキンラーメン (wiki edit-only, no published table); カップヌードル (price history only, capacity cells blank on wiki).

## Caveats

1. **Volunteer wiki + AI-assisted updates** — not a statistical agency series; verify against maker PR / Wayback when using for claims.
2. **Event dates are sparse** — often year-only; some months; undated baselines.
3. **Pack definitions drift** — convenience vs non-convenience, multipack `ml×2`, count vs total g (Country Ma'am: capacity is 枚; total g copied into `note` from 備考 when present).
4. **Ranges** (e.g. うまい棒 `7～9g`): stored as **lower bound** with note `range …; using lower bound as listed` — not invented midpoints.
5. **Prices** may stay sticky on the wiki while open-price retail moved; do not treat as CPI.
6. Dual-size cells (コンビニ / コンビニ以外) may appear as separate rows with `pack_note` channel tags.

## Rebuild hint

HTML cache: `raw/shrinkflation/pages/`. Candidate list from `https://shrinkflation.info/?cmd=list`.
