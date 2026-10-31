# Pack-ratio sensitivity — pre-declaration only (NOT RUN)

Date: 2026-10-24 (Asia/Tokyo)  
Amended: 2026-10-24 (Asia/Tokyo) — test-year lock, family reading rule, % formula condition, E 1999→2000 flag; Implications 表を R ごとの値に差し替え（「20〜40円」廃止）

**Status:** Pre-lock / declaration only. **No R-grid executed. No adoption re-run. No new metrics.**  
Execution is **not urgent**: existing judgment windows (2005 / 2010 / 2015+) all start in **2002+**, so R uncertainty does **not** affect those locked judgments.

Judgment windows remain **2005 / 2010 / 2015+**.  
Existing adoption judgment (`claude_adoption_judgment_2026-10-24.md`) is **not rewritten**.

Context: `pack_unit_ratio_overlap.md` — ÷2 is a splice convention; equal ¥/kg not confirmed; measured R span **1.81〜2.03**.

## Series roles (unchanged)

| series | years | n | role if sensitivity ever runs |
|--------|-------|---|-------------------------------|
| `5kg_continuous` | 2002–2025 | 24 | Main — judgment reference (unchanged) |
| `connected_packscale` | 1999–2001 | 3 | Sensitivity rows only |

## Pre-declared rules (if/when 1999–2001 sensitivity is run)

### 1. Level — one sensitivity family
- Candidate splice ratios: **R ∈ {1.8, 1.9, 2.0, 2.05}**
- Treat as **one sensitivity family** (not four separate claims).
- When counting multiplicity **m**, add **+1 family** (not +4).
- Conversion if applied: `P_yen = price_10kg / R`, `q_kg = 5.0` (same column semantics as the locked ÷2 rule, with R replacing 2).
- Do **not** promote any single R to a new primary form.

### 2. Test years fixed to the main window
- Move **only** training start and R. **Do not** move the set of test years.
- If training starts in 1999, the first rolling test year would become 2004 and would **not** match the main judgment windows — that misalignment is forbidden for the sensitivity row.
- Sensitivity rows use the **same test years** as the corresponding main window (2005 / 2010 / 2015+ designs as already declared). Training may start earlier (e.g. 1999) while OOS years stay those of the main window.

### 3. Family reading rule (no best-R cherry-pick)
- Report the four R results as one family.
- Write **「R に依らない」** only when **all four R** agree in direction / qualitative conclusion.
- **Do not** select the best R and treat it as the family result.
- Otherwise “+1 family” undercounts exploration (same spirit as m_eff for best-form claims).

### 4. YoY — no R grid
- Inside 1999–2001, a constant R **cancels** in year-over-year ratios.
- R affects only the **2002 splice** YoY (2001→2002).
- Rule: **exclude or flag** that splice year-over-year point.
- **Do not** run an R grid for YoY.
- Also **flag** **1999→2000** YoY: E definition break (農林漁家を除く → 含む). Same treatment spirit as the pack splice point. Note: 2000 E was 23.3% under both definitions in available tables, so expected impact is small — still flag, do not silently ignore.

### 5. Mean-K shift formula (condition on the “1〜2% / 20〜40円” remark)
- The rough “1〜2%（20〜40円）” figure is for the case **3 of 11 training years** shift by factor `2/R`.
- General: fractional mean-K shift ≈ `(3 / n_train) × (2/R − 1)` when exactly those three pack-scale years are in the training sample (and other years unscaled).
- Longer train → smaller shift. Example: `n_train=26`, `R=1.9` → ≈ `3/26 × (2/1.9 − 1)` ≈ **0.6%**.
- Always state `n_train` and R when quoting a % or yen impact.

### 6. What this prelock does *not* authorize
- Running the R grid now
- Rewriting windows or adoption conclusions
- Adding new shells / metrics / forms beyond the R family above
- Mixing `connected_packscale` into the main continuous judgment panel
- Changing test years relative to the main window

## Implications already recorded (for when a run is authorized)

See also splice table in `pack_unit_ratio_overlap.md`:

| R | splice K scale vs ÷2 | 2001→2002 YoY |
|---|----------------------|---------------|
| 1.8 | +11.1% | −8.8% |
| 1.9 | +5.3% | −3.7% |
| 2.0 | 0% | +1.4% |
| 2.05 | −2.4% | +3.9% |

Mean-K shift under **n_train=11** (3 pack-scale years in train), formula §5, with rough yen at P≈2,100:

| R | mean K shift (n_train=11) | ≈ yen (P≈2,100) |
|---|---------------------------|-----------------|
| 1.8 | +3.0% | +63円 |
| 1.9 | +1.4% | +30円 |
| 2.05 | −0.7% | −14円 |

The older phrase「1〜2%（20〜40円）」was approximately the **R=1.9, n_train=11** case (~**+1.4% / +30円**), not the whole R grid. Always pair %/yen with R and n_train (§5).

Conclusion unchanged: legacy aoff 2020–21 win margins (~6–19円) can flip under R=1.8–1.9 (large move) and remain comparable even at R=2.05 (~14円).

## Timestamp
Declared 2026-10-24 (Asia/Tokyo). Amended same day with test-year lock, family reading, % condition, E 1999→2000 flag, and Implications 表を R ごとの値に差し替え（「20〜40円」廃止）. Execution requires a later explicit go-ahead; not urgent for existing windows.
