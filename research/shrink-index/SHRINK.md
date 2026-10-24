# Shrink index (cycle 2, idea 2: the Country Ma'am index)

An index for products whose content shrinks while the price stays. The first product is Country Ma'am (カントリーマアム). **The basis is the total quantity per package, not the piece count.** Pieces alone mislead: the count can go up (28 -> 30) while each piece gets lighter.

## Definition

```text
q_t = n_t * w_t                              total content per package (g); n = pieces per bag, w = grams per piece
                                             (or q_t given directly in g)
s_t = q_t / q_ref                            level; ref = the first year where q is known
r   = (log1p(q_j) - log1p(q_i)) / (j - i)    change per year between two neighbouring known points (an interval)
m_t = log1p(q_t) - log1p(q_d)                margin to the danger level q_d (> 0 above it, <= 0 inside the zone)
D_t = 1 / (1 + exp(m_t))                     closeness to danger in (0, 1); 0.5 at q_d; defined at q_t = 0
u_t = (p_t / q_t) / (p_ref / q_ref)          unit-price level (rises when the price is held and q falls)
```

`log1p` keeps zero inside the function (no value is thrown away to avoid it), and D is smooth in q, so the index stays differentiable up to the zone and stops at 1 instead of running to zero.

## Rules (fixed before any result is read)

- q is computed only for a year where both n and w are known. **No interpolation and no carry-forward** between years. Where a source states a range ("since 2014"), the row says so in `note`.
- `q_d` (the size at which a person cannot eat it) is **not estimated from data**. A person sets it with `--danger-total`. The synthetic check uses an illustrative 60 g.
- `MIN_POINTS = 5`: with fewer known q points the output says **insufficient**. It is "the evidence is not enough", not "failed".
- A rate `r` is an interval between two known points. With sparse points a step and a slide cannot be told apart, so the code does not try.
- No straight-line regression and no rounded verdict. `--whatif` is an explicit opt-in ("if this rate continued, q reaches q_d in X years") and is printed as `WHAT-IF (not a forecast)`.
- A gap in the weight can be filled by a labelled assumption: `--assume-weight 2005:10.5,2007:10.5`. The output marks those years `ASSUMED`; an observed weight always wins; assumptions are never written into the data file.
- No currency, unit conversion or exchange rate.

## Observed data: `countrymaam_observed_vertical.csv`

Same columns as `staple_survey_vertical.csv`; `variable = <product>:<measure>` with measures `pieces`, `grams_per_piece`, `total_g`, `price`.

- **Secondary sources** (two media articles), not manufacturer data. The URL is in `source`; the retrieval date and the wording are in `note`.
- The articles call the line `ファミリーサイズ カントリーマアム（バニラ＆ココア）` and `大袋`. They are **treated as the same line** (an assumption, recorded in the notes).
- Recorded only where the article gives a year. Not recorded as dated rows: the 10.5 g before 2014 (no start year), the 30-piece period of the other article (no year), and the 16 pieces before the 2024-09-24 change of 贅沢バニラ / 贅沢チョコ (no start year).
- No price series is available yet, so the unit-price level cannot be computed for the real product.
- Never mix these rows with the synthetic ones (`docs/data-policy.md`).

## Synthetic data: `synthetic_shrink_vertical.csv` (SYNTHETIC)

Fictional products with a known truth, 1992-2024, written to a separate file. `country = SYN`, `variable = synthetic_shrink:<ID>_<name>:<measure>`, `unit` ends with `(synthetic)`, `source` starts with `SYNTHETIC`. A **recommended condition**, not an acceptance condition; a result on synthetic data is never a conclusion about a real product. Rules are fixed in `synthetic_shrink.py`; do not change one after seeing a result, add a new pattern with a new ID.

| ID | Name | n (pieces) | w (g per piece) | What it tests |
|---|---|---|---|---|
| M1 | gradual_slide | 30 | 10 * exp(-0.02 t) | plausible: a steady slide |
| M2 | stepwise_pieces | 30 - 2 * floor(t / 6) | 10 | steps in the piece count |
| M3 | accelerating | 30 | 10 * exp(-0.002 t^2) | the slide speeds up and enters the zone |
| M4 | pieces_nonmonotone | 30 + 3 * (floor(t / 8) mod 2) | 10 * exp(-0.015 t) | pieces alone say "no shrink"; the total says otherwise |
| M5 | price_fixed_quantity_down | 30 | 10 * exp(-0.02 t) | price held at 300; the unit price rises |
| M6 | growth_impossible | 30 | 10 * exp(0.01 t) | the content grows: not a shrinking product |
| M7 | hits_zero_nonexistent | 30 | 10 * (1 - t / 32) | the weight reaches exactly 0 in the last year |
| M8 | rounded_noisy_sparse | 30 | M1 with noise 0.05 in log, rounded to 0.5 g | only 4 points (1992, 2002, 2012, 2024): insufficient |

`t = year - 1992`. M8 is the only pattern with randomness (`random.Random(20261024 + 7)`).

## Commands

```bash
python research/shrink-index/shrink_index.py --product shrink:countrymaam_family_vanilla_cocoa
python research/shrink-index/shrink_index.py --product shrink:countrymaam_family_vanilla_cocoa --assume-weight 2005:10.5,2007:10.5
python research/shrink-index/shrink_index.py --product shrink:countrymaam_family_vanilla_cocoa --danger-total 60 --whatif
python research/shrink-index/synthetic_shrink.py --check
```

## Not made yet

Other products (gram-based items, items sold at a fixed price with a shrinking quantity), a real price series, a danger level for a single piece (`q_d` on w instead of on q), hooking the index into the proposition engine (`docs/propositions.md`), and patterns for mixed units.
