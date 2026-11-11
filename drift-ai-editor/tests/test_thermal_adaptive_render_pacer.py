import unittest
from core.thermal_adaptive_render_pacer import ThermalAdaptiveRenderPacer


class TestThermalAdaptiveRenderPacer(unittest.TestCase):
    def test_short_work_no_pause(self):
        res = ThermalAdaptiveRenderPacer.calculate_inter_scene_pause(
            elapsed_work_seconds=15.0,
            profile="balanced"
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["needs_cool_down"])
        self.assertEqual(res["pause_ms"], 0)

    def test_heavy_work_triggers_pause(self):
        res = ThermalAdaptiveRenderPacer.calculate_inter_scene_pause(
            elapsed_work_seconds=75.0,
            profile="balanced"
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["needs_cool_down"])
        self.assertGreater(res["pause_ms"], 0)


if __name__ == "__main__":
    unittest.main()
