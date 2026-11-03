"""
2.5D Parallax Projection & Depth Motion Engine for CutWire Drift AI.
Converts flat 2D historical photos (museum/archive prints) into spatial 2.5D depth projections:
separates foreground subject from background with differential scale and camera translation matrices.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class ParallaxCameraMove(str, Enum):
    SLOW_DOLLY_IN = "slow_dolly_in"        # Camera moves forward, background pushes back
    LATERAL_TRUCK = "lateral_truck"        # Foreground shifts left, background pans right
    ORBITAL_TILT = "orbital_tilt"          # Subtle circular perspective shift

@dataclass
class ParallaxMotionSpec:
    move_type: ParallaxCameraMove
    foreground_scale_start: float
    foreground_scale_end: float
    background_scale_start: float
    background_scale_end: float
    duration_sec: float
    ffmpeg_complex_filter: str

class ParallaxProjectionEngine:
    """
    Creates dynamic optical depth animations from single static historical photos.
    """

    @classmethod
    def generate_parallax_spec(
        cls,
        move: ParallaxCameraMove = ParallaxCameraMove.SLOW_DOLLY_IN,
        duration_sec: float = 5.0
    ) -> ParallaxMotionSpec:
        if move == ParallaxCameraMove.LATERAL_TRUCK:
            fg_s, fg_e = (1.10, 1.15)
            bg_s, bg_e = (1.00, 1.05)
            f_str = f"zoompan=z='min(zoom+0.001,1.15)':x='iw/2-(iw/zoom/2)+10*sin(it)':d={int(duration_sec*30)}:s=1920x1080"
        else:  # SLOW_DOLLY_IN
            fg_s, fg_e = (1.00, 1.12)
            bg_s, bg_e = (1.00, 1.04)
            f_str = f"zoompan=z='min(zoom+0.0015,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duration_sec*30)}:s=1920x1080"

        return ParallaxMotionSpec(
            move_type=move,
            foreground_scale_start=fg_s,
            foreground_scale_end=fg_e,
            background_scale_start=bg_s,
            background_scale_end=bg_e,
            duration_sec=duration_sec,
            ffmpeg_complex_filter=f_str
        )

