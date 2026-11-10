"""
One-Click Niche Preset Video Templates for CutWire Drift AI.
Applies synchronized multi-layer configurations (color grading, subtitle typography,
audio profile, camera motion, transitions, and aspect ratio) calibrated for specialized YouTube channel niches.
"""
from dataclasses import dataclass
from typing import Dict, List, Any
from models.scene_plan import ProjectPlan, ProjectConfig

@dataclass
class ChannelTemplate:
    id: str
    name: str
    niche: str
    aspect_ratio: str
    color_grade: str
    subtitle_style: str
    transition_kind: str
    audio_profile: str
    enable_ken_burns: bool
    description: str

class OneClickPresetVideoTemplates:
    """
    Applies synchronized production profiles with a single click.
    """

    TEMPLATES: Dict[str, ChannelTemplate] = {
        "space_scifi": ChannelTemplate(
            id="space_scifi",
            name="Cosmos & Mistérios do Espaço (Sci-Fi)",
            niche="Ciência & Astronomia",
            aspect_ratio="16:9",
            color_grade="deep_space",
            subtitle_style="neon_glow",
            transition_kind="luma_fade",
            audio_profile="broadcast_lufs_14",
            enable_ken_burns=True,
            description="Pretos intensos, legendas neon ciano/magenta e transições de luz ideais para astronomia e astrofísica."
        ),
        "history_documentary": ChannelTemplate(
            id="history_documentary",
            name="Documentário Histórico & Filosofia",
            niche="História & Cultura",
            aspect_ratio="16:9",
            color_grade="warm_documentary",
            subtitle_style="cinema_classic",
            transition_kind="dip_to_black",
            audio_profile="radio_podcast_warmth",
            enable_ken_burns=True,
            description="Tons dourados e sépia, legendas discretas estilo Netflix, pausas solenes e transições para preto."
        ),
        "viral_shorts": ChannelTemplate(
            id="viral_shorts",
            name="Viral Shorts & TikTok (Alta Retenção)",
            niche="Shorts / Reels / TikTok",
            aspect_ratio="9:16",
            color_grade="teal_and_orange",
            subtitle_style="hormozi_viral",
            transition_kind="none",
            audio_profile="crisp_clarity",
            enable_ken_burns=True,
            description="Formato vertical 1080x1920, legendas estilo Hormozi/MrBeast, cortes secos e safe zones ativadas."
        ),
        "business_tech": ChannelTemplate(
            id="business_tech",
            name="Negócios, Finanças & Tech",
            niche="Educação & Tecnologia",
            aspect_ratio="16:9",
            color_grade="neutral",
            subtitle_style="minimalist_clean",
            transition_kind="crossfade",
            audio_profile="crisp_clarity",
            enable_ken_burns=False,
            description="Design limpo e moderno, tipografia sem serifa aerea e áudio ultra-inteligível sem excesso de efeitos."
        )
    }

    @classmethod
    def list_templates(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": t.id,
                "name": t.name,
                "niche": t.niche,
                "aspect_ratio": t.aspect_ratio,
                "color_grade": t.color_grade,
                "subtitle_style": t.subtitle_style,
                "transition_kind": t.transition_kind,
                "audio_profile": t.audio_profile,
                "description": t.description
            }
            for t in cls.TEMPLATES.values()
        ]

    @classmethod
    def apply_template_to_plan(cls, plan: ProjectPlan, template_id: str = "space_scifi") -> ProjectPlan:
        tmpl = cls.TEMPLATES.get(template_id, cls.TEMPLATES["space_scifi"])

        # Update ProjectConfig
        plan.config.aspect_ratio = tmpl.aspect_ratio
        plan.config.update_resolution()
        plan.config.transition_kind = tmpl.transition_kind
        plan.config.enable_ken_burns = tmpl.enable_ken_burns

        # Extra configuration bundle
        plan.config.extra = plan.config.extra or {}
        plan.config.extra["template_id"] = tmpl.id
        plan.config.extra["color_grading"] = tmpl.color_grade
        plan.config.extra["subtitle_style"] = tmpl.subtitle_style
        plan.config.extra["audio_profile"] = tmpl.audio_profile

        return plan
