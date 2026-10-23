"""Bitwise symbolic surrogate and active holdout repair (experiment).

A feature vector is a Python int: bit ``i`` is set when feature ``i`` is present.
A rule in the proposed fragment is

    evaluate(X) = (X & M_AND) == M_AND
                  and (X & M_NOT) == 0
                  and every OR-clause mask shares a bit with X.

That is a conjunction of positive units, negative units, and positive
disjunctions. It is not general DNF. ``rule_search.py`` already searches
OR-of-AND rules with bitsets over *rows*. This module does not replace that
search and it does not judge a proposition.

Active repair edits the masks when a fresh labeled row disagrees with the
surrogate. Probe steps call an oracle on counterfactual vectors (``X`` with
some bits flipped). A column of observed labels is not enough: flipping
"rd < -50" on a historical team-season is not an observation this repository
stores. Known limits of the repair heuristic are listed on ``repair_disagreement``.

The module's import surface is the standard library and is written for
Python 3.9 (no ``int.bit_count``, no ``match``). Loading NPB rows is optional
and imports polars only inside ``season_report``.

Claimed fidelities, query counts, and microsecond timings from the external
proposal are not constants here. ``synthetic_report`` and ``season_report``
measure them. See ``docs/bitwise-surrogate-repair.md``.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import random
import secrets
import sys
import time

# Claimed feature story, used only as a synthetic index choice. These indexes
# are not columns in cycles/c001-chunichi/rule_candidates.toml (17 candidates).
CLAIMED_AND = (12, 19)
CLAIMED_NOT = (25,)
CLAIMED_SLIDE_TO = 20
CLAIMED_DECOY = 30
N_FEATURES = 40

SCHEMA = "pythdragoras-bitwise-surrogate-benchmark/1"


def _mask_value(value, name):
    if type(value) is not int or value < 0:
        raise ValueError("%s must be a nonnegative int" % name)
    return value


def mask_of(bits):
    """Pack feature indexes into a bitmask. Order does not matter."""
    out = 0
    for bit in bits:
        _mask_value(bit, "bit")
        out |= 1 << bit
    return out


def iter_bits(mask):
    """Ascending feature indexes. Python ``int`` is unbounded, so this walks the set bits."""
    _mask_value(mask, "mask")
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def bit_list(mask):
    return list(iter_bits(mask))


class BitwiseSymbolicSurrogate:
    """``M_AND``, OR-clause masks, and ``M_NOT`` as nonnegative Python ints."""

    def __init__(self, m_and=0, or_clauses=(), m_not=0):
        self.m_and = _mask_value(m_and, "m_and")
        self.m_not = _mask_value(m_not, "m_not")
        clauses = []
        for i, clause in enumerate(or_clauses):
            clause = _mask_value(clause, "or_clauses[%d]" % i)
            if clause == 0:
                raise ValueError("an OR clause mask must contain a feature")
            clauses.append(clause)
        self.or_clauses = clauses

    def copy(self):
        return BitwiseSymbolicSurrogate(self.m_and, tuple(self.or_clauses), self.m_not)

    def describe(self):
        return {
            "m_and_bits": bit_list(self.m_and),
            "or_clauses": [bit_list(clause) for clause in self.or_clauses],
            "m_not_bits": bit_list(self.m_not),
        }

    def evaluate_fast(self, x):
        """Proposal predicate. ``X & ~M_AND`` is well-defined: Python ints are two's complement."""
        _mask_value(x, "x")
        if (x & self.m_and) != self.m_and:
            return False
        if x & self.m_not:
            return False
        for clause in self.or_clauses:
            if (x & clause) == 0:
                return False
        return True

    def evaluate_reference(self, x):
        """Same predicate, written with sets so tests can catch a bitmask slip."""
        _mask_value(x, "x")
        have = set(iter_bits(x))
        if not set(iter_bits(self.m_and)) <= have:
            return False
        if set(iter_bits(self.m_not)) & have:
            return False
        for clause in self.or_clauses:
            if not (set(iter_bits(clause)) & have):
                return False
        return True


def compile_bit_dnf(groups):
    """Compile an OR of positive ANDs into this fragment, or return None.

    Exact cases include one conjunction, a common prefix AND a single
    disjunction of the leftover literals, and a shorter group that subsumes
    the others. ``[A AND B] OR [C AND D]`` does not fit. Negated literals are
    not accepted here; use ``distill_literals`` for those.
    """
    if not groups or any(not group for group in groups):
        return None
    normalized = []
    for group in groups:
        seen = []
        for bit in group:
            _mask_value(bit, "bit")
            if bit not in seen:
                seen.append(bit)
        normalized.append(seen)
    common = set(normalized[0])
    for group in normalized[1:]:
        common &= set(group)
    remainders = [[bit for bit in group if bit not in common] for group in normalized]
    if any(len(rest) > 1 for rest in remainders):
        return None
    # A group that is exactly the common prefix subsumes every longer group.
    if any(not rest for rest in remainders):
        return BitwiseSymbolicSurrogate(mask_of(common), (), 0)
    if len(remainders) == 1:
        return BitwiseSymbolicSurrogate(mask_of(list(common) + remainders[0]), (), 0)
    return BitwiseSymbolicSurrogate(mask_of(common), (mask_of(rest[0] for rest in remainders),), 0)


def distill_literals(literals):
    """Build a conjunction. ``literals`` is ``(bit, polarity)`` with True meaning required."""
    m_and = 0
    m_not = 0
    for bit, positive in literals:
        _mask_value(bit, "bit")
        if type(positive) is not bool:
            raise ValueError("polarity must be a bool")
        if positive:
            m_and |= 1 << bit
        else:
            m_not |= 1 << bit
    return BitwiseSymbolicSurrogate(m_and, (), m_not)


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError("%s must be a bool" % name)
    return value


