"""
AI Automated Thumbnail Variator A/B/C/D for CutWire Drift AI.
Generates 4 distinct, high-CTR visual thumbnail compositions (Subject Focus, Big Headline,
Mystery Glow, and Split Comparison) for YouTube Studio's native 'Test & Compare' feature.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from models.scene_plan import ProjectPlan

@dataclass
class ThumbnailVariant:
    variant_id: str  # "variant_a", "variant_b", "variant_c", "variant_d"
    name: str
    archetype: str
    headline_text: str
    overlay_filter: str
    foveal_focus_zone: str
    estimated_ctr_boost_pct: int

class AIAutomatedThumbnailVariatorAB:
    """
    Builds 4 diverse thumbnail variations tailored to maximize YouTube click-through rate.
    """

    @classmethod
    def generate_thumbnail_quad(cls, plan: ProjectPlan) -> List[ThumbnailVariant]:
        raw_title = plan.title or "O Enigma Inexplicável"
        clean = re.sub(r'^(projeto|video|roteiro)\s*:\s*', '', raw_title, flags=re.IGNORECASE).strip()
        words = clean.split()

        # Short 2-3 word punchy headline
        punchy_headline = " ".join(words[:3]).upper() if len(words) >= 3 else clean.upper()

        # Variant A: Extreme Subject Contrast
        var_a = ThumbnailVariant(
            variant_id="variant_a",
            name="Versão A: Foco Extremo no Sujeito (Close-Up Dramático)",
            archetype="subject_focus",
            headline_text=punchy_headline,
            overlay_filter="eq=contrast=1.20:saturation=1.25,vignette=PI/4",
            foveal_focus_zone="Centro Superior (Rosto/Sujeito Principal)",
            estimated_ctr_boost_pct=14
        )

        # Variant B: Big Bold Headline (Yellow/Neon Impact)
        var_b = ThumbnailVariant(
            variant_id="variant_b",
            name="Versão B: Tipografia Gigante Neon (Alto Contraste)",
            archetype="big_headline",
            headline_text=f"A VERDADE: {punchy_headline}",
            overlay_filter="eq=contrast=1.15,drawbox=y=ih-180:color=black@0.7:width=iw:height=180:t=fill",
            foveal_focus_zone="Terço Inferior (Texto de Alto Impacto)",
            estimated_ctr_boost_pct=18
        )

        # Variant C: Mystery Box / Glowing Question
        var_c = ThumbnailVariant(
            variant_id="variant_c",
            name="Versão C: Aura Misteriosa & Segredo Oculto",
            archetype="mystery_highlight",
            headline_text="NUNCA REVELADO?",
            overlay_filter="colorbalance=rs=0.10:gs=-0.05:bs=0.15,eq=contrast=1.25,vignette=PI/3",
            foveal_focus_zone="Ponto Focal com Brilho Magenta/Ciano",
            estimated_ctr_boost_pct=16
        )

        # Variant D: Cinematic Split Comparison
        var_d = ThumbnailVariant(
            variant_id="variant_d",
            name="Versão D: Split Frame Cinematográfico (Antes vs Depois)",
            archetype="split_comparison",
            headline_text="O QUE MUDOU?",
            overlay_filter="drawgrid=w=iw/2:h=ih:t=4:c=white@0.8,eq=contrast=1.18",
            foveal_focus_zone="Linha Divisória de Contraste Bipolar",
            estimated_ctr_boost_pct=15
        )

        return [var_a, var_b, var_c, var_d]

    @classmethod
    def plan_thumbnail_suite(cls, plan: ProjectPlan) -> Dict[str, Any]:
        variants = cls.generate_thumbnail_quad(plan)
        return {
            "project_id": plan.project_id,
            "project_title": plan.title,
            "total_variants": len(variants),
            "variants": [v.__dict__ for v in variants],
            "youtube_test_and_compare_ready": True
        }
