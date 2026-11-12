import unittest
from pipeline.simd_packed_yuv_to_rgb_matrix_converter import SIMDPackedYUVToRGBMatrixConverter


class TestSIMDPackedYUVToRGBMatrixConverter(unittest.TestCase):
    def test_convert_yuv_pixel(self):
        # Preto (Y=16, U=128, V=128) -> RGB(0, 0, 0)
        r, g, b = SIMDPackedYUVToRGBMatrixConverter.convert_yuv_pixel(16, 128, 128)
        self.assertEqual(r, 0)
        self.assertEqual(g, 0)
        self.assertEqual(b, 0)

        # Branco (Y=235, U=128, V=128) -> RGB(255, 255, 255)
        r, g, b = SIMDPackedYUVToRGBMatrixConverter.convert_yuv_pixel(235, 128, 128)
        self.assertEqual(r, 255)
        self.assertEqual(g, 255)
        self.assertEqual(b, 255)

    def test_benchmark_conversion_throughput(self):
        bench = SIMDPackedYUVToRGBMatrixConverter.benchmark_conversion_throughput(total_pixels=1920 * 1080)
        self.assertEqual(bench["status"], "success")
        self.assertEqual(bench["tested_pixels"], 1920 * 1080)
        self.assertEqual(bench["fpu_workload_reduction_pct"], 100.0)


if __name__ == "__main__":
    unittest.main()
