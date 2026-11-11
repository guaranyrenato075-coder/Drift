import unittest
from editing.timeline_visual_viewport_culler import TimelineVisualViewportCuller


class TestTimelineVisualViewportCuller(unittest.TestCase):
    def test_cull_clips(self):
        clips = [
            {"id": "clip_0_10", "start_sec": 0.0, "end_sec": 10.0},
            {"id": "clip_10_20", "start_sec": 10.0, "end_sec": 20.0},
            {"id": "clip_20_30", "start_sec": 20.0, "end_sec": 30.0},
            {"id": "clip_30_40", "start_sec": 30.0, "end_sec": 40.0},
            {"id": "clip_40_50", "start_sec": 40.0, "end_sec": 50.0},
        ]
        # Janela visível de 12.0s a 28.0s -> apenas clip_10_20 e clip_20_30 visíveis
        res = TimelineVisualViewportCuller.cull_non_visible_clips(clips, view_start_sec=12.0, view_end_sec=28.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["visible_clips_count"], 2)
        self.assertEqual(res["culled_clips_count"], 3)
        self.assertEqual(res["ui_render_savings_pct"], 60.0)
        self.assertIn("clip_10_20", res["visible_clip_ids"])
        self.assertIn("clip_20_30", res["visible_clip_ids"])


if __name__ == "__main__":
    unittest.main()
