"""Verify exit contracts with real child processes, including intentional failures."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from loss_tail import split

HERE=Path(__file__).resolve().parent


class LossTailTests(unittest.TestCase):
    def test_cap_definition_includes_body_of_large_scores(self):
        self.assertEqual(split([0,2],[2,10],6),(5,3,2))

    def test_invalid_stage_exit_64(self):
        p=subprocess.run([sys.executable,str(HERE/"loss_tail.py"),"invalid-stage"],capture_output=True,text=True)
        self.assertEqual(p.returncode,64)

    def test_missing_input_exit_66(self):
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,str(HERE/'loss_tail.py'),'analyze','--games',str(Path(d)/'absent.jsonl')],capture_output=True,text=True)
            self.assertEqual(p.returncode,66)
            self.assertEqual(json.loads(p.stderr)['exit_code'],66)

    def test_bad_manifest_exit_65(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'games.jsonl'
            path.write_text('')
            path.with_suffix('.manifest.json').write_text('{}')
            verify=Path(d)/'verification.json';verify.write_text('{}')
            p=subprocess.run([sys.executable,str(HERE/'loss_tail.py'),'analyze','--games',str(path),'--verification',str(verify)],capture_output=True,text=True)
            self.assertEqual(p.returncode,65)

    def test_existing_engine_returns_objection_not_success(self):
        sys.path.insert(0,str(HERE.parents[1]/'pythdragoras'))
        import polars as pl
        import propositions as pr
        prop=pr.load(HERE/'tail_propositions.toml')[0][0]
        rows=[dict(season=2000+i,team='d',team_name='d',away_more=True,tail_dominates=False,gap=5,body_gap=3,tail_gap=2) for i in range(12)]
        result=pr.evaluate(prop,pl.DataFrame(rows))
        self.assertEqual(result['judgement']['code'],3)
        forms={x['form']:x for x in result['forms']}
        self.assertEqual(len(forms['original']['counterexamples']),12)
        self.assertEqual(len(forms['contrapositive']['counterexamples']),12)


if __name__=='__main__':
    unittest.main()
