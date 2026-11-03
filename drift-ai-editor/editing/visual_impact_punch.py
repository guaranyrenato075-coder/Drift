"""
Visual Impact Punch & Micro-Zoom Engine for CutWire Drift AI.
Generates instantaneous snap zooms (108-115% scale impulse) and subtle camera shakes
aligned precisely with high-energy verbal cues or dramatic reveals to prevent visual fatigue.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List

class ImpactType(str, Enum):
    SNAP_ZOOM = "snap_zoom"             # Fast scale jump + smooth ease out
    FLASH_FRAME = "flash_frame"         # 1-frame subtle white/bloom flash
    SHAKE_PUNCH = "shake_punch"         # Micro-rotational camera shake impulse

@dataclass
class VisualImpactSpec:
    impact_type: ImpactType
    trigger_time_sec: float
    duration_frames: int
    scale_factor: float
    ffmpeg_video_filter: str

class VisualImpactPunch:
    """
    Constructs high-octane visual accentuation filters.
    """

    @classmethod
    def create_snap_zoom(
        cls,
        trigger_time_sec: float,
        duration_frames: int = 10,
        scale_factor: float = 1.12
    ) -> VisualImpactSpec:
        # Duration in seconds assuming 30 fps
        dur_sec = duration_frames / 30.0
        end_time = trigger_time_sec + dur_sec

        # Smooth scale interpolation from scale_factor down to 1.0
        filter_str = (
            f"zoompan=z='if(between(it,{trigger_time_sec},{end_time}),"
            f"{scale_factor}-({scale_factor}-1.0)*((it-{trigger_time_sec})/{dur_sec}),1.0)':"
            f"d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=hd1080"
        )

        return VisualImpactSpec(
            impact_type=ImpactType.SNAP_ZOOM,
            trigger_time_sec=trigger_time_sec,
            duration_frames=duration_frames,
            scale_factor=scale_factor,
            ffmpeg_video_filter=filter_str
        )

    @classmethod
    def create_flash_frame(cls, trigger_time_sec: float) -> VisualImpactSpec:
        end_time = trigger_time_sec + (2.0 / 30.0) # 2 frames flash
        filter_str = f"eq=brightness='if(between(t,{trigger_time_sec},{end_time}),0.35,0.0)'"
        return VisualImpactSpec(
            impact_type=ImpactType.FLASH_FRAME,
            trigger_time_sec=trigger_time_sec,
            duration_frames=2,
            scale_factor=1.0,
            ffmpeg_video_filter=filter_str
        )

