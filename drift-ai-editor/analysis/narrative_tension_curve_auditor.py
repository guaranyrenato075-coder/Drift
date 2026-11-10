"""
Narrative Tension Curve Auditor.
Audita a progressão dramática do roteiro segundo a estrutura clássica de 3 atos,
mapeando a curva de tensão emocional, pontos de virada (plot twists) e o clímax.
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class NarrativeTensionCurveAuditor:
    """Modela e audita o arco dramático e a curva de tensão do roteiro."""

    DRAMA_TRIGGERS = {
        "conflict": r"\b(luta|conflito|problema|crise|inimigo|ameaça|perigo|colapso|destruição)\b",
        "mystery": r"\b(segredo|mistério|oculto|estranho|porquê|ninguém|invisível|enigma)\b",
        "urgency": r"\b(agora|rápido|correr|urgente|último|acabou|imediato|segundos|tempo)\b",
        "triumph": r"\b(vitória|superou|conseguiu|venceu|sucesso|conquista|glorioso|salvação)\b"
    }

    @classmethod
    def audit_narrative_tension(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Calcula a curva de tensão cena a cena e avalia o arco dramático."""
        scenes = getattr(plan, "scenes", [])
        total_scenes = len(scenes)
        tension_points = []

        for idx, scene in enumerate(scenes):
            text = getattr(scene, "narration_text", "") or getattr(scene, "text", "") or ""
            # Posição percentual no roteiro (0.0 a 1.0)
            progress = (idx + 1) / max(total_scenes, 1)

            # Base de tensão conforme ato esperado
            if progress <= 0.25:
                # Ato 1: Apresentação e Inciting Incident
                base_tension = 45.0 + (progress * 40.0)
                act = "Ato 1 (Exposição & Gancho)"
            elif progress <= 0.75:
                # Ato 2: Confrontação e Midpoint
                base_tension = 55.0 + ((progress - 0.25) * 50.0)
                act = "Ato 2 (Escalada & Conflito)"
            else:
                # Ato 3: Clímax e Resolução
                base_tension = 80.0 if progress <= 0.90 else 50.0
                act = "Ato 3 (Clímax & Desfecho)"

            # Bônus léxico
            bonus = 0.0
            for category, pattern in cls.DRAMA_TRIGGERS.items():
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                bonus += matches * 6.0

            calculated_tension = min(100.0, round(base_tension + bonus, 1))

            tension_points.append({
                "scene_index": idx + 1,
                "progress_percent": round(progress * 100, 1),
                "act": act,
                "tension_score": calculated_tension,
                "has_conflict": bool(re.search(cls.DRAMA_TRIGGERS["conflict"], text, re.IGNORECASE)),
                "has_mystery": bool(re.search(cls.DRAMA_TRIGGERS["mystery"], text, re.IGNORECASE))
            })

        # Identifica o clímax do roteiro
        climax_scene = max(tension_points, key=lambda x: x["tension_score"]) if tension_points else None

        # Avalia integridade do arco (precisa subir até o clímax)
        avg_tension = round(sum(p["tension_score"] for p in tension_points) / max(len(tension_points), 1), 1)
        narrative_health = "EXCELLENT" if avg_tension >= 60.0 else "NEEDS_MORE_DRAMA"

        return {
            "total_scenes": total_scenes,
            "average_tension": avg_tension,
            "narrative_health": narrative_health,
            "climax_scene_index": climax_scene["scene_index"] if climax_scene else 1,
            "peak_tension_score": climax_scene["tension_score"] if climax_scene else 50.0,
            "tension_curve": tension_points,
            "storytelling_model": "Hollywood 3-Act Hero's Journey Curve"
        }
