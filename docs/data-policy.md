# Aoi Data Policy

This document defines how data should be collected, stored, transformed, preserved, and interpreted within the Aoi ecosystem.

Data is not merely an input.

Data is evidence.

Evidence is one of the foundations of understanding.

For this reason, data handling must remain consistent with the philosophy of Aoi.

---

# Core Principle

The primary objective of data handling within Aoi is not convenience.

The primary objective is preserving the ability to investigate reality.

A dataset is valuable not because it supports a conclusion.

A dataset is valuable because it makes investigation possible.

---

# Evidence Before Conclusions

Data must not be altered to fit an explanation.

Explanations may change.

Data should remain stable.

Whenever possible:

- preserve original observations
- preserve intermediate transformations
- preserve final outputs

Future investigators should be capable of revisiting earlier decisions.

---

# Raw Data Is Sacred

Raw observations occupy the highest level of trust.

Whenever technically and legally possible:

raw data should be preserved.

Examples:

- downloaded files
- HTML documents
- source records
- logs
- API responses

Processed outputs should never replace the original source.

---

# Unknown Is Better Than Silent Failure

Aoi strongly prefers visible uncertainty.

Unknown values should be recorded rather than discarded.

Unknown structures should be preserved rather than ignored.

Examples:

Preferred:

```text
status = UNKNOWN
```

Not preferred:

```text
record silently removed
```

Missing information is evidence.

Hidden missing information is risk.

---

# Every Transformation Must Be Explainable

Whenever data changes:

the transformation should be understandable.

Questions that future researchers should be able to answer:

- What changed?
- Why did it change?
- When did it change?
- Which process changed it?

Transformations should be documented whenever practical.

---

# Preserve Traceability

Every important record should maintain a connection to its source.

The path should be reconstructable.

```text
Conclusion
↓
Analysis
↓
Dataset
↓
Source
```

Traceability allows independent verification.

Without traceability, confidence becomes difficult to justify.

---

# Missing Data

Missing data is itself a form of information.

Do not automatically:

- delete missing values
- replace missing values
- estimate missing values

without documentation.

If an estimated value is introduced:

the estimation should be clearly labeled.

Future users should always be able to distinguish:

- observed values
- derived values
- estimated values

---

# Divergence Is Information

A derived value can diverge: a ratio whose denominator is close to zero, a logarithm of zero, a rate over an empty group.

Divergence is not a failure of the data, and it is not a reason to discard a measure.
Calling a diverging measure "unusable" is often impatience with data that cannot be obtained, not a property of the data.

When a value diverges:

- record which units diverge and which converge. Divergence on one side only (for example, the focus team converges while the others diverge) is itself an observation and can become the next proposition
- do not silently replace the measure. If another form is used, record the change and the reason
- read the same quantity in several forms and check whether the reading survives all of them. Typical forms for a ratio near zero:
  - mean of ratios (diverges)
  - ratio of means
  - median of ratios (reads by order)
  - mode of binned ratios (a typical value; undefined when units scatter, which is also information)
  - mean of logarithms, returned with exp (compresses large ratios; defined only for positive values)
  - a bounded share such as a ÷ (a + b), kept between 0 and 1
- no form is correct by default. A reading that changes direction between forms is not stated as a conclusion

---

# Unknown Formats

Unknown formats should be treated as observations.

Unknown data can indicate:

- source changes
- parser failures
- previously unseen structures
- new categories

Unknown formats should therefore be reported.

Whenever possible:

store examples.

Do not silently discard them.

---

# Historical Preservation

Data should remain available even after newer versions appear.

Older datasets are often required for:

- validation
- replication
- historical comparison
- hypothesis testing

History is part of the evidence.

---

# Reproducibility

A dataset should be reproducible whenever practical.

Future investigators should be able to answer:

- Where did the data come from?
- How was it collected?
- How was it processed?
- Which version produced it?

Reproducibility is required for reliable validation.

---

# Prefer Documentation Over Assumption

When uncertainty exists:

document it.

When assumptions exist:

document them.

When interpretation is necessary:

document it.

Future investigators should not be forced to rediscover implicit decisions.

---

# Data Quality Hierarchy

Aoi generally prioritizes data quality as follows:

```text
Observed Source Data
        >
Validated Derived Data
        >
Estimated Data
        >
Assumed Data
```

The further a dataset moves from direct observation, the more documentation becomes necessary.

---

# Data Retention Philosophy

Storage is generally cheaper than rediscovery.

If a record may become useful later:

preserve it.

Data should not be discarded merely because its current value is unclear.

The future may reveal significance that is not visible today.

---

# Data And Residuals

Residuals are first-class research artifacts.

Residual data should be preserved whenever possible.

Examples:

- prediction errors
- expectation gaps
- unexplained observations
- contradictory outcomes

Residuals often generate new hypotheses.

Deleting them destroys future opportunities for understanding.

---

# Data And Automation

Automation should never override evidence preservation.

An automated process that silently drops information violates Aoi principles.

When uncertainty occurs:

- log it
- record it
- report it

Automation exists to assist investigation.

Not to hide complexity.

---

# Data And AI Systems

AI-generated information must always remain distinguishable from observed data.

Never mix:

- observed records
- inferred records
- generated records

without labeling.

Users of a dataset should always know which information originated from evidence and which originated from inference.

---

# Data Lifecycle

Within Aoi, data generally follows this lifecycle:

```text
Observation
    ↓

Collection
    ↓

Preservation
    ↓

Transformation
    ↓

Analysis
    ↓

Validation
    ↓

Archival
```

At every stage:

evidence should remain recoverable.

---

# Final Principle

Data is not merely a resource.

Data is memory.

Data is evidence.

Data is the record of what reality allowed us to observe.

For this reason:

Preserve observations.

Preserve uncertainty.

Preserve history.

Preserve residuals.

Aoi does not seek to collect data in order to support conclusions.

Aoi collects data so that conclusions remain challengeable.
