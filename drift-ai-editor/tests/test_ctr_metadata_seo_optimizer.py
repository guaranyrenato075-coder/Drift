import unittest
from models.scene_plan import ProjectPlan, Scene
from pipeline.ctr_metadata_seo_optimizer import CTRMetadataSEOOptimizer


class TestCTRMetadataSEOOptimizer(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Inteligência Artificial em 2026",
            scenes=[
                Scene(order=1, narration_text="A virada da tecnologia.", duration=4.0),
                Scene(order=2, narration_text="O mundo mudou para sempre.", duration=6.0),
                Scene(order=3, narration_text="O que nos espera nos próximos anos.", duration=5.0)
            ]
        )

    def test_generate_metadata_package(self):
        pkg = CTRMetadataSEOOptimizer.generate_metadata_package(self.plan)
        self.assertIn("title_variants", pkg)
        self.assertEqual(len(pkg["title_variants"]), 5)
        self.assertIn("structured_description", pkg)
        self.assertIn("recommended_tags", pkg)
        self.assertIn("chapters", pkg)
        self.assertEqual(len(pkg["chapters"]), 3)
        self.assertGreaterEqual(pkg["seo_score"], 90)


if __name__ == "__main__":
    unittest.main()
