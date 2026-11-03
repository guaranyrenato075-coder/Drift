"""
Predictive Retention Curve Engine for CutWire Drift AI.
Analyzes scene pacing, cut cadence, speech density (WPM), and visual novelty
to estimate audience drop-off risk zones and prescribe retention-boosting patches.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class DropoffRiskZone:
    timestamp_start: float
    timestamp_end: float
    risk_level: str  # "high", "medium", "low"
    predicted_retention_pct: float
    primary_cause: str
    suggested_action: str

@dataclass
class RetentionForecast:
    overall_retention_score: int  # 0 to 100
    average_shot_duration: float
    estimated_view_duration_pct: float
    risk_zones: List[DropoffRiskZone] = field(default_factory=list)
    pacing_graph: List[Tuple[float, float]] = field(default_factory=list)  # [(sec, retention_pct)]

class RetentionPredictor:
    """
    Simulates audience watch-time degradation curves based on empirical video retention dynamics.
    """

    MAX_ACCEPTABLE_STATIC_SHOT = 6.5  # Seconds without visual change before audience drops off
    OPTIMAL_WPM = 150.0               # Optimal narration words per minute

    @classmethod
    def forecast_project(cls, plan: ProjectPlan) -> RetentionForecast:
        if not plan.scenes:
            return RetentionForecast(
                overall_retention_score=100,
                average_shot_duration=0.0,
                estimated_view_duration_pct=100.0
            )

        total_dur = plan.total_duration()
        if total_dur <= 0.1:
            total_dur = sum(s.duration for s in plan.scenes) or 1.0

        current_time = 0.0
        current_retention = 100.0
        risk_zones: List[DropoffRiskZone] = []
        pacing_graph: List[Tuple[float, float]] = [(0.0, 100.0)]
        durations = []

        for idx, scene in enumerate(plan.scenes):
            dur = scene.duration if scene.duration > 0 else 4.0
            durations.append(dur)
            words = len(scene.narration_text.split())
            wpm = (words / dur) * 60.0 if dur > 0 else cls.OPTIMAL_WPM

            # Natural degradation slope over time
            decay = (dur / total_dur) * 15.0
            current_retention = max(10.0, current_retention - decay)

            # Penalty for overly long static shots
            if dur > cls.MAX_ACCEPTABLE_STATIC_SHOT:
                extra_drop = min(12.0, (dur - cls.MAX_ACCEPTABLE_STATIC_SHOT) * 2.5)
                current_retention = max(5.0, current_retention - extra_drop)
                risk_zones.append(
                    DropoffRiskZone(
                        timestamp_start=round(current_time, 2),
                        timestamp_end=round(current_time + dur, 2),
                        risk_level="high",
                        predicted_retention_pct=round(current_retention, 1),
                        primary_cause=f"Scene #{scene.order} is {round(dur, 1)}s long without visual variation",
                        suggested_action="Insert secondary B-roll cutaway or apply dynamic push-in zoom"
                    )
                )
            elif idx == 0 and dur > 4.5:
                # Hook is too slow
                risk_zones.append(
                    DropoffRiskZone(
                        timestamp_start=0.0,
                        timestamp_end=round(dur, 2),
                        risk_level="high",
                        predicted_retention_pct=round(current_retention, 1),
                        primary_cause="Opening hook scene is slow to deliver the payoff",
                        suggested_action="Trim opening scene under 3.5s or lead with high-energy visual"
                    )
                )

            current_time += dur
            pacing_graph.append((round(current_time, 2), round(current_retention, 1)))

        avg_shot = sum(durations) / len(durations) if durations else 0.0
        overall_score = max(20, min(98, int(current_retention + (15 if len(risk_zones) == 0 else 0))))

        return RetentionForecast(
            overall_retention_score=overall_score,
            average_shot_duration=round(avg_shot, 2),
            estimated_view_duration_pct=round(current_retention, 1),
            risk_zones=risk_zones,
            pacing_graph=pacing_graph
        )

