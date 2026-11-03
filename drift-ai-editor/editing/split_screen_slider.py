"""
Animated Split-Screen Comparison Engine for CutWire Drift AI.
Generates dynamic side-by-side or sliding comparison wipes between two footage streams
(e.g., historical vs present day, unedited vs color-graded, before vs after).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class SplitOrientation(str, Enum):
    VERTICAL_SLIDER = "vertical_slider"      # Left to right moving line
    HORIZONTAL_SLIDER = "horizontal_slider"  # Top to bottom moving line
    STATIC_50_50 = "static_50_50"            # Fixed split screen

@dataclass
class SplitScreenRecipe:
    orientation: SplitOrientation
    label_left: str
    label_right: str
    duration_sec: float
    divider_line_width_px: int
    ffmpeg_complex_filter: str

class SplitScreenSlider:
    """
    Builds FFmpeg filter graphs for before/after comparison sequences.
    """

    @classmethod
    def create_comparison_plan(
        cls,
        clip_a_path: str,
        clip_b_path: str,
        duration_sec: float = 5.0,
        label_a: str = "Antes",
        label_b: str = "Depois",
        orientation: SplitOrientation = SplitOrientation.VERTICAL_SLIDER
    ) -> SplitScreenRecipe:
        if orientation == SplitOrientation.STATIC_50_50:
            f_str = (
                "[0:v]crop=iw/2:ih:0:0[left];"
                "[1:v]crop=iw/2:ih:iw/2:0[right];"
                "[left][right]hstack=inputs=2[out]"
            )
        else:
            # Dynamic wipe filter
            f_str = (
                f"[0:v][1:v]blend=all_expr='if(lte(X/W,T/{duration_sec}),B,A)'[out]"
            )

        return SplitScreenRecipe(
            orientation=orientation,
            label_left=label_a,
            label_right=label_b,
            duration_sec=duration_sec,
            divider_line_width_px=3,
            ffmpeg_complex_filter=f_str
        )

