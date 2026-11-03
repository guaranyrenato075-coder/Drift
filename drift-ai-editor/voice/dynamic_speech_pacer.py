"""
Dynamic Speech Pacer for CutWire Drift AI.
Monitors Words-Per-Minute (WPM) across narration tracks, flags lethargic or frantic speech,
and calculates adaptive ffmpeg atempo correction curves to keep retention locked in the sweet spot (~140-160 WPM).
"""
from dataclasses import dataclass
from enum import Enum
from typing import List
from models.scene_plan import ProjectPlan, Scene

class PacingStatus(str, Enum):
    TOO_SLOW = "too_slow"        # < 125 WPM (causes dropoff / boredom)
    OPTIMAL = "optimal"          # 125 - 165 WPM (ideal YouTube/TikTok retention zone)
    TOO_FAST = "too_fast"        # > 165 WPM (unintelligible / rushed)

@dataclass
class ScenePacingMetric:
    scene_order: int
    word_count: int
    duration_sec: float
    wpm: float
    status: PacingStatus
    recommended_tempo_factor: float
    ffmpeg_atempo_filter: str

@dataclass
class ProjectPacingSummary:
    average_wpm: float
    optimal_scenes_pct: float
    scenes: List[ScenePacingMetric]

class DynamicSpeechPacer:
    """
    Analyzes narration cadence and harmonizes speech speed.
    """

    TARGET_WPM = 150.0

    @classmethod
    def audit_scene(cls, scene: Scene) -> ScenePacingMetric:
        words = len(scene.narration_text.split())
        dur = max(0.5, scene.duration)
        wpm = (words / dur) * 60.0

        if wpm < 125.0:
            status = PacingStatus.TOO_SLOW
            factor = min(1.35, cls.TARGET_WPM / max(wpm, 60.0))
        elif wpm > 165.0:
            status = PacingStatus.TOO_FAST
            factor = max(0.85, cls.TARGET_WPM / wpm)
        else:
            status = PacingStatus.OPTIMAL
            factor = 1.0

        filter_str = f"atempo={factor:.3f}" if abs(factor - 1.0) > 0.02 else "anull"

        return ScenePacingMetric(
            scene_order=scene.order,
            word_count=words,
            duration_sec=dur,
            wpm=round(wpm, 1),
            status=status,
            recommended_tempo_factor=round(factor, 3),
            ffmpeg_atempo_filter=filter_str
        )

    @classmethod
    def audit_project(cls, plan: ProjectPlan) -> ProjectPacingSummary:
        metrics = [cls.audit_scene(sc) for sc in plan.scenes]
        if not metrics:
            return ProjectPacingSummary(0.0, 100.0, [])

        avg_wpm = sum(m.wpm for m in metrics) / len(metrics)
        optimal_count = sum(1 for m in metrics if m.status == PacingStatus.OPTIMAL)
        pct = (optimal_count / len(metrics)) * 100.0

        return ProjectPacingSummary(
            average_wpm=round(avg_wpm, 1),
            optimal_scenes_pct=round(pct, 1),
            scenes=metrics
        )

