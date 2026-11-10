import unittest
from models.scene_plan import ProjectPlan, Scene
from pipeline.auto_social_cutpack_exporter import AutoSocialCutpackExporter


class TestAutoSocialCutpackExporter(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Meu Vídeo Master",
            scenes=[
                Scene(order=1, duration=30.0),
                Scene(order=2, duration=30.0)
            ]
        )

    def test_get_cutpack_templates(self):
        templates = AutoSocialCutpackExporter.get_cutpack_templates()
        self.assertIn("youtube_master_16x9", templates)
        self.assertIn("vertical_shorts_9x16", templates)
        self.assertIn("square_feed_1x1", templates)
        self.assertIn("portrait_feed_4x5", templates)
        self.assertIn("teaser_trailer_15s", templates)

    def test_generate_cutpack_render_plan(self):
        res = AutoSocialCutpackExporter.generate_cutpack_render_plan(self.plan)
        self.assertEqual(res["total_cutpack_deliverables"], 5)
        self.assertEqual(len(res["jobs"]), 5)
        # Verifica se gerou o job 9:16
        job_916 = next(j for j in res["jobs"] if j["aspect_ratio"] == "9:16" and j["job_id"] == "vertical_shorts_9x16")
        self.assertIn("boxblur=", job_916["ffmpeg_command"])


if __name__ == "__main__":
    unittest.main()
