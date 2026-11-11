import unittest
from editing.integer_matrix_3d_lut_interpolator import IntegerMatrix3DLUTInterpolator


class TestIntegerMatrix3DLUTInterpolator(unittest.TestCase):
    def test_sample_interpolation(self):
        r, g, b = IntegerMatrix3DLUTInterpolator.interpolate_sample_rgb(100, 100, 100)
        self.assertGreaterEqual(r, 0)
        self.assertLessEqual(r, 255)
        self.assertGreaterEqual(g, 0)
        self.assertLessEqual(g, 255)
        self.assertGreaterEqual(b, 0)
        self.assertLessEqual(b, 255)

    def test_benchmark_metrics(self):
        bench = IntegerMatrix3DLUTInterpolator.benchmark_lut_interpolation(frame_pixels_count=1000)
        self.assertEqual(bench["status"], "success")
        self.assertEqual(bench["fpu_operations_eliminated_per_frame"], 15000)


if __name__ == "__main__":
    unittest.main()
