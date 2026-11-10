"""
Smart Scene Pacing & Audience Retention Auditor for CutWire Drift AI.
Analyzes speech velocity (Words Per Minute - WPM), shot duration limits, and visual monotony risks
to prevent audience drop-off and maximize watch time on YouTube, Shorts, and documentaries.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re
from models.scene_plan import Scene, ProjectPlan

@dataclass
class ScenePacingMetric:
    scene_order: int
    duration_sec: float
    word_count: int
    wpm: float  # Words per minute
    pacing_status: str  # "optimal", "too_slow", "too_fast", "monotonous"
    risk_level: str  # "safe", "moderate", "high"
    actionable_recommendation: str

@dataclass
class PacingAuditReport:
    project_id: str
    overall_retention_score: int  # 0 to 100
    average_wpm: float
    total_scenes_analyzed: int
    monotonous_scenes_count: int
    scenes_requiring_attention: int
    summary: str
    scene_metrics: List[ScenePacingMetric]

class ScenePacingAuditor:
    """
    Audits narrative pacing and scene durations to maintain high retention.
    """

    OPTIMAL_MIN_WPM = 120.0
    OPTIMAL_MAX_WPM = 175.0
    MAX_STATIC_DURATION_SEC = 6.5

    @classmethod
    def audit_scene(cls, scene: Scene, aspect_ratio: str = "landscape") -> ScenePacingMetric:
        text = scene.narration_text or ""
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        dur = max(scene.duration or 3.0, 0.5)

        wpm = round((word_count / dur) * 60.0, 1)

        pacing_status = "optimal"
        risk_level = "safe"
        recommendation = "Ritmo e duração ideais para engajamento visual."

        # Monotony check: Long duration with same shot
        if dur > cls.MAX_STATIC_DURATION_SEC:
            pacing_status = "monotonous"
            risk_level = "high" if dur > 9.0 else "moderate"
            recommendation = f"Cena muito longa ({dur:.1f}s). Divida em 2 cortes ou ative o efeito Ken Burns Punch-In para manter o dinamismo."
        elif wpm < cls.OPTIMAL_MIN_WPM and word_count > 3:
            pacing_status = "too_slow"
            risk_level = "moderate"
            recommendation = f"Ritmo vocal lento ({wpm:.0f} WPM). Aumente a velocidade ou encurte a pausa para evitar dispersão do espectador."
        elif wpm > cls.OPTIMAL_MAX_WPM:
            pacing_status = "too_fast"
            risk_level = "moderate"
            recommendation = f"Cadência muito acelerada ({wpm:.0f} WPM). Considere dar 0.5s a mais de respiro para melhor compreensão."

        return ScenePacingMetric(
            scene_order=scene.order,
            duration_sec=round(dur, 2),
            word_count=word_count,
            wpm=wpm,
            pacing_status=pacing_status,
            risk_level=risk_level,
            actionable_recommendation=recommendation
        )

    @classmethod
    def audit_plan(cls, plan: ProjectPlan) -> PacingAuditReport:
        if not plan.scenes:
            return PacingAuditReport(
                project_id=plan.project_id,
                overall_retention_score=100,
                average_wpm=0.0,
                total_scenes_analyzed=0,
                monotonous_scenes_count=0,
                scenes_requiring_attention=0,
                summary="Nenhuma cena para analisar.",
                scene_metrics=[]
            )

        metrics = [cls.audit_scene(s, plan.config.aspect_ratio) for s in plan.scenes]
        total_wpm = sum(m.wpm for m in metrics)
        avg_wpm = round(total_wpm / len(metrics), 1)

        monotonous_count = sum(1 for m in metrics if m.pacing_status == "monotonous")
        high_risk = sum(1 for m in metrics if m.risk_level == "high")
        mod_risk = sum(1 for m in metrics if m.risk_level == "moderate")

        # Compute score (100 base, deductions for pacing defects)
        score = 100 - (high_risk * 15) - (mod_risk * 6)
        score = max(25, min(100, score))

        if score >= 85:
            summary = "Excelente ritmo narrativo! As transições e cadência mantêm o espectador altamente engajado."
        elif score >= 65:
            summary = "Bom ritmo geral com poucas cenas lentas que podem ser otimizadas com zoom punch-in."
        else:
            summary = "Atenção: Existem cenas estáticas prolongadas que podem derrubar a retenção de público no YouTube."

        return PacingAuditReport(
            project_id=plan.project_id,
            overall_retention_score=score,
            average_wpm=avg_wpm,
            total_scenes_analyzed=len(metrics),
            monotonous_scenes_count=monotonous_count,
            scenes_requiring_attention=high_risk + mod_risk,
            summary=summary,
            scene_metrics=metrics
        )
