import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".github" / "scripts"))
import copy
import re
import ast
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from add_ci_label import request
from add_ci_label import confirmed_failure, process
from ci_label_api import pages, open_pulls
R='owner/repo'; H='a'*40; B='repos/'+R
class Tests(unittest.TestCase):
    def setUp(self):
        self.pr={'state':'open','head':{'sha':H}}
        self.check={'id':1,'head_sha':H,'status':'completed','conclusion':'failure','app':{'id':15368,'slug':'github-actions'},'check_suite':{'id':4}}
        self.run={'id':5,'head_sha':H,'check_suite_id':4,'repository':{'full_name':R},'status':'completed','conclusion':'failure','workflow_id':6}
        self.workflow={'id':6,'path':'.github/workflows/test.yml'}
        self.statuses=[];self.writes=[];self.pr_reads=0
    def get(self,path):
        self.assertTrue(path.startswith(B+'/'))
        if '/pulls/' in path:
            self.pr_reads+=1;return copy.deepcopy(self.pr),None
        if '/check-runs?' in path:return {'total_count':1,'check_runs':[self.check]},None
        if '/statuses?' in path:return self.statuses,None
        if '/actions/runs?' in path:return {'total_count':1,'workflow_runs':[self.run]},None
        if '/workflows/' in path:return self.workflow,None
        raise ValueError(path)
    def write(self,*args):self.writes.append(args)
    def test_add_only(self):
        self.assertEqual(process(R,1,self.get,self.write),'ADD')
        self.assertEqual(self.writes,[(B+'/issues/1/labels','POST',{'labels':['status:ci-failing']})])
    def test_nonfailure_conclusions_never_write_or_remove(self):
        for conclusion in ('success', 'cancelled', 'skipped', 'neutral', 'stale', None, 'unknown'):
            with self.subTest(conclusion=conclusion):
                self.setUp()
                self.check['conclusion'] = conclusion
                self.assertEqual(process(R, 1, self.get, self.write), 'HOLD')
                self.assertFalse(self.writes)
    def test_empty_checks_never_write_or_remove(self):
        original = self.get
        def get(path):
            if '/check-runs?' in path:
                return {'total_count': 0, 'check_runs': []}, None
            return original(path)
        self.assertEqual(process(R, 1, get, self.write), 'HOLD')
        self.assertFalse(self.writes)
    def test_negative_identity_matrix(self):
        for target,key,bad in [('check','head_sha','b'*40),('check','status','queued'),('check','conclusion','success'),('check','conclusion',None),('run','head_sha','b'*40),('run','check_suite_id',8),('run','workflow_id',None),('run','conclusion','success'),('workflow','path','outside.yml'),('workflow','id',99)]:
            with self.subTest(target=target,key=key):
                self.setUp();getattr(self,target)[key]=bad
                self.assertIsNone(confirmed_failure(R,1,self.get))
    def test_producer_and_repo(self):
        for mutate in [lambda:self.check['app'].update(id=1),lambda:self.check['app'].update(slug='fake'),lambda:self.run['repository'].update(full_name='foreign/repo')]:
            self.setUp();mutate();self.assertIsNone(confirmed_failure(R,1,self.get))
    def test_legacy_only_holds(self):
        self.check['conclusion']='success';self.statuses=[{'id':2,'creator':{'id':3},'context':'ci','state':'failure'}]
        self.assertEqual(process(R,1,self.get,self.write),'HOLD');self.assertFalse(self.writes)
    def test_head_race(self):
        original=self.get
        def get(path):
            if self.pr_reads>=1:self.pr['head']['sha']='b'*40
            return original(path)
        self.assertEqual(process(R,1,get,self.write),'HOLD');self.assertFalse(self.writes)
    def test_same_head_rerun_race(self):
        original=self.get
        def get(path):
            if self.pr_reads>=2:self.check['conclusion']='success'
            return original(path)
        self.assertEqual(process(R,1,get,self.write),'HOLD');self.assertFalse(self.writes)
    def test_final_head_race(self):
        original=self.get
        def get(path):
            if self.pr_reads>=4:self.pr['state']='closed'
            return original(path)
        self.assertEqual(process(R,1,get,self.write),'HOLD');self.assertFalse(self.writes)
    def test_pagination(self):
        stem=B+'/commits/'+H+'/check-runs?filter=latest&per_page=100&page='
        def get(path):
            n=int(path[-1]);return {'total_count':101,'check_runs':[{'id':i} for i in (range(100) if n==1 else [100])]},stem+'2' if n==1 else None
        self.assertEqual(len(pages(get,stem.split('&per_page')[0],'check_runs')),101)
        for malformed in [lambda p:({'total_count':101,'check_runs':[{'id':1}]},None),lambda p:({'total_count':1,'check_runs':[{'id':1}]},'repos/foreign/repo?page=2')]:
            with self.assertRaises(ValueError):pages(malformed,stem.split('&per_page')[0],'check_runs')
    def test_open_pr_pagination(self):
        def get(path):
            n=int(path[-1]);return ([{'id':i} for i in (range(100) if n==1 else [100])],B+'/pulls?state=open&per_page=100&page=2' if n==1 else None)
        self.assertEqual(len(open_pulls(R,get)),101)
    def test_errors_never_write(self):
        def bad(path):raise OSError('API unavailable')
        with self.assertRaises(OSError):process(R,1,bad,self.write)
        self.assertFalse(self.writes)
    def test_status_pagination(self):
        stem=B+'/commits/'+H+'/statuses'
        def get(path):
            n=int(path[-1]);return ([{'id':i} for i in (range(100) if n==1 else [100])],stem+'?per_page=100&page=2' if n==1 else None)
        self.assertEqual(len(pages(get,stem)),101)
    def test_transport_links(self):
        path=B+'/commits/'+H+'/check-runs?filter=latest&per_page=100&page=1'
        link='https://api.github.com/'+B+'/commits/'+H+'/check-runs?page=2&per_page=100&filter=latest'
        def result(url):return SimpleNamespace(stdout='HTTP/2.0 200 OK\nLink: <'+url+'>; rel="next"\n\n{"total_count": 0, "check_runs": []}')
        with patch.dict('os.environ',{'GH_REPO':R}), patch('add_ci_label.subprocess.run',return_value=result(link)):
            self.assertEqual(request(path)[1],path[:-1]+'2')
        for wrong in [link.replace('api.github.com','evil.example'),link.replace(B,'repos/other/repo'),link.replace('latest','all'),link+'&page=3']:
            with self.subTest(link=wrong), patch.dict('os.environ',{'GH_REPO':R}), patch('add_ci_label.subprocess.run',return_value=result(wrong)):
                with self.assertRaises(ValueError):request(path)
    def test_transport_explicit_repo(self):
        with patch.dict('os.environ',{'GH_REPO':R}), patch('add_ci_label.subprocess.run') as run:
            with self.assertRaises(ValueError):request('repos/foreign/repo/pulls/1')
            run.assert_not_called()
