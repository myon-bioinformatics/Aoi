"""Connect the Lean rule model to the actual stdlib bitmask implementation.

The oracle uses sets of feature identifiers, independently of the production
bitmask evaluator. These finite checks do not prove Python correct for all ints.
Run without Aoi, Polars or Lean: python -S -m unittest discover -s tests -p test_formal_bridge.py -v
"""

import importlib.util
import itertools
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "core" / "bitwise_surrogate.py"
SPEC = importlib.util.spec_from_file_location("formal_bridge_subject", SOURCE)
bs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bs)


def subsets(features):
    return [frozenset(values) for n in range(len(features) + 1)
            for values in itertools.combinations(features, n)]


def pack(features):
    return sum(1 << bit for bit in features)


def holds(specification, row):
    """Set interpretation of Lean Holds; no production evaluator is used."""
    required, forbidden, clauses = specification
    return required <= row and not (forbidden & row) and all(clause & row for clause in clauses)


def make_rule(specification):
    required, forbidden, clauses = specification
    return bs.BitwiseSymbolicSurrogate(pack(required), tuple(pack(c) for c in clauses), pack(forbidden))


def small_cases():
    rows = subsets((0, 1))
    clause_lists = [tuple(values) for n in range(3)
                    for values in itertools.combinations(rows[1:], n)]
    cases = []
    for required, forbidden, clauses in itertools.product(rows, rows, clause_lists):
        spec = required, forbidden, clauses
        accepted = frozenset(index for index, row in enumerate(rows) if holds(spec, row))
        cases.append((spec, make_rule(spec), accepted))
    return rows, cases


class FormalRuleBridge(unittest.TestCase):
    def test_all_small_rules_match_total_assignment_semantics(self):
        rows, cases = small_cases()
        self.assertEqual(len(cases), 112)
        for index, (_, rule, accepted) in enumerate(cases):
            with self.subTest(rule=index):
                self.assertEqual([rule.evaluate_fast(pack(row)) for row in rows],
                                 [i in accepted for i in range(len(rows))])
                self.assertEqual(bs.satisfiable(rule), bool(accepted))
                witness = bs.witness(rule)
                if accepted:
                    self.assertIn(witness, [pack(rows[i]) for i in accepted])
                else:
                    self.assertIsNone(witness)

    def test_all_small_rule_pairs_match_implication_and_exclusivity(self):
        rows, cases = small_cases()
        for left_index, (_, left, in_left) in enumerate(cases):
            for right_index, (_, right, in_right) in enumerate(cases):
                with self.subTest(left=left_index, right=right_index):
                    # Exhaustive truth tables are independent of implies()'s
                    # required/singleton-clause/allowed-clause decisions.
                    self.assertEqual(bs.implies(left, right), in_left <= in_right)
                    joint = bs._both(left, right)
                    self.assertEqual(frozenset(i for i, row in enumerate(rows)
                                              if joint.evaluate_fast(pack(row))), in_left & in_right)
                    relation = bs.rule_relation([left], [right])
                    if not in_left or not in_right:
                        self.assertEqual(relation["relation"], "never_a" if not in_left else "never_b")
                        self.assertIsNone(relation["witness"])
                    elif not (in_left & in_right):
                        self.assertEqual(relation, {"relation": "exclusive", "witness": None})
                    else:
                        self.assertIn(relation["witness"], [pack(rows[i]) for i in in_left & in_right])
                        expected = ("equivalent" if in_left == in_right else
                                    "a_implies_b" if in_left <= in_right else
                                    "b_implies_a" if in_right <= in_left else "overlap")
                        self.assertEqual(relation["relation"], expected)

    def test_sparse_high_bits_preserve_rule_semantics_and_witnesses(self):
        # Cross machine-word boundaries and keep a completely unrelated bit:
        # the model allows arbitrary feature identifiers and extra true bits.
        rows, cases = small_cases()
        rename = {0: 65, 1: 511}
        for index, (spec, _, accepted) in enumerate(cases):
            mapped = (frozenset(rename[x] for x in spec[0]),
                      frozenset(rename[x] for x in spec[1]),
                      tuple(frozenset(rename[x] for x in clause) for clause in spec[2]))
            rule = make_rule(mapped)
            with self.subTest(rule=index):
                actual = [rule.evaluate_fast(pack({rename[x] for x in row} | {127})) for row in rows]
                self.assertEqual(actual, [i in accepted for i in range(len(rows))])
                self.assertEqual(bs.satisfiable(rule), bool(accepted))
                witness = bs.witness(rule)
                if accepted:
                    self.assertIsNotNone(witness)
                    row = frozenset(bit for bit in (65, 511) if witness & (1 << bit))
                    self.assertTrue(holds(mapped, row))
                    self.assertEqual(witness, pack(row))
                else:
                    self.assertIsNone(witness)

    def test_singleton_allowed_clause_forces_a_required_feature(self):
        # An OR of feature 65 or 511, with 65 forbidden, forces feature 511.
        antecedent = bs.BitwiseSymbolicSurrogate(0, (pack({65, 511}),), pack({65}))
        consequent = bs.BitwiseSymbolicSurrogate(pack({511}))
        self.assertTrue(bs.implies(antecedent, consequent))
        self.assertFalse(bs.implies(consequent, antecedent))
        self.assertFalse(antecedent.evaluate_fast(pack({65, 511})))
        self.assertTrue(consequent.evaluate_fast(pack({65, 511})))

    def test_unknown_rows_remain_outside_the_total_assignment_claim(self):
        rule = bs.BitwiseSymbolicSurrogate(pack({65}))
        self.assertFalse(rule.evaluate_fast(0))
        self.assertIsNone(bs.evaluate_row(rule, 0, pack({65})))
        result = bs.counts([None, True, False], [True, None, False])
        self.assertEqual(result, {"tp": 0, "fp": 0, "fn": 0, "tn": 1,
                                  "undetermined": 2, "n": 3})


if __name__ == "__main__":
    unittest.main()
