"""
AI Story Hook A/B Split Tester for CutWire Drift AI.
Generates 3 psychologically calibrated opening hook variations (Provocative Question,
Climactic Revelation, and Counter-Intuitive Paradox) to maximize first 5-second viewer retention.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from models.scene_plan import ProjectPlan, Scene

@dataclass
class HookVariation:
    hook_id: str
    archetype: str  # "provocative_question", "climactic_revelation", "counter_intuitive"
    title: str
    narration_text: str
    visual_description: str
    target_emotion: str
    estimated_hook_power: int  # 0-100

class AIStoryHookABSplitTester:
    """
    Formulates high-retention opening hooks for video intros.
    """

    @classmethod
    def generate_hook_variations(cls, plan: ProjectPlan) -> List[HookVariation]:
        base_topic = plan.title or "O Enigma Inexplicável"
        clean_topic = re.sub(r'^(projeto|video|roteiro)\s*:\s*', '', base_topic, flags=re.IGNORECASE).strip()

        # 1. Provocative Question (Curiosity gap)
        hook_1 = HookVariation(
            hook_id="hook_provocative_question",
            archetype="provocative_question",
            title="Gancho 1: Pergunta Provocativa (Curiosity Gap)",
            narration_text=f"Você já se perguntou por que quase ninguém conhece a verdade oculta sobre {clean_topic}?",
            visual_description="Close-up dinâmico em câmera lenta com iluminação misteriosa em contraluz.",
            target_emotion="Curiosidade Intensa",
            estimated_hook_power=94
        )

        # 2. Climactic Revelation (In medias res)
        hook_2 = HookVariation(
            hook_id="hook_climactic_revelation",
            archetype="climactic_revelation",
            title="Gancho 2: Revelação de Clímax (In Medias Res)",
            narration_text=f"Em poucos segundos, uma única descoberta sobre {clean_topic} mudou para sempre a história.",
            visual_description="Corte rápido com transição de impacto e imagem dramática do evento culminante.",
            target_emotion="Urgência & Choque",
            estimated_hook_power=96
        )

        # 3. Counter-Intuitive Paradox (Belief break)
        hook_3 = HookVariation(
            hook_id="hook_counter_intuitive",
            archetype="counter_intuitive",
            title="Gancho 3: Paradoxo Contra-Intuitivo (Quebra de Crença)",
            narration_text=f"Tudo o que você ouviu sobre {clean_topic} até hoje está completamente errado. E aqui está a prova.",
            visual_description="Gráfico visual de contradição seguido de revelação impactante em alta definição.",
            target_emotion="Fascínio & Desafio Intelectual",
            estimated_hook_power=98
        )

        return [hook_1, hook_2, hook_3]

    @classmethod
    def apply_hook_to_plan(cls, plan: ProjectPlan, hook_id: str) -> ProjectPlan:
        variations = cls.generate_hook_variations(plan)
        selected = next((h for h in variations if h.hook_id == hook_id), variations[0])

        if plan.scenes:
            first_scene = plan.scenes[0]
            first_scene.narration_text = selected.narration_text
            first_scene.visual_description = selected.visual_description
            first_scene.duration = min(first_scene.duration or 5.0, 5.0)

        plan.config.extra = plan.config.extra or {}
        plan.config.extra["active_story_hook"] = selected.__dict__

        return plan
