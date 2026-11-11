import unittest
from editing.smart_keyframe_interval_aligner import SmartKeyframeIntervalAligner


class TestSmartKeyframeIntervalAligner(unittest.TestCase):
    def test_align_cut_close_to_keyframe(self):
        # 60 frames a 30fps = I-frame a cada 2.0s
        # Pede corte em 2.05s -> desvio de 50ms (dentro dos 200ms)
        res = SmartKeyframeIntervalAligner.align_cut_to_nearest_keyframe(
            requested_cut_sec=2.05,
            keyframe_interval_frames=60,
            fps=30.0,
            max_drift_tolerance_ms=200.0
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_lossless_stream_copyable"])
        self.assertEqual(res["aligned_cut_sec"], 2.0)
        self.assertEqual(res["cpu_energy_saved_pct"], 100.0)

    def test_cut_far_from_keyframe(self):
        # Pede corte em 3.1s -> desvio de 1100ms
        res = SmartKeyframeIntervalAligner.align_cut_to_nearest_keyframe(
            requested_cut_sec=3.1,
            keyframe_interval_frames=60,
            fps=30.0,
            max_drift_tolerance_ms=200.0
        )
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_lossless_stream_copyable"])


if __name__ == "__main__":
    unittest.main()
