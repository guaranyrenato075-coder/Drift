import unittest
from editing.gamma_space_integer_fast_lut import GammaSpaceIntegerFastLUT


class TestGammaSpaceIntegerFastLUT(unittest.TestCase):
    def test_gamma_boundaries(self):
        # 0 sRGB deve ser 0 linear
        self.assertEqual(GammaSpaceIntegerFastLUT.srgb_to_linear(0), 0)
        # 255 sRGB deve ser 65535 linear
        self.assertEqual(GammaSpaceIntegerFastLUT.srgb_to_linear(255), 65535)

        # Conversão reversa
        self.assertEqual(GammaSpaceIntegerFastLUT.linear_to_srgb(0), 0)
        self.assertEqual(GammaSpaceIntegerFastLUT.linear_to_srgb(255), 255)

    def test_benchmark_metrics(self):
        bench = GammaSpaceIntegerFastLUT.benchmark_lut_performance(total_pixels=1000)
        self.assertEqual(bench["status"], "success")
        self.assertEqual(bench["fpu_pow_operations_eliminated_per_frame"], 3000)


if __name__ == "__main__":
    unittest.main()
