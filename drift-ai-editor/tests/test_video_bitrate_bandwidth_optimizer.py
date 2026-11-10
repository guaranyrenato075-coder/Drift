import unittest
from models.scene_plan import ProjectPlan, Scene
from pipeline.video_bitrate_bandwidth_optimizer import VideoBitrateBandwidthOptimizer


class TestVideoBitrateBandwidthOptimizer(unittest.TestCase):
    def setUp(self):
        self.plan = ProjectPlan(
            title="Vídeo Alta Taxa de Bits",
            scenes=[
                Scene(order=1, duration=10.0),
                Scene(order=2, duration=20.0),
                Scene(order=3, duration=30.0)
            ]
        )

    def test_get_available_profiles(self):
        profiles = VideoBitrateBandwidthOptimizer.get_available_profiles()
        self.assertIn("youtube_4k_ultra", profiles)
        self.assertIn("youtube_1080p_pro", profiles)
        self.assertIn("web_fast_stream", profiles)
        self.assertIn("archive_lossless_prores", profiles)

    def test_calculate_project_bitrate_plan(self):
        res = VideoBitrateBandwidthOptimizer.calculate_project_bitrate_plan(self.plan, "youtube_1080p_pro")
        self.assertEqual(res["status"], "CALCULATED")
        self.assertEqual(res["total_duration_seconds"], 60.0)
        self.assertGreater(res["estimated_file_size_mb"], 50.0)
        self.assertIn("-b:v 12000k", res["ffmpeg_compression_args"])


if __name__ == "__main__":
    unittest.main()