def repair_false_negative(rule, x, oracle):
    """Proposal false-negative edit. Mutates ``rule``.

    For each missing AND bit, probe extras ``X & ~M_AND`` from low index to
    high and keep the first bit whose removal makes the oracle false. Relax
    the lost bit into the OR clause ``(lost | replacement)``, or drop it.
    Then clear forbidden bits that this positive actually has.

    The proposal does not say what to do when an OR clause misses. Those
    clauses are left in place and named in ``unhandled_missed_or``.
    """
    _mask_value(x, "x")
    missing = rule.m_and & ~x
    extras = x & ~rule.m_and
    probes = []
    edits = []
    for lost in iter_bits(missing):
        replacement = None
        for candidate in iter_bits(extras):
            verdict = _require_bool(oracle(x ^ (1 << candidate)), "oracle")
            probes.append({"lost": lost, "candidate": candidate, "oracle_true": verdict})
            if not verdict:
                replacement = candidate
                break
        rule.m_and &= ~(1 << lost)
        if replacement is None:
            edits.append({"op": "prune", "lost": lost})
        else:
            clause = (1 << lost) | (1 << replacement)
            rule.or_clauses.append(clause)
            edits.append({"op": "relax_or", "lost": lost, "replacement": replacement})
    hit_not = x & rule.m_not
    if hit_not:
        rule.m_not &= ~hit_not
        edits.append({"op": "clear_not", "bits": bit_list(hit_not)})
    missed = [bit_list(clause) for clause in rule.or_clauses if (x & clause) == 0]
    return {
        "kind": "false_negative",
        "probes": probes,
        "edits": edits,
        "unhandled_missed_or": missed,
    }


def repair_false_positive(rule, x, oracle):
    """Proposal false-positive edit. Mutates ``rule``.

    Binary-search the ascending extra bits. If ``oracle(X ^ left_half)`` is
    true, the inhibitory bit is assumed to lie in that half. The surviving
    bit is added to ``M_NOT`` even when flipping it alone does not make the
    oracle true (no extra probe is spent to check; that would change the
    query count).
    """
    _mask_value(x, "x")
    bits = bit_list(x & ~rule.m_and)
    probes = []
    if not bits:
        return {
            "kind": "false_positive",
            "probes": probes,
            "edits": [{"op": "no_extra_bit"}],
            "culprit": None,
        }
    lo, hi = 0, len(bits)
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        left = bits[lo:mid]
        left_mask = mask_of(left)
        verdict = _require_bool(oracle(x ^ left_mask), "oracle")
        probes.append({"left_bits": left, "oracle_true": verdict})
        if verdict:
            hi = mid
        else:
            lo = mid
    culprit = bits[lo]
    rule.m_not |= 1 << culprit
    return {
        "kind": "false_positive",
        "probes": probes,
        "edits": [{"op": "add_not", "bit": culprit}],
        "culprit": culprit,
    }


def repair_disagreement(rule, x, label, oracle):
    """Apply one proposal repair, or do nothing when the row already agrees.

    Limits, matching the proposal rather than patched around:

    - A false-negative probe stops at the first extra bit that flips the oracle.
    - Several lost bits can therefore be paired with that same bit.
    - A lost bit with no flipping candidate is deleted.
    - Every forbidden bit present on a row labeled positive is cleared.
    - A false positive commits one extra bit, including a bit that is not
      individually inhibitory.
    - Later rows can edit the rule again, including undoing a useful edit.
    - Labels that do not come from the same oracle as the probes (noise) are
      followed anyway.
    """
    _mask_value(x, "x")
    label = _require_bool(label, "label")
    predicted = rule.evaluate_fast(x)
    if predicted == label:
        return {"kind": "agree", "probes": [], "edits": [], "predict_before": predicted, "predict_after": predicted}
    if label:
        trace = repair_false_negative(rule, x, oracle)
    else:
        trace = repair_false_positive(rule, x, oracle)
    trace["predict_before"] = predicted
    trace["predict_after"] = rule.evaluate_fast(x)
    return trace


def active_repair(rule, rows, oracle, max_repairs=None):
    """Copy ``rule`` and repair the first disagreements in ``rows``.

    ``rows`` is a sequence of ``(x, label)`` or dicts with those keys plus an
    optional ``id``. ``max_repairs`` counts edits, not agreeing rows. The
    input rule is not mutated.
    """
    if max_repairs is not None and (type(max_repairs) is not int or max_repairs < 1):
        raise ValueError("max_repairs must be a positive int or None")
    edited = rule.copy()
    traces = []
    inspected = 0
    for index, row in enumerate(rows):
        if type(row) is dict:
            x, label = row["x"], row["y"] if "y" in row else row["label"]
            row_id = row.get("id", index)
        else:
            x, label = row
            row_id = index
        inspected += 1
        if edited.evaluate_fast(x) == _require_bool(label, "label"):
            continue
        trace = repair_disagreement(edited, x, label, oracle)
        trace["index"] = index
        trace["id"] = row_id
        trace["x"] = x
        traces.append(trace)
        if max_repairs is not None and len(traces) >= max_repairs:
            break
    return edited, traces, inspected


def rule_from_describe(description):
    """Inverse of ``describe`` for tests and report checks."""
    return BitwiseSymbolicSurrogate(
        mask_of(description["m_and_bits"]),
        tuple(mask_of(clause) for clause in description["or_clauses"]),
        mask_of(description["m_not_bits"]),
    )


def confusion(rule, rows):
    """Agreement with stored labels. Fidelity is ``(tp + tn) / n``."""
    tp = fp = fn = tn = 0
    for row in rows:
        if type(row) is dict:
            x, label = row["x"], row["y"] if "y" in row else row["label"]
        else:
            x, label = row
        label = _require_bool(label, "label")
        predicted = rule.evaluate_fast(x)
        if predicted and label:
            tp += 1
        elif predicted and not label:
            fp += 1
        elif label:
            fn += 1
        else:
            tn += 1
    n = tp + fp + fn + tn
    if n == 0:
        raise ValueError("confusion requires at least one row")
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "n": n,
        "fidelity": (tp + tn) / n,
        "precision": (tp / (tp + fp)) if (tp + fp) else None,
        "recall": (tp / (tp + fn)) if (tp + fn) else None,
    }


