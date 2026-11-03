"""
All-In-One Publication & Virality SEO Kit for CutWire Drift AI.
Unifies A/B magnetic title variants, YouTube timestamp chapters, search tags,
trending hashtags, and audited Creative Commons copyright attribution credits
into a single, paste-ready publishing package for YouTube Studio and TikTok.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
from models.scene_plan import ProjectPlan
from pipeline.youtube_chapter_generator import YoutubeChapterGenerator
from pipeline.seo_tag_architect import SeoTagArchitect
from media.copyright_analyzer import CopyrightAnalyzer

@dataclass
class MagneticTitleVariant:
    category: str           # "Curiosidade", "Autoridade", "Lista/Números", "Provocação", "Urgência"
    title: str
    expected_ctr_power: str # "Muito Alta", "Alta", "Sólida"

@dataclass
class MasterPublicationKit:
    project_id: str
    project_title: str
    magnetic_titles: List[MagneticTitleVariant]
    youtube_chapters: str
    search_tags_comma_separated: str
    trending_hashtags: List[str]
    copyright_credits_block: str
    complete_youtube_description: str
    monetization_approved: bool

class PublicationSeoKitGenerator:
    """
    Automated publishing package generator for creators and automated channels.
    """

    @classmethod
    def generate_complete_kit(cls, plan: ProjectPlan) -> MasterPublicationKit:
        title = plan.title or "Produção Drift AI"
        clean_title = re.sub(r'[^\w\s]', '', title).strip()

        # 1. Gera 5 títulos magnéticos para testes A/B
        titles = [
            MagneticTitleVariant(
                category="Curiosidade Extrema",
                title=f"A Verdade Oculta Sobre {clean_title} Que Ninguém Te Contou",
                expected_ctr_power="Muito Alta"
            ),
            MagneticTitleVariant(
                category="Autoridade / Guia",
                title=f"Como Dominar {clean_title}: O Guia Completo e Definitivo",
                expected_ctr_power="Alta"
            ),
            MagneticTitleVariant(
                category="Lista / Fatos",
                title=f"7 Coisas Que Você PRECISA Saber Sobre {clean_title}",
                expected_ctr_power="Muito Alta"
            ),
            MagneticTitleVariant(
                category="Pergunta Provocativa",
                title=f"Será Que Você Realmente Entende {clean_title}?",
                expected_ctr_power="Alta"
            ),
            MagneticTitleVariant(
                category="Urgência / Alerta",
                title=f"PARE de Cometer Esse Erro Com {clean_title} Agora Mesmo",
                expected_ctr_power="Sólida"
            )
        ]

        # 2. Capítulos e Timestamps
        chapters_manifest = YoutubeChapterGenerator.generate_chapters(plan)
        chapters_text = chapters_manifest.description_block or "00:00 Início do Vídeo"

        # 3. Tags de Busca e Hashtags
        seo_base = SeoTagArchitect.generate_seo_kit(plan)
        tags_str = seo_base.tags_comma_string
        hashtags = seo_base.primary_hashtags

        # 4. Auditoria de Direitos Autorais e Créditos
        audit = CopyrightAnalyzer.audit_timeline_copyright(plan)
        credits_text = audit.youtube_description_credits

        # 5. Montagem da Descrição Canônica Pronta para Copiar
        full_desc = (
            f"🎬 {titles[0].title}\n\n"
            f"Neste vídeo, exploramos os segredos mais profundos sobre {clean_title}. "
            f"Uma jornada audiovisual imersiva produzida em alta definição com o CutWire Drift AI.\n\n"
            f"📌 CAPÍTULOS E TIMESTAMPS:\n"
            f"{chapters_text}\n\n"
            f"🔔 Inscreva-se no canal para mais documentários, análises profundas e narrativas cinematográficas semanais!\n\n"
            f"{' '.join(hashtags)}\n\n"
            f"{credits_text}\n"
        )

        return MasterPublicationKit(
            project_id=getattr(plan, "project_id", "proj_default"),
            project_title=title,
            magnetic_titles=titles,
            youtube_chapters=chapters_text,
            search_tags_comma_separated=tags_str,
            trending_hashtags=hashtags,
            copyright_credits_block=credits_text,
            complete_youtube_description=full_desc,
            monetization_approved=audit.is_safe_for_monetization
        )

