import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import Scene

@dataclass
class VisualIntent:
    scene_order: int
    core_concept: str
    emotional_tone: str       # e.g., 'hesitation', 'inspirational', 'somber', 'revelation', 'epic'
    shot_type: str            # e.g., 'close_up', 'wide_angle', 'drone_aerial', 'medium_shot'
    camera_movement: str      # e.g., 'slow_push_in', 'static', 'tracking_follow', 'slow_pan'
    semantic_intent: str      # Humanized visual direction
    search_queries: List[str] # Curated, highly specific search queries
    negative_tags: List[str]  # What to avoid (e.g. 'crowded office', 'cartoons')
    quality_criteria: str     # e.g., 'cinematic lighting, 4K resolution, authentic human expression'

@dataclass
class HookOption:
    hook_type: str            # 'provocative', 'narrative', 'question'
    text: str
    visual_direction: str
    target_emotion: str

class StoryboardEngine:
    """
    AI Storyboard Director:
    Interprets narration semantics to determine visual purpose, psychological tone,
    framing, and anti-cliché filters before performing media queries.
    Also produces opening retention hooks for video hooks.
    """

    EMOTIONAL_LEXICON = {
        "hesitation": ["medo", "fracassar", "dúvida", "insegurança", "hesitar", "paralisar", "parado", "angústia", "fear", "hesitate", "doubt"],
        "inspirational": ["vitória", "conquista", "superação", "força", "evoluir", "clareza", "foco", "disciplina", "inspire", "victory", "success"],
        "contemplative": ["pensar", "mente", "alma", "reflexão", "silêncio", "tempo", "solidão", "viver", "contemplate", "mind", "ponder"],
        "cosmic_wonder": ["universo", "estrelas", "espaço", "galáxia", "infinito", "cosmos", "planeta", "universe", "stars", "space"],
        "urgency": ["rápido", "agora", "perigo", "alerta", "crise", "correr", "urgente", "urgent", "danger", "rush"],
        "technological": ["futuro", "tecnologia", "inteligência", "dados", "digital", "código", "robô", "future", "tech", "ai"]
    }

    @classmethod
    def generate_hooks(cls, topic: str) -> List[HookOption]:
        """
        Generates 3 distinctive opening retention hooks for the project topic:
        1. Provocative (contrarian statement)
        2. Narrative (in media res storytelling)
        3. Curiosity/Question (hook question)
        """
        clean_topic = topic.strip().capitalize()
        return [
            HookOption(
                hook_type="provocative",
                text=f"A maioria das pessoas está completamente errada sobre {clean_topic}.",
                visual_direction="Close-up intenso em olhar sério ou plano de alto impacto e corte rápido.",
                target_emotion="Quebra de padrão e surpresa"
            ),
            HookOption(
                hook_type="narrative",
                text=f"Em silêncio, uma decisão simples sobre {clean_topic} mudou o rumo da história.",
                visual_direction="Plano cinematográfico aberto com iluminação suave e movimento lento de aproximação.",
                target_emotion="Imersão dramática e curiosidade"
            ),
            HookOption(
                hook_type="question",
                text=f"E se tudo o que você aprendeu sobre {clean_topic} for apenas uma ilusão?",
                visual_direction="Pessoa diante de uma encruzilhada ou vista aérea de uma cidade nublada com névoa.",
                target_emotion="Reflexão profunda e busca de resposta"
            )
        ]

    @classmethod
    def analyze_scene_intent(cls, scene: Scene, index: int, total_scenes: int) -> VisualIntent:
        """
        Derives cinematographic framing, emotional resonance, and precise search direction
        for a given scene based on semantic concept rather than superficial keywords.
        """
        text_lower = (scene.narration_text + " " + scene.visual_description).lower()

        # 1. Detect dominant emotional tone
        detected_emotion = "contemplative"
        highest_score = 0
        for emotion, tokens in cls.EMOTIONAL_LEXICON.items():
            score = sum(1 for tok in tokens if tok in text_lower)
            if score > highest_score:
                highest_score = score
                detected_emotion = emotion

        # 2. Determine shot type and camera movement based on narrative pacing
        if index == 0:
            shot_type = "wide_angle"
            camera_mov = "slow_push_in"
            framing_purpose = "Estabelecer o universo e atmosfera do tema."
        elif index == total_scenes - 1:
            shot_type = "medium_shot"
            camera_mov = "slow_pan"
            framing_purpose = "Conclusão, fechamento reflexivo e chamada para ação."
        elif detected_emotion == "hesitation":
            shot_type = "close_up"
            camera_mov = "static"
            framing_purpose = "Expressar tensão interna, dúvida ou isolamento psicológico."
        elif detected_emotion == "inspirational":
            shot_type = "drone_aerial"
            camera_mov = "tracking_follow"
            framing_purpose = "Sensação de amplitude, conquista e horizonte aberto."
        elif detected_emotion == "cosmic_wonder":
            shot_type = "wide_angle"
            camera_mov = "slow_push_in"
            framing_purpose = "Imensidão cósmica, profundidade e detalhe estelar."
        else:
            shot_type = "medium_shot"
            camera_mov = "slow_pan"
            framing_purpose = "Acompanhamento natural do fluxo da mensagem."

        # 3. Formulate tailored search queries (semantic intent instead of literal text)
        base_queries: List[str] = []
        if detected_emotion == "hesitation":
            base_queries = ["person standing at crossroads decision", "shadow silhouette alone thoughtful", "person looking out window rain contemplating"]
        elif detected_emotion == "inspirational":
            base_queries = ["person mountain peak sunrise looking horizon", "athlete determined focus eyes", "sun breaking through clouds cinematic"]
        elif detected_emotion == "cosmic_wonder":
            base_queries = ["galaxy deep space stars nebula", "earth from space orbit cinematic", "observatory telescope night sky"]
        elif detected_emotion == "technological":
            base_queries = ["modern futuristic abstract data flow", "person working with futuristic holographic interface", "server room fiber optic glow"]
        else:
            base_queries = [
                f"{scene.english_keywords[0]} cinematic" if scene.english_keywords else "cinematic mood",
                f"{scene.english_keywords[1]} atmospheric" if len(scene.english_keywords) > 1 else "calm reflection"
            ]

        # Add visual planner keywords as fallback
        if scene.english_keywords:
            base_queries.extend([f"{kw} cinematic lighting" for kw in scene.english_keywords[:2]])

        # Remove duplicates while preserving order
        unique_queries = list(dict.fromkeys(base_queries))[:4]

        return VisualIntent(
            scene_order=scene.order,
            core_concept=scene.concept or (scene.english_keywords[0] if scene.english_keywords else "general"),
            emotional_tone=detected_emotion,
            shot_type=shot_type,
            camera_movement=camera_mov,
            semantic_intent=framing_purpose,
            search_queries=unique_queries,
            negative_tags=["ugly cartoons", "blurry low quality", "commercial watermark", "oversaturated"],
            quality_criteria="Iluminação cinematográfica, 1080p/4K, composição em regra dos terços e movimento orgânico."
        )

    @classmethod
    def apply_storyboard(cls, scenes: List[Scene]) -> Dict[int, VisualIntent]:
        """Processes all project scenes and attaches visual intent metadata."""
        intents: Dict[int, VisualIntent] = {}
        total = len(scenes)
        for idx, scene in enumerate(scenes):
            intent = cls.analyze_scene_intent(scene, idx, total)
            intents[scene.order] = intent
            # Enrich scene's search keywords with semantic visual queries
            for sq in intent.search_queries:
                if sq not in scene.english_keywords:
                    scene.english_keywords.insert(0, sq)
        return intents

