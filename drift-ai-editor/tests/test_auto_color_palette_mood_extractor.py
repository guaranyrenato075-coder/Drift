import unittest
from models.scene_plan import ProjectPlan, Scene
from pipeline.auto_color_palette_mood_extractor import AutoColorPaletteMoodExtractor


class TestAutoColorPaletteMoodExtractor(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Futuro Cyberpunk",
            scenes=[
                Scene(order=1, narration_text="No futuro da tecnologia e inteligência artificial, o código comanda os robôs.")
            ]
        )

    def test_get_preset_palettes(self):
        palettes = AutoColorPaletteMoodExtractor.get_preset_palettes()
        self.assertIn("cyberpunk_neon", palettes)
        self.assertIn("cinematic_warm_gold", palettes)
        self.assertIn("mystery_cold_steel", palettes)
        self.assertIn("nature_documentary", palettes)

    def test_extract_palette_from_plan(self):
        res = AutoColorPaletteMoodExtractor.extract_palette_from_plan(self.plan)
        self.assertEqual(res["status"], "EXTRACTED")
        self.assertEqual(res["dominant_palette_key"], "cyberpunk_neon")
        self.assertEqual(len(res["hex_colors"]), 5)
        self.assertIn("linear-gradient", res["css_gradient"])


if __name__ == "__main__":
    unittest.main()