def label_of(x, required, forbidden):
    """Monotone conjunction used as a synthetic oracle."""
    for bit in required:
        if (x & (1 << bit)) == 0:
            return False
    for bit in forbidden:
        if x & (1 << bit):
            return False
    return True


def _draw(rng, n_features, on, off):
    on = set(on)
    off = set(off)
    if on & off:
        raise ValueError("a feature cannot be forced on and off")
    x = 0
    for bit in range(n_features):
        if bit in on or (bit not in off and rng.randrange(2)):
            x |= 1 << bit
    return x


def _draw_labeled(rng, n_features, required, forbidden, forced_off, positive):
    required = tuple(required)
    forbidden = tuple(forbidden)
    if positive:
        return _draw(rng, n_features, required, set(forbidden) | set(forced_off))
    modes = [("drop", bit) for bit in required] + [("set", bit) for bit in forbidden]
    kind, bit = modes[rng.randrange(len(modes))]
    on = set(required)
    off = set(forbidden) | set(forced_off)
    if kind == "drop":
        on.discard(bit)
        off.add(bit)
    else:
        off.discard(bit)
        on.add(bit)
    return _draw(rng, n_features, on, off)


def _balanced_rows(rng, n, n_features, required, forbidden, forced_off, id_prefix):
    if n < 2 or n % 2:
        raise ValueError("balanced draws use a positive even count")
    rows = []
    half = n // 2
    for positive in (True, False):
        for i in range(half):
            x = _draw_labeled(rng, n_features, required, forbidden, forced_off, positive)
            rows.append({
                "id": "%s-%s-%d" % (id_prefix, "pos" if positive else "neg", i),
                "x": x,
                "y": positive,
            })
    rng.shuffle(rows)
    return rows


def _ids(rows):
    return [row["id"] for row in rows]


def _timing(fn, values, min_seconds=0.05, min_calls=2000):
    for value in values:
        fn(value)
    start = time.perf_counter()
    calls = 0
    while True:
        for value in values:
            fn(value)
            calls += 1
        elapsed = time.perf_counter() - start
        if elapsed >= min_seconds and calls >= min_calls:
            break
        if calls >= 5_000_000:
            break
    return {
        "seconds": elapsed,
        "calls": calls,
        "seconds_per_call": elapsed / calls,
        "microseconds_per_call": elapsed / calls * 1e6,
    }


def _probe_queries(traces):
    return sum(len(trace["probes"]) for trace in traces)


def _scenario_record(name, rule, initial, repair_rows, eval_rows, oracle, note):
    one, traces_one, inspected_one = active_repair(rule, repair_rows, oracle, max_repairs=1)
    full, traces_full, inspected_full = active_repair(rule, repair_rows, oracle, max_repairs=None)
    return {
        "name": name,
        "note": note,
        "start_rule": rule.describe(),
        "initial": confusion(rule, initial),
        "unrepaired_eval": confusion(rule, eval_rows),
        "repaired_one_rule": one.describe(),
        "repaired_one_eval": confusion(one, eval_rows),
        "repaired_one_on_repair_rows": confusion(one, repair_rows),
        "repaired_all_rule": full.describe(),
        "repaired_all_eval": confusion(full, eval_rows),
        "repaired_all_on_repair_rows": confusion(full, repair_rows),
        "probe_queries_one": _probe_queries(traces_one),
        "probe_queries_all": _probe_queries(traces_full),
        "rows_inspected_one": inspected_one,
        "rows_inspected_all": inspected_full,
        "repairs_one": len(traces_one),
        "repairs_all": len(traces_full),
        "traces_one": traces_one,
        "repair_ids": _ids(repair_rows),
        "eval_ids": _ids(eval_rows),
        "ids_disjoint": set(_ids(repair_rows)).isdisjoint(_ids(eval_rows)),
    }


