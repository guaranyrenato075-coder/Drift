import unittest
from core.windows_background_thread_qos_governor import WindowsBackgroundThreadQoSGovernor


class TestWindowsBackgroundThreadQoSGovernor(unittest.TestCase):
    def test_apply_eco_qos(self):
        res_enabled = WindowsBackgroundThreadQoSGovernor.apply_eco_qos_policy(enable_eco_qos=True)
        self.assertEqual(res_enabled["status"], "success")
        self.assertTrue(res_enabled["eco_qos_enabled"])
        self.assertGreater(res_enabled["p_core_thermal_relief_pct"], 0.0)

        res_disabled = WindowsBackgroundThreadQoSGovernor.apply_eco_qos_policy(enable_eco_qos=False)
        self.assertFalse(res_disabled["eco_qos_enabled"])
        self.assertEqual(res_disabled["background_power_reduction_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
