"""
AI Color Grading & Cinematic Look Engine for CutWire Drift AI.
Applies curated color profiles, saturation balancing, contrast curves, and atmospheric LUT-like
adjustments via FFmpeg video filters to unify heterogeneous stock and public domain media into a single cohesive aesthetic.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class ColorGradePreset:
    id: str
    name: str
    description: str
    ffmpeg_filter: str
    temperature: str  # "warm", "cool", "neutral", "dramatic"
    recommended_genre: str

class ColorGradingEngine:
    """
    Manages and applies cinematic color grading transforms to video scenes.
    """

    PRESETS: Dict[str, ColorGradePreset] = {
        "neutral": ColorGradePreset(
            id="neutral",
            name="Natural / Sem Gradação",
            description="Mantém as cores e contraste originais das fontes de acervo.",
            ffmpeg_filter="null",
            temperature="neutral",
            recommended_genre="any"
        ),
        "teal_and_orange": ColorGradePreset(
            id="teal_and_orange",
            name="Teal & Orange (Blockbuster)",
            description="Sombras azuladas/ciano e realces quentes na pele e luzes. Look hollywoodiano moderno.",
            ffmpeg_filter="colorbalance=rs=0.08:gs=0.02:bs=-0.1:rm=-0.05:gm=0.02:bm=0.08:rh=-0.08:gh=0.01:bh=0.12,eq=contrast=1.12:saturation=1.15",
            temperature="dramatic",
            recommended_genre="cinematic_action"
        ),
        "warm_documentary": ColorGradePreset(
            id="warm_documentary",
            name="Warm Documentary (História & Arte)",
            description="Tons âmbar aconchegantes, realce dourado suave e contraste equilibrado.",
            ffmpeg_filter="colorbalance=rs=0.10:gs=0.04:bs=-0.08:rm=0.08:gm=0.03:bm=-0.06:rh=0.05:gh=0.02:bh=-0.04,eq=contrast=1.05:saturation=1.08:gamma=1.02",
            temperature="warm",
            recommended_genre="history_documentary"
        ),
        "deep_space": ColorGradePreset(
            id="deep_space",
            name="Deep Space Contrast (Cosmos & Sci-Fi)",
            description="Pretos absolutos com alto alcance dinâmico, realçando nebulosas, estrelas e iluminação volumétrica.",
            ffmpeg_filter="eq=contrast=1.28:brightness=-0.03:saturation=1.22,curves=preset=strong_contrast",
            temperature="cool",
            recommended_genre="space_science"
        ),
        "nordic_moody": ColorGradePreset(
            id="nordic_moody",
            name="Nordic Moody (Suspense & Mistério)",
            description="Dessaturação parcial com tonalidade fria esverdeada e sombras densas.",
            ffmpeg_filter="colorbalance=rs=-0.08:gs=0.03:bs=0.06:rm=-0.06:gm=0.04:bm=0.08,eq=contrast=1.18:saturation=0.82:brightness=-0.02",
            temperature="cool",
            recommended_genre="mystery_crime"
        ),
        "vintage_35mm": ColorGradePreset(
            id="vintage_35mm",
            name="Vintage 35mm (Cinema Analógico)",
            description="Pretos ligeiramente elevados (fade film), sépia suave e textura clássica de celulóide.",
            ffmpeg_filter="curves=preset=vintage,eq=contrast=1.08:saturation=0.92:gamma=1.05",
            temperature="warm",
            recommended_genre="biography_retro"
        )
    }

    @classmethod
    def list_presets(cls) -> List[Dict[str, str]]:
        """Returns all available presets metadata."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "temperature": p.temperature,
                "recommended_genre": p.recommended_genre
            }
            for p in cls.PRESETS.values()
        ]

    @classmethod
    def get_filter(cls, preset_id: str) -> str:
        """Returns the FFmpeg video filter chain for the given preset."""
        preset = cls.PRESETS.get(preset_id, cls.PRESETS["neutral"])
        return preset.ffmpeg_filter

    @classmethod
    def auto_detect_preset_for_plan(cls, plan: ProjectPlan) -> str:
        """
        Suggests the most suitable color grade based on keywords, title and genre.
        """
        text = (plan.title + " " + " ".join(
            " ".join(s.english_keywords or []) + " " + s.narration_text
            for s in plan.scenes
        )).lower()

        if any(w in text for w in ["galaxy", "space", "nebula", "mars", "star", "telescope", "nasa"]):
            return "deep_space"
        if any(w in text for w in ["history", "rome", "century", "ancient", "museum", "sculpture", "philosophy"]):
            return "warm_documentary"
        if any(w in text for w in ["dark", "mystery", "crime", "secret", "cold", "fog", "investigation"]):
            return "nordic_moody"
        if any(w in text for w in ["retro", "vintage", "classic", "memory", "1970", "1980", "nostalgia"]):
            return "vintage_35mm"
        if any(w in text for w in ["action", "epic", "battle", "future", "power", "energy"]):
            return "teal_and_orange"

        return "warm_documentary"
