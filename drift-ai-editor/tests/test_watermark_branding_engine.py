"""
Unit tests for VideoWatermarkBrandingEngine in CutWire Drift AI.
Verifies watermark coordinate calculations and animated lower-third FFmpeg drawtext filters.
"""
import unittest
from editing.watermark_branding_engine import VideoWatermarkBrandingEngine, BrandingConfig

class TestWatermarkBrandingEngine(unittest.TestCase):

    def test_position_coords_calculation(self):
        # Default top_right
        x_tr, y_tr = VideoWatermarkBrandingEngine.get_position_coords("top_right", margin=25)
        self.assertEqual(x_tr, "w-tw-25")
        self.assertEqual(y_tr, "25")

        # Top left
        x_tl, y_tl = VideoWatermarkBrandingEngine.get_position_coords("top_left", margin=20)
        self.assertEqual(x_tl, "20")
        self.assertEqual(y_tl, "20")

        # Bottom right
        x_br, y_br = VideoWatermarkBrandingEngine.get_position_coords("bottom_right", margin=30)
        self.assertEqual(x_br, "w-tw-30")
        self.assertEqual(y_br, "h-th-30")

        # Bottom left
        x_bl, y_bl = VideoWatermarkBrandingEngine.get_position_coords("bottom_left", margin=15)
        self.assertEqual(x_bl, "15")
        self.assertEqual(y_bl, "h-th-15")

    def test_generate_ffmpeg_branding_filter_with_lower_third(self):
        cfg = BrandingConfig(
            channel_tag="@DriftStudio",
            position="top_right",
            opacity=0.80,
            enable_lower_third=True,
            lower_third_title="MISTÉRIOS DO COSMOS",
            lower_third_duration_sec=5.0
        )
        filt = VideoWatermarkBrandingEngine.generate_ffmpeg_branding_filter(cfg, 1920, 1080)

        self.assertIn("drawtext=text='@DriftStudio'", filt)
        self.assertIn("fontcolor=white@0.8", filt)
        self.assertIn("drawtext=text='MISTÉRIOS DO COSMOS'", filt)
        self.assertIn("between(t,0.5,5.0)", filt)

    def test_generate_ffmpeg_branding_filter_watermark_only(self):
        cfg = BrandingConfig(
            channel_tag="@MinimalChannel",
            position="bottom_left",
            opacity=0.60,
            enable_lower_third=False
        )
        filt = VideoWatermarkBrandingEngine.generate_ffmpeg_branding_filter(cfg, 1920, 1080)

        self.assertIn("drawtext=text='@MinimalChannel'", filt)
        self.assertNotIn("between(t,", filt)

if __name__ == '__main__':
    unittest.main()
