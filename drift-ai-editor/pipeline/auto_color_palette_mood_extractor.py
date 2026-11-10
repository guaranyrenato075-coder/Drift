"""
Auto Color Palette & Mood Extractor.
Analisa a atmosfera emocional e temática do roteiro e extrai uma paleta de 5 cores
cromáticas harmônicas (HEX) representativas do tom narrativo do projeto.
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class AutoColorPaletteMoodExtractor:
    """Extrai paletas cromáticas narrativas baseadas na atmosfera emocional do projeto."""

    THEMATIC_PALETTES = {
        "cyberpunk_neon": {
            "name": "Cyberpunk Neon & Distopia",
            "mood": "Futurista, Alta Tecnologia, Noturno",
            "colors": ["#0B0E14", "#00F0FF", "#7000FF", "#FF0055", "#FFE600"],
            "keywords": ["futuro", "ia", "tecnologia", "robô", "código", "hacker", "cyber", "digital"]
        },
        "cinematic_warm_gold": {
            "name": "Cinema Dourado & Épico",
            "mood": "Calor Humano, Triunfo, Inspiração",
            "colors": ["#1A1612", "#D4AF37", "#E67E22", "#F39C12", "#FDFEFE"],
            "keywords": ["vitória", "sucesso", "conquista", "herói", "ouro", "luz", "superou", "rico"]
        },
        "mystery_cold_steel": {
            "name": "Mistério & Aço Frio",
            "mood": "Suspense, Investigação, Tensão",
            "colors": ["#0A0F1D", "#1E293B", "#38BDF8", "#64748B", "#E2E8F0"],
            "keywords": ["segredo", "mistério", "perigo", "investigação", "crime", "oculto", "noite"]
        },
        "nature_documentary": {
            "name": "Natureza & Vida Selvagem",
            "mood": "Orgânico, Serenidade, Vasto",
            "colors": ["#1C2826", "#2D5A27", "#8FBC8F", "#D2B48C", "#FAF0E6"],
            "keywords": ["floresta", "terra", "planeta", "vida", "animal", "mar", "natureza", "selva"]
        },
        "historical_warm_sepia": {
            "name": "Histórico & Sépia Nobre",
            "mood": "Memória, Ancestralidade, Documentário",
            "colors": ["#2C221E", "#7D5A44", "#C89666", "#E1B168", "#F5EBE6"],
            "keywords": ["história", "passado", "antigo", "século", "guerra", "origem", "império"]
        }
    }

    @classmethod
    def get_preset_palettes(cls) -> Dict[str, Dict[str, Any]]:
        return cls.THEMATIC_PALETTES

    @classmethod
    def extract_palette_from_plan(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Varre o roteiro e determina a paleta cromática dominante com base nas palavras-chave."""
        scenes = getattr(plan, "scenes", [])
        full_text = " ".join((getattr(s, "narration_text", "") or getattr(s, "text", "") or "") for s in scenes).lower()

        # Pontua cada paleta por relevância de palavras-chave
        scores = {}
        for key, p in cls.THEMATIC_PALETTES.items():
            matches = sum(len(re.findall(rf"\b{kw}\b", full_text)) for kw in p["keywords"])
            scores[key] = matches

        # Seleciona a paleta de maior correspondência
        best_palette_key = max(scores, key=scores.get) if any(scores.values()) else "cinematic_warm_gold"
        selected = cls.THEMATIC_PALETTES[best_palette_key]

        return {
            "dominant_palette_key": best_palette_key,
            "palette_name": selected["name"],
            "mood": selected["mood"],
            "hex_colors": selected["colors"],
            "relevance_score": scores.get(best_palette_key, 1),
            "css_gradient": f"linear-gradient(90deg, {', '.join(selected['colors'])})",
            "status": "EXTRACTED"
        }
