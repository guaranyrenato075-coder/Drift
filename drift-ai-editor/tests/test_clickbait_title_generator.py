"""
Unit tests for ClickbaitTitleHookGenerator in Drift AI.
Verifies psychological headline formulas, thumbnail hooks, and CTR estimates.
"""
import unittest
from pipeline.clickbait_title_generator import ClickbaitTitleHookGenerator
from models.scene_plan import ProjectPlan, Scene

class TestClickbaitTitleHookGenerator(unittest.TestCase):

    def test_generate_title_package_formulas(self):
        plan = ProjectPlan(title="Buracos Negros")
        plan.scenes = [
            Scene(order=1, narration_text="No centro da galáxia existe um horizonte de eventos insondável.")
        ]
        pkg = ClickbaitTitleHookGenerator.generate_title_package(plan)
        self.assertIn("base_topic", pkg)
        self.assertEqual(pkg["base_topic"], "Buracos Negros")
        self.assertIn("titles", pkg)
        self.assertEqual(len(pkg["titles"]), 5)

        first_title = pkg["titles"][0]
        self.assertIn("Verdade Oculta", first_title["headline"])
        self.assertIn("S-Tier", first_title["estimated_ctr"])

    def test_thumbnail_badges(self):
        plan = ProjectPlan(title="Projeto: A Queda de Roma")
        pkg = ClickbaitTitleHookGenerator.generate_title_package(plan)
        self.assertEqual(pkg["base_topic"], "A Queda de Roma")
        self.assertIn("thumbnail_badge_options", pkg)
        self.assertIn("A VERDADE", pkg["thumbnail_badge_options"])

if __name__ == "__main__":
    unittest.main()
