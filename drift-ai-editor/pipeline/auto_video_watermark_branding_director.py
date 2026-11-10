"""
Auto Video Watermark & Branding Director.
Gerencia marca d'água de proteção contra pirataria e branding de canal,
calculando posicionamento seguro (Safe Margins), opacidade e fade-in elegante.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class AutoVideoWatermarkBrandingDirector:
    """Configura e gera filtros FFmpeg de marca d'água e branding visual."""

    CORNER_POSITIONS = {
        "top_right": {
            "name": "Canto Superior Direito",
            "overlay_coords": "W-w-35:35",
            "safe_margin": "35px"
        },
        "bottom_right": {
            "name": "Canto Inferior Direito",
            "overlay_coords": "W-w-35:H-h-35",
            "safe_margin": "35px"
        },
        "top_left": {
            "name": "Canto Superior Esquerdo",
            "overlay_coords": "35:35",
            "safe_margin": "35px"
        },
        "bottom_left": {
            "name": "Canto Inferior Esquerdo",
            "overlay_coords": "35:H-h-35",
            "safe_margin": "35px"
        }
    }

    @classmethod
    def get_corner_positions(cls) -> Dict[str, Dict[str, Any]]:
        return cls.CORNER_POSITIONS

    @classmethod
    def generate_watermark_filter_plan(
        cls,
        watermark_path: str = "assets/branding/logo_watermark.png",
        position: str = "bottom_right",
        opacity: float = 0.55,
        fade_in_seconds: float = 1.5,
        target_width_px: int = 180
    ) -> Dict[str, Any]:
        """Gera comando de overlay com opacidade e fade-in transparente."""
        if position not in cls.CORNER_POSITIONS:
            position = "bottom_right"

        pos_info = cls.CORNER_POSITIONS[position]
        coords = pos_info["overlay_coords"]

        # Constrói filtro FFmpeg complexo com scale, format, colorchannelmixer e overlay
        ffmpeg_filter = (
            f"[1:v]scale={target_width_px}:-1,format=rgba,"
            f"colorchannelmixer=aa={opacity},"
            f"fade=in:st=0:d={fade_in_seconds}:alpha=1[wm];"
            f"[0:v][wm]overlay={coords}:enable='between(t,1,999999)'"
        )

        return {
            "watermark_path": watermark_path,
            "position": position,
            "position_name": pos_info["name"],
            "opacity": opacity,
            "fade_in_seconds": fade_in_seconds,
            "target_width_px": target_width_px,
            "ffmpeg_overlay_filter": ffmpeg_filter,
            "copyright_protection": "ACTIVE"
        }

    @classmethod
    def apply_watermark_to_plan(
        cls,
        plan: ProjectPlan,
        watermark_path: str = "assets/branding/logo_watermark.png",
        position: str = "bottom_right",
        opacity: float = 0.55
    ) -> Dict[str, Any]:
        """Aplica os metadados de marca d'água ao plano do projeto."""
        plan_info = cls.generate_watermark_filter_plan(watermark_path, position, opacity)
        setattr(plan, "branding_watermark_config", plan_info)
        return {
            "status": "APPLIED",
            "config": plan_info
        }
