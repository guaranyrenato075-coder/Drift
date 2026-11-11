import unittest
from media.prores_dnxhr_passthrough_muxer import ProResDNxHRPassthroughMuxer


class TestProResDNxHRPassthroughMuxer(unittest.TestCase):
    def test_passthrough_eligible(self):
        res = ProResDNxHRPassthroughMuxer.evaluate_clip_passthrough_viability(
            codec_name="prores",
            has_color_grading=False,
            has_transitions=False,
            has_scale_change=False
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["can_passthrough"])
        self.assertEqual(res["ffmpeg_video_flag"], "-c:v copy")
        self.assertEqual(res["render_workload_saved_pct"], 100.0)

    def test_passthrough_ineligible_when_graded(self):
        res = ProResDNxHRPassthroughMuxer.evaluate_clip_passthrough_viability(
            codec_name="prores",
            has_color_grading=True,
            has_transitions=False,
            has_scale_change=False
        )
        self.assertFalse(res["can_passthrough"])
        self.assertEqual(res["ffmpeg_video_flag"], "-c:v prores")
        self.assertEqual(res["render_workload_saved_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()
