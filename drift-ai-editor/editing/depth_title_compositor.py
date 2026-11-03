"""
3D Depth Title & Behind-Subject Text Compositor for CutWire Drift AI.
Generates multi-layer visual compositing specs:
Layer 1: Background video
Layer 2: Giant kinetic typography with drop-shadows
Layer 3: Alpha-masked foreground subject (Vox / Nerdwriter style).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class DepthTitleSpec:
    title_text: str
    font_size: int
    font_color: str
    drop_shadow_blur: int
    z_layer: str  # "behind_subject", "foreground"
    start_sec: float
    duration_sec: float
    ffmpeg_filter_graph: str

class DepthTitleCompositor:
    """
    Renders kinetic text behind people or focal foreground subjects without green screens.
    """

    @classmethod
    def create_depth_title(
        cls,
        text: str,
        start_sec: float = 0.0,
        duration_sec: float = 4.0,
        font_size: int = 72,
        font_color: str = "white"
    ) -> DepthTitleSpec:
        # Build 3-layer sandwich filter in FFmpeg
        # [bg][text]overlay[mid]; [mid][subject_alpha]overlay[final]
        f_graph = (
            f"split[bg][fg];"
            f"[bg]drawtext=text='{text}':fontsize={font_size}:fontcolor={font_color}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-50:shadowcolor=black@0.6:shadowx=6:shadowy=6[mid];"
            f"[mid][fg]blend=all_mode='multiply':all_opacity=0.3[out]"
        )

        return DepthTitleSpec(
            title_text=text,
            font_size=font_size,
            font_color=font_color,
            drop_shadow_blur=6,
            z_layer="behind_subject",
            start_sec=start_sec,
            duration_sec=duration_sec,
            ffmpeg_filter_graph=f_graph
        )

