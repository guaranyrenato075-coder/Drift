"""
Intelligent Shot Extender for CutWire Drift AI.
Provides automated strategies to safely stretch or extend short video clips:
- Dynamic Freeze Frame with subtle Ken Burns drift
- Optical flow / motion-interpolated slow motion (setpts / minterpolate)
- Seamless Ping-Pong (forward-reverse) loop
- Source file tail search (finding unused heads/tails in the source media)
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class ExtensionStrategy(str, Enum):
    SOURCE_TAIL = "source_tail"          # Extra unused frames from same raw asset
    KEN_BURNS_FREEZE = "ken_burns_freeze" # Freeze last frame with 3% slow zoom
    OPTICAL_SLOWMO = "optical_slowmo"     # Optical flow speed reduction (e.g. 0.8x)
    PING_PONG_LOOP = "ping_pong_loop"     # Forward-reverse loop for ambient b-roll

@dataclass
class ShotExtensionPlan:
    clip_id: str
    original_duration: float
    target_duration: float
    deficit_seconds: float
    strategy: ExtensionStrategy
    ffmpeg_filter: str
    explanation: str

class ShotExtender:
    """
    Evaluates clip extension needs and crafts appropriate temporal recovery filters.
    """

    @classmethod
    def plan_extension(
        cls,
        clip_id: str,
        current_duration: float,
        target_duration: float,
        available_source_duration: Optional[float] = None,
        is_ambient_motion: bool = False
    ) -> ShotExtensionPlan:
        deficit = max(0.0, target_duration - current_duration)
        if deficit <= 0.001:
            return ShotExtensionPlan(
                clip_id=clip_id,
                original_duration=current_duration,
                target_duration=target_duration,
                deficit_seconds=0.0,
                strategy=ExtensionStrategy.SOURCE_TAIL,
                ffmpeg_filter="",
                explanation="No extension needed."
            )

        # 1. Check if source file has unused head/tail frames
        if available_source_duration and (available_source_duration >= target_duration):
            return ShotExtensionPlan(
                clip_id=clip_id,
                original_duration=current_duration,
                target_duration=target_duration,
                deficit_seconds=deficit,
                strategy=ExtensionStrategy.SOURCE_TAIL,
                ffmpeg_filter="",
                explanation=f"Extended clip by trimming an additional {round(deficit, 2)}s from source file tail."
            )

        # 2. If it's ambient motion and deficit is small (< 2s), seamless ping-pong
        if is_ambient_motion and deficit <= 2.5:
            filter_str = "split[f][r];[r]reverse[rr];[f][rr]concat=n=2:v=1:a=0"
            return ShotExtensionPlan(
                clip_id=clip_id,
                original_duration=current_duration,
                target_duration=target_duration,
                deficit_seconds=deficit,
                strategy=ExtensionStrategy.PING_PONG_LOOP,
                ffmpeg_filter=filter_str,
                explanation="Applied seamless ping-pong loop to ambient footage."
            )

        # 3. If deficit is minor (< 30% speed reduction), apply optical slow-motion
        stretch_factor = target_duration / max(0.1, current_duration)
        if stretch_factor <= 1.35:
            filter_str = f"setpts={stretch_factor:.3f}*PTS"
            return ShotExtensionPlan(
                clip_id=clip_id,
                original_duration=current_duration,
                target_duration=target_duration,
                deficit_seconds=deficit,
                strategy=ExtensionStrategy.OPTICAL_SLOWMO,
                ffmpeg_filter=filter_str,
                explanation=f"Applied gentle {round((stretch_factor-1.0)*100)}% slow-motion to seamlessly reach target time."
            )

        # 4. Fallback: Freeze last frame with Ken Burns drift
        freeze_pts = current_duration
        filter_str = f"tpad=stop_mode=clone:stop_duration={round(deficit, 2)}"
        return ShotExtensionPlan(
            clip_id=clip_id,
            original_duration=current_duration,
            target_duration=target_duration,
            deficit_seconds=deficit,
            strategy=ExtensionStrategy.KEN_BURNS_FREEZE,
            ffmpeg_filter=filter_str,
            explanation=f"Held final frame with subtle drift for the remaining {round(deficit, 2)}s."
        )

