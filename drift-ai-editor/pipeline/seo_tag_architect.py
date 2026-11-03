"""
AI SEO Tag & Search Rank Architect for CutWire Drift AI.
Generates optimized long-tail keyword clusters, YouTube search tag comma strings (<500 chars),
structured description outlines, and trending hashtag stacks to maximize organic algorithmic reach.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import re
from models.scene_plan import ProjectPlan, Scene

@dataclass
class SeoKit:
    optimized_title: str
    description_markdown: str
    tags_comma_string: str
    tags_character_count: int
    primary_hashtags: List[str]
    target_search_intent: str

class SeoTagArchitect:
    """
    Automates video metadata engineering for YouTube and search engines.
    """

    @classmethod
    def generate_seo_kit(cls, plan: ProjectPlan) -> SeoKit:
        title = plan.title or "Vídeo Educativo"
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', title.lower())

        # Generate long-tail tags
        tags = [
            title,
            f"o que é {title}",
            f"{title} documentario",
            f"{title} explicado",
            f"{title} historia",
            "curiosidades",
            "resumo completo",
            "ciencia",
            "educacao"
        ]
        tag_str = ", ".join(tags)
        if len(tag_str) > 480:
            tag_str = tag_str[:480]

        hashtags = [f"#{w}" for w in words[:3]] + ["#documentario", "#curiosidades", "#aprendizado"]

        desc = (
            f"Confira neste vídeo uma análise profunda e detalhada sobre {title}.\n\n"
            f"🔔 Inscreva-se no canal para acompanhar produções completas e documentários imersivos toda semana!\n\n"
            f"{' '.join(hashtags)}"
        )

        return SeoKit(
            optimized_title=f"{title}: A Verdade Revelada",
            description_markdown=desc,
            tags_comma_string=tag_str,
            tags_character_count=len(tag_str),
            primary_hashtags=hashtags,
            target_search_intent="Informational & High-Retention Documentary"
        )

