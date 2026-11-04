"""Executable via unittest discover without site-packages."""
import ast
import itertools
from pathlib import Path
import sys
import socket
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "pythdragoras"))
from bitwise_surrogate import BitwiseSymbolicSurrogate
from compact_bitmask import CompactRule, FeatureLayout, Part, match_scene


class CompactBitmaskTests(unittest.TestCase):
    def test_projection_exhaustive_roundtrip_and_discarded_features(self):
        layout = FeatureLayout((0, 3, 7))
        for source in range(256):
            self.assertEqual(layout.expand(layout.project(source)), source & 0x89)
            self.assertEqual(layout.decode(layout.encode(source)), source & 0x89)

    def test_rule_all_small_masks_and_inputs(self):
        positions = (0, 31, 255)
        layout = FeatureLayout(positions)
        for required, forbidden, clause in itertools.product(range(8), repeat=3):
            rule = BitwiseSymbolicSurrogate(layout.expand(required),
                () if not clause else (layout.expand(clause),), layout.expand(forbidden))
            compact = CompactRule(rule)
            for dense in range(8):
                source = layout.expand(dense) | (1 << 99)
                self.assertEqual(rule.evaluate_reference(source), compact.evaluate_source(source))
                self.assertEqual(rule.evaluate_fast(source),
                    compact.evaluate_dense(compact.layout.project(source)))

    def test_invalid_layout_and_wire_padding(self):
        for positions in ((1, 0), (1, 1), (-1,), (True,), [1]):
            with self.assertRaises(ValueError):
                FeatureLayout(positions)
        layout = FeatureLayout((0, 7))
        for payload in (b'', b'\x04', b'\x00\x00'):
            with self.assertRaises(ValueError):
                layout.decode(payload)
        for value in (-1, True, 4):
            with self.assertRaises(ValueError):
                layout.expand(value)
        empty = FeatureLayout(())
        self.assertEqual(empty.decode(b''), 0)
        self.assertTrue(CompactRule(BitwiseSymbolicSurrogate()).evaluate_source(999))

    def test_snapshot_does_not_alias_source(self):
        rule = BitwiseSymbolicSurrogate(1, (2,), 4)
        compact = CompactRule(rule)
        rule.or_clauses.append(8)
        self.assertTrue(compact.evaluate_source(3))
        self.assertFalse(rule.evaluate_fast(3))

    def test_overlapping_leaf_bits_do_not_starve_later_parts(self):
        parts = (Part('a', 7), Part('b', 11))
        for ordering in itertools.permutations(parts):
            result = match_scene(15, ordering)
            self.assertEqual(set(result['compatible_parts']), {'a', 'b'})
            self.assertEqual(result['unexplained_mask'], 0)
            self.assertFalse(result['unique_decomposition_proven'])

    def test_no_invented_shared_bit_ownership(self):
        result = match_scene(0x7017, (Part('sword', 0x17),))
        self.assertEqual(result['unexplained_mask'], 0x7000)
        # 0x7001 and 0x7003 are both compatible OR explanations.
        self.assertEqual(0x17 | 0x7001, 0x17 | 0x7003)

    def test_partial_observation_and_negatives(self):
        parts = (Part('a', 3, 4),)
        self.assertEqual(match_scene(1, parts, 1)['pending_parts'], ['a'])
        self.assertEqual(match_scene(3, parts, 7)['compatible_parts'], ['a'])
        self.assertEqual(match_scene(7, parts, 7)['rejected_parts'], ['a'])
        self.assertEqual(match_scene(1, parts, 7)['rejected_parts'], ['a'])
        with self.assertRaises(ValueError):
            match_scene(2, parts, 1)
        with self.assertRaises(ValueError):
            match_scene(3, parts + parts)

    def test_socket_payload_roundtrip(self):
        layout = FeatureLayout((0, 31, 255))
        rows = [layout.expand(value) for value in range(8)]
        sender, receiver = socket.socketpair()
        with sender, receiver:
            sender.settimeout(2)
            receiver.settimeout(2)
            sender.sendall(b''.join(layout.encode(row) for row in rows))
            sender.shutdown(socket.SHUT_WR)
            payload = bytearray()
            while True:
                chunk = receiver.recv(3)  # deliberately split the message
                if not chunk:
                    break
                payload.extend(chunk)
            self.assertEqual([layout.decode(bytes([value])) for value in payload], rows)

    def test_no_multiply_or_float_in_core(self):
        source = Path(__file__).resolve().parents[1] / 'compact_bitmask.py'
        for node in ast.walk(ast.parse(source.read_text())):
            self.assertFalse(isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Div)))
            self.assertFalse(isinstance(node, ast.Constant) and isinstance(node.value, float))


if __name__ == '__main__':
    unittest.main()
