"""Unit tests for sakanalytics scale helpers (stdlib only; collected by pytest too).

    python3 -S -m unittest tests/test_log_scale.py
"""
from __future__ import annotations

import io, json, math, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # sakanalytics.py はリポジトリ根（python -S -m unittest でも読める）
import sakanalytics as scale  # noqa: E402


# Public portfolio Languages bar example (docs/skills.md): unrounded scores.
# The markdown itself shows 69.1 and 59.4; these are the exact ratios.
PYTHON_BYTES = 26235991
NODE_BYTES = 500501
TS_BYTES = 79007
NODE_UNROUNDED = 69.14053257346154
TS_UNROUNDED = 59.41454195162007
TS_NARROW = 44.56090646371506


class LogScaleTests(unittest.TestCase):
    def test_anchor_defaults_to_max_and_maps_max_to_top(self):
        self.assertEqual(scale.log_scale([1, 9, 3], top=90, round_to=None),
                         scale.log_scale([1, 9, 3], anchor=9, top=90, round_to=None))
        self.assertEqual(scale.log_scale([9], top=90, round_to=None), [90.0])

    def test_zero_without_floor_is_zero(self):
        self.assertEqual(scale.log_scale([0, 9], anchor=9, top=90, round_to=None), [0.0, 90.0])

    def test_zero_with_floor_uses_floor_unrounded(self):
        self.assertEqual(scale.log_scale([0, 9], anchor=9, top=90, floor=3, round_to=5), [3, 90])

    def test_round_to_none_disables_rounding(self):
        raw = scale.log_scale([NODE_BYTES], anchor=PYTHON_BYTES, top=90, round_to=None)
        self.assertEqual(raw, [NODE_UNROUNDED])
        self.assertNotEqual(raw[0], 70)

    def test_round_to_default_is_multiple_of_five_half_away_from_zero(self):
        self.assertEqual(scale.round_score(69.14053257346154), 70)
        self.assertEqual(scale.round_score(44.56090646371506), 45)
        self.assertEqual(scale.round_score(2.5), 5)
        self.assertEqual(scale.round_score(-2.5), -5)
        self.assertEqual(scale.round_score(67.5), 70)
        self.assertEqual(scale.log_scale([NODE_BYTES], anchor=PYTHON_BYTES, top=90), [70])

    def test_base_does_not_change_the_normalized_ratio(self):
        kwargs = dict(anchor=PYTHON_BYTES, top=90, round_to=None)
        values = [PYTHON_BYTES, NODE_BYTES, TS_BYTES]
        by_ten = scale.log_scale(values, base=10, **kwargs)
        for base in (2, math.e, 3, 16):
            other = scale.log_scale(values, base=base, **kwargs)
            for left, right in zip(by_ten, other):
                self.assertAlmostEqual(left, right, places=12)

    def test_top_none_returns_unnormalized_log(self):
        values = [0, 3, 4]
        self.assertEqual(scale.log_scale(values, top=None, round_to=None, base=math.e),
                         [math.log1p(x) for x in values])
        self.assertEqual(scale.log_scale(values, top=None, round_to=None, base=10),
                         [math.log10(1 + x) for x in values])

    def test_anchor_zero_with_all_zeros(self):
        self.assertEqual(scale.log_scale([0, 0], round_to=None), [0.0, 0.0])
        self.assertEqual(scale.log_scale([0, 0], anchor=0, floor=35, round_to=5), [35, 35])

    def test_anchor_zero_rejects_positive_values(self):
        with self.assertRaises(ValueError):
            scale.log_scale([0, 1], anchor=0)

    def test_negatives_and_nonfinite_are_rejected(self):
        for args, kwargs in (
            (([-1, 2],), {}),
            (([1, 2],), {"anchor": -1}),
            (([float("nan")],), {}),
            (([float("inf")],), {}),
            (([True, 1],), {}),
            (([1],), {"top": float("nan")}),
            (([1],), {"base": 1}),
            (([1],), {"base": 0}),
            (([1],), {"base": -2}),
            (([1],), {"round_to": 0}),
            (([1],), {"round_to": -5}),
            (([1],), {"floor": float("inf")}),
            (("",), {}),
            (([],), {}),
            ((5,), {}),
        ):
            with self.subTest(args=args, kwargs=kwargs), self.assertRaises(ValueError):
                scale.log_scale(*args, **kwargs)

    def test_portfolio_language_example_before_and_after_narrow_adjust(self):
        raw = scale.log_scale(
            [PYTHON_BYTES, NODE_BYTES, TS_BYTES],
            anchor=PYTHON_BYTES, top=90, round_to=None)
        self.assertEqual(raw, [90.0, NODE_UNROUNDED, TS_UNROUNDED])
        self.assertEqual(scale.adjust_narrow(raw[1], 8), NODE_UNROUNDED)
        self.assertEqual(scale.adjust_narrow(raw[2], 2), TS_NARROW)
        self.assertEqual(scale.round_score(scale.adjust_narrow(raw[1], 8)), 70)
        self.assertEqual(scale.round_score(scale.adjust_narrow(raw[2], 2)), 45)

    def test_narrow_adjustment_then_round_differs_from_round_then_adjust(self):
        # Composition order matters; the Languages bar adjusts, then rounds.
        score = 48.0
        self.assertEqual(scale.round_score(scale.adjust_narrow(score, 2)), 35)
        self.assertEqual(scale.adjust_narrow(scale.round_score(score), 2), 37.5)


