"""
AI Script Tone Polisher & Viral Hook Crafter for CutWire Drift AI.
Re-engineers scene narrations and scripts into specialized retention archetypes:
High-Pacing Shorts/TikTok Viral, BBC/History Channel Documentary, Mystery/Investigation, and Didactic Explainer.
"""
from dataclasses import dataclass
from typing import Dict, List, Any
import re
from models.scene_plan import ProjectPlan, Scene

@dataclass
class ToneProfile:
    id: str
    name: str
    description: str
    target_format: str
    hook_prefix: str

class ScriptTonePolisher:
    """
    Transforms script tone to maximize engagement and emotional resonance.
    """

    TONE_PROFILES: Dict[str, ToneProfile] = {
        "shorts_viral": ToneProfile(
            id="shorts_viral",
            name="Viral Dinâmico (Shorts / Reels / TikTok)",
            description="Frases ultra-curtas, ganchos instantâneos e corte de palavras desnecessárias.",
            target_format="9:16",
            hook_prefix="Você não vai acreditar nisso: "
        ),
        "bbc_documentary": ToneProfile(
            id="bbc_documentary",
            name="Documentário Solene (Estilo BBC / History)",
            description="Vocabulário nobre, transições históricas reflexivas e pausas contemplativas.",
            target_format="16:9",
            hook_prefix="Ao longo das eras, poucos mistérios desafiaram tanto a humanidade quanto este. "
        ),
        "mystery_investigation": ToneProfile(
            id="mystery_investigation",
            name="Investigação & Suspense (True Crime / Sci-Fi)",
            description="Ganchos de curiosidade, perguntas retóricas e revelações graduais.",
            target_format="16:9",
            hook_prefix="Tudo parecia normal, até que um detalhe perturbador veio à tona. "
        ),
        "didactic_friendly": ToneProfile(
            id="didactic_friendly",
            name="Didático & Inspirador (Educação & Negócios)",
            description="Clareza máxima, analogias simples e linguagem empática e envolvente.",
            target_format="any",
            hook_prefix="Se você quer dominar este assunto de verdade, preste muita atenção nisto: "
        )
    }

    @classmethod
    def list_tone_profiles(cls) -> List[Dict[str, str]]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "target_format": p.target_format
            }
            for p in cls.TONE_PROFILES.values()
        ]

    @classmethod
    def polish_text(cls, raw_text: str, tone_id: str = "shorts_viral") -> str:
        """
        Polishes text according to the selected tone archetype.
        """
        profile = cls.TONE_PROFILES.get(tone_id, cls.TONE_PROFILES["shorts_viral"])
        sentences = [s.strip() for s in re.split(r'[.!?]+', raw_text) if s.strip()]

        if not sentences:
            return raw_text

        polished_sentences = []
        for i, s in enumerate(sentences):
            clean_s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()

            if tone_id == "shorts_viral":
                # Make punchy, add hook on first sentence
                if i == 0 and not clean_s.startswith(profile.hook_prefix):
                    clean_s = f"{profile.hook_prefix}{clean_s}"
                clean_s = clean_s.replace(" muito ", " ")
                clean_s = clean_s.replace(" bastante ", " ")
            elif tone_id == "bbc_documentary":
                if i == 0 and not clean_s.startswith(profile.hook_prefix):
                    clean_s = f"{profile.hook_prefix}{clean_s}"
                elif i == 1:
                    clean_s = f"No entanto, {clean_s.lower()}"
            elif tone_id == "mystery_investigation":
                if i == 0 and not clean_s.startswith(profile.hook_prefix):
                    clean_s = f"{profile.hook_prefix}{clean_s}"
                elif i == len(sentences) - 1:
                    clean_s = f"Mas a verdadeira pergunta permanece: {clean_s.lower()}?"
            elif tone_id == "didactic_friendly":
                if i == 0 and not clean_s.startswith(profile.hook_prefix):
                    clean_s = f"{profile.hook_prefix}{clean_s}"

            polished_sentences.append(clean_s)

        return ". ".join(polished_sentences) + "."

    @classmethod
    def polish_plan(cls, plan: ProjectPlan, tone_id: str = "shorts_viral") -> ProjectPlan:
        """
        Applies stylistic polish across all scene narrations in the project plan.
        """
        for i, s in enumerate(plan.scenes):
            if i == 0:
                s.narration_text = cls.polish_text(s.narration_text, tone_id=tone_id)
            else:
                s.narration_text = cls.polish_text(s.narration_text, tone_id=tone_id)
        return plan
