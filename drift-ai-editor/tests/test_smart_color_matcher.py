"""
Unit tests for SmartLutCinematicColorMatcher in CutWire Drift AI.
Verifies color temperature bias classification and FFmpeg color balance normalization filters.
"""
import unittest
from editing.smart_color_matcher import SmartLutCinematicColorMatcher
from models.scene_plan import ProjectPlan, Scene

class TestSmartLutCinematicColorMatcher(unittest.TestCase):

    def test_analyze_color_bias_space(self):
        scene = Scene(order=1, visual_description="O espaço cósmico estrelado capturado pela NASA.")
        bias = SmartLutCinematicColorMatcher.analyze_scene_color_bias(scene)
        self.assertEqual(bias, "cool_space_blue")

        filt, expl = SmartLutCinematicColorMatcher.calculate_harmonization_filter(bias)
        self.assertIn("colorbalance=", filt)
        self.assertIn("eq=contrast=", filt)

    def test_analyze_color_bias_museum(self):
        scene = Scene(order=2, visual_description="Uma pintura a óleo com estátua em museu de arte.")
        bias = SmartLutCinematicColorMatcher.analyze_scene_color_bias(scene)
        self.assertEqual(bias, "warm_tungsten")

        filt, expl = SmartLutCinematicColorMatcher.calculate_harmonization_filter(bias)
        self.assertIn("colorbalance=", filt)

    def test_harmonize_project_colors(self):
        plan = ProjectPlan(title="Projeto Harmonizado")
        plan.scenes = [
            Scene(order=1, visual_description="Nebulosa no espaço."),
            Scene(order=2, visual_description="Galeria de museu com ouro."),
            Scene(order=3, visual_description="Cena cotidiana em daylight.")
        ]

        result = SmartLutCinematicColorMatcher.harmonize_project_colors(plan)
        self.assertEqual(result["total_scenes_harmonized"], 3)
        self.assertEqual(len(result["recipes"]), 3)
        self.assertEqual(result["target_aesthetic"], "Cinematic Hollywood 5600K Balanced")

if __name__ == '__main__':
    unittest.main()
