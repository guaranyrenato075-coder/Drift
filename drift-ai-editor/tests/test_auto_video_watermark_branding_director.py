import unittest
from models.scene_plan import ProjectPlan
from pipeline.auto_video_watermark_branding_director import AutoVideoWatermarkBrandingDirector


class TestAutoVideoWatermarkBrandingDirector(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(title="Projeto com Watermark")

    def test_get_corner_positions(self):
        corners = AutoVideoWatermarkBrandingDirector.get_corner_positions()
        self.assertIn("bottom_right", corners)
        self.assertIn("top_right", corners)
        self.assertIn("bottom_left", corners)
        self.assertIn("top_left", corners)

    def test_generate_watermark_filter_plan(self):
        res = AutoVideoWatermarkBrandingDirector.generate_watermark_filter_plan(
            watermark_path="logo.png",
            position="top_right",
            opacity=0.6,
            fade_in_seconds=2.0
        )
        self.assertEqual(res["position"], "top_right")
        self.assertEqual(res["opacity"], 0.6)
        self.assertIn("overlay=W-w-35:35", res["ffmpeg_overlay_filter"])
        self.assertIn("colorchannelmixer=aa=0.6", res["ffmpeg_overlay_filter"])

    def test_apply_watermark_to_plan(self):
        res = AutoVideoWatermarkBrandingDirector.apply_watermark_to_plan(self.plan, position="bottom_left")
        self.assertEqual(res["status"], "APPLIED")
        self.assertTrue(hasattr(self.plan, "branding_watermark_config"))


if __name__ == "__main__":
    unittest.main()
