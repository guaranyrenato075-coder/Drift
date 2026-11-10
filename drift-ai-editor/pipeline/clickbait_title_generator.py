"""
High-CTR Title & Thumbnail Hook Generator for CutWire Drift AI.
Generates psychologically engineered YouTube titles and 2-4 word thumbnail punchlines
based on proven click-through formulas (Curiosity Gap, Paradox, Secret Revelation, and Urgency).
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import re
from models.scene_plan import ProjectPlan

@dataclass
class TitleFormula:
    formula_id: str
    category: str
    headline: str
    thumbnail_hook: str
    estimated_ctr_rating: str  # "S-Tier (8-12%)", "A-Tier (6-9%)"

class ClickbaitTitleHookGenerator:
    """
    Automated viral headline and thumbnail hook crafter.
    """

    @classmethod
    def _extract_main_topic(cls, plan: ProjectPlan) -> str:
        topic = plan.title.strip()
        # Clean generic prefixes like "Projeto:", "Roteiro:", "Video:"
        topic = re.sub(r'^(projeto|roteiro|video|documentario)\s*:\s*', '', topic, flags=re.IGNORECASE).strip()
        if not topic:
            # Fallback to first keywords
            for s in plan.scenes:
                if s.english_keywords:
                    return s.english_keywords[0].capitalize()
            return "Este Mistério"
        return topic

    @classmethod
    def generate_title_package(cls, plan: ProjectPlan) -> Dict[str, Any]:
        topic = cls._extract_main_topic(plan)
        
        formulas = [
            TitleFormula(
                formula_id="curiosity_gap",
                category="Curiosidade & Segredo",
                headline=f"A Verdade Oculta Sobre {topic} Que Ninguém Te Contou",
                thumbnail_hook="NUNCA REVELADO",
                estimated_ctr_rating="S-Tier (9-13%)"
            ),
            TitleFormula(
                formula_id="paradox_contradiction",
                category="Paradoxo & Choque",
                headline=f"Como {topic} Quase Destruiu Tudo (E Por Que Ignoramos Isso)",
                thumbnail_hook="O ERRO FATAL",
                estimated_ctr_rating="S-Tier (8-12%)"
            ),
            TitleFormula(
                formula_id="unmasking_revelation",
                category="Revelação de Impacto",
                headline=f"O Que Realmente Aconteceu Com {topic}? O Registro Final",
                thumbnail_hook="ELES MENTIRAM?",
                estimated_ctr_rating="A-Tier (7-10%)"
            ),
            TitleFormula(
                formula_id="storytelling_timeline",
                category="Jornada Épica",
                headline=f"{topic}: A História Que Mudou o Rumo do Mundo Para Sempre",
                thumbnail_hook="O FIM DE TUDO",
                estimated_ctr_rating="A-Tier (6-9%)"
            ),
            TitleFormula(
                formula_id="urgency_challenge",
                category="Aviso & Mistério",
                headline=f"O Maior Erro Sobre {topic} Que Você Continua Cometendo",
                thumbnail_hook="ACABOU!",
                estimated_ctr_rating="A-Tier (6-8%)"
            )
        ]

        thumbnail_badges = [
            "A VERDADE",
            "O ERRO FATAL",
            "NUNCA REVELADO",
            "ELES MENTIRAM?",
            "INACREDITÁVEL"
        ]

        return {
            "project_id": plan.project_id,
            "base_topic": topic,
            "recommended_primary_title": formulas[0].headline,
            "titles": [
                {
                    "formula_id": f.formula_id,
                    "category": f.category,
                    "headline": f.headline,
                    "thumbnail_hook": f.thumbnail_hook,
                    "estimated_ctr": f.estimated_ctr_rating
                }
                for f in formulas
            ],
            "thumbnail_badge_options": thumbnail_badges
        }
