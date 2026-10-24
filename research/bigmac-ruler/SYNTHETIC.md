# Synthetic staples (SYNTHETIC)

Fictional staples for the Big Mac ruler (cycle 2). **They are generated, not observed.**

## Why

Real staple prices are scarce, and a few real series invite early conclusions (a straight line, a rounded number, a convenient subset). A synthetic staple has a **known truth**, so a test or a proposition can be tried on it first and its behaviour can be read before it is read on real data. Patterns range from plausible to impossible to nonexistent on purpose.

## What it is and is not

- A **recommended condition** for preparing propositions. It is not a completion condition or an acceptance condition.
- A result on synthetic data is never a conclusion about real data. Synthetic rows never count as real observations (see `docs/propositions.md`: synthetic evidence never increases the count of real observations).
- The generation rules are fixed in `synthetic_staples.py` **before** the results are read. They are a round grid over structure, not values chosen from estimates on real data. Do not change a rule after seeing a result; add a new pattern with a new ID instead.

## Labelling (`docs/data-policy.md`: never mix observed and generated records without labelling)

- Generated rows live in `synthetic_staples_vertical.csv`, a separate file. Never append them to `staple_survey_vertical.csv`.
- `variable = synthetic_staple:<id>_<name>`, `unit` ends with `(synthetic)`, `source` starts with `SYNTHETIC`, and `note` records the generation parameters.

## Generation rule

The covariates are real: every country-year in 2021-2025 that has E (food share), household consumption, population and two Big Mac prices in the year. Only the response (the staple price) is synthetic.

```text
log b = log B0 + beta*(log E - median) + gamma*(log M - median) + eps,   eps ~ N(0, sigma^2)
b = staple price / Big Mac price,   M = household consumption per person / Big Mac price
staple price (local currency) = b * Big Mac price,   B0 = 0.5,   seed = 20261024 + pattern index
```

| ID | Name | beta | gamma | sigma | Step | What it tests |
|---|---|---|---|---|---|---|
| S1 | plausible_rice_like | 0.5 | 0.5 | 0.2 | no | plausible: partly Big Mac, partly household |
| S2 | bigmac_tracking | 0 | 0 | 0.2 | no | price follows the Big Mac only |
| S3 | household_tracking | 1 | 1 | 0.2 | no | price follows household spending; the Big Mac cancels out |
| S4 | luxury | 0 | 1.5 | 0.2 | no | rich countries pay disproportionately more |
| S5 | inverse | 0 | -0.5 | 0.2 | no | rich countries pay less (close to impossible) |
| S6 | noisy_measurement | 0.5 | 0.5 | 1.0 | no | S1 with five times the noise: how much noise hides the structure |
| S7 | step_discontinuity | 0.5 | 0.5 | 0.2 | x3 above median M | continuity is broken: the smooth fit is the wrong model |
| S8 | constant_nonexistent | 0 | 0 | 0 | no | every country always pays B0: the fit cannot be judged (R2 undefined) |

## Commands

```bash
python research/bigmac-ruler/synthetic_staples.py --check       # does the fit recover the known truth?
python research/bigmac-ruler/synthetic_staples.py --calibrate   # how often does the 95% CI contain the truth?
```

## Candidates not made yet

Prices of zero mixed in (log handling), shrinking quantities (shrinkflation), and a price that ignores the currency unit. Each would be a new pattern with a new ID.
