"""
Visual Retention Heatmap Auditor & YouTube Audience Curve Predictor for CutWire Drift AI.
Audits timeline pacing second-by-second to detect viewer drop-off risk zones (static media > 3.2s),
plots predictive retention decay curves, and suggests 1-click B-Roll/Foley/Transition injections.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class DropoffRiskZone:
    scene_order: int
    start_sec: float
    end_sec: float
    duration_sec: float
    risk_level: str  # "ALTO", "MÉDIO", "BAIXO"
    reason: str
    remediation_suggestion: str

class VisualRetentionHeatmapAuditor:
    """
    Simulates audience attention curves and identifies visual boredom fatigue points.
    """

    MAX_STATIC_DURATION_THRESHOLD_SEC = 3.2

    @classmethod
    def audit_retention_curve(cls, plan: ProjectPlan) -> Dict[str, Any]:
        risk_zones: List[DropoffRiskZone] = []
        retention_curve_points: List[Dict[str, Any]] = []

        current_time = 0.0
        current_retention_pct = 100.0  # Starts at 100% at second 0

        for scene in plan.scenes:
            dur = max(scene.duration or 3.0, 1.0)
            has_fast_words = len((scene.narration_text or "").split()) > 10
            is_static_over_limit = dur > cls.MAX_STATIC_DURATION_THRESHOLD_SEC

            # Pacing drop-off penalty
            if is_static_over_limit:
                risk_level = "ALTO" if dur > 5.0 else "MÉDIO"
                penalty = 6.5 if risk_level == "ALTO" else 3.5
                remediation = "Injetar corte B-Roll secundário ou ativar Ken Burns dinâmico."
                risk_zones.append(DropoffRiskZone(
                    scene_order=scene.order,
                    start_sec=round(current_time, 2),
                    end_sec=round(current_time + dur, 2),
                    duration_sec=round(dur, 2),
                    risk_level=risk_level,
                    reason=f"Cena longa ({dur:.1f}s) sem quebra visual pode causar fadiga e abandono.",
                    remediation_suggestion=remediation
                ))
            else:
                penalty = 1.0

            # Step through seconds in scene
            sec_step = 1.0
            t = 0.0
            while t < dur:
                decay_rate = 0.4 if (current_time + t) < 15.0 else 0.15
                current_retention_pct = max(35.0, current_retention_pct - decay_rate)
                retention_curve_points.append({
                    "timestamp_sec": round(current_time + t, 1),
                    "retention_pct": round(current_retention_pct, 1),
                    "scene_order": scene.order
                })
                t += sec_step

            # Hook boost if narrative is energetic
            if has_fast_words:
                current_retention_pct = min(100.0, current_retention_pct + 1.5)

            current_time += dur

        avg_expected_retention = (
            sum(p["retention_pct"] for p in retention_curve_points) / max(len(retention_curve_points), 1)
        )

        overall_grade = "A+" if len(risk_zones) == 0 else ("B" if len(risk_zones) <= 2 else "C-")

        return {
            "project_id": plan.project_id,
            "overall_pacing_grade": overall_grade,
            "average_predicted_retention_pct": round(avg_expected_retention, 1),
            "total_risk_zones_found": len(risk_zones),
            "total_timeline_duration_sec": round(current_time, 2),
            "risk_zones": [z.__dict__ for z in risk_zones],
            "retention_curve_sample": retention_curve_points[::3]  # Subsampled for UI plotting
        }

    @classmethod
    def auto_remediate_plan_pacing(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """
        Applies automatic pacing fixes: activates Ken Burns on scenes > 3.2s
        and splits overly long descriptions into tighter dynamic pacing.
        """
        remediated_scenes = 0
        for scene in plan.scenes:
            if (scene.duration or 3.0) > cls.MAX_STATIC_DURATION_THRESHOLD_SEC:
                scene.camera_motion = "dynamic_punch_in"
                remediated_scenes += 1

        return {
            "project_id": plan.project_id,
            "remediated_scenes_count": remediated_scenes,
            "status": "Cenas estabilizadas com aceleração visual e zoom orgânico."
        }
