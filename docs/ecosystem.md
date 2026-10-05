# Aoi Ecosystem

This document defines the structure of the Aoi ecosystem.

Aoi is intentionally designed as a collection of independent projects rather than a single monolithic application.

Each project exists to answer a different type of question.

Together, they form a continuous research and understanding cycle.

---

# Ecosystem Overview

The Aoi ecosystem currently consists of six primary projects.

```text
Reality
    │
    ▼

BlueProbe
    │
    ▼

QueRyu
    │
    ▼

SakAnalytics
    │
    ▼

DRAgoWing
    │
    ▼

PythDRagoras
    │
    ▼

New Questions
    │
    ▼

Reality
```

Automation and orchestration are provided by NagoyAction, which operates across the entire ecosystem.

---

# Design Philosophy

The ecosystem is not organized around technologies.

It is organized around understanding.

Each project owns a different stage of the research process.

This separation exists to prevent responsibilities from becoming mixed.

Observation is different from analysis.

Analysis is different from visualization.

Visualization is different from explanation.

Explanation is different from validation.

The ecosystem preserves these distinctions.

---

# BlueProbe

## Purpose

Observation and discovery.

## Fundamental Question

> What actually exists?

BlueProbe is responsible for interacting with reality as directly as possible.

Its role is not to explain.

Its role is not to analyze.

Its role is to observe.

Examples:

- crawling
- parsing
- source inspection
- HTML analysis
- structure discovery
- cache inspection
- data acquisition research

BlueProbe prefers observation over interpretation.

Unknown structures should remain visible.

Unexpected structures should be reported.

---

# QueRyu

## Purpose

Retrieval and execution.

## Fundamental Question

> How can information be accessed reliably?

QueRyu sits between raw observations and analytical systems.

Its primary concern is reproducibility.

Examples:

- querying
- data loading
- execution pipelines
- dataset generation
- command interfaces
- reproducible extraction

QueRyu focuses on obtaining information consistently.

---

# SakAnalytics

## Purpose

Statistical and analytical reasoning.

## Fundamental Question

> What patterns can be measured?

SakAnalytics contains the analytical knowledge of the ecosystem.

Examples:

- statistics
- hypothesis testing
- residual analysis
- distributions
- prediction models
- evaluation metrics

SakAnalytics transforms observations into measurable structures.

Implementation: [remaining-season simulation, CS probability and title magic](../SakAnalytics/baseball/SEASON_SIMULATOR.md).

---

# DRAgoWing

## Purpose

Visualization and communication.

## Fundamental Question

> How can understanding become visible?

Not every discovery is useful if it cannot be communicated.

DRAgoWing exists to make structures visible.

Examples:

- charts
- diagrams
- reports
- dashboards
- visual storytelling
- exploratory visualizations

DRAgoWing serves as the visual layer of Aoi.

---

# NagoyAction

## Purpose

Automation and orchestration.

## Fundamental Question

> How can research be repeated reliably?

NagoyAction manages execution across the ecosystem.

Examples:

- scheduled workflows
- orchestration
- automation
- pipelines
- operational tasks
- repeatable research processes

Its purpose is reliability rather than analysis.

---

# PythDRagoras

## Purpose

Hypothesis generation and explanation validation.

## Fundamental Question

> Are we sure this explanation is sufficient?

PythDRagoras is unique within the ecosystem.

Every other project contributes toward understanding reality.

PythDRagoras contributes toward questioning understanding itself.

Examples:

- residual investigation
- contradiction analysis
- model validation
- hypothesis generation
- explanation boundaries
- assumption discovery

PythDRagoras is not an answer engine.

PythDRagoras is a question engine.

Its role is to identify:

- unexplained outcomes
- hidden assumptions
- model boundaries
- opportunities for new hypotheses

---

# Information Flow

A simplified view of ecosystem interactions:

```text
Reality
    │
    ▼

BlueProbe
Observe

    │
    ▼

QueRyu
Retrieve

    │
    ▼

SakAnalytics
Analyze

    │
    ▼

DRAgoWing
Visualize

    │
    ▼

PythDRagoras
Question

    │
    ▼

New Hypothesis

    │
    ▼

Reality
```

The cycle intentionally loops.

Understanding is never considered complete.

---

# Independence

Each project should remain independently usable whenever practical.

This provides several benefits:

- easier maintenance
- clearer responsibilities
- simpler testing
- better documentation
- future reuse outside Aoi

Projects may evolve separately while still sharing common philosophy.

---

# Shared Principles

Every ecosystem project must follow:

- GENESIS.md
- philosophy.md
- principles.md

Implementation details may differ.

The philosophy should remain consistent.

---

# Future Expansion

The ecosystem described here is not final.

New projects may emerge.

Existing projects may split.

Existing projects may merge.

The ecosystem should evolve when evidence suggests a better structure.

The objective is not stability.

The objective is understanding.

---

# Final Principle

The Aoi ecosystem exists because understanding is not a single activity.

Observation.

Retrieval.

Analysis.

Visualization.

Validation.

Questioning.

Each deserves its own tools.

Together they create a system capable of improving explanations rather than merely producing them.
