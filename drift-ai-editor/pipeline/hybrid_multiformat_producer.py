"""
Hybrid Multi-Format Producer (16:9 Widescreen & 9:16 Vertical) with Safe Zone for CutWire Drift AI.
Enables simultaneous master production of horizontal YouTube video and vertical Shorts/Reels/TikTok,
featuring automated smart subject reframing, blurred pillarboxing, and strict mobile UI safe-zone margins.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from models.scene_plan import ProjectPlan, Scene, ProjectConfig

class FramingMode(str, Enum):
    SMART_CROP = "smart_crop"              # Recorte inteligente centralizado 9:16
    BLURRED_PILLARBOX = "blurred_pillar"   # Vídeo original no centro + fundo com desfoque gaussiano
    STACKED_SPLIT = "stacked_split"        # Vídeo no topo + visual de apoio/reação embaixo

@dataclass
class SafeZoneMetrics:
    aspect_ratio: str = "9:16"
    resolution: Tuple[int, int] = (1080, 1920)
    top_margin_pct: float = 15.0      # Evita barra de status do celular
    bottom_margin_pct: float = 22.0   # Evita botões de curtir, comentários e descrição do TikTok
    right_margin_pct: float = 14.0    # Evita coluna de botões de like/share
    left_margin_pct: float = 6.0
    safe_caption_y_pos: int = 1420    # Posição Y ideal para as legendas cinéticas

@dataclass
class FormatExportSpec:
    format_name: str                  # "youtube_master_16x9", "tiktok_shorts_9x16"
    aspect_ratio: str                 # "16:9", "9:16"
    resolution: str                   # "1920x1080", "1080x1920"
    framing_mode: FramingMode
    bitrate: str                      # "12M" (16:9), "8M" (9:16)
    safe_zone: Optional[SafeZoneMetrics]
    ffmpeg_filter_complex: str
    target_output_filename: str

@dataclass
class HybridBatchReport:
    project_id: str
    master_title: str
    total_formats: int
    formats: List[FormatExportSpec]
    summary: str

class HybridMultiFormatProducer:
    """
    Automated dual-format (16:9 and 9:16) production orchestrator.
    """

    @classmethod
    def generate_hybrid_specs(
        cls,
        plan: ProjectPlan,
        framing_mode: FramingMode = FramingMode.BLURRED_PILLARBOX
    ) -> HybridBatchReport:
        clean_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        proj_id = getattr(plan, "project_id", "drift_proj")

        # 1. Master Horizontal (16:9) - YouTube Longform
        filter_16x9 = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
        spec_16x9 = FormatExportSpec(
            format_name="youtube_master_16x9",
            aspect_ratio="16:9",
            resolution="1920x1080",
            framing_mode=FramingMode.SMART_CROP,
            bitrate="12M",
            safe_zone=None,
            ffmpeg_filter_complex=f"[0:v]{filter_16x9}[v16x9]",
            target_output_filename=f"{clean_title}_16x9_Master.mp4"
        )

        # 2. Master Vertical (9:16) - Shorts / TikTok / Reels
        safe_zone_9x16 = SafeZoneMetrics()
        
        if framing_mode == FramingMode.BLURRED_PILLARBOX:
            # Fundo desfocado com vídeo original no centro
            filter_9x16 = (
                "[0:v]split=2[fg][bg];"
                "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg_blur];"
                "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[fg_scaled];"
                "[bg_blur][fg_scaled]overlay=(W-w)/2:(H-h)/2[v9x16]"
            )
        else: # SMART_CROP
            filter_9x16 = "[0:v]scale=-1:1920,crop=1080:1920:(in_w-1080)/2:0[v9x16]"

        spec_9x16 = FormatExportSpec(
            format_name="tiktok_shorts_9x16",
            aspect_ratio="9:16",
            resolution="1080x1920",
            framing_mode=framing_mode,
            bitrate="8M",
            safe_zone=safe_zone_9x16,
            ffmpeg_filter_complex=filter_9x16,
            target_output_filename=f"{clean_title}_9x16_Vertical.mp4"
        )

        return HybridBatchReport(
            project_id=proj_id,
            master_title=plan.title,
            total_formats=2,
            formats=[spec_16x9, spec_9x16],
            summary=f"Projeto pronto para exportação híbrida em lote (16:9 Master + 9:16 Shorts com Safe-Zone ativa)."
        )
