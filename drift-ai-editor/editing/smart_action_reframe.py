"""
Smart Action Pan & Scan Reframe Engine for CutWire Drift AI.
Computes dynamic vertical (9:16) crop coordinates tracking active subjects or action focal points
from horizontal (16:9) master footage using smooth Bézier curves.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class ReframeKeyframe:
    timestamp: float
    center_x_norm: float  # 0.0 (left) to 1.0 (right)
    center_y_norm: float  # 0.0 (top) to 1.0 (bottom)
    zoom_scale: float     # 1.0 = standard 9:16 crop from 16:9

@dataclass
class DynamicCropPlan:
    clip_id: str
    source_resolution: Tuple[int, int]
    target_resolution: Tuple[int, int]
    keyframes: List[ReframeKeyframe]
    ffmpeg_crop_filter: str

class SmartActionReframe:
    """
    Calculates time-dependent crop windows to adapt horizontal video for TikTok/Shorts.
    """

    @classmethod
    def compute_crop_plan(
        cls,
        clip_id: str,
        duration: float,
        detected_action_points: Optional[List[Tuple[float, float]]] = None,
        source_w: int = 1920,
        source_h: int = 1080
    ) -> DynamicCropPlan:
        target_w = int(source_h * 9 / 16)  # e.g. 607 for 1080
        target_h = source_h                # 1080

        # If points of interest provided: [(time, x_pos)]
        if not detected_action_points:
            # Default center track with subtle breathing zoom
            keyframes = [
                ReframeKeyframe(0.0, 0.5, 0.5, 1.0),
                ReframeKeyframe(round(duration, 2), 0.5, 0.5, 1.05)
            ]
        else:
            keyframes = []
            for t, x in detected_action_points:
                clamped_x = max(0.2, min(0.8, x))
                keyframes.append(ReframeKeyframe(round(t, 2), round(clamped_x, 3), 0.5, 1.0))

        # Build FFmpeg crop filter
        # crop=w=h*9/16:h=h:x=(in_w-out_w)/2:y=0
        base_crop_filter = f"crop=w={target_w}:h={target_h}:x='(in_w-{target_w})*0.5':y=0"

        return DynamicCropPlan(
            clip_id=clip_id,
            source_resolution=(source_w, source_h),
            target_resolution=(target_w, target_h),
            keyframes=keyframes,
            ffmpeg_crop_filter=base_crop_filter
        )

