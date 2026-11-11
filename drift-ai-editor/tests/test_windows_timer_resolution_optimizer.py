import unittest
from core.windows_timer_resolution_optimizer import WindowsTimerResolutionOptimizer


class TestWindowsTimerResolutionOptimizer(unittest.TestCase):
    def test_set_high_precision_mode(self):
        res = WindowsTimerResolutionOptimizer.set_timer_resolution(high_precision_mode=True)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["high_precision_mode"])
        self.assertEqual(res["target_resolution_ms"], 1.0)

    def test_set_idle_economy_mode(self):
        res = WindowsTimerResolutionOptimizer.set_timer_resolution(high_precision_mode=False)
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["high_precision_mode"])
        self.assertEqual(res["target_resolution_ms"], 15.6)
        self.assertGreater(res["cpu_idle_power_savings_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
