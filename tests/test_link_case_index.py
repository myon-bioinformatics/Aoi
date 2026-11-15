import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from nagoyaction import linkcheck


class LinkCaseIndexTests(unittest.TestCase):
    def test_case_directory_missing_and_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'README.md').write_text('[ok](Target.txt) [case](target.txt) [dir](folder) [missing](absent.md) [again](target.txt)',encoding='utf-8')
            records=linkcheck.check_local(root,['README.md','Target.txt','Folder/item.txt'])
            self.assertEqual([r['status'] for r in records],['ok','broken','broken','broken','broken'])
            self.assertIn('Target.txt',records[1]['reason'])
            self.assertIn('Folder',records[2]['reason'])
            self.assertEqual(records[1]['reason'],records[4]['reason'])
            self.assertEqual(records[3]['reason'],'git に登録されたファイルがない')


if __name__=='__main__':unittest.main()
