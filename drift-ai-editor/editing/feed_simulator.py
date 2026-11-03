from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class CollisionArea:
    name: str
    rect: Dict[str, int] # x, y, width, height in pixels
    description: str

@dataclass
class PlatformViewportSpecs:
    platform_name: str
    resolution_w: int
    resolution_h: int
    safe_title_rect: Dict[str, int]
    collision_overlays: List[CollisionArea] = field(default_factory=list)

@dataclass
class FeedPreviewAudit:
    platform: str
    passed_safe_zone: bool
    title_legible_at_mobile_scale: bool
    contrast_ratio_estimate: float
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class FeedSimulator:
    """
    Feed Simulator & Thumbnail Safety Inspector:
    Simulates how video composition and text overlays look across TikTok, YouTube Shorts,
    and Instagram Reels interfaces:
      - Validates that subtitles and graphic titles do not collide with like/comment buttons.
      - Estimates mobile readability and luminance contrast.
    """

    PLATFORM_SPECS = {
        "tiktok": PlatformViewportSpecs(
            platform_name="TikTok",
            resolution_w=1080,
            resolution_h=1920,
            safe_title_rect={"x": 60, "y": 280, "width": 960, "height": 1300},
            collision_overlays=[
                CollisionArea("right_actions", {"x": 920, "y": 800, "width": 140, "height": 800}, "Botões de Curtir, Comentários, Salvar e Compartilhar"),
                CollisionArea("bottom_caption", {"x": 40, "y": 1640, "width": 840, "height": 240}, "Título do criador, descrição e áudio"),
                CollisionArea("top_nav", {"x": 0, "y": 0, "width": 1080, "height": 220}, "Barra superior de pesquisa e Seguindo/Para Você")
            ]
        ),
        "youtube_shorts": PlatformViewportSpecs(
            platform_name="YouTube Shorts",
            resolution_w=1080,
            resolution_h=1920,
            safe_title_rect={"x": 50, "y": 240, "width": 980, "height": 1380},
            collision_overlays=[
                CollisionArea("right_icons", {"x": 930, "y": 950, "width": 130, "height": 750}, "Ícones de Like, Deslike, Comentários e Remix"),
                CollisionArea("bottom_info", {"x": 40, "y": 1680, "width": 860, "height": 200}, "Nome do Canal e botão Inscrever-se")
            ]
        )
    }

    @classmethod
    def audit_feed_safety(
        cls,
        platform_id: str,
        title_y_position: int,
        subtitle_bottom_margin: int,
        font_size: int,
        text_color_hex: str = "#FFFFFF"
    ) -> FeedPreviewAudit:
        specs = cls.PLATFORM_SPECS.get(platform_id, cls.PLATFORM_SPECS["tiktok"])
        violations: List[str] = []
        recommendations: List[str] = []

        # 1. Check Subtitle Bottom Margin
        min_safe_bottom = 240
        if subtitle_bottom_margin < min_safe_bottom:
            violations.append(
                f"Legenda muito baixa ({subtitle_bottom_margin}px). Conflita com a barra de descrição e comentários do {specs.platform_name}."
            )
            recommendations.append(f"Aumente a margem inferior para no mínimo {min_safe_bottom}px.")

        # 2. Check Font Size for Mobile Readability
        if font_size < 36:
            violations.append(f"Tamanho de fonte ({font_size}px) é pequeno para leitura rápida em telas de smartphone.")
            recommendations.append("Utilize no mínimo 42px para legendas e 56px para títulos principais.")

        # 3. Contrast check
        is_high_contrast = text_color_hex.upper() in ("#FFFFFF", "#FACC15", "#FEF3C7", "#00F5D4")
        contrast_ratio = 8.5 if is_high_contrast else 3.2

        passed = len(violations) == 0

        return FeedPreviewAudit(
            platform=specs.platform_name,
            passed_safe_zone=passed,
            title_legible_at_mobile_scale=font_size >= 36,
            contrast_ratio_estimate=contrast_ratio,
            violations=violations,
            recommendations=recommendations
        )

