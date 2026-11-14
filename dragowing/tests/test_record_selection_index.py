"""Stdlib parity for multi-ID indexing, duplicate rows and error ordering."""
import random, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from records import select_items


class RecordSelectionTests(unittest.TestCase):
    def test_order_duplicates_and_object_identity(self):
        rng = random.Random(20261104)
        items = [{'id':str(rng.randrange(20)), 'value':i} for i in range(1000)]
        ids = ['3','8','3','1','2','4','2','8']
        expected = [item for ident in ids for item in items if item['id']==ident]
        got = select_items(items, {}, ids)
        self.assertEqual(got, expected)
        self.assertTrue(all(a is b for a,b in zip(got,expected)))
        self.assertEqual(select_items(items, {}, None), items)
        self.assertIsNot(select_items(items, {}, []), items)

    def test_error_order_and_unusual_record_ids(self):
        rows = [{'id':'P1'}, {'id':'E1'}, {'id':[]}, {}]
        self.assertEqual(select_items(rows, {'propositions.jsonl':True}, ['P1'] * 8), rows[:1] * 8)
        for rows in (rows, rows[:2]):
            with self.assertRaisesRegex(FileNotFoundError, 'propositions.jsonl'):
                select_items(rows, {}, ['P1','E1'] * 4)
            with self.assertRaisesRegex(ValueError, 'missing'):
                select_items(rows, {}, ['missing','E1'] * 4)
            with self.assertRaisesRegex(FileNotFoundError, 'sets.jsonl'):
                select_items(rows, {'propositions.jsonl':True}, ['P1','E1'] * 4)


if __name__ == '__main__':
    unittest.main()
