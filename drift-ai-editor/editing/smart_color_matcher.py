"""
Smart LUT & Cinematic Color Matcher for CutWire Drift AI.
Harmonizes white balance, color temperature, and contrast across multi-source media (Wikimedia, NASA, Pexels, Museums)
to ensure continuous aesthetic coherence like Hollywood color grading pipelines.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class HarmonizedColorRecipe:
    scene_order: int
    detected_color_bias: str  # "warm_tungsten", "cool_space_blue", "vintage_sepia", "neutral"
    target_temperature: str  # "5600K Daylight"
    ffmpeg_filter: str
    explanation: str

class SmartLutCinematicColorMatcher:
    """
    Normalizes divergent color profiles across disparate archive sources.
    """

    @classmethod
    def analyze_scene_color_bias(cls, scene: Scene) -> str:
        text = (scene.visual_description + " " + (scene.narration_text or "")).lower()

        if any(k in text for k in ["espaço", "nasa", "noite", "oceano", "gelo", "frio", "ciber", "tecnologia"]):
            return "cool_space_blue"
        elif any(k in text for k in ["museu", "pintura", "estátua", "vela", "ouro", "deserto", "sol", "fogo", "antigo"]):
            return "warm_tungsten"
        elif any(k in text for k in ["século", "história", "guerra", "arquivo", "preto e branco", "séphia"]):
            return "vintage_sepia"
        return "neutral"

    @classmethod
    def calculate_harmonization_filter(cls, bias: str) -> tuple[str, str]:
        """
        Calculates FFmpeg eq and colorbalance parameters to neutralize bias toward cinematic 5600K daylight.
        """
        if bias == "cool_space_blue":
            # Excessive blue: boost red shadows and slightly warm midtones
            filt = "colorbalance=rs=0.06:rm=0.04:bs=-0.08:bm=-0.04,eq=contrast=1.08:saturation=1.05"
            expl = "Correção de azul frio excessivo: elevação de vermelhos quentes e equilíbrio de ciano."
        elif bias == "warm_tungsten":
            # Excessive warm yellow/red: cool down slightly to match natural daylight
            filt = "colorbalance=rs=-0.05:rm=-0.04:bs=0.06:bm=0.05,eq=contrast=1.06:saturation=0.98"
            expl = "Neutralização de tungstênio alaranjado: compensação suave em tons de azul e ciano."
        elif bias == "vintage_sepia":
            # Desaturated/faded historical footage: enhance contrast and dynamic range
            filt = "eq=contrast=1.14:brightness=0.02:saturation=1.12,colorbalance=rh=0.04:bh=-0.02"
            expl = "Restauração de acervo desbotado: ganho de contraste e restauração sutil de gama."
        else:
            # Neutral baseline: gentle cinematic curve
            filt = "eq=contrast=1.05:saturation=1.02"
            expl = "Curva base de contraste cinematográfico neutro."

        return filt, expl

    @classmethod
    def harmonize_project_colors(cls, plan: ProjectPlan) -> Dict[str, Any]:
        recipes: List[HarmonizedColorRecipe] = []

        for scene in plan.scenes:
            bias = cls.analyze_scene_color_bias(scene)
            filt, expl = cls.calculate_harmonization_filter(bias)
            recipes.append(HarmonizedColorRecipe(
                scene_order=scene.order,
                detected_color_bias=bias,
                target_temperature="5600K Daylight",
                ffmpeg_filter=filt,
                explanation=expl
            ))

        return {
            "project_id": plan.project_id,
            "target_aesthetic": "Cinematic Hollywood 5600K Balanced",
            "total_scenes_harmonized": len(recipes),
            "recipes": [r.__dict__ for r in recipes]
        }
