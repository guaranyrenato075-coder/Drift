import unittest
from editing.auto_cinematic_motion_blur_interpolator import AutoCinematicMotionBlurInterpolator


class TestAutoCinematicMotionBlurInterpolator(unittest.TestCase):
    def test_calculate_motion_blur_kernel(self):
        # Elemento em movimento rápido
        res = AutoCinematicMotionBlurInterpolator.calculate_motion_blur_kernel(delta_x=20.0, delta_y=0.0, shutter_angle=180.0)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["is_motion_blur_active"])
        self.assertEqual(res["blur_radius_pixels"], 10)  # 20 * 0.5 = 10
        self.assertEqual(res["blur_direction_deg"], 0.0)

        # Elemento estático
        static_res = AutoCinematicMotionBlurInterpolator.calculate_motion_blur_kernel(delta_x=0.0, delta_y=0.0)
        self.assertFalse(static_res["is_motion_blur_active"])
        self.assertEqual(static_res["blur_radius_pixels"], 0)

    def test_benchmark_blur_efficiency(self):
        bench = AutoCinematicMotionBlurInterpolator.benchmark_blur_efficiency()
        self.assertEqual(bench["status"], "success")
        self.assertGreater(bench["gpu_workload_saved_pct"], 50.0)


if __name__ == "__main__":
    unittest.main()
