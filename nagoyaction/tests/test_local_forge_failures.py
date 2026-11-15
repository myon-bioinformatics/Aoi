"""Failure paths must not announce completed startup or commit an unapplied dial."""
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("forge_failure_subject", ROOT / "local_forge.py")
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


class FailurePaths(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name, path in {"LOG": root / "log", "PID": root / "pid",
                           "FSTATE": root / "state", "DIAL_FILE": root / "dial"}.items():
            patch = mock.patch.object(f, name, path)
            patch.start()
            self.addCleanup(patch.stop)
        self.child = mock.Mock(pid=123456)
        self.child.poll.return_value = None
        for name, value in {"_running": 0, "hub_port": 3000}.items():
            patch = mock.patch.object(f, name, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch.object(f.subprocess, "Popen", return_value=self.child)
        patch.start()
        self.addCleanup(patch.stop)

    def test_timeout_fails_cli_and_reaps_only_own_child(self):
        with mock.patch.object(f, "_fetch", side_effect=f.urllib.error.URLError("offline")), \
             mock.patch.object(f.time, "sleep"), mock.patch.object(f.os, "kill") as kill:
            with self.assertRaisesRegex(SystemExit, "timed out"):
                f.main(["up"])
        self.child.terminate.assert_called_once()
        self.child.wait.assert_called_once_with(timeout=5)
        kill.assert_not_called()
        self.assertFalse(f.PID.exists())

    def test_early_exit_does_not_accept_other_server_health(self):
        self.child.poll.return_value = 1
        with mock.patch.object(f, "_fetch") as fetch:
            with self.assertRaisesRegex(SystemExit, "exited"):
                f.hub_up()
        fetch.assert_not_called()
        self.child.terminate.assert_not_called()
        self.assertFalse(f.PID.exists())

    def test_child_exit_during_health_check_is_failure(self):
        self.child.poll.side_effect = [None, 1, 1]
        with mock.patch.object(f, "_fetch", return_value=b"healthy"):
            with self.assertRaisesRegex(SystemExit, "exited"):
                f.hub_up()
        self.child.terminate.assert_not_called()

    def test_success_keeps_child_and_pid(self):
        with mock.patch.object(f, "_fetch", return_value=b"healthy"):
            self.assertEqual(f.hub_up(), self.child.pid)
        self.child.terminate.assert_not_called()
        self.assertEqual(f.PID.read_text(), str(self.child.pid))

    def test_replaced_pid_is_not_removed_or_signalled(self):
        def failed(*a, **kw):
            f.PID.write_text("987654")
            raise OSError("injected startup failure")
        with mock.patch.object(f, "_fetch", side_effect=failed), mock.patch.object(f.os, "kill") as kill:
            with self.assertRaises(OSError):
                f.hub_up()
        self.assertEqual(f.PID.read_text(), "987654")
        kill.assert_not_called()
        self.child.terminate.assert_called_once()

    def test_unresponsive_child_is_killed_and_reaped(self):
        self.child.wait.side_effect = [f.subprocess.TimeoutExpired("forge", 5), 0]
        with mock.patch.object(f, "_fetch", side_effect=RuntimeError("failure")):
            with self.assertRaises(RuntimeError):
                f.hub_up()
        self.child.kill.assert_called_once()
        self.assertEqual(self.child.wait.call_count, 2)

    def test_apply_failure_does_not_commit_dial_or_claim_success(self):
        f.FSTATE.write_text("{}")
        f.DIAL_FILE.write_text("3\n")
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.object(f, "_hub_apply", side_effect=SystemExit("apply failed")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            with self.assertRaises(SystemExit):
                f.dial(1)
        self.assertEqual(f.DIAL_FILE.read_text(), "3\n")
        self.assertNotIn("→", output.getvalue())
        self.assertIn("not automatically rolled back", errors.getvalue())

    def test_success_commits_dial_after_apply(self):
        f.FSTATE.write_text("{}")
        f.DIAL_FILE.write_text("3\n")
        def apply(level):
            self.assertEqual(level, 1)
            self.assertEqual(f.DIAL_FILE.read_text(), "3\n")
        with mock.patch.object(f, "_hub_apply", side_effect=apply):
            self.assertEqual(f.dial(1), 1)
        self.assertEqual(f.DIAL_FILE.read_text(), "1\n")

    def test_failed_cleanup_preserves_pid_and_original_error(self):
        self.child.terminate.side_effect = PermissionError("not allowed")
        with mock.patch.object(f, "_fetch", side_effect=RuntimeError("original failure")):
            with self.assertRaisesRegex(RuntimeError, "original failure"):
                f.hub_up()
        self.assertEqual(f.PID.read_text(), str(self.child.pid))
        self.child.kill.assert_not_called()
