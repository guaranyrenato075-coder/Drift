import unittest
from pipeline.gpu_power_state_transition_shield import GPUPowerStateTransitionShield


class TestGPUPowerStateTransitionShield(unittest.TestCase):
    def test_in_hysteresis_state(self):
        # 200 ms após atividade (abaixo da janela de 500 ms)
        res = GPUPowerStateTransitionShield.evaluate_state_transition(
            time_since_last_activity_ms=200.0,
            gpu_vendor="nvidia"
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["in_hysteresis"])
        self.assertTrue(res["thermal_cycling_prevented"])
        self.assertEqual(res["recommended_target_state"], "D0_LOW_VOLTAGE_STABILIZED")

    def test_outside_hysteresis_state(self):
        # 800 ms após atividade (acima da janela de 500 ms)
        res = GPUPowerStateTransitionShield.evaluate_state_transition(
            time_since_last_activity_ms=800.0,
            gpu_vendor="nvidia"
        )
        self.assertFalse(res["in_hysteresis"])
        self.assertFalse(res["thermal_cycling_prevented"])
        self.assertEqual(res["recommended_target_state"], "D3_HOT_IDLE")


if __name__ == "__main__":
    unittest.main()
