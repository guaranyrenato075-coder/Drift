from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene
from analysis.storyboard_engine import VisualIntent

@dataclass
class ContinuityAlert:
    alert_type: str       # 'framing_fatigue', 'jarring_lighting', 'thematic_clash', 'missing_establishing_shot'
    scene_order: int
    severity: str         # 'warning', 'info'
    message: str
    remediation: str

@dataclass
class ContinuityReport:
    is_cinematically_sound: bool
    score: int            # 0 to 100
    alerts: List[ContinuityAlert] = field(default_factory=list)
    cinematic_shot_flow: List[str] = field(default_factory=list)

class VisualContinuityDirector:
    """
    Cinematographic Continuity & Grammar Auditor:
    Enforces classical film grammar and visual coherence:
      1. Avoids framing fatigue (e.g. 3 consecutive close-ups or 3 consecutive static shots).
      2. Ensures an establishing shot at head of sequence.
      3. Validates lighting and color temperature compatibility across adjacent cuts.
      4. Suggests shot variety (Wide -> Medium -> Detail -> Action).
    """

    @classmethod
    def audit_visual_continuity(
        cls,
        scenes: List[Scene],
        scene_intents: Optional[Dict[int, VisualIntent]] = None
    ) -> ContinuityReport:
        alerts: List[ContinuityAlert] = []
        shot_flow: List[str] = []

        if not scenes:
            return ContinuityReport(is_cinematically_sound=True, score=100)

        # 1. Check for Establishing Shot (Scene 1)
        first_intent = scene_intents.get(1) if scene_intents else None
        first_shot = first_intent.shot_type if first_intent else "wide_angle"
        shot_flow.append(f"Cena 01: {first_shot}")

        if first_shot not in ("wide_angle", "drone_aerial") and len(scenes) > 2:
            alerts.append(
                ContinuityAlert(
                    alert_type="missing_establishing_shot",
                    scene_order=1,
                    severity="info",
                    message="A abertura não possui um plano de estabelecimento (Wide/Aéreo) para situar o espectador.",
                    remediation="Recomenda-se iniciar com um plano aberto cinematográfico antes de planos fechados."
                )
            )

        # 2. Check for Consecutive Framing Repetitions (Framing Fatigue)
        for i in range(1, len(scenes)):
            prev_order = scenes[i - 1].order
            curr_order = scenes[i].order

            prev_intent = scene_intents.get(prev_order) if scene_intents else None
            curr_intent = scene_intents.get(curr_order) if scene_intents else None

            prev_shot = prev_intent.shot_type if prev_intent else "medium_shot"
            curr_shot = curr_intent.shot_type if curr_intent else "medium_shot"
            shot_flow.append(f"Cena {curr_order:02d}: {curr_shot}")

            # Check if 3 consecutive scenes share identical framing
            if i >= 2:
                p2_intent = scene_intents.get(scenes[i - 2].order) if scene_intents else None
                p2_shot = p2_intent.shot_type if p2_intent else ""
                if prev_shot == curr_shot == p2_shot:
                    alerts.append(
                        ContinuityAlert(
                            alert_type="framing_fatigue",
                            scene_order=curr_order,
                            severity="warning",
                            message=f"Três cenas consecutivas usam o mesmo enquadramento ({curr_shot}), causando monotonia visual.",
                            remediation="Alterne para um plano detalhe (Close-up) ou movimento de câmera para renovar a atenção do espectador."
                        )
                    )

            # Check for sudden emotional / lighting clashes
            if prev_intent and curr_intent:
                if prev_intent.emotional_tone == "cosmic_wonder" and curr_intent.emotional_tone == "hesitation":
                    alerts.append(
                        ContinuityAlert(
                            alert_type="jarring_lighting",
                            scene_order=curr_order,
                            severity="info",
                            message="Transição brusca de iluminação entre escuridão cósmica e cena humana com dúvida.",
                            remediation="Insira uma transição crossfade suave de pelo menos 600ms para amortecer o corte."
                        )
                    )

        score = max(0, 100 - (len(alerts) * 15))
        return ContinuityReport(
            is_cinematically_sound=len([a for a in alerts if a.severity == "warning"]) == 0,
            score=score,
            alerts=alerts,
            cinematic_shot_flow=shot_flow
        )

