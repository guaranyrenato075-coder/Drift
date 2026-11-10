import unittest
from pipeline.youtube_thumbnail_ab_grid_renderer import YouTubeThumbnailABGridRenderer


class TestYouTubeThumbnailABGridRenderer(unittest.TestCase):
    def test_generate_ab_test_matrix(self):
        res = YouTubeThumbnailABGridRenderer.generate_ab_test_matrix(
            video_title="Como a Inteligência Artificial Mudará o Cinema em 2026",
            keywords=["IA", "Cinema", "Futuro"]
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["total_variants"], 4)
        self.assertEqual(len(res["matrix"]), 4)
        variants = [m["id"] for m in res["matrix"]]
        self.assertIn("variant_a_high_contrast", variants)
        self.assertIn("variant_c_emotion_close_up", variants)


if __name__ == "__main__":
    unittest.main()
