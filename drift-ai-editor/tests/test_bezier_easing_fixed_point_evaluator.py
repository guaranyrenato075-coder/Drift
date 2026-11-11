import unittest
from editing.bezier_easing_fixed_point_evaluator import BezierEasingFixedPointEvaluator


class TestBezierEasingFixedPointEvaluator(unittest.TestCase):
    def test_easing_boundaries(self):
        val_0 = BezierEasingFixedPointEvaluator.evaluate_ease_in_out(0.0)
        self.assertAlmostEqual(val_0, 0.0, places=2)

        val_mid = BezierEasingFixedPointEvaluator.evaluate_ease_in_out(0.5)
        self.assertAlmostEqual(val_mid, 0.5, places=2)

        val_1 = BezierEasingFixedPointEvaluator.evaluate_ease_in_out(1.0)
        self.assertAlmostEqual(val_1, 1.0, places=2)

    def test_benchmark_metrics(self):
        bench = BezierEasingFixedPointEvaluator.benchmark_fixed_point_savings(animated_keyframes=5000)
        self.assertEqual(bench["status"], "success")
        self.assertGreater(bench["fpu_cycles_saved"], 0)


if __name__ == "__main__":
    unittest.main()
