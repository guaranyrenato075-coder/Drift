import unittest
from editing.variable_framerate_jitter_smoother import VariableFramerateJitterSmoother


class TestVariableFramerateJitterSmoother(unittest.TestCase):
    def test_calculate_vfr_stabilization_filter(self):
        res = VariableFramerateJitterSmoother.calculate_vfr_stabilization_filter(target_fps=30.0)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["target_constant_fps"], 30.0)
        self.assertIn("setpts=", res["video_pts_filter"])
        self.assertIn("aresample=", res["audio_sync_filter"])


if __name__ == "__main__":
    unittest.main()
