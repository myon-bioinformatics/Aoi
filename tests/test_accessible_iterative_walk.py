"""Stdlib deep-DOM regression and preorder parity."""
import random, sys, unittest
from pathlib import Path; from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blueprobe
from blueprobe import names


def recursive(node):
    for child in node.children:
        if isinstance(child, blueprobe._Node):
            yield child
            yield from recursive(child)


class WalkTests(unittest.TestCase):
    def test_shuffled_trees_preorder_and_full_report_parity(self):
        rng = random.Random(20261104)
        for _ in range(30):
            depths = [rng.randrange(8) for _ in range(10)]
            html = ''.join('<div>' * depth + '<button aria-label="go">x</button>'
                           + '</div>' * depth for depth in depths)
            html += '<label for="input">label</label><input id="input"><a href="a">same</a><a href="b">same</a>'
            tree = blueprobe._Tree()
            tree.feed(html)
            self.assertEqual(list(blueprobe._walk(tree.root)), list(recursive(tree.root)))
            got = names.observe(html)
            with patch.object(blueprobe, '_walk', recursive):
                expected = names.observe(html)
            self.assertEqual(got, expected)

    def test_dom_beyond_recursion_limit(self):
        depth = sys.getrecursionlimit() + 100
        html = '<div>' * depth + '<button aria-label="go">go</button>' + '</div>' * depth
        tree = blueprobe._Tree()
        tree.feed(html)
        self.assertEqual(len(list(blueprobe._walk(tree.root))), depth + 1)
        with self.assertRaises(RecursionError):
            list(recursive(tree.root))
        report = names.observe(html)
        self.assertEqual(len(report['records']), 1)
        self.assertEqual(report['records'][0]['name'], 'go')
        self.assertEqual(report['records'][0]['key'], '#' + str(depth))


if __name__ == '__main__':
    unittest.main()
