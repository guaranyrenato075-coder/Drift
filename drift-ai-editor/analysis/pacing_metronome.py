"""
Editing Pacing Metronome & Cut Cadence Monitor for CutWire Drift AI.
Computes cuts-per-minute (CPM), Average Shot Length (ASL), and maps visual rhythm dynamics
to alert the editor when scenes drag or cut too erratically.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional
from models.scene_plan import ProjectPlan, Scene

class CadenceClassification(str, Enum):
    FRANTIC_PUNCHY = "frantic_punchy"      # ASL < 2.0s (Hyperactive TikTok style)
    DYNAMIC_ENGAGING = "dynamic_engaging"  # ASL 2.0s - 4.5s (YouTube Documentary sweet-spot)
    CINEMATIC_MEASURED = "cinematic_measured" # ASL 4.5s - 7.5s (Classic film/essay pacing)
    DRAGGING_SLUGGISH = "dragging_sluggish" # ASL > 7.5s (Risk of viewer boredom)

@dataclass
class PacingProfile:
    total_cuts: int
    total_duration_sec: float
    average_shot_length_sec: float
    cuts_per_minute: float
    cadence: CadenceClassification
    scene_durations: List[float]
    rhythm_std_deviation: float

class PacingMetronome:
    """
    Audits the tempo and heartbeat of timeline edits.
    """

    @classmethod
    def analyze_pacing(cls, plan: ProjectPlan) -> PacingProfile:
        if not plan.scenes:
            return PacingProfile(0, 0.0, 0.0, 0.0, CadenceClassification.DYNAMIC_ENGAGING, [], 0.0)

        durations = [s.duration if s.duration > 0 else 4.0 for s in plan.scenes]
        total_dur = sum(durations)
        asl = total_dur / len(durations) if durations else 0.0
        cpm = (len(durations) / max(0.1, total_dur)) * 60.0

        # Calculate standard deviation of durations
        mean = asl
        variance = sum((d - mean) ** 2 for d in durations) / len(durations) if durations else 0.0
        std_dev = variance ** 0.5

        if asl < 2.0:
            cadence = CadenceClassification.FRANTIC_PUNCHY
        elif asl <= 4.5:
            cadence = CadenceClassification.DYNAMIC_ENGAGING
        elif asl <= 7.5:
            cadence = CadenceClassification.CINEMATIC_MEASURED
        else:
            cadence = CadenceClassification.DRAGGING_SLUGGISH

        return PacingProfile(
            total_cuts=len(durations),
            total_duration_sec=round(total_dur, 2),
            average_shot_length_sec=round(asl, 2),
            cuts_per_minute=round(cpm, 1),
            cadence=cadence,
            scene_durations=durations,
            rhythm_std_deviation=round(std_dev, 2)
        )

