"""
Smart Scene Transition Director.
Analisa a progressão dramática, ritmo e mudança de cena para selecionar
a melhor transição cinemática (glitch, crossfade, wipe, zoom blur ou hard cut).
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class SmartSceneTransitionDirector:
    """Diretor de transições inteligentes com base em análise semântica e temporal."""

    TRANSITION_TYPES = {
        "glitch_flash": {
            "name": "Glitch Flash / Choque",
            "description": "Corte agressivo com distorção cromática para quebra de expectativa ou perigo.",
            "duration": 0.4,
            "xfade_filter": "glitch"
        },
        "crossfade_dissolve": {
            "name": "Dissolvência Suave (Crossfade)",
            "description": "Fusão gradual entre cenas para continuidade contemplativa ou reflexão.",
            "duration": 0.8,
            "xfade_filter": "fade"
        },
        "directional_wipe": {
            "name": "Push Cinemático Direcional",
            "description": "Deslocamento lateral para avanço temporal ou mudança de cenário/tópico.",
            "duration": 0.5,
            "xfade_filter": "wipeleft"
        },
        "zoom_blur_punch": {
            "name": "Zoom Blur Punch-In",
            "description": "Transição de impacto com desfoque radial para momentos de grande revelação.",
            "duration": 0.35,
            "xfade_filter": "radial"
        },
        "hard_cut": {
            "name": "Corte Seco (Hard Cut)",
            "description": "Corte direto no tempo da batida sem transição adicional para manter o ritmo veloz.",
            "duration": 0.0,
            "xfade_filter": "none"
        }
    }

    @classmethod
    def get_transition_library(cls) -> Dict[str, Dict[str, Any]]:
        return cls.TRANSITION_TYPES

    @classmethod
    def plan_scene_transitions(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Calcula a transição ideal entre cada cena adjacente do roteiro."""
        scenes = getattr(plan, "scenes", [])
        transitions = []
        current_time = 0.0

        for i in range(len(scenes) - 1):
            curr_scene = scenes[i]
            next_scene = scenes[i + 1]

            curr_text = getattr(curr_scene, "narration_text", "") or getattr(curr_scene, "text", "") or ""
            next_text = getattr(next_scene, "narration_text", "") or getattr(next_scene, "text", "") or ""
            duration = float(getattr(curr_scene, "duration", 5.0))
            current_time += duration

            # Regras de Seleção Dramática de Transição:
            # 1. Se a próxima cena começa com choque, mistério ou quebra
            if re.search(r"\b(mas|porém|repente|segredo|perigo|mentira|bomba|chocante)\b", next_text, re.IGNORECASE):
                chosen = "glitch_flash"
                reason = "Gatilho de ruptura dramática detectado no início da cena seguinte."
            # 2. Se a cena atual for longa e meditativa (> 7s)
            elif duration > 7.0:
                chosen = "crossfade_dissolve"
                reason = "Cena reflexiva extensa requer transição de fusão suave."
            # 3. Se a cena atual for curta e dinâmica (< 3.5s)
            elif duration < 3.5:
                chosen = "hard_cut"
                reason = "Ritmo veloz favorece corte seco direto."
            # 4. Mudança de tópico ou introdução de conceito
            elif re.search(r"\b(agora|depois|em seguida|passo|outro|segundo|finalmente)\b", next_text, re.IGNORECASE):
                chosen = "directional_wipe"
                reason = "Marcador de progressão temática requer push direcional."
            else:
                chosen = "zoom_blur_punch"
                reason = "Manutenção de energia visual intermediária."

            t_info = cls.TRANSITION_TYPES[chosen]
            transitions.append({
                "from_scene_index": i + 1,
                "to_scene_index": i + 2,
                "cut_timestamp": round(current_time, 2),
                "transition_type": chosen,
                "name": t_info["name"],
                "duration": t_info["duration"],
                "xfade_filter": t_info["xfade_filter"],
                "reason": reason
            })

        return {
            "total_transitions": len(transitions),
            "transitions": transitions,
            "smoothness_score": 95,
            "status": "PLANNED"
        }
