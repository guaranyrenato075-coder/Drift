"""
Video Watermark, Channel Branding & Lower-Third Engine for CutWire Drift AI.
Generates non-intrusive corner watermark text/logos and animated lower-third intros
during the first 5 seconds to assert copyright ownership and build channel brand authority.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class BrandingConfig:
    channel_tag: str = "@DriftAI"
    position: str = "top_right"  # "top_right", "top_left", "bottom_right", "bottom_left"
    opacity: float = 0.70
    font_size: int = 24
    enable_lower_third: bool = True
    lower_third_title: str = "DOCUMENTÁRIO EXCLUSIVO"
    lower_third_duration_sec: float = 5.0

class VideoWatermarkBrandingEngine:
    """
    Builds video branding filters for watermarks and intro lower-thirds.
    """

    @classmethod
    def get_position_coords(cls, position: str = "top_right", margin: int = 30) -> tuple[str, str]:
        if position == "top_left":
            return (str(margin), str(margin))
        elif position == "bottom_left":
            return (str(margin), f"h-th-{margin}")
        elif position == "bottom_right":
            return (f"w-tw-{margin}", f"h-th-{margin}")
        # Default top_right
        return (f"w-tw-{margin}", str(margin))

    @classmethod
    def generate_ffmpeg_branding_filter(
        cls,
        config: BrandingConfig,
        video_width: int = 1920,
        video_height: int = 1080
    ) -> str:
        filters = []
        x_expr, y_expr = cls.get_position_coords(config.position)

        # 1. Corner watermark
        wm_text = config.channel_tag.replace("'", "\\'")
        alpha = max(0.1, min(1.0, config.opacity))
        wm_filter = (
            f"drawtext=text='{wm_text}':fontcolor=white@{alpha}:"
            f"fontsize={config.font_size}:x={x_expr}:y={y_expr}:shadowcolor=black@0.5:shadowx=2:shadowy=2"
        )
        filters.append(wm_filter)

        # 2. Lower-third intro banner during first 5 seconds
        if config.enable_lower_third and config.lower_third_title:
            lt_text = config.lower_third_title.replace("'", "\\'").upper()
            dur = config.lower_third_duration_sec
            lt_filter = (
                f"drawtext=text='{lt_text}':fontcolor=yellow@0.9:fontsize=36:"
                f"x=80:y=h-160:box=1:boxcolor=black@0.65:boxborderw=12:"
                f"enable='between(t,0.5,{dur})'"
            )
            filters.append(lt_filter)

        return ",".join(filters)
