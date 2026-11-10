"""
Automated YouTube Community Post & Social Poll Packager for CutWire Drift AI.
Analyzes video transcripts and themes to generate engaging multi-choice community polls,
curiosity teaser updates, and discussion-sparking questions to maximize organic channel reach.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from models.scene_plan import ProjectPlan

@dataclass
class CommunityPollItem:
    poll_question: str
    options: List[str]
    context_note: str

@dataclass
class CommunityPostPackage:
    project_id: str
    poll: CommunityPollItem
    teaser_post_text: str
    open_discussion_question: str
    recommended_publish_timing: str

class AutoYouTubeCommunityPostPackager:
    """
    Builds YouTube Community tab posts to engage subscribers before and after video uploads.
    """

    @classmethod
    def generate_community_kit(cls, plan: ProjectPlan) -> CommunityPostPackage:
        raw_title = plan.title or "O Enigma do Século"
        clean = re.sub(r'^(projeto|video|roteiro)\s*:\s*', '', raw_title, flags=re.IGNORECASE).strip()

        # 1. Interactive Poll
        poll = CommunityPollItem(
            poll_question=f"Qual é o maior mistério envolvendo {clean} na sua opinião?",
            options=[
                "A explicação científica oficial",
                "O que os documentos antigos relatam",
                "Teorias alternativas e novas descobertas",
                "Ainda é um segredo total para a humanidade"
            ],
            context_note="Enquetes com 4 opções têm em média 2.4x mais engajamento no feed de inscritos."
        )

        # 2. Teaser post
        teaser = (
            f"🚨 Novo documentário saindo em breve: '{clean}'.\n\n"
            f"Passamos semanas investigando arquivos raros e fatos nunca antes revelados. "
            f"Você acredita que a história que nos contaram é 100% verdadeira?\n\n"
            f"Deixe seu voto na enquete e ative as notificações! 🔔"
        )

        # 3. Open discussion
        discussion = (
            f"Se você pudesse voltar no tempo e presenciar {clean} com seus próprios olhos, "
            f"qual seria a primeira pergunta que você faria aos envolvidos? Comente abaixo!"
        )

        return CommunityPostPackage(
            project_id=plan.project_id,
            poll=poll,
            teaser_post_text=teaser,
            open_discussion_question=discussion,
            recommended_publish_timing="Publicar a enquete 24h antes da estreia do vídeo e o teaser 2h antes."
        )

    @classmethod
    def export_kit_dict(cls, plan: ProjectPlan) -> Dict[str, Any]:
        kit = cls.generate_community_kit(plan)
        return {
            "project_id": kit.project_id,
            "poll": kit.poll.__dict__,
            "teaser_post_text": kit.teaser_post_text,
            "open_discussion_question": kit.open_discussion_question,
            "recommended_publish_timing": kit.recommended_publish_timing
        }