def synthetic_report(seed, n_features=N_FEATURES, n_initial=256, n_repair=64, n_eval=512, measure_time=True):
    """Seeded measurements. Numbers are observations for this protocol, not targets.

    Protocols (balanced classes, background bits Bernoulli 1/2, near-miss negatives):

    - ``feature_shift_dead``: F12 AND F19 AND NOT F25 becomes F12 AND F20 AND NOT F25,
      and bit 19 is forced off after the slide. One clean false negative is first
      in the repair stream.
    - ``feature_shift_residual``: the same slide, but bit 19 stays a free bit.
      The eval set includes one row that still has bit 19 and lacks bit 20.
    - ``new_decoy``: the old rule gains NOT F30. The first repair row is a
      false positive that carries the decoy.
    """
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative int")
    rng = random.Random(seed)
    old_required = CLAIMED_AND
    old_forbidden = CLAIMED_NOT
    new_required = (CLAIMED_AND[0], CLAIMED_SLIDE_TO)
    decoy_forbidden = CLAIMED_NOT + (CLAIMED_DECOY,)
    for bit in list(old_required) + list(old_forbidden) + [CLAIMED_SLIDE_TO, CLAIMED_DECOY]:
        if bit >= n_features:
            raise ValueError("claimed feature index does not fit n_features")

    initial = _balanced_rows(rng, n_initial, n_features, old_required, old_forbidden, (), "initial")
    start = distill_literals([(bit, True) for bit in old_required] + [(bit, False) for bit in old_forbidden])

    # The canonical counterexample is extra, so the random block can stay even.
    dead_repair = _balanced_rows(rng, n_repair, n_features, new_required, old_forbidden, (CLAIMED_AND[1],), "dead-repair")
    dead_canon = {
        "id": "dead-repair-canonical",
        "x": _draw(rng, n_features, new_required, set(old_forbidden) | {CLAIMED_AND[1]}),
        "y": True,
    }
    dead_eval = _balanced_rows(rng, n_eval, n_features, new_required, old_forbidden, (CLAIMED_AND[1],), "dead-eval")

    residual_repair = _balanced_rows(rng, n_repair, n_features, new_required, old_forbidden, (), "residual-repair")
    residual_canon = {
        "id": "residual-repair-canonical",
        "x": _draw(rng, n_features, new_required, set(old_forbidden) | {CLAIMED_AND[1]}),
        "y": True,
    }
    residual_eval = _balanced_rows(rng, n_eval, n_features, new_required, old_forbidden, (), "residual-eval")
    # Old feature on, slid feature off, rest of the new rule's other literals satisfied.
    # The relaxed OR accepts this row; the new rule does not.
    residual_fp = {
        "id": "residual-eval-injected-fp",
        "x": _draw(rng, n_features, (CLAIMED_AND[0], CLAIMED_AND[1]), set(old_forbidden) | {CLAIMED_SLIDE_TO}),
        "y": False,
    }

    decoy_repair = _balanced_rows(rng, n_repair, n_features, old_required, decoy_forbidden, (), "decoy-repair")
    decoy_canon = {
        "id": "decoy-repair-canonical",
        "x": _draw(rng, n_features, old_required + (CLAIMED_DECOY,), old_forbidden),
        "y": False,
    }
    decoy_eval = _balanced_rows(rng, n_eval, n_features, old_required, decoy_forbidden, (), "decoy-eval")

    dead_oracle = lambda x: label_of(x, new_required, old_forbidden)
    residual_oracle = dead_oracle
    decoy_oracle = lambda x: label_of(x, old_required, decoy_forbidden)
    shift_note = (
        "Synthetic indexes %s AND NOT %s slide %s -> %s. "
        "Not an NPB column. Repair sees a constructed counterexample first, then fresh draws."
        % (list(old_required), list(old_forbidden), CLAIMED_AND[1], CLAIMED_SLIDE_TO)
    )
    scenario_list = [
        _scenario_record(
            "feature_shift_dead", start, initial,
            [dead_canon] + dead_repair, dead_eval, dead_oracle,
            shift_note + " Bit %d is forced off on every drifted row." % CLAIMED_AND[1],
        ),
        _scenario_record(
            "feature_shift_residual", start, initial,
            [residual_canon] + residual_repair, residual_eval + [residual_fp], residual_oracle,
            shift_note + " Bit %d remains a free background bit. Eval contains residual-eval-injected-fp." % CLAIMED_AND[1],
        ),
        _scenario_record(
            "new_decoy", start, initial,
            [decoy_canon] + decoy_repair, decoy_eval, decoy_oracle,
            "Same base rule plus NOT bit %d. First repair row is a false positive." % CLAIMED_DECOY,
        ),
    ]
    scenarios = {row["name"]: row for row in scenario_list}
    scenarios["feature_shift_residual"]["injected_false_positive"] = residual_fp
    probe_span = _probe_span(seed)
    sample_x = [row["x"] for row in dead_eval[:32]]
    if measure_time:
        timing = {
            "evaluate_fast": _timing(start.evaluate_fast, sample_x),
            "evaluate_reference": _timing(start.evaluate_reference, sample_x),
            "python_call_floor": _timing(lambda _value: None, sample_x),
            "host": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "machine": platform.machine(),
            },
        }
    else:
        timing = None
    return {
        "schema": SCHEMA,
        "seed": seed,
        "n_features": n_features,
        "n_initial": n_initial,
        "n_repair": n_repair,
        "n_eval": n_eval,
        "class_balance": "equal positive and negative counts",
        "background": "independent Bernoulli 1/2, then forced literals",
        "negatives": "one uniformly chosen violated literal (near miss)",
        "probe_order": "ascending feature index; the proposal does not specify order",
        "scenarios": scenarios,
        "probe_span": probe_span,
        "timing": timing,
        "flaws_exercised_by_construction": flaw_examples(seed),
    }


