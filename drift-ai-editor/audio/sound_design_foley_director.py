"""
Sound Design & Foley Auto Director.
Analisa a timeline e diálogos para gerar trilha de sound design procedural
com efeitos foley sincrônicos (whooshes, impactos, risers e cliques).
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class SoundDesignFoleyAutoDirector:
    """Gera marcações e filtros de Sound Design (SFX / Foley) para a timeline."""

    FOLEY_KEYWORDS = {
        "impact": [
            r"\b(segredo|perigo|nunca|destruiu|bomba|chocante|parar|morreu|catástrofe|urgente)\b",
            "impact_sub_bass.wav",
            -2.0
        ],
        "glitch": [
            r"\b(erro|bug|falha|hack|quebrou|conspiração|mentira|ilusion|falso)\b",
            "glitch_distortion.wav",
            -4.0
        ],
        "cash_register": [
            r"\b(dinheiro|lucro|milhões|bilhões|rico|vendas|investimento|dólares|reais)\b",
            "cash_register_ding.wav",
            -5.0
        ],
        "digital_pop": [
            r"\b(clique|veja|olhe|aqui|link|abaixo|exemplo|passo|dica)\b",
            "ui_pop_bright.wav",
            -6.0
        ]
    }

    @classmethod
    def get_foley_categories(cls) -> List[str]:
        return ["transitions", "impacts", "glitches", "ui_clicks", "risers"]

    @classmethod
    def generate_foley_cues(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Gera eventos de SFX/Foley sincronizados com cortes e palavras-chave."""
        scenes = getattr(plan, "scenes", [])
        cues = []
        current_time = 0.0

        for idx, scene in enumerate(scenes):
            duration = float(getattr(scene, "duration", 5.0))
            text = getattr(scene, "narration_text", "") or getattr(scene, "text", "") or getattr(scene, "narration", "") or ""

            # 1. Foley de Transição de Cena (Whoosh / Swoosh no corte)
            if idx > 0:
                cues.append({
                    "timestamp": round(current_time, 2),
                    "type": "transition",
                    "sample": "whoosh_cinematic_fast.wav",
                    "category": "transitions",
                    "volume_db": -8.0,
                    "description": f"Transição rápida para Cena #{idx + 1}"
                })

            # 2. Foley Lexical baseado no texto da cena
            for category, (pattern, sample_file, vol) in cls.FOLEY_KEYWORDS.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Estima a posição temporal aproximada da palavra na cena
                    word_pos = match.start()
                    total_chars = max(len(text), 1)
                    rel_offset = (word_pos / total_chars) * duration
                    cue_time = round(current_time + rel_offset, 2)

                    cues.append({
                        "timestamp": cue_time,
                        "type": category,
                        "sample": sample_file,
                        "category": category,
                        "volume_db": vol,
                        "trigger_word": match.group(0),
                        "description": f"Ênfase dramática em '{match.group(0)}'"
                    })

            # 3. Riser / Clímax nos últimos 20% da cena se for a penúltima ou cena de clímax
            if idx == len(scenes) - 2 and duration > 4.0:
                riser_start = round(current_time + (duration - 3.0), 2)
                cues.append({
                    "timestamp": riser_start,
                    "type": "riser",
                    "sample": "cinematic_tension_riser.wav",
                    "category": "risers",
                    "volume_db": -6.0,
                    "description": "Subida de tensão pré-clímax"
                })

            current_time += duration

        # Ordena por timestamp
        cues.sort(key=lambda x: x["timestamp"])

        return {
            "total_cues": len(cues),
            "total_duration": round(current_time, 2),
            "cues": cues,
            "sound_density": round(len(cues) / max(current_time / 60.0, 0.1), 1),
            "mix_guideline": "Mixagem de Foley calibrada em -6dB True Peak para não mascarar a locução principal."
        }
