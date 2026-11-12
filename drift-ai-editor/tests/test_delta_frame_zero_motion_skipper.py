import unittest
from editing.delta_frame_zero_motion_skipper import DeltaFrameZeroMotionSkipper


class TestDeltaFrameZeroMotionSkipper(unittest.TestCase):
    def test_evaluate_frame_delta(self):
        # Quadro idêntico
        res_zero = DeltaFrameZeroMotionSkipper.evaluate_frame_delta(123456, 123456)
        self.assertEqual(res_zero["status"], "success")
        self.assertTrue(res_zero["zero_motion_detected"])
        self.assertEqual(res_zero["action"], "SKIP_GPU_RENDER_REUSE_FRAME_BUFFER")

        # Quadro com movimento
        res_motion = DeltaFrameZeroMotionSkipper.evaluate_frame_delta(123456, 654321)
        self.assertEqual(res_motion["status"], "success")
        self.assertFalse(res_motion["zero_motion_detected"])

    def test_benchmark_static_scene_efficiency(self):
        bench = DeltaFrameZeroMotionSkipper.benchmark_static_scene_efficiency(static_duration_sec=2.0, fps=60)
        self.assertEqual(bench["status"], "success")
        self.assertEqual(bench["frames_rendered"], 1)
        self.assertEqual(bench["frames_skipped_zero_copy"], 119)
        self.assertGreater(bench["gpu_render_workload_reduction_pct"], 95.0)


if __name__ == "__main__":
    unittest.main()