class ScanTests(unittest.TestCase):
    def test_empty_scan_is_explicit_and_never_writes(self):
        from add_ci_label import scan
        from io import StringIO
        from contextlib import redirect_stdout
        writes = []
        out = StringIO()
        with redirect_stdout(out):
            scan(R, lambda path: ([], None), lambda *a: writes.append(a))
        self.assertEqual(out.getvalue(), 'SCAN open_prs=0\n')
        self.assertEqual(writes, [])

    def test_scan_rechecks_each_pr_and_reports_invalid_evidence(self):
        from add_ci_label import scan
        from io import StringIO
        from contextlib import redirect_stdout
        out = StringIO()
        def get(path):
            if '/pulls?' in path:
                return [{'id': 1, 'number': 7}, {'id': 2, 'number': 8}], None
            raise OSError('unavailable')
        with redirect_stdout(out), patch('add_ci_label.process', side_effect=['HOLD', OSError()]) as proc:
            scan(R, get, lambda *a: self.fail('unexpected write'))
        self.assertEqual([c.args[1] for c in proc.call_args_list], [7, 8])
        self.assertIn('SCAN open_prs=2', out.getvalue())
        self.assertIn('8 HOLD: incomplete or invalid evidence', out.getvalue())

    def test_completion_allowlist_matches_workflow_inventory(self):
        workflows = Path(__file__).resolve().parents[1] / '.github/workflows'
        text = (workflows / 'ci-status-label.yml').read_text(encoding='utf-8')
        block = text.split('    workflows:\n', 1)[1].split('    types:', 1)[0]
        allowed = [ast.literal_eval(line.removeprefix('      - '))
                   for line in block.splitlines() if line.strip()]
        names = [re.search(r'^name: (.+)$', path.read_text(encoding='utf-8'), re.M)[1]
                 for path in workflows.glob('*.yml')]
        excluded = {'CI failure label (add only)', 'Aoi question inbox'}
        self.assertEqual(len(names), len(set(names)), 'Workflow names must be unique')
        self.assertEqual(len(allowed), len(set(allowed)))
        self.assertEqual(set(allowed), set(names) - excluded)
        self.assertTrue(excluded.isdisjoint(allowed))
        self.assertFalse(any(any(c in name for c in '*?![') for name in allowed))

    def test_workflow_trust_boundary_and_fallback(self):
        # This is an exact contract for one security-sensitive workflow, not a
        # YAML parser. Ignore only empty/comment-only lines; preserve indentation,
        # duplicate keys, expressions, and every executable step.
        path = Path(__file__).resolve().parents[1] / '.github/workflows/ci-status-label.yml'
        actual = '\n'.join(
            line.rstrip() for line in path.read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.lstrip().startswith('#')
        )
        expected = """name: CI failure label (add only)
on:
  schedule:
    - cron: '23 */6 * * *'
  workflow_run:
    workflows:
      - 'Action uses'
      - 'Browser startup validation'
      - 'c001 offline replay audit'
      - 'c001 saved input verification'
      - 'CDN module experiment'
      - 'CI'
      - 'DRAgoWing reports'
      - 'Links'
      - 'LittleBit holdout drift'
      - 'Minimal stdlib distributions'
      - 'Nano research environment comparison'
      - 'numpy_min backends'
      - 'Pages'
      - 'requests tqdm biopython surface'
      - 'py_launch tests'
      - 'Season simulator'
      - 'Shared tool lock'
      - 'Shrink linalg experiment'
      - 'Shrink module experiment'
      - 'Shrink polars experiment'
      - 'Stdlib feasibility survey'
      - 'Third-party min experiment'
    types: [completed]
  pull_request_target:
    types: [opened, reopened, synchronize, ready_for_review]
  workflow_dispatch:
permissions:
  contents: read
  checks: read
  actions: read
  pull-requests: read
  issues: write
concurrency:
  group: ci-failure-label-add-only
  cancel-in-progress: false
jobs:
  label:
    if: >-
      (github.event_name == 'pull_request_target' ||
       github.ref == format('refs/heads/{0}', github.event.repository.default_branch)) &&
      (github.event_name != 'workflow_run' ||
       contains(fromJSON('["failure","timed_out","action_required","startup_failure"]'), github.event.workflow_run.conclusion))
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          ref: ${{ github.event.repository.default_branch }}
          persist-credentials: false
      - name: Add confirmed latest-head failure labels; hold all removals
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
        run: python3 -B .github/scripts/add_ci_label.py"""
        self.assertEqual(actual, expected)

if __name__=='__main__':unittest.main()
