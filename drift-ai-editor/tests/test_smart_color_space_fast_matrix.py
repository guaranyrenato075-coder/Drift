import unittest
from media.smart_color_space_fast_matrix import SmartColorSpaceFastMatrix


class TestSmartColorSpaceFastMatrix(unittest.TestCase):
    def test_build_fast_matrix_filter_bt601_to_bt709(self):
        res = SmartColorSpaceFastMatrix.build_fast_matrix_filter(source_space="bt601", target_space="bt709")
        self.assertEqual(res["status"], "success")
        self.assertIn("in_color_matrix=smpte170m", res["fast_ffmpeg_filter"])
        self.assertIn("out_color_matrix=bt709", res["fast_ffmpeg_filter"])
        self.assertIn("flags=fast_bilinear+full_chroma_int", res["fast_ffmpeg_filter"])
        self.assertGreater(res["cpu_overhead_vs_3d_lut_reduction_pct"], 80.0)


if __name__ == "__main__":
    unittest.main()
