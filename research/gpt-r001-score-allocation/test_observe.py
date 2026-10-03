"""Real-world failure shape, with synthetic scores (not republished source rows)."""
import unittest
from observe import parse


class CompetitionTests(unittest.TestCase):
    def test_same_day_regular_and_postseason_are_separated_by_labels(self):
        html = '''<div class="stvsteam"><div class="tescheaten">CS ファーストS</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>
        <div class="stvsteam"><div><a href="/bis/2013/games/s2013101200002.html">楽 3 - 2 オ</a></div></div>'''
        report, excluded = parse(html, "https://npb.jp/example")
        self.assertEqual(len(report["records"]), 1)
        self.assertEqual(report["records"][0]["home"], "e")
        self.assertEqual(excluded[0]["label"], "CS ファーストS")

    def test_allstar_abbreviations_are_excluded_with_evidence(self):
        html = '''<div class="stvsteam"><div class="tescheaten">オールスター</div>
        <div><a href="/bis/2013/games/s2013071900001.html">パ 2 - 2 セ</a></div></div>'''
        report, excluded = parse(html, "https://npb.jp/example")
        self.assertEqual(report["unknown"], [])
        self.assertEqual(len(excluded), 1)

    def test_unknown_label_is_not_silently_discarded(self):
        html = '''<div class="stvsteam"><div class="tescheaten">未知大会</div>
        <div><a href="/bis/2013/games/s2013101200001.html">神 2 - 1 広</a></div></div>'''
        with self.assertRaisesRegex(ValueError, "unclassified"):
            parse(html, "https://npb.jp/example")


if __name__ == "__main__":
    unittest.main()
