import unittest
from editing.alpha_channel_integer_fast_blender import AlphaChannelIntegerFastBlender


class TestAlphaChannelIntegerFastBlender(unittest.TestCase):
    def test_blending_values(self):
        # 100% transparente (alpha=0): deve ser dst_val
        val_transp = AlphaChannelIntegerFastBlender.blend_pixels(src_val=255, dst_val=50, alpha_byte=0)
        self.assertEqual(val_transp, 50)

        # 100% opaco (alpha=255): deve ser src_val
        val_opaque = AlphaChannelIntegerFastBlender.blend_pixels(src_val=255, dst_val=50, alpha_byte=255)
        self.assertEqual(val_opaque, 255)

        # 50% alfa (alpha=128): meio do caminho aproximado (~152)
        val_mid = AlphaChannelIntegerFastBlender.blend_pixels(src_val=200, dst_val=100, alpha_byte=128)
        self.assertAlmostEqual(val_mid, 150, delta=2)

    def test_benchmark_metrics(self):
        bench = AlphaChannelIntegerFastBlender.benchmark_blend_operations(total_pixels=1000)
        self.assertEqual(bench["status"], "success")
        self.assertEqual(bench["float_conversions_eliminated_per_frame"], 4000)


if __name__ == "__main__":
    unittest.main()
