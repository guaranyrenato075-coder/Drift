"""
Safe Zone Multi-Format Framing Engine for CutWire Drift AI.
Computes platform-accurate UI overlay boundaries (TikTok, Instagram Reels, YouTube Shorts)
to guarantee that captions, key visual subjects, and lower-third graphics are never obscured
by platform interaction buttons (Like, Comment, Share, Audio Disc, Caption Bar).
"""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class SafeZoneRect:
    top_margin_pct: float     # e.g. 14% to avoid camera/notch & search bar
    bottom_margin_pct: float  # e.g. 20% to avoid caption title & sound info
    right_margin_pct: float   # e.g. 15% to avoid like/comment action buttons
    left_margin_pct: float    # e.g. 5% standard padding
    caption_safe_y_pct: float # Ideal Y-offset for subtitles (e.g. 72%)

class SafeZoneMultiFormatFraming:
    """
    Manages safe zones and visual composition guides for multi-platform video exports.
    """

    SAFE_ZONES: Dict[str, SafeZoneRect] = {
        "9:16_tiktok_shorts": SafeZoneRect(
            top_margin_pct=14.0,
            bottom_margin_pct=22.0,
            right_margin_pct=16.0,
            left_margin_pct=5.0,
            caption_safe_y_pct=70.0
        ),
        "16:9_youtube": SafeZoneRect(
            top_margin_pct=6.0,
            bottom_margin_pct=8.0,
            right_margin_pct=6.0,
            left_margin_pct=6.0,
            caption_safe_y_pct=84.0
        ),
        "1:1_square": SafeZoneRect(
            top_margin_pct=8.0,
            bottom_margin_pct=12.0,
            right_margin_pct=8.0,
            left_margin_pct=8.0,
            caption_safe_y_pct=80.0
        )
    }

    @classmethod
    def get_safe_zone(cls, aspect_ratio: str = "portrait") -> SafeZoneRect:
        if aspect_ratio in ["portrait", "9:16", "vertical"]:
            return cls.SAFE_ZONES["9:16_tiktok_shorts"]
        if aspect_ratio in ["square", "1:1"]:
            return cls.SAFE_ZONES["1:1_square"]
        return cls.SAFE_ZONES["16:9_youtube"]

    @classmethod
    def calculate_pixel_bounds(cls, width: int = 1080, height: int = 1920, aspect_ratio: str = "portrait") -> Dict[str, int]:
        """
        Calculates exact pixel boundaries for the safe area.
        """
        sz = cls.get_safe_zone(aspect_ratio)
        x_min = int(width * (sz.left_margin_pct / 100.0))
        x_max = int(width * (1.0 - (sz.right_margin_pct / 100.0)))
        y_min = int(height * (sz.top_margin_pct / 100.0))
        y_max = int(height * (1.0 - (sz.bottom_margin_pct / 100.0)))
        caption_y = int(height * (sz.caption_safe_y_pct / 100.0))

        return {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "safe_width": x_max - x_min,
            "safe_height": y_max - y_min,
            "caption_y": caption_y
        }

    @classmethod
    def generate_css_overlay_guide(cls, aspect_ratio: str = "portrait") -> str:
        """
        Generates CSS styling string for showing transparent safe zone boundary in Web UI.
        """
        sz = cls.get_safe_zone(aspect_ratio)
        return (
            f"position: absolute; "
            f"top: {sz.top_margin_pct}%; "
            f"bottom: {sz.bottom_margin_pct}%; "
            f"left: {sz.left_margin_pct}%; "
            f"right: {sz.right_margin_pct}%; "
            f"border: 1px dashed rgba(239, 68, 68, 0.6); "
            f"pointer-events: none; "
            f"box-shadow: inset 0 0 12px rgba(239, 68, 68, 0.15);"
        )
