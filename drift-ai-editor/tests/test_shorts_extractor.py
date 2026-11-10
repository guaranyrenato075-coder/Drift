"""
Unit tests for ContentRepurposerShortsExtractor in Drift AI.
Verifies automated vertical shorts extraction, hook scoring, and 9:16 aspect ratio config.
"""
import unittest
from pipeline.shorts_extractor import ContentRepurposerShortsExtractor
from models.scene_plan import ProjectPlan, Scene

class TestShortsExtractor(unittest.TestCase):

    def test_extract_viral_shorts_from_long_project(self):
        plan = ProjectPlan(title="Documentário sobre Civilizações")
        plan.scenes = [
            Scene(order=1, narration_text="Introdução ao tema histórico.", duration=12.0),
            Scene(order=2, narration_text="O segredo e o mistério nunca revelados da cidade perdida.", duration=15.0),
            Scene(order=3, narration_text="Um choque e uma verdade incrível descoberta pelos arqueólogos.", duration=15.0),
            Scene(order=4, narration_text="Conclusão final com análise dos historiadores.", duration=12.0)
        ]

        shorts = ContentRepurposerShortsExtractor.extract_viral_shorts(plan, max_shorts=2, target_min_sec=25.0, target_max_sec=45.0)
        self.assertGreaterEqual(len(shorts), 1)

        first_short = shorts[0]
        self.assertEqual(first_short["target_aspect_ratio"], "9:16")
        self.assertIn("plan_dict", first_short)
        self.assertGreaterEqual(first_short["viral_hook_score"], 60)
        self.assertEqual(first_short["plan_dict"]["config"]["aspect_ratio"], "9:16")
        self.assertEqual(first_short["plan_dict"]["config"]["width"], 1080)
        self.assertEqual(first_short["plan_dict"]["config"]["height"], 1920)

if __name__ == "__main__":
    unittest.main()
