import unittest
from models.scene_plan import ProjectPlan, Scene
from pipeline.youtube_shorts_repurposer import YouTubeShortsRepurposer


class TestYouTubeShortsRepurposer(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="A Verdade Oculta",
            scenes=[
                Scene(order=1, narration_text="Existe um segredo incrível que nunca foi contado.", duration=6.0),
                Scene(order=2, narration_text="Aqui está a prova definitiva do que ocorreu.", duration=5.0),
                Scene(order=3, narration_text="Eles perderam milhões de reais em minutos.", duration=7.0)
            ]
        )

    def test_generate_shorts_packages(self):
        res = YouTubeShortsRepurposer.generate_shorts_packages(self.plan)
        self.assertIn("shorts", res)
        self.assertGreaterEqual(res["total_shorts_generated"], 1)
        self.assertLessEqual(res["total_shorts_generated"], 3)
        short = res["shorts"][0]
        self.assertEqual(short["target_aspect_ratio"], "9:16")
        self.assertIn("boxblur=", short["ffmpeg_filter"])
        self.assertGreater(short["viral_potential_score"], 70)


if __name__ == "__main__":
    unittest.main()
