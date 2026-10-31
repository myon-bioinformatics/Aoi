# numpy_min acceptance contract v2

Version: `numpy-min-decomposition-v2`, 2026-10-31. This explicitly replaces
mandatory NumPy end-to-end score/ranking parity, following owner approval.
It does **not** retroactively turn the old comparison failures into successes.

## What a green v2 check means

For the tested supported operations, both available backends must satisfy the
operation-level tests. SVD tests check reconstruction, **both** U and Vt
orthogonality, finite/nonnegative/descending singular values, shape and dtype.
They do not require identical singular vectors, binary scores or candidate IDs.
This is an approximate implementation, not a bitwise NumPy replacement.
A passing finite fixture suite is not a universal error-bound proof.

New tiny, analytically specified fixtures exercise both dtypes, rectangular and
square matrices, repeated/zero singular values, and scales 1/8, 1 and 8. Their
policy budget is declared as `32 * max(m,n) * eps(dtype)` for dimensionless
1-norm residuals. Reconstruction is scaled by `||A||_1`; singular-value error
by the same norm; zero input requires exactly zero singular values and
reconstruction. Both orthogonality residuals use the same dimensionless budget.
The coefficient 32 is an explicit engineering acceptance policy, **not** a
proven universal constant, an observed corpus maximum, or a score tolerance.
Existing tighter full-rank tests remain unchanged except for adding U checks.

This normalization follows the structure of LAPACK's
[DBDT01 reconstruction test](https://raw.githubusercontent.com/Reference-LAPACK/lapack/master/TESTING/EIG/dbdt01.f).
LAPACK's [error analysis](https://netlib.org/lapack/lug/node97.html) distinguishes
backward error from singular-vector/subspace error, which also depends on
spectral separation. Its guarantees must not be presumed for the custom Gram
or Jacobi implementation without validation.

## Backend differences and preserved failures

The historical v1 c001 comparison is preserved, with its assertions and latest
owner thresholds unchanged, in `scripts/legacy_numpy_min_parity.py` (source
snapshot `0284b2198077d9b8c04b3cffde1b36b8e75961b6`). It is deliberately outside
the ordinary test suite. Explicit manual invocation still enforces that old
contract and can fail. It is **not** xfailed, skipped, or silently made green.
Running it is a new corpus measurement and requires separate authorization.

Earlier failed thresholds and actual failures are recorded in
[`evidence/numpy-min-parity-history.json`](../evidence/numpy-min-parity-history.json).
They remain failed observations. No new c001 results were collected for v2.

Repeated singular values allow rotated bases. Binary compression uses coordinate
signs and per-coordinate magnitudes, so it is not rotation-invariant even with
exact arithmetic. The saved three-document example and an analytic rotation
counterexample remain explicit. Float Gram invariance requires the same retained
subspace; truncating through a cluster and normalizing near-zero vectors require
additional conditioning analysis. Candidate order is backend-specific; ranking
stability cannot be inferred merely from reconstruction accuracy.

## Supported scope and unresolved numerical limitations

The stdlib SVD dispatcher uses Gram/Jacobi when `max(m,n)>400` and
`min(m,n)<=200`, otherwise one-sided Jacobi. Exact-zero vector completion fixes
the previously returned zero vectors, without changing positive singular values.

The earlier Gram route left a factor vector zero for positive
`sigma <= sigma_max * 1e-12`. For example, a 2-by-401 matrix with only
`A[0,0]=1` and `A[1,1]=1e-13` reaches that public route. That historical result
was not a valid orthonormal SVD. The repaired route now detects this specific
strictly-positive suppression condition and delegates to the existing one-sided
Jacobi solver using the original input. The cutoff itself is unchanged; exact
zero and unaffected positive spectra retain their prior paths. Tiny public-path
regressions cover both orientations, affected positive values, unaffected values,
and exact zero; they check the small reconstructed component itself as well as
both orthogonality conditions.

The affected path performs Gram work followed by one-sided work and may cost
more. No performance or corpus measurement was performed to quantify that cost.
This targeted fallback is not a comprehensive repair of Gram conditioning:
formation of the Gram matrix can still lose information, and the trigger does
not certify all remaining singular values or factors. No v2 claim covers
arbitrary ill-conditioned, underflow/overflow, or unconverged cases. Both Jacobi
routines have finite sweep limits; comprehensive convergence certification
remains unverified. Finite tests must not be described as certifying every
decomposition.
