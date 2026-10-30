import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sync_history as s

class Guards(unittest.TestCase):
    def test_remote_base_and_new_destination_required(self):
        for outputs, succeeds in [([s.BASE + '\trefs/heads/' + s.BASE_BRANCH, ''], True),
                                  (['0'*40 + '\trefs/heads/' + s.BASE_BRANCH, ''], False),
                                  ([s.BASE + '\trefs/heads/' + s.BASE_BRANCH, 'existing'], False)]:
            with patch.object(s, 'git', side_effect=outputs):
                if succeeds:
                    s.check_remote(Path('.'))
                else:
                    with self.assertRaises(RuntimeError): s.check_remote(Path('.'))

    def test_publish_guards_and_absent_destination_lease(self):
        good = {'GITHUB_REPOSITORY':'myon-bioinformatics/Aoi',
                'GITHUB_REF':'refs/heads/' + s.STAGING_BRANCH,
                'GITHUB_EVENT_NAME':'push', 'GITHUB_RUN_ATTEMPT':'1'}
        for key in good:
            with patch.dict(os.environ, {**good, key:'wrong'}, clear=True), patch.object(s, 'git') as git:
                with self.assertRaises(RuntimeError): s.publish(Path('.'))
                git.assert_not_called()
        with patch.dict(os.environ, good, clear=True), patch.object(s, 'validate', return_value='a'*40), patch.object(s,'check_remote'), patch.object(s,'git') as git:
            s.publish(Path('.'))
            git.assert_called_once_with(Path('.'), 'push', '--force-with-lease=refs/heads/'+s.OUTPUT_BRANCH+':', s.REPO, 'a'*40+':refs/heads/'+s.OUTPUT_BRANCH)
            self.assertNotIn(s.BASE_BRANCH, git.call_args.args[-1])
            self.assertNotIn('refs/heads/main', git.call_args.args[-1])

    def test_no_push_after_validation_or_remote_failure(self):
        good = {'GITHUB_REPOSITORY':'myon-bioinformatics/Aoi', 'GITHUB_REF':'refs/heads/'+s.STAGING_BRANCH, 'GITHUB_EVENT_NAME':'push', 'GITHUB_RUN_ATTEMPT':'1'}
        for failing in ['validate','check_remote']:
            with patch.dict(os.environ, good, clear=True), patch.object(s, 'validate'), patch.object(s,'check_remote'), patch.object(s, failing, side_effect=RuntimeError('gate')), patch.object(s,'git') as git:
                with self.assertRaises(RuntimeError): s.publish(Path('.'))
                git.assert_not_called()

    def test_validate_rejects_tree_ancestry_and_research_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            import json
            (root/'child-heads.json').write_text(json.dumps({'heads':{'myon-bioinformatics/'+n:{'sha':h} for n,h in s.UPSTREAM.values()}}))
            def fake(root,*args):
                if args[:2] == ('rev-parse','HEAD:dragowing'): return 'tree-d'
                if args[:2] == ('rev-parse',s.UPSTREAM['dragowing'][1]+'^{tree}'): return 'tree-d'
                if args[:2] == ('rev-parse','HEAD:nagoyaction'): return 'tree-n'
                if args[:2] == ('rev-parse',s.UPSTREAM['nagoyaction'][1]+'^{tree}'): return 'tree-n'
                if args[0]=='diff': return 'research/data.json'
                return ''
            with patch.object(s,'git',side_effect=fake):
                with self.assertRaisesRegex(RuntimeError,'unreviewed'): s.validate(root)
            with patch.object(s,'git',side_effect=RuntimeError('not ancestor')):
                with self.assertRaisesRegex(RuntimeError,'not ancestor'): s.validate(root)
            def mismatch(root,*args):
                if args[:2] == ('rev-parse','HEAD:dragowing'): return 'wrong'
                return fake(root,*args)
            with patch.object(s,'git',side_effect=mismatch):
                with self.assertRaisesRegex(RuntimeError,'identity'): s.validate(root)

    def test_build_requires_exact_clean_base_before_network(self):
        with patch.object(s,'git',return_value='wrong') as git:
            with self.assertRaisesRegex(RuntimeError,'fixed base'): s.build(Path('.'),Path('.'),Path('.'))
            self.assertEqual(git.call_count,1)
        with patch.object(s,'git',side_effect=[s.BASE,'dirty']) as git:
            with self.assertRaisesRegex(RuntimeError,'dirty input'): s.build(Path('.'),Path('.'),Path('.'))
            self.assertEqual(git.call_count,2)

class BuildFailures(unittest.TestCase):
    def test_wrong_upstream_parent_stops_before_publication(self):
        calls = []
        def fake(root, *args):
            calls.append(args)
            if args == ('rev-parse', 'HEAD'): return s.BASE
            if args == ('rev-parse', 'HEAD^2'): return 'wrong-parent'
            return ''
        with patch.object(s, 'git', side_effect=fake), patch.object(s, 'check_remote'):
            with self.assertRaisesRegex(RuntimeError, 'upstream parent'):
                s.build(Path('.'), Path('.'), Path('.'))
        self.assertTrue(any(c[0] == 'subtree' for c in calls))
        self.assertFalse(any(c[0] == 'push' for c in calls))
        self.assertFalse(any('--squash' in c for c in calls))

    def test_subtree_failure_cannot_publish_or_continue(self):
        calls = []
        def fake(root, *args):
            calls.append(args)
            if args == ('rev-parse', 'HEAD'): return s.BASE
            if args[0] == 'subtree': raise RuntimeError('merge conflict')
            return ''
        with patch.object(s, 'git', side_effect=fake), patch.object(s, 'check_remote'):
            with self.assertRaisesRegex(RuntimeError, 'merge conflict'):
                s.build(Path('.'), Path('.'), Path('.'))
        self.assertEqual(sum(c[0] == 'subtree' for c in calls), 1)
        self.assertFalse(any(c[0] in ('push', 'apply') for c in calls))

class TrackedOutputs(unittest.TestCase):
    def test_tracked_ignored_distribution_can_be_staged_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            s.git(root, 'init')
            (root / 'dist').mkdir()
            output = root / 'dist/example.py'
            output.write_text('old\n')
            s.git(root, 'add', 'dist/example.py')
            (root / '.gitignore').write_text('dist/\n')
            output.write_text('new\n')
            (root / 'dist/untracked.py').write_text('must not be staged\n')
            s.git(root, 'add', '-u', '--', 'dist/example.py')
            self.assertEqual(s.git(root, 'show', ':dist/example.py'), 'new')
            self.assertEqual(s.git(root, 'ls-files', 'dist'), 'dist/example.py')

if __name__ == '__main__': unittest.main()
