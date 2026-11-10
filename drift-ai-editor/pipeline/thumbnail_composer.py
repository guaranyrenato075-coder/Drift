"""
Automated High-Resolution Thumbnail Visual Composer for CutWire Drift AI.
Assembles 1280x720 YouTube/Social thumbnails by blending hero scene imagery,
high-contrast edge vignettes, saturation boosting, and punchy typography overlays.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import os
from models.scene_plan import ProjectPlan, MediaCandidate

@dataclass
class ThumbnailCompositionResult:
    project_id: str
    output_image_path: str
    width: int
    height: int
    hero_platform: str
    headline_text: str
    used_engine: str  # "pillow" or "ffmpeg_fallback"

class AutoThumbnailVisualComposer:
    """
    Automated visual thumbnail compositor and renderer.
    """

    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 720

    @classmethod
    def _select_hero_media(cls, plan: ProjectPlan) -> Optional[MediaCandidate]:
        # Prioritize scenes with safe copyright risk and high quality platforms
        for s in plan.scenes:
            if s.selected_media and s.selected_media.copyright_risk == "safe":
                return s.selected_media
        for s in plan.scenes:
            if s.selected_media:
                return s.selected_media
        return None

    @classmethod
    def compose_thumbnail(
        cls,
        plan: ProjectPlan,
        headline_text: str = "A VERDADE",
        output_path: Optional[str] = None
    ) -> ThumbnailCompositionResult:
        safe_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        if not output_path:
            out_file = Path("d:/CUTWIREDRIFT") / f"Thumbnail_{safe_title}.png"
        else:
            out_file = Path(output_path)

        out_file.parent.mkdir(parents=True, exist_ok=True)
        hero = cls._select_hero_media(plan)
        hero_platform = hero.platform if hero else "drift_canvas"

        used_engine = "fallback"

        # Attempt Pillow composition first
        try:
            from PIL import Image, ImageDraw, ImageFont, ImageEnhance
            # Create base 1280x720 canvas
            base_img = Image.new("RGB", (cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT), color=(18, 24, 38))
            
            # If local media image exists, paste it
            if hero and hero.local_cached_path and os.path.exists(hero.local_cached_path):
                try:
                    src_img = Image.open(hero.local_cached_path).convert("RGB")
                    src_img = src_img.resize((cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT), Image.Resampling.LANCZOS)
                    # Contrast and saturation boost
                    enhancer = ImageEnhance.Contrast(src_img)
                    src_img = enhancer.enhance(1.2)
                    sat_enhancer = ImageEnhance.Color(src_img)
                    src_img = sat_enhancer.enhance(1.25)
                    base_img.paste(src_img, (0, 0))
                except Exception:
                    pass

            draw = ImageDraw.Draw(base_img)

            # Dark gradient / vignette band at the bottom for text legibility
            gradient_height = 240
            for y in range(gradient_height):
                alpha = int((y / gradient_height) * 200)
                draw.line([(0, cls.DEFAULT_HEIGHT - gradient_height + y), (cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT - gradient_height + y)], fill=(0, 0, 0))

            # Draw punchy headline text
            text = headline_text.upper()
            try:
                font = ImageFont.truetype("arialbd.ttf", 64)
            except Exception:
                font = ImageFont.load_default()

            # Shadow and foreground text
            x, y = 60, cls.DEFAULT_HEIGHT - 130
            draw.text((x + 4, y + 4), text, font=font, fill=(0, 0, 0))
            draw.text((x, y), text, font=font, fill=(255, 220, 0))  # Vivid Yellow

            base_img.save(str(out_file), format="PNG")
            used_engine = "pillow"
        except ImportError:
            # Fallback: create placeholder PNG with raw binary header if PIL not available
            used_engine = "placeholder"
            # Write minimal valid PNG or text marker
            out_file.write_text(f"Thumbnail render placeholder for {safe_title} [{headline_text}]", encoding="utf-8")

        return ThumbnailCompositionResult(
            project_id=plan.project_id,
            output_image_path=str(out_file),
            width=cls.DEFAULT_WIDTH,
            height=cls.DEFAULT_HEIGHT,
            hero_platform=hero_platform,
            headline_text=headline_text,
            used_engine=used_engine
        )
