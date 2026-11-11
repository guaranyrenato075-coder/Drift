import unittest
from core.thermal_throttling_prediction_governor import ThermalThrottlingPredictionGovernor


class TestThermalThrottlingPredictionGovernor(unittest.TestCase):
    def setUp(self):
        self.governor = ThermalThrottlingPredictionGovernor(target_max_temp=82.0)

    def test_safe_temperature_pacing(self):
        res = self.governor.evaluate_thermal_pacing(current_temp_celsius=65.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["thermal_state"], "SAFE")
        self.assertEqual(res["recommended_micro_pause_ms"], 0.0)

    def test_critical_temperature_pacing(self):
        res = self.governor.evaluate_thermal_pacing(current_temp_celsius=92.0)
        self.assertEqual(res["thermal_state"], "CRITICAL")
        self.assertEqual(res["throttling_risk"], "HIGH")
        self.assertGreater(res["recommended_micro_pause_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
