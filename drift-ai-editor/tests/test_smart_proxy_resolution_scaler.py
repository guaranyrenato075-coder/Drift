import unittest
from media.smart_proxy_resolution_scaler import SmartProxyResolutionScaler


class TestSmartProxyResolutionScaler(unittest.TestCase):
    def test_calculate_proxy_scaling_widescreen(self):
        res = SmartProxyResolutionScaler.calculate_proxy_scaling(
            source_width=3840,
            source_height=2160,
            tier="ultra_light_540p"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["proxy_resolution"], "960x540")
        self.assertIn("scale=960:540", res["ffmpeg_scale_filter"])
        self.assertGreater(res["ram_reduction_pct"], 50.0)

    def test_calculate_proxy_scaling_vertical(self):
        res = SmartProxyResolutionScaler.calculate_proxy_scaling(
            source_width=1080,
            source_height=1920,
            tier="ultra_light_540p"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["proxy_resolution"], "540x960")


if __name__ == "__main__":
    unittest.main()
