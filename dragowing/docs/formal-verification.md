# Formal verification of overlap partitions

`formal/OverlapPartition.lean` models the row-index partition constructed by
`dragowing.py::load_overlap()`. It verifies bookkeeping before visualization.
Normal execution remains standard-library-only; the fixed Lean toolchain is
used in a separate verification lane, without Mathlib. The runner and
named-theorem axiom audit come from the
[parent's `lean_verify.py`](https://github.com/myon-bioinformatics/myon-bioinformatics/blob/main/lean_verify.py).

## Model and guarantees

For `rows` observations and `sets` conditions, each row has one signature in
`Fin (2 ^ sets)`: the code for its Boolean condition vector. The model enumerates
every signature and filters the original row-index list for each region.
Row indices, rather than display labels or complete row values, identify
observations. Identical records therefore remain distinct observations.

| Audited theorem, in namespace `DRAgoWing` | Guarantee | Python connection |
| --- | --- | --- |
| `region_contains_exact_signature` | An index belongs to a region exactly when its signature equals that region's signature | The `all(bits[i][j] == on ...)` filter inside `load_overlap()` |
| `every_row_once` | Every original index occurs exactly once across the concatenation of all regions | `_patterns()`, each region's `unit_index`, and `_overlap_result()` |

The theorem concerns arbitrary finite row counts and condition counts. There
are no fabricated indices because each region filters `List.finRange rows`.
Each index's multiplicity is one, so a missing row cannot be hidden by a
duplicated row elsewhere. The runtime's total-count check is a useful final
consistency check, but does not by itself establish this stronger property.
`_overlap_result()` is not being promoted to a validator for arbitrary
caller-supplied region structures.

The mapping from Python's Boolean tuples to finite codes, and the comparison
semantics that produce those tuples, are connection assumptions rather than
Lean proofs of the Python evaluator. The model does not depend on record names,
team identities, numerical coordinates, or the significance of a condition.

## Independent connection tests

`tests/test_formal_overlap_partition.py` calls the actual stdlib `load_overlap()`
on temporary JSONL files. Fixtures supply the expected truth vectors directly;
the oracle uses Cartesian Boolean products and a dictionary of row-index
lists. Neither overlap backend nor `condition_bits()` computes the expected
partition.

The tests enumerate every Boolean pattern for condition counts 0 through 8,
reverse input order, and repeat exact records. All display unit labels are the
same, so a label-based join or deduplication would fail. They compare each
region's ordered index list, each row's signature, region enumeration, and a
frequency table requiring every original index to occur once.

A second fixture combines duplicate conditions, complementary conditions,
null and missing cells, and an always-false null comparison. Three condition
orders verify that unreachable regions remain empty and that permutations
change signature positions without losing observations. There are two unittest
methods with 12 subcases.

The low-level overlap API accepts zero or one condition; the grid display
requires 2 through 8. Testing the low-level boundary does not change that display
contract. Existing `tests/test_overlap_stdlib.py` still checks native/stdlib
parity and scalar/schema boundaries; `tests/test_venn.py` checks the figure
specifications. The independent index oracle complements those tests because
the two backends share `_patterns()` and `_overlap_result()`.

The test file has a specific basename and supports both the standalone module
and pytest's `dragowing` package. It does not require changes to Aoi's list of
special-case test basenames or to pytest's import mode.

## Limits

Applying the model to Python requires well-shaped Boolean signatures and
correspondence between `_patterns()` and the model's complete finite
enumeration. Input parsing, null semantics, floating-point comparisons, schema
inference, and unsupported-input rejection remain Python responsibilities.
Their supported range is documented in
[the stdlib overlap guide](overlap-stdlib.md).

The proof does not verify the whole Python program, native dependencies,
Plotly, browser rendering, color or layout choices, image appearance, or the
scientific correctness of the conditions. `structure_figure()` and its XYZ
coordinate rendering are outside this model. DRAgoWing continues to display
recorded results; the partition proof adds no scientific judgment.

## Run

The connection tests need no third-party libraries or Lean:

```sh
python -S -m unittest discover -s tests -p test_formal_overlap_partition.py -v
```

With the parent repository checked out alongside this repository as
`myon-bioinformatics`, run the shared verifier:

```sh
python -S ../myon-bioinformatics/lean_verify.py \
  --cwd formal --required --json-output build/lean-verification.json \
  --theorem DRAgoWing.region_contains_exact_signature \
  --theorem DRAgoWing.every_row_once \
  OverlapPartition.lean
```

The dedicated CI lane uses the parent workflow at a fixed commit. Missing Lean
means **unverified** and fails the required lane. Proof failure, warnings,
`sorryAx`, and unexpected axiom dependencies also fail. Normal Python execution
and its tests do not require Lean.
