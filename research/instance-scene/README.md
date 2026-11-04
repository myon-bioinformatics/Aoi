# Opt-in Layer 21 consumer experiment

Run against a reviewed checkout containing Ironmate's `scripts/instance_scene.py`:

```
python -S research/instance-scene/verify_stream.py --ironmate-root ../Ironmate
```

This invokes a local Python stdlib JSON bridge, without duplicating the engine,
installing packages, fetching code, or changing fixed vendor/subtree references.
Only use a trusted local checkout. The subprocess uses `-S`, a fixed module name,
an explicit working directory, a 30-second timeout and explicit mismatch failure
(which remains active under `python -O`).

The synthetic stream preserves two identical-archetype IDs through a velocity-
disambiguated crossing, then checks disappearance and a new ID after reappearance.
It does not interpret NPB team counts as image detections, prove true physical
identity, benchmark 1,000 frames, or claim MOTA/accuracy numbers. Fully merged
same-class observations remain unresolved. No Layer 1–20 master engine was found
in this integration; compact-bitmask remains a separate feature-space experiment.

The engine PR must land before this becomes usable with Ironmate main. It is an
explicit development-checkout integration, not a new runtime dependency.
