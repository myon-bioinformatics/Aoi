"""Independent row-index partition checks, including repeated display identities."""
from collections import Counter
import importlib
import itertools
import json
from pathlib import Path
import tempfile
import unittest

import dragowing

# The single-file stdlib entry point and pytest's package use the same runtime.
drawing = (dragowing if hasattr(dragowing, 'load_overlap')
           else importlib.import_module('dragowing.dragowing'))


def repeated_label_row(**values):
    return dict(team='repeated', team_name='Repeated label', season=2000,
                league='fixture', upper_half=False, **values)


class FormalOverlapPartitionTests(unittest.TestCase):
    def check_partition(self, rows, conditions, signatures):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'records.jsonl'
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows),
                            encoding='utf-8')
            result = drawing.load_overlap(path, conditions, backend='stdlib')

        width = len(conditions)
        # The fixtures supply the truth vectors; neither condition_bits nor
        # either overlap backend constructs the expected partition.
        patterns = list(itertools.product((False, True), repeat=width))
        expected = {pattern: [] for pattern in patterns}
        for index, signature in enumerate(signatures):
            expected[signature].append(index)

        self.assertEqual(len(result['units']), len(rows))
        self.assertEqual([unit['index'] for unit in result['units']], list(range(len(rows))))
        self.assertEqual([tuple(unit['in_set']) for unit in result['units']], signatures)
        self.assertEqual(result['matrix'],
                         [[signature[index] for signature in signatures] for index in range(width)])
        self.assertEqual({unit['unit'] for unit in result['units']}, {'repeated-2000'})
        self.assertEqual([tuple(region['bits']) for region in result['regions']],
                         [tuple(reversed(pattern)) for pattern in patterns])
        for region in result['regions']:
            self.assertEqual(region['unit_index'], expected[tuple(region['bits'])])
            self.assertEqual(region['count'], len(region['unit_index']))

        # Equal total counts alone could hide a missing row and a doubled row.
        # Every original index, even for identical rows, must occur once.
        memberships = Counter(index for region in result['regions']
                              for index in region['unit_index'])
        self.assertEqual(memberships, Counter(range(len(rows))))

    def test_all_patterns_keep_duplicate_rows_and_labels_as_distinct_indices(self):
        for width in range(drawing.MAX_SETS + 1):
            with self.subTest(width=width):
                base = list(itertools.product((False, True), repeat=width))
                # Reverse source order and repeat exact records. A label-based
                # join or set-based deduplication cannot preserve this input.
                signatures = list(reversed(base + base[:2] + base[-1:]))
                rows = [repeated_label_row(**{f'flag{i}': value
                                            for i, value in enumerate(signature)})
                        for signature in signatures]
                conditions = [{'col': f'flag{i}', 'op': '==', 'value': True}
                              for i in range(width)]
                self.check_partition(rows, conditions, signatures)

    def test_dependent_conditions_nulls_and_permutations_keep_empty_regions(self):
        rows = [repeated_label_row(flag=True, vacant=None),
                repeated_label_row(flag=None, vacant=None),
                repeated_label_row(flag=False, vacant=None),
                repeated_label_row(vacant=None),
                repeated_label_row(flag=True, vacant=None)]
        conditions = [{'col': 'flag', 'op': '==', 'value': True},
                      {'col': 'flag', 'op': '==', 'value': True},
                      {'col': 'flag', 'op': '==', 'value': False},
                      {'col': 'vacant', 'op': '!=', 'value': None}]
        signatures = [(True, True, False, False), (False, False, False, False),
                      (False, False, True, False), (False, False, False, False),
                      (True, True, False, False)]
        for order in ((0, 1, 2, 3), (3, 2, 1, 0), (1, 3, 0, 2)):
            with self.subTest(order=order):
                self.check_partition(rows, [conditions[index] for index in order],
                                     [tuple(signature[index] for index in order)
                                      for signature in signatures])


if __name__ == '__main__':
    unittest.main()
