"""
Unit tests for AIHashtagTagCloudGenerator in CutWire Drift AI.
Verifies keyword extraction, niche cluster categorization, and YouTube Studio 500-char tag compliance.
"""
import unittest
from pipeline.hashtag_tag_cloud_generator import AIHashtagTagCloudGenerator
from models.scene_plan import ProjectPlan, Scene, ProjectConfig

class TestAIHashtagTagCloudGenerator(unittest.TestCase):

    def test_generate_seo_metadata_for_space_documentary(self):
        plan = ProjectPlan(title="Mistérios do Universo e Buracos Negros")
        plan.config = ProjectConfig(aspect_ratio="16:9")
        plan.scenes = [
            Scene(
                order=1,
                narration_text="O espaço sideral guarda segredos profundos sobre a física cósmica.",
                visual_description="Uma nebulosa brilhante e estrelas cintilantes.",
                english_keywords=["space", "nebula", "astronomy"]
            ),
            Scene(
                order=2,
                narration_text="Os buracos negros e a teoria da gravidade explicam o cosmos.",
                visual_description="Visão telescópica de um buraco negro supermassivo.",
                english_keywords=["blackhole", "gravity", "cosmos"]
            )
        ]

        meta = AIHashtagTagCloudGenerator.generate_seo_metadata(plan)

        self.assertEqual(meta["project_id"], plan.project_id)
        self.assertIn("Ciência & Astronomia", meta["niche_category"])
        self.assertIsInstance(meta["hashtags"], list)
        self.assertGreater(len(meta["hashtags"]), 0)
        self.assertIsInstance(meta["youtube_tags_string"], str)
        self.assertLessEqual(len(meta["youtube_tags_string"]), 500)
        self.assertIn("espaço", meta["formatted_hashtags_string"].lower())
        self.assertGreater(len(meta["long_tail_keywords"]), 0)

    def test_generate_seo_metadata_for_shorts(self):
        plan = ProjectPlan(title="Fato Histórico Rápido")
        plan.config = ProjectConfig(aspect_ratio="9:16")
        plan.scenes = [
            Scene(
                order=1,
                narration_text="Roma antiga dominou séculos de história militar e política imperial.",
                visual_description="Legionários romanos marchando perante o imperador.",
                english_keywords=["rome", "history", "empire"]
            )
        ]

        meta = AIHashtagTagCloudGenerator.generate_seo_metadata(plan)
        self.assertIn("#Shorts", meta["hashtags"])
        self.assertIn("História", meta["niche_category"])
        self.assertLessEqual(len(meta["youtube_tags_string"]), 500)

if __name__ == '__main__':
    unittest.main()
