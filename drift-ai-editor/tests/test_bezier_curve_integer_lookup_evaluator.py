import unittest
from editing.bezier_curve_integer_lookup_evaluator import BezierCurveIntegerLookupEvaluator


class TestBezierCurveIntegerLookupEvaluator(unittest.TestCase):
    def test_evaluate_easing_bounds(self):
        val_0 = BezierCurveIntegerLookupEvaluator.evaluate_easing(0.0, "ease_in_out")
        val_1 = BezierCurveIntegerLookupEvaluator.evaluate_easing(1.0, "ease_in_out")
        val_mid = BezierCurveIntegerLookupEvaluator.evaluate_easing(0.5, "ease_in_out")

        self.assertAlmostEqual(val_0, 0.0, places=2)
        self.assertAlmostEqual(val_1, 1.0, places=2)
        self.assertAlmostEqual(val_mid, 0.5, places=2)

    def test_benchmark_lookup_efficiency(self):
        bench = BezierCurveIntegerLookupEvaluator.benchmark_lookup_efficiency(total_keyframes=1000)
        self.assertEqual(bench["status"], "success")
        self.assertEqual(bench["evaluated_keyframes"], 1000)
        self.assertGreater(bench["cpu_fpu_relief_pct"], 90.0)


if __name__ == "__main__":
    unittest.main()
