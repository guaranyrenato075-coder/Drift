"""
Unit tests for ColorGradingEngine in Drift AI.
Verifies preset retrieval, auto-detection, and FFmpeg filter compilation.
"""
import unittest
from editing.color_grading_engine import ColorGradingEngine
from models.scene_plan import ProjectPlan, Scene

class TestColorGradingEngine(unittest.TestCase):

    def test_list_presets(self):
        presets = ColorGradingEngine.list_presets()
        self.assertGreaterEqual(len(presets), 5)
        preset_ids = {p["id"] for p in presets}
        self.assertIn("teal_and_orange", preset_ids)
        self.assertIn("warm_documentary", preset_ids)
        self.assertIn("deep_space", preset_ids)
        self.assertIn("nordic_moody", preset_ids)
        self.assertIn("vintage_35mm", preset_ids)

    def test_get_filter(self):
        filter_str = ColorGradingEngine.get_filter("teal_and_orange")
        self.assertIn("colorbalance", filter_str)
        self.assertIn("eq=", filter_str)

        neutral = ColorGradingEngine.get_filter("neutral")
        self.assertEqual(neutral, "null")

    def test_auto_detect_space_preset(self):
        plan = ProjectPlan(title="Cosmic Wonders of Deep Space")
        plan.scenes = [
            Scene(order=1, narration_text="The galaxy unfolds with mysterious stars and distant nebulae.", english_keywords=["galaxy", "space"])
        ]
        detected = ColorGradingEngine.auto_detect_preset_for_plan(plan)
        self.assertEqual(detected, "deep_space")

    def test_auto_detect_history_preset(self):
        plan = ProjectPlan(title="The Marcus Aurelius Legacy")
        plan.scenes = [
            Scene(order=1, narration_text="Ancient statues in Rome tell the story of ancient philosophy.", english_keywords=["ancient", "rome", "philosophy"])
        ]
        detected = ColorGradingEngine.auto_detect_preset_for_plan(plan)
        self.assertEqual(detected, "warm_documentary")

if __name__ == "__main__":
    unittest.main()
