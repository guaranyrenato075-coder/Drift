"""
Smart Audience Retention Pacer & Hollywood Dopamine Wave Director for CutWire Drift AI.
Orchestrates dynamic pacing modulation by alternating between contemplative scenes (4-6s)
and rapid information burst cuts (1.2-1.8s) during key revelations to keep audience retention peak.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class PacingWaveBeat:
    scene_order: int
    rhythm_phase: str  # "contemplative", "tension_build", "information_burst", "resolution"
    original_duration: float
    optimized_duration: float
    recommended_cut_tempo: str
    dopamine_target: str

class SmartAudienceRetentionPacer:
    """
    Directs emotional and rhythmic pacing waves across the video timeline.
    """

    @classmethod
    def calculate_pacing_waves(cls, plan: ProjectPlan) -> Dict[str, Any]:
        total_scenes = len(plan.scenes)
        beats: List[PacingWaveBeat] = []
        total_optimized_time = 0.0

        for idx, scene in enumerate(plan.scenes):
            orig_dur = max(scene.duration or 3.5, 1.0)
            text = (scene.narration_text or "").lower()

            # Pacing wave pattern:
            # 1. First scene: punchy intro
            if idx == 0:
                phase = "tension_build"
                opt_dur = min(orig_dur, 3.2)
                tempo = "Rápido & Dinâmico"
                dopamine = "Captura Imediata de Atenção (Hook)"

            # 2. Climax / High-intensity keywords -> Information burst
            elif any(k in text for k in ["choque", "perigo", "revelou", "confronto", "urgente", "segredo"]):
                phase = "information_burst"
                opt_dur = max(1.4, min(orig_dur * 0.75, 2.2))
                tempo = "Rajada Rápida (1.5s - 2.0s)"
                dopamine = "Pico de Adrenalina & Aceleração Visual"

            # 3. Last scene -> Resolution
            elif idx == total_scenes - 1:
                phase = "resolution"
                opt_dur = max(orig_dur, 4.0)
                tempo = "Solene & Cadenciado"
                dopamine = "Fechamento Emocional & Satisfação"

            # 4. Even scenes -> Contemplative rest
            elif idx % 2 == 0:
                phase = "contemplative"
                opt_dur = max(orig_dur, 4.2)
                tempo = "Lento & Contemplativo (4s - 5s)"
                dopamine = "Respiração Cognitiva & Assimilação"

            # 5. Odd scenes -> Tension build
            else:
                phase = "tension_build"
                opt_dur = min(orig_dur, 3.0)
                tempo = "Moderado Acelerando"
                dopamine = "Crescimento de Curiosidade"

            scene.duration = round(opt_dur, 2)
            total_optimized_time += opt_dur

            beats.append(PacingWaveBeat(
                scene_order=scene.order,
                rhythm_phase=phase,
                original_duration=round(orig_dur, 2),
                optimized_duration=round(opt_dur, 2),
                recommended_cut_tempo=tempo,
                dopamine_target=dopamine
            ))

        return {
            "project_id": plan.project_id,
            "total_scenes_paced": len(beats),
            "total_timeline_duration_sec": round(total_optimized_time, 2),
            "pacing_strategy": "Hollywood Dopamine Wave (Contemplation & Burst Alternate)",
            "pacing_beats": [b.__dict__ for b in beats]
        }