class AdjustNarrowAndLinearTests(unittest.TestCase):
    def test_adjust_narrow_only_when_count_is_strictly_between(self):
        self.assertEqual(scale.adjust_narrow(80, 0), 80)
        self.assertEqual(scale.adjust_narrow(80, 1), 60.0)
        self.assertEqual(scale.adjust_narrow(80, 2), 60.0)
        self.assertEqual(scale.adjust_narrow(80, 3), 80)
        self.assertEqual(scale.adjust_narrow(80, 2, below=2, factor=0.5), 80)
        self.assertEqual(scale.adjust_narrow(80, 1, below=2, factor=0.5), 40.0)

    def test_adjust_narrow_rejects_nonfinite(self):
        for kwargs in ({"score": float("nan"), "count": 1},
                       {"score": 1, "count": True},
                       {"score": 1, "count": 1, "below": float("inf")},
                       {"score": 1, "count": 1, "factor": float("nan")}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                scale.adjust_narrow(**kwargs)

    def test_linear_scale_multiplies_and_optional_floor_and_rounding(self):
        self.assertEqual(scale.linear_scale((3, 4), factor=.97), [.97 * 3, .97 * 4])
        self.assertEqual(scale.linear_scale([0, 10], factor=2, floor=3, round_to=5), [3, 20])
        self.assertEqual(scale.linear_scale([0, 10], factor=2, round_to=None), [0, 20])

    def test_linear_scale_rejects_negatives(self):
        with self.assertRaises(ValueError):
            scale.linear_scale([-1, 1])
        with self.assertRaises(ValueError):
            scale.linear_scale([1], factor=float("nan"))

    def test_public_api_is_on_sakanalytics_and_the_old_module_is_gone(self):
        for name in ("log_scale", "linear_scale", "adjust_narrow", "round_score"):
            self.assertTrue(callable(getattr(scale, name)))
        self.assertFalse((ROOT / "core" / "log_scale.py").exists())

    def test_round_score_none_and_invalid_step(self):
        self.assertEqual(scale.round_score(12.3, step=None), 12.3)
        with self.assertRaises(ValueError):
            scale.round_score(1, step=0)
        with self.assertRaises(ValueError):
            scale.round_score(float("nan"))



class ScaleCliTests(unittest.TestCase):
    def invoke(self, argv, stdin=""):
        stdout, stderr = io.StringIO(), io.StringIO()
        old = sys.stdin, sys.stdout, sys.stderr
        sys.stdin, sys.stdout, sys.stderr = io.StringIO(stdin), stdout, stderr
        try:
            try:
                code = scale.main(list(argv))
            except SystemExit as exc:
                code = 0 if exc.code is None else exc.code
        finally:
            sys.stdin, sys.stdout, sys.stderr = old
        return code, stdout.getvalue(), stderr.getvalue()

    def scores(self, *argv):
        code, out, err = self.invoke(argv)
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        return payload["mode"], payload["scores"]

    def test_bare_number_still_dispatches_to_boundary(self):
        code, out, err = self.invoke(["0", "--lo", "0"])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["boundary"], True)

    def test_log_defaults_and_portfolio_language_example(self):
        mode, scores = self.scores("scale", "26235991", "500501", "--anchor", "26235991")
        self.assertEqual((mode, scores), ("log", [90, 70]))
        mode, scores = self.scores("scale", "26235991", "500501", "--anchor", "26235991", "--round-to", "none")
        self.assertEqual(mode, "log")
        self.assertEqual(scores, [90.0, NODE_UNROUNDED])

    def test_top_none_floor_and_base(self):
        mode, scores = self.scores("scale", "0", "3", "--top", "none", "--round-to", "none", "--base", str(math.e))
        self.assertEqual((mode, scores), ("log", [math.log1p(0), math.log1p(3)]))
        mode, scores = self.scores("scale", "0", "9", "--anchor", "9", "--floor", "3")
        self.assertEqual((mode, scores), ("log", [3, 90]))
        ten = self.scores("scale", "500501", "--anchor", "26235991", "--round-to", "none", "--base", "10")[1]
        two = self.scores("scale", "500501", "--anchor", "26235991", "--round-to", "none", "--base", "2")[1]
        self.assertAlmostEqual(ten[0], two[0], places=12)

    def test_linear_mode_and_optional_factor_and_rounding(self):
        mode, scores = self.scores("scale", "--linear", "--factor", ".97", "3", "4")
        self.assertEqual((mode, scores), ("linear", [.97 * 3, .97 * 4]))
        mode, scores = self.scores("scale", "--linear", "0", "10")
        self.assertEqual((mode, scores), ("linear", [0, 10]))
        mode, scores = self.scores("scale", "--linear", "--factor", "2", "--round-to", "5", "0", "10", "--floor", "3")
        self.assertEqual((mode, scores), ("linear", [3, 20]))

    def test_stdin_values(self):
        code, out, err = self.invoke(["scale", "-"], stdin="1 10\n")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["scores"], scale.log_scale([1, 10]))

    def test_error_paths(self):
        cases = [
            (["scale"], ""),
            (["scale", "-1", "2"], ""),
            (["scale", "--factor", "0.97", "3"], ""),
            (["scale", "--linear", "--anchor", "10", "3"], ""),
            (["scale", "--linear", "--top", "90", "3"], ""),
            (["scale", "--linear", "--base", "10", "3"], ""),
            (["scale", "1", "--base", "1"], ""),
            (["scale", "1", "--round-to", "0"], ""),
            (["scale", "1", "--top", "inf"], ""),
            (["scale", "1", "--top", "abc"], ""),
            (["scale", "-", "-"], "1\n"),
            (["scale", "0", "1", "--anchor", "0"], ""),
        ]
        for argv, stdin in cases:
            with self.subTest(argv=argv):
                code, _out, err = self.invoke(argv, stdin=stdin)
                self.assertEqual(code, 2, err)
                self.assertTrue(err)

class LeagueLaboratoryStandaloneTests(unittest.TestCase):
    def test_help_runs_with_isolated_python_and_without_pythonpath(self):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        script = ROOT / "npb" / "league_laboratory.py"
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, "-S", str(script), "--help"],
                cwd=cwd, env=env, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--cycle-dir", result.stdout)



if __name__ == "__main__":
    unittest.main()
