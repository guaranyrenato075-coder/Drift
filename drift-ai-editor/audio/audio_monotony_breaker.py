"""
Audio Monotony Breaker & Attention Anchor for CutWire Drift AI.
Audits the soundscape for prolonged static audio intervals (>10s without acoustic shifts),
scheduling micro-variations (beat dropouts, ambient string swells, subtle pitch lifts) to reignite attention.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

class MonotonyBreakerType(str, Enum):
    BEAT_DROPOUT = "beat_dropout"      # 1-beat silence before big phrase
    STRING_SWELL = "string_swell"      # Gradual crescendo pad
    SUB_PULSE = "sub_pulse"            # Low frequency heartbeat
    REVERSE_CYMBAL = "reverse_cymbal"  # Transition build

@dataclass
class AudioVariationCue:
    timestamp: float
    duration: float
    breaker_type: MonotonyBreakerType
    volume_shift_db: float
    description: str

class AudioMonotonyBreaker:
    """
    Prevents cognitive audio fatigue and listener disengagement.
    """

    MAX_STATIC_AUDIO_SECONDS = 11.0

    @classmethod
    def audit_and_schedule_variations(cls, plan: ProjectPlan) -> List[AudioVariationCue]:
        cues: List[AudioVariationCue] = []
        current_time = 0.0
        last_variation_time = 0.0

        for scene in getattr(plan, "scenes", []):
            dur = getattr(scene, "duration", 4.0)

            # If gap since last acoustic accent exceeds limit, schedule a breaker
            if (current_time - last_variation_time) >= cls.MAX_STATIC_AUDIO_SECONDS:
                cues.append(
                    AudioVariationCue(
                        timestamp=round(current_time + 1.0, 2),
                        duration=1.5,
                        breaker_type=MonotonyBreakerType.STRING_SWELL,
                        volume_shift_db=2.5,
                        description=f"Acoustic dynamic swell in Scene #{scene.order} to combat auditory fatigue"
                    )
                )
                last_variation_time = current_time + 1.0

            current_time += dur

        return cues

