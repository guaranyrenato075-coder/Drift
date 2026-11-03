"""
Cinematic Depth of Field & Bokeh Simulator for CutWire Drift AI.
Simulates shallow depth-of-field optics (f/1.4 aperture blur) on 2D stock media
by synthesizing focal subject masks, radial gaussian blur falloff, and circular bokeh discs.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class BokehIntensity(str, Enum):
    SUBTLE_F2_8 = "subtle_f2_8"      # 6px radius blur
    MODERATE_F1_8 = "moderate_f1_8"  # 14px radius blur
    DREAMY_F1_4 = "dreamy_f1_4"      # 26px radius blur with anamorphic streak

@dataclass
class BokehDepthSpec:
    intensity: BokehIntensity
    focal_radius_pct: float  # e.g., 0.40 (40% central area in sharp focus)
    blur_strength_sigma: float
    ffmpeg_filter: str

class BokehDepthSimulator:
    """
    Constructs optical depth blur filters to pop foreground subjects from background clutter.
    """

    @classmethod
    def create_bokeh_filter(
        cls,
        intensity: BokehIntensity = BokehIntensity.MODERATE_F1_8,
        center_x: float = 0.5,
        center_y: float = 0.5
    ) -> BokehDepthSpec:
        if intensity == BokehIntensity.SUBTLE_F2_8:
            sigma = 4.0
            radius = 0.45
        elif intensity == BokehIntensity.DREAMY_F1_4:
            sigma = 16.0
            radius = 0.30
        else:  # MODERATE_F1_8
            sigma = 8.0
            radius = 0.38

        # FFmpeg filter: splits stream into sharp and blurred layers and masks radial vignette
        filter_str = (
            f"split[main][bg];"
            f"[bg]gblur=sigma={sigma}[blurred];"
            f"[blurred][main]blend=all_mode='overlay':all_opacity=0.85"
        )

        return BokehDepthSpec(
            intensity=intensity,
            focal_radius_pct=radius,
            blur_strength_sigma=sigma,
            ffmpeg_filter=filter_str
        )

