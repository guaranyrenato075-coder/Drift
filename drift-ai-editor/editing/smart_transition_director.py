"""
Smart Scene Transition Director for CutWire Drift AI.
Dynamically orchestrates cinematic transitions (Hard Cut, Dip to Black, Crossfade, Luma Wipe)
by analyzing dramatic shifts, temporal leaps, and narrative continuity between adjacent scenes.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import re
from models.scene_plan import Scene, ProjectPlan

@dataclass
class SceneTransitionPlan:
    from_scene_order: int
    to_scene_order: int
    transition_type: str    # "hard_cut", "dip_to_black", "crossfade", "luma_fade"
    duration_sec: float
    narrative_reason: str

class SmartSceneTransitionDirector:
    """
    Directs scene-to-scene transitions based on emotional and narrative context.
    """

    TEMPORAL_KEYWORDS = {"anos", "séculos", "décadas", "época", "passado", "futuro", "tempo", "depois", "eras", "outrora"}
    SHOCK_KEYWORDS = {"repente", "tragédia", "perigo", "inesperado", "choque", "destruição", "segredo", "revelou", "mas", "porém", "mentira"}
    TRAVEL_KEYWORDS = {"viajou", "chegou", "distante", "espaço", "viagem", "planeta", "caminho", "fronteira", "mundo", "mar"}

    @classmethod
    def evaluate_transition(cls, scene_a: Scene, scene_b: Scene) -> SceneTransitionPlan:
        text_b = (scene_b.narration_text + " " + scene_b.visual_description).lower()
        words_b = set(re.findall(r'\b\w+\b', text_b))

        # 1. Shock / Sudden revelation -> Hard Cut (0s) for punchy impact
        if words_b.intersection(cls.SHOCK_KEYWORDS):
            return SceneTransitionPlan(
                from_scene_order=scene_a.order,
                to_scene_order=scene_b.order,
                transition_type="hard_cut",
                duration_sec=0.0,
                narrative_reason="Revelação dramática ou choque narrativo: corte seco para máximo impacto emocional."
            )

        # 2. Temporal leap / Century change -> Dip to Black (0.7s)
        if words_b.intersection(cls.TEMPORAL_KEYWORDS):
            return SceneTransitionPlan(
                from_scene_order=scene_a.order,
                to_scene_order=scene_b.order,
                transition_type="dip_to_black",
                duration_sec=0.7,
                narrative_reason="Salto temporal ou transição de época: fade para preto denotando passagem de tempo."
            )

        # 3. Spatial displacement / Travel -> Luma Fade (0.5s)
        if words_b.intersection(cls.TRAVEL_KEYWORDS):
            return SceneTransitionPlan(
                from_scene_order=scene_a.order,
                to_scene_order=scene_b.order,
                transition_type="luma_fade",
                duration_sec=0.5,
                narrative_reason="Deslocamento geográfico ou exploração espacial: transição de luminância fluida."
            )

        # 4. Standard thematic continuity -> Gentle Crossfade (0.4s)
        return SceneTransitionPlan(
            from_scene_order=scene_a.order,
            to_scene_order=scene_b.order,
            transition_type="crossfade",
            duration_sec=0.4,
            narrative_reason="Continuidade de raciocínio e tema: fusão suave de imagem e áudio."
        )

    @classmethod
    def plan_project_transitions(cls, plan: ProjectPlan) -> List[SceneTransitionPlan]:
        if len(plan.scenes) < 2:
            return []

        transitions = []
        for i in range(len(plan.scenes) - 1):
            t = cls.evaluate_transition(plan.scenes[i], plan.scenes[i + 1])
            transitions.append(t)
        return transitions
