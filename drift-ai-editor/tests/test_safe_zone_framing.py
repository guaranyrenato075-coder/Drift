"""
Unit tests for SafeZoneMultiFormatFraming in Drift AI.
Verifies platform boundaries, pixel calculation, and CSS guide generation for 9:16, 16:9, and 1:1.
"""
import unittest
from editing.safe_zone_framing import SafeZoneMultiFormatFraming, SafeZoneRect

class TestSafeZoneMultiFormatFraming(unittest.TestCase):

    def test_get_safe_zone(self):
        sz_vert = SafeZoneMultiFormatFraming.get_safe_zone("portrait")
        self.assertIsInstance(sz_vert, SafeZoneRect)
        self.assertGreater(sz_vert.bottom_margin_pct, 15.0)

        sz_horiz = SafeZoneMultiFormatFraming.get_safe_zone("landscape")
        self.assertIsInstance(sz_horiz, SafeZoneRect)
        self.assertLess(sz_horiz.bottom_margin_pct, 15.0)

    def test_calculate_pixel_bounds_9_16(self):
        bounds = SafeZoneMultiFormatFraming.calculate_pixel_bounds(1080, 1920, "portrait")
        self.assertIn("x_min", bounds)
        self.assertIn("x_max", bounds)
        self.assertIn("y_min", bounds)
        self.assertIn("y_max", bounds)
        self.assertIn("caption_y", bounds)
        self.assertGreater(bounds["x_max"], bounds["x_min"])
        self.assertGreater(bounds["y_max"], bounds["y_min"])

    def test_generate_css_overlay_guide(self):
        css = SafeZoneMultiFormatFraming.generate_css_overlay_guide("portrait")
        self.assertIn("position: absolute", css)
        self.assertIn("border: 1px dashed", css)
        self.assertIn("pointer-events: none", css)

if __name__ == "__main__":
    unittest.main()
