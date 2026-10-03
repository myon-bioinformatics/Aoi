# Aoi Principles

This document describes the operational principles of the Aoi ecosystem.

While philosophy explains what Aoi believes, principles explain how those beliefs should influence implementation, analysis, documentation, and decision-making.

If philosophy represents intent, principles represent behavior.

These principles apply equally to:

- humans
- AI contributors
- automated agents
- analytical systems
- future sub-projects

---

# Principle 1: Observe Before Explaining

Observation always comes before interpretation.

Before proposing explanations, preserve observations.

Before creating theories, preserve evidence.

Before making assumptions, preserve uncertainty.

In practice:

- Store evidence.
- Store raw observations.
- Preserve original context.
- Delay interpretation whenever possible.

Aoi values observation more than premature explanation.

---

# Principle 2: Never Hide Unknowns

Unknown information must remain visible.

Unknown does not mean failure.

Unknown means more investigation is required.

Do not:

- silently discard records
- silently normalize data
- silently fill gaps
- silently remove anomalies

Instead:

- report unknown observations
- document uncertainty
- expose assumptions

A visible unknown is better than invisible error.

---

# Principle 3: Separate Facts From Explanations

Facts and explanations must never be merged.

Example:

Fact:

> Team A finished 5th.

Explanation:

> Team A finished 5th because its offense was poor.

The first statement is an observation.

The second statement is an interpretation.

Aoi requires those distinctions to remain explicit.

---

# Principle 4: Preserve Contradictions

Contradictions are valuable.

When observations contradict expectations:

do not remove the contradiction.

Investigate it.

A contradiction may reveal:

- hidden variables
- flawed assumptions
- model boundaries
- incorrect abstractions

Contradictions are often where discovery begins.

---

# Principle 5: Treat Residuals As Evidence

Residuals should not automatically be dismissed as noise.

A gap between:

- prediction and outcome
- expectation and observation
- model and reality

may contain important information.

Whenever possible:

- calculate residuals
- preserve residuals
- investigate residuals

Residuals are first-class research artifacts.

---

# Principle 6: Prefer Reproducibility

Any result should be reproducible.

Future researchers should be able to answer:

- What was collected?
- How was it processed?
- What assumptions were introduced?
- How was the conclusion reached?

If a result cannot be reproduced, its value becomes limited.

---

# Principle 7: Prefer Simplicity Over Complexity

Complexity must justify itself.

A simple explanation that survives evidence is generally preferable to a complex explanation that merely fits observations.

Avoid:

- unnecessary models
- unnecessary abstractions
- unnecessary transformations

Complexity is not evidence of quality.

---

# Principle 8: Preserve Traceability

Every important conclusion should be traceable.

A reader should be able to move from:

Conclusion
↓
Analysis
↓
Observation
↓
Source

without losing context.

Traceability is required for trust.

---

# Principle 9: Questions Are Legitimate Outputs

Not every investigation produces an answer.

Sometimes an investigation produces a better question.

This is acceptable.

Aoi explicitly recognizes:

- hypotheses
- open questions
- unresolved contradictions
- unexplained outcomes

as meaningful outputs.

---

# Principle 10: Models Must Remain Replaceable

No model is permanent.

No framework is sacred.

No metric is final.

Every model should be designed with the expectation that:

- new evidence may appear
- assumptions may fail
- better explanations may emerge

Adaptability is a feature.

---

# Principle 11: Local Optimization Must Not Override Philosophy

An implementation may appear technically superior while violating Aoi's goals.

Examples include:

- hiding uncertainty to improve presentation
- discarding observations to improve success rates
- prioritizing prediction over understanding
- removing contradictions because they are inconvenient

Such optimizations are discouraged.

The philosophy of Aoi takes priority over local performance gains.

---

# Principle 12: Evidence Comes Before Conclusions

Aoi does not begin with answers.

Aoi begins with observations.

Conclusions are temporary.

Evidence remains primary.

Whenever evidence and explanation disagree:

investigate the explanation first.

Never force reality to fit a model.

---

# Principle 13: Follow The Question

Aoi was created because one explanation felt insufficient.

The purpose of the project is not to defend a particular outcome.

The purpose is to follow questions wherever evidence leads.

Future evidence may:

- support current assumptions
- modify current assumptions
- invalidate current assumptions

All outcomes are acceptable.

Truth is preferred over consistency.

---

# Final Principle

Observe.

Measure.

Question.

Repeat.

Every explanation is temporary.

Every contradiction is valuable.

Every residual is evidence.

Every question is an opportunity for discovery.
