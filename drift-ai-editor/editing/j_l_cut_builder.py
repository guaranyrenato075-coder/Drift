"""
J-Cut & L-Cut Split Audio Transition Director for CutWire Drift AI.
Implements classical cinematic split edits where incoming audio leads video by 0.5s (J-Cut),
or outgoing dialogue continues over the subsequent video cut (L-Cut) for invisible narrative flow.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

class SplitCutType(str, Enum):
    J_CUT = "j_cut"  # Audio leads video
    L_CUT = "l_cut"  # Video leads audio
    STANDARD_CUT = "standard_cut"

@dataclass
class SplitTransitionCue:
    from_scene_order: int
    to_scene_order: int
    split_type: SplitCutType
    audio_lead_offset_sec: float
    video_cut_timestamp: float
    audio_start_timestamp: float

class JLCutDirector:
    """
    Computes split audio/video cut points across narrative scenes.
    """

    DEFAULT_LEAD_OFFSET = 0.50  # 500ms audio pre-roll

    @classmethod
    def schedule_split_cuts(cls, plan: ProjectPlan) -> List[SplitTransitionCue]:
        cues: List[SplitTransitionCue] = []
        if not plan.scenes or len(plan.scenes) < 2:
            return cues

        current_time = 0.0
        for i in range(1, len(plan.scenes)):
            s_prev = plan.scenes[i - 1]
            s_curr = plan.scenes[i]
            dur_prev = s_prev.duration if s_prev.duration > 0 else 4.0
            video_cut_time = current_time + dur_prev

            # Alternate between J-Cut and L-Cut for natural organic pacing
            split = SplitCutType.J_CUT if i % 2 == 1 else SplitCutType.L_CUT
            audio_start = video_cut_time - cls.DEFAULT_LEAD_OFFSET if split == SplitCutType.J_CUT else video_cut_time

            cues.append(
                SplitTransitionCue(
                    from_scene_order=s_prev.order,
                    to_scene_order=s_curr.order,
                    split_type=split,
                    audio_lead_offset_sec=cls.DEFAULT_LEAD_OFFSET,
                    video_cut_timestamp=round(video_cut_time, 2),
                    audio_start_timestamp=round(audio_start, 2)
                )
            )
            current_time += dur_prev

        return cues

