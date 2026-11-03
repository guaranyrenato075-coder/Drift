"""
Punctuation Sound FX Director for CutWire Drift AI.
Detects narrative emphasis points, scene transitions, and dramatic reveals to schedule
micro sound effects (whooshes, risers, sub-hits, pops, UI clicks) on dedicated audio track A3.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple
from models.scene_plan import ProjectPlan, Scene

class SfxType(str, Enum):
    WHOOSH_TRANSITION = "whoosh_transition"
    SUB_HIT_IMPACT = "sub_hit_impact"
    POINTER_CLICK = "pointer_click"
    DRAMATIC_RISER = "dramatic_riser"
    GLITCH_REVEAL = "glitch_reveal"

@dataclass
class SfxCue:
    timestamp: float
    sfx_type: SfxType
    target_volume_db: float  # e.g., -14.0 dB
    description: str
    timeline_track: str = "A3_SFX"

class PunctuationSfxDirector:
    """
    Schedules dynamic audio accents to punctuate narrative pacing.
    """

    @classmethod
    def schedule_project_sfx(cls, plan: ProjectPlan) -> List[SfxCue]:
        cues: List[SfxCue] = []
        current_time = 0.0

        for idx, scene in enumerate(plan.scenes):
            dur = scene.duration if scene.duration > 0 else 4.0
            text_lower = scene.narration_text.lower()

            # 1. Transition Whoosh at start of scene (except first scene)
            if idx > 0:
                cues.append(
                    SfxCue(
                        timestamp=round(current_time, 2),
                        sfx_type=SfxType.WHOOSH_TRANSITION,
                        target_volume_db=-16.0,
                        description=f"Whoosh transition into Scene #{scene.order}"
                    )
                )

            # 2. Sub-hit on climax / shock words
            impact_keywords = ["mas", "porém", "contudo", "perigo", "destruição", "segredo", "nunca", "choque", "explosão"]
            if any(k in text_lower for k in impact_keywords):
                cues.append(
                    SfxCue(
                        timestamp=round(current_time + min(1.2, dur * 0.3), 2),
                        sfx_type=SfxType.SUB_HIT_IMPACT,
                        target_volume_db=-12.0,
                        description=f"Sub-bass impact on narrative revelation in Scene #{scene.order}"
                    )
                )

            # 3. Riser before the final scene
            if idx == len(plan.scenes) - 2 and dur >= 3.0:
                cues.append(
                    SfxCue(
                        timestamp=round(current_time + dur - 2.5, 2),
                        sfx_type=SfxType.DRAMATIC_RISER,
                        target_volume_db=-18.0,
                        description="Dramatic tension riser building up to the conclusion"
                    )
                )

            current_time += dur

        return cues