def _probe_span(seed, draws=32):
    """Probe counts for the canonical dead-slide and decoy rows across subseeds."""
    dead_counts = []
    decoy_counts = []
    parent = random.Random(seed)
    for _ in range(draws):
        sub = random.Random(parent.randrange(2 ** 63))
        dead_x = _draw(sub, N_FEATURES, (CLAIMED_AND[0], CLAIMED_SLIDE_TO), set(CLAIMED_NOT) | {CLAIMED_AND[1]})
        decoy_x = _draw(sub, N_FEATURES, CLAIMED_AND + (CLAIMED_DECOY,), CLAIMED_NOT)
        start = distill_literals([(bit, True) for bit in CLAIMED_AND] + [(bit, False) for bit in CLAIMED_NOT])
        dead_rule = start.copy()
        decoy_rule = start.copy()
        dead_trace = repair_false_negative(dead_rule, dead_x, lambda x: label_of(x, (CLAIMED_AND[0], CLAIMED_SLIDE_TO), CLAIMED_NOT))
        decoy_trace = repair_false_positive(decoy_rule, decoy_x, lambda x: label_of(x, CLAIMED_AND, CLAIMED_NOT + (CLAIMED_DECOY,)))
        dead_counts.append(len(dead_trace["probes"]))
        decoy_counts.append(len(decoy_trace["probes"]))
    def _pack(counts):
        ordered = sorted(counts)
        return {
            "draws": draws,
            "min": ordered[0],
            "median": ordered[draws // 2],
            "max": ordered[-1],
            "equal_to_3": sum(count == 3 for count in counts),
        }
    return {"feature_shift_dead_canonical": _pack(dead_counts), "new_decoy_canonical": _pack(decoy_counts)}


def flaw_examples(seed):
    """Concrete counterexamples. Indexes are one sample from ``seed``; trap is the lower necessary bit."""
    rng = random.Random(seed + 17)
    a, old, new, trap, banned, noise, b, c, b2, c2 = rng.sample(range(N_FEATURES), 10)
    if trap > new:
        trap, new = new, trap
    # First flipping candidate is the lower necessary bit, not the later one.
    rule = distill_literals([(a, True), (old, True), (banned, False)])
    oracle = lambda x: label_of(x, (a, trap, new), (banned,))
    positive = mask_of((a, trap, new, noise))
    _trace = repair_disagreement(rule, positive, True, oracle)
    replacement = next(edit["replacement"] for edit in _trace["edits"] if edit["op"] == "relax_or")
    false_positive = mask_of((a, trap))
    low, high = (b2, c2) if b2 < c2 else (c2, b2)
    multi = distill_literals([(a, True), (b, True), (c, True)])
    multi_oracle = lambda x: label_of(x, (a, b2, c2), ())
    multi_row = mask_of((a, b2, c2))
    multi_trace = repair_disagreement(multi, multi_row, True, multi_oracle)
    multi_fp = mask_of((a, low))
    # Noisy positive clears a real ban.
    noisy = distill_literals([(a, True), (banned, False)])
    noisy_oracle = lambda x: label_of(x, (a,), (banned,))
    noisy_row = mask_of((a, banned))
    noisy_rule_result = repair_disagreement(noisy, noisy_row, True, noisy_oracle)
    harmful_positive = mask_of((a, banned))
    # Missing-bit false positive: binary search still commits a bit.
    # Simulate the state after a correct OR relaxation, then a residual FP.
    relaxed = distill_literals([(a, True)])
    relaxed.or_clauses.append((1 << old) | (1 << new))
    residual = mask_of((a, old, noise))
    residual_oracle = lambda x: label_of(x, (a, new), ())
    residual_trace = repair_disagreement(relaxed, residual, False, residual_oracle)
    culprit = residual_trace["culprit"]
    spoiled = mask_of((a, new, culprit)) if culprit is not None else None
    return {
        "first_candidate": {
            "replacement": replacement,
            "trap": trap,
            "later_necessary_bit": new,
            "false_positive_accepted": rule.evaluate_fast(false_positive) and not oracle(false_positive),
        },
        "multiple_lost_bits": {
            "replacements": [edit.get("replacement") for edit in multi_trace["edits"] if edit["op"] == "relax_or"],
            "low_new_bit": low,
            "high_new_bit": high,
            "false_positive_accepted": multi.evaluate_fast(multi_fp) and not multi_oracle(multi_fp),
        },
        "noisy_clear_not": {
            "cleared": next(edit["bits"] for edit in noisy_rule_result["edits"] if edit["op"] == "clear_not"),
            "banned": banned,
            "positive_with_banned_bit_now_accepted": noisy.evaluate_fast(harmful_positive) and not noisy_oracle(harmful_positive),
        },
        "false_positive_on_a_missing_bit": {
            "culprit": culprit,
            "flipping_culprit_restores_true": (culprit is not None and residual_oracle(residual ^ (1 << culprit))),
            "true_positive_rejected_after_commit": (
                spoiled is not None and residual_oracle(spoiled) and not relaxed.evaluate_fast(spoiled)
            ),
        },
    }


def format_report(report):
    """Plain-text table for a human. The JSON has the counts."""
    lines = [
        "schema: %s" % report.get("schema", SCHEMA),
        "seed: %s" % report["seed"],
        "",
        "Fidelity is (tp + tn) / n on the named split. repaired_*_on_repair_rows is the split the edits saw.",
        "",
        "| scenario | initial | unrepaired eval | repaired once, eval | repaired all, eval | probes once | probes all |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    synthetic = report.get("synthetic", report)
    scenarios = synthetic["scenarios"] if "scenarios" in synthetic else report["scenarios"]
    for name, row in scenarios.items():
        lines.append("| %s | %.4f | %.4f | %.4f | %.4f | %d | %d |" % (
            name,
            row["initial"]["fidelity"],
            row["unrepaired_eval"]["fidelity"],
            row["repaired_one_eval"]["fidelity"],
            row["repaired_all_eval"]["fidelity"],
            row["probe_queries_one"],
            row["probe_queries_all"],
        ))
    if "probe_span" in synthetic:
        lines.append("")
        lines.append("Canonical probe counts over %d subseeds (dead slide / decoy):" % synthetic["probe_span"]["feature_shift_dead_canonical"]["draws"])
        for key, row in synthetic["probe_span"].items():
            lines.append("- %s min %d median %d max %d (count of draws with exactly 3 probes: %d)" % (
                key, row["min"], row["median"], row["max"], row["equal_to_3"]))
    timing = synthetic.get("timing")
    if timing:
        fast = timing["evaluate_fast"]
        lines.append("")
        lines.append("evaluate_fast: %.3f µs/call over %d calls (%.3f s) on %s" % (
            fast["microseconds_per_call"], fast["calls"], fast["seconds"], timing["host"]["python"]))
        floor = timing["python_call_floor"]
        lines.append("empty Python call: %.3f µs/call over %d calls" % (
            floor["microseconds_per_call"], floor["calls"]))
    season = report.get("season")
    if season:
        lines.append("")
        lines.append(format_season(season))
    return "\n".join(lines) + "\n"


def _split_seasons(seasons):
    """Earlier seasons train, then repair, then eval. Remainder stays in train.

    The cut is by count of seasons, fixed before any fidelity is computed.
    """
    seasons = list(seasons)
    if len(seasons) < 3:
        raise ValueError("need at least three seasons to separate train, repair, and eval")
    n_eval = max(1, len(seasons) // 4)
    n_repair = max(1, len(seasons) // 4)
    n_train = len(seasons) - n_eval - n_repair
    if n_train < 1:
        raise ValueError("season split left no training season")
    return seasons[:n_train], seasons[n_train:n_train + n_repair], seasons[n_train + n_repair:]


def _search_seconds(df, target, candidates, max_terms, top, runs=5):
    import rule_search
    rule_search.search(df, target, candidates, max_terms=max_terms, max_conds=2, top=top)
    samples = []
    for _ in range(runs):
        start = time.perf_counter()
        rule_search.search(df, target, candidates, max_terms=max_terms, max_conds=2, top=top)
        samples.append(time.perf_counter() - start)
    samples.sort()
    return {
        "max_terms": max_terms,
        "max_conds": 2,
        "top": top,
        "runs": runs,
        "seconds": samples,
        "min_seconds": samples[0],
        "median_seconds": samples[len(samples) // 2],
        "max_seconds": samples[-1],
    }


def _candidate_index(cond, candidates):
    for index, candidate in enumerate(candidates):
        if candidate["col"] == cond["col"] and candidate["op"] == cond["op"] and candidate["value"] == cond["value"]:
            return index
    raise ValueError("searched condition is not one of the registered candidates: %r" % (cond,))


def _force(x, on, off):
    for bit in on:
        x |= 1 << bit
    for bit in off:
        x &= ~(1 << bit)
    return x


def load_candidate_rows(root):
    """Team-seasons as feature masks. Candidate order is the TOML order, which is the bit index."""
    import tomllib

    import polars as pl

    root = Path(root).expanduser().resolve()
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.append(root_text)
    import aoi_paths
    from propositions import _cond, text
    from pythdragoras import apply_exclusions

    cycle = aoi_paths.resolve_cycle_path(root)
    spec = tomllib.loads((cycle / "rule_candidates.toml").read_text(encoding="utf-8"))
    cfg = tomllib.loads((cycle / "analysis.toml").read_text(encoding="utf-8"))
    frame = pl.read_ndjson(cycle / "outputs" / "season.jsonl")
    frame, removed = apply_exclusions(frame, cfg.get("exclude", []))
    candidates = spec["candidate"]
    target = spec["target"]
    columns = sorted({item["col"] for item in [*target, *candidates]})
    before = frame.height
    frame = frame.drop_nulls(columns).sort("season", "team")
    flag_columns = [frame.select(x=_cond([candidate], frame.columns))["x"].to_list() for candidate in candidates]
    target_flags = frame.select(x=_cond(target, frame.columns))["x"].to_list()
    seasons = frame["season"].to_list()
    teams = frame["team"].to_list()
    rows = []
    seen = set()
    for index in range(frame.height):
        x = 0
        for bit, flags in enumerate(flag_columns):
            if flags[index]:
                x |= 1 << bit
        row_id = "%s-%s" % (teams[index], int(seasons[index]))
        if row_id in seen:
            raise ValueError("duplicate team-season: %s" % row_id)
        seen.add(row_id)
        rows.append({
            "id": row_id,
            "season": int(seasons[index]),
            "team": teams[index],
            "x": x,
            "y": bool(target_flags[index]),
        })
    distinct_columns = []
    for index, candidate in enumerate(candidates):
        if candidate["col"] not in [name for name, _ in distinct_columns]:
            distinct_columns.append((candidate["col"], index))
    confirm = [int(season) for season in cfg.get("confirm", {}).get("seasons", [])]
    return {
        "frame": frame,
        "target": target,
        "candidates": candidates,
        "candidate_text": [text([candidate]) for candidate in candidates],
        "rows": rows,
        "dropped_null_rows": before - frame.height,
        "exclusions": removed,
        "confirm_seasons": confirm,
        "distinct_column_bits": distinct_columns,
        "cycle": str(cycle),
    }


def _planted_roles(distinct_column_bits):
    """First registered condition of the first four distinct columns. Not chosen by accuracy."""
    if len(distinct_column_bits) < 4:
        raise ValueError("need four distinct candidate columns to plant a slide")
    _and, old, new, banned = [bit for _name, bit in distinct_column_bits[:4]]
    return {"and": _and, "old": old, "new": new, "not": banned}


def _roles_from_train_prevalence(train_rows, candidates, low=0.40, high=0.80):
    """First four distinct columns whose train-season rate sits in ``[low, high]``.

    Uses only training rows and ignores the B-class target. The window exists so a
    planted conjunction is not forced onto the rarest thresholds. It is not fit to
    repaired fidelity.
    """
    if not train_rows:
        raise ValueError("prevalence roles need training rows")
    chosen = []
    used = set()
    rates = []
    n = len(train_rows)
    for index, candidate in enumerate(candidates):
        on = sum(1 for row in train_rows if row["x"] & (1 << index))
        rate = on / n
        rates.append(rate)
        if candidate["col"] in used or not (low <= rate <= high):
            continue
        chosen.append(index)
        used.add(candidate["col"])
        if len(chosen) == 4:
            break
    if len(chosen) < 4:
        raise ValueError("train prevalence window did not yield four columns")
    return {"and": chosen[0], "old": chosen[1], "new": chosen[2], "not": chosen[3]}, rates


def _planted_bundle(train_rows, repair_rows, eval_rows, roles):
    """Plant a slide on these roles. Mechanism repair sees a constructed positive first."""
    if not repair_rows:
        raise RuntimeError("repair split is empty")

    def _plant(rows, required, forbidden, dead_bits):
        planted = []
        for row in rows:
            x = _force(row["x"], (), dead_bits)
            planted.append({
                "id": row["id"],
                "season": row["season"],
                "x": x,
                "y": label_of(x, required, forbidden),
            })
        return planted

    old_required = (roles["and"], roles["old"])
    new_required = (roles["and"], roles["new"])
    forbidden = (roles["not"],)
    old_rule = distill_literals([(roles["and"], True), (roles["old"], True), (roles["not"], False)])
    oracle = lambda x: label_of(x, new_required, forbidden)
    natural_train = _plant(train_rows, old_required, forbidden, ())
    natural_repair = _plant(repair_rows, new_required, forbidden, ())
    natural_eval = _plant(eval_rows, new_required, forbidden, ())
    background = repair_rows[0]["x"]
    canonical = {
        "id": "planted-canonical-positive",
        "x": _force(background, new_required, forbidden + (roles["old"],)),
        "y": True,
    }
    mechanism = _scenario_record(
        "planted_natural_bits",
        old_rule,
        natural_train,
        [canonical] + natural_repair,
        natural_eval,
        oracle,
        "Labels are the planted function of observed candidate bits, not upper_half.",
    )
    one_rule, one_traces, one_inspected = active_repair(old_rule, natural_repair, oracle, max_repairs=1)
    all_rule, all_traces, all_inspected = active_repair(old_rule, natural_repair, oracle, max_repairs=None)
    dead_eval = _plant(eval_rows, new_required, forbidden, (roles["old"],))
    dead_repair = _plant(repair_rows, new_required, forbidden, (roles["old"],))
    dead_train = _plant(train_rows, old_required, forbidden, ())
    dead = _scenario_record(
        "planted_dead_old_bit",
        old_rule,
        dead_train,
        [{
            "id": "planted-dead-canonical-positive",
            "x": _force(background, new_required, forbidden + (roles["old"],)),
            "y": True,
        }] + dead_repair,
        dead_eval,
        oracle,
        "Drifted rows have the old bit cleared. Other candidate bits stay as observed.",
    )
    def _positives(rows):
        return sum(1 for row in rows if row["y"])
    return {
        "mechanism": mechanism,
        "observational": {
            "note": "No constructed counterexample. Only drifted team-seasons, labeled by the planted new rule.",
            "unrepaired_eval": confusion(old_rule, natural_eval),
            "repaired_one_rule": one_rule.describe(),
            "repaired_one_eval": confusion(one_rule, natural_eval),
            "probe_queries_one": _probe_queries(one_traces),
            "rows_inspected_one": one_inspected,
            "repairs_one": len(one_traces),
            "repaired_all_rule": all_rule.describe(),
            "repaired_all_eval": confusion(all_rule, natural_eval),
            "probe_queries_all": _probe_queries(all_traces),
            "rows_inspected_all": all_inspected,
            "repairs_all": len(all_traces),
            "traces_one": one_traces,
        },
        "dead_old_bit": dead,
        "positive_counts": {
            "train": _positives(natural_train),
            "repair": _positives(natural_repair),
            "eval": _positives(natural_eval),
        },
    }


def _rows_for(rows, seasons):
    wanted = set(seasons)
    return [row for row in rows if row["season"] in wanted]


def season_report(root, seed):
    """Real candidate masks, plus what repair cannot do with observational labels.

    ``natural_target`` scores the best single conjunction from ``rule_search``
    on earlier seasons against later seasons. There is no counterfactual oracle
    for ``upper_half``, so repair is not run.

    ``planted_natural_bits`` relabels the same masks with a planted slide at the
    repair boundary. Probes are legal because the oracle is that planted function.
    ``planted_dead_old_bit`` additionally turns the old bit off on drifted rows,
    which is the case where an OR relaxation matches the new rule.
    """
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative int")
    loaded = load_candidate_rows(root)
    present = []
    for row in loaded["rows"]:
        if row["season"] not in present:
            present.append(row["season"])
    confirm = set(loaded["confirm_seasons"])
    pool = [season for season in present if season not in confirm]
    train_seasons, repair_seasons, eval_seasons = _split_seasons(pool)
    train_rows = _rows_for(loaded["rows"], train_seasons)
    repair_rows = _rows_for(loaded["rows"], repair_seasons)
    eval_rows = _rows_for(loaded["rows"], eval_seasons)
    untouched_rows = _rows_for(loaded["rows"], [season for season in present if season in confirm])
    roles = _planted_roles(loaded["distinct_column_bits"])
    names = loaded["candidate_text"]

    import polars as pl
    import rule_search

    frame = loaded["frame"]
    train_frame = frame.filter(pl.col("season").is_in(train_seasons))
    searched = rule_search.search(
        train_frame, loaded["target"], loaded["candidates"], max_terms=1, max_conds=2, top=1)[0]
    group = searched["if_any"][0]
    compiled = compile_bit_dnf([[_candidate_index(cond, loaded["candidates"]) for cond in group]])
    if compiled is None or len(searched["if_any"]) != 1:
        raise RuntimeError("max_terms=1 did not compile to a conjunction")
    # The compiled DNF uses only positive bits. A searched condition is a positive
    # literal on that candidate, so M_NOT stays empty. That is the representation
    # gap with the proposal's forbidden-bit mask.
    natural = {
        "counterfactual_oracle": False,
        "repair_ran": False,
        "reason": (
            "Observed B-class labels do not answer oracle(X with one candidate bit flipped). "
            "Active repair was not applied to this target."
        ),
        "rule_text": rule_search.rule_text(searched),
        "rule": compiled.describe(),
        "train_counts_from_search": {key: searched[key] for key in ("tp", "fp", "fn", "tn", "mcc")},
        "initial": confusion(compiled, train_rows),
        "unrepaired_repair_seasons": confusion(compiled, repair_rows),
        "unrepaired_eval": confusion(compiled, eval_rows),
        "search_seconds_max_terms_1_top_1": _search_seconds(
            train_frame, loaded["target"], loaded["candidates"], 1, 1),
        "search_seconds_max_terms_2_top_20": _search_seconds(
            train_frame, loaded["target"], loaded["candidates"], 2, 20),
    }
    if untouched_rows:
        natural["untouched_confirm_seasons"] = confusion(compiled, untouched_rows)

    file_order = _planted_bundle(train_rows, repair_rows, eval_rows, roles)
    prevalent_roles, train_rates = _roles_from_train_prevalence(train_rows, loaded["candidates"])
    prevalent = _planted_bundle(train_rows, repair_rows, eval_rows, prevalent_roles)
    sample = [row["x"] for row in eval_rows] or [0]
    timer_rule = distill_literals([(roles["and"], True), (roles["old"], True), (roles["not"], False)])
    return {
        "schema": SCHEMA,
        "seed": seed,
        "seed_used_for_sampling": False,
        "cycle": loaded["cycle"],
        "n_candidates": len(loaded["candidates"]),
        "claimed_indexes_12_19_25_fit": len(loaded["candidates"]) > 25,
        "candidate_index_12_text": names[12] if len(names) > 12 else None,
        "candidate_text": names,
        "roles": {key: {"bit": bit, "text": names[bit]} for key, bit in roles.items()},
        "prevalence_roles": {key: {"bit": bit, "text": names[bit]} for key, bit in prevalent_roles.items()},
        "train_bit_rates": train_rates,
        "train_seasons": train_seasons,
        "repair_seasons": repair_seasons,
        "eval_seasons": eval_seasons,
        "confirm_seasons_held_out": [season for season in present if season in confirm],
        "excluded": loaded["exclusions"],
        "dropped_null_rows": loaded["dropped_null_rows"],
        "n_train": len(train_rows),
        "n_repair": len(repair_rows),
        "n_eval": len(eval_rows),
        "season_ids_disjoint": set(_ids(train_rows)).isdisjoint(_ids(repair_rows)) and set(_ids(repair_rows)).isdisjoint(_ids(eval_rows)),
        "natural_target": natural,
        "planted_file_order": file_order,
        "planted_natural_bits": file_order["mechanism"],
        "planted_observational_rows_only": file_order["observational"],
        "planted_dead_old_bit": file_order["dead_old_bit"],
        "planted_prevalence_window": prevalent,
        "surrogate_timing": _timing(timer_rule.evaluate_fast, sample),
    }


def format_season(season):
    natural = season["natural_target"]
    lines = [
        "NPB candidate rows: %s" % season["cycle"],
        "seasons train %s repair %s eval %s" % (
            season["train_seasons"], season["repair_seasons"], season["eval_seasons"]),
        "candidates: %d (indexes 12, 19, and 25 all exist: %s)" % (
            season["n_candidates"], season["claimed_indexes_12_19_25_fit"]),
        "natural target rule: %s" % natural["rule_text"],
        "natural initial fidelity %.4f; unrepaired eval %.4f; repair ran: %s" % (
            natural["initial"]["fidelity"], natural["unrepaired_eval"]["fidelity"], natural["repair_ran"]),
        "search max_terms=2 top=20 median %.6f s (min %.6f, max %.6f)" % (
            natural["search_seconds_max_terms_2_top_20"]["median_seconds"],
            natural["search_seconds_max_terms_2_top_20"]["min_seconds"],
            natural["search_seconds_max_terms_2_top_20"]["max_seconds"]),
    ]
    def _bundle_lines(title, bundle, role_map):
        out = ["%s: (%s) AND (%s) AND NOT (%s) -> (%s); positives train/repair/eval %s" % (
            title, role_map["and"]["text"], role_map["old"]["text"], role_map["not"]["text"], role_map["new"]["text"],
            bundle["positive_counts"])]
        mechanism = bundle["mechanism"]
        dead = bundle["dead_old_bit"]
        obs = bundle["observational"]
        out.append("  mechanism unrepaired %.4f repaired-once %.4f probes %d; repaired-all %.4f" % (
            mechanism["unrepaired_eval"]["fidelity"], mechanism["repaired_one_eval"]["fidelity"],
            mechanism["probe_queries_one"], mechanism["repaired_all_eval"]["fidelity"]))
        out.append("  dead-old unrepaired %.4f repaired-once %.4f probes %d" % (
            dead["unrepaired_eval"]["fidelity"], dead["repaired_one_eval"]["fidelity"], dead["probe_queries_one"]))
        out.append("  observational unrepaired %.4f repaired-once %.4f probes %d repaired-all %.4f probes %d" % (
            obs["unrepaired_eval"]["fidelity"], obs["repaired_one_eval"]["fidelity"], obs["probe_queries_one"],
            obs["repaired_all_eval"]["fidelity"], obs["probe_queries_all"]))
        return out
    lines.extend(_bundle_lines("planted file-order", season["planted_file_order"], season["roles"]))
    lines.extend(_bundle_lines("planted prevalence window", season["planted_prevalence_window"], season["prevalence_roles"]))
    fast = season["surrogate_timing"]
    lines.append("evaluate_fast on these masks: %.3f µs/call over %d calls" % (
        fast["microseconds_per_call"], fast["calls"]))
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Measure the bitwise surrogate and active repair. Claimed percentages are not targets.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--season", action="store_true", help="Score NPB candidate rows. Needs AOI_ROOT or --aoi-root, and polars.")
    parser.add_argument("--aoi-root", type=Path, default=None)
    args = parser.parse_args(argv)
    seed = secrets.randbits(63) if args.seed is None else args.seed
    print("bitwise_surrogate seed=%d" % seed)
    report = {"schema": SCHEMA, "seed": seed, "synthetic": synthetic_report(seed)}
    if args.season:
        root = args.aoi_root if args.aoi_root is not None else os.environ.get("AOI_ROOT")
        if not root:
            parser.error("pass --aoi-root or set AOI_ROOT for --season")
        report["season"] = season_report(root, seed)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.json else format_report(report)
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
