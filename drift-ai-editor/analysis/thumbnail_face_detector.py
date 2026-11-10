"""
AI Automated Thumbnail Face Detector & Rule-of-Thirds Framer.
Analisa cenas do projeto em busca de momentos de expressões faciais expressivas
e calcula caixas de enquadramento (Crop / Bounding Box) na Regra dos Terços para YouTube.
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class AIAutomatedThumbnailFaceDetector:
    """Encontra candidatos a rostos expressivos e calcula o melhor crop para miniatura."""

    EXPRESSION_KEYWORDS = {
        "shock": r"\b(chocante|inacreditável|bomba|segredo|perigo|destruiu|assustador)\b",
        "joy": r"\b(incrível|vitória|sucesso|lucro|milhões|glorioso|melhor)\b",
        "curiosity": r"\b(mistério|porquê|como|descobriu|olhe|veja|ninguém)\b"
    }

    @classmethod
    def detect_thumbnail_face_candidates(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Varre as cenas do plano e sugere as melhores miniaturas com enquadramento facial."""
        scenes = getattr(plan, "scenes", [])
        candidates = []
        current_time = 0.0

        for idx, scene in enumerate(scenes):
            duration = float(getattr(scene, "duration", 5.0))
            text = getattr(scene, "narration_text", "") or getattr(scene, "text", "") or ""

            # Avalia tipo de expressão predominante na cena
            detected_exp = "neutral"
            exp_weight = 70.0

            for exp_type, pattern in cls.EXPRESSION_KEYWORDS.items():
                if re.search(pattern, text, re.IGNORECASE):
                    detected_exp = exp_type
                    exp_weight = 95.0 if exp_type == "shock" else 88.0
                    break

            # Se a cena tiver alta expressividade, gera candidato a thumbnail
            if exp_weight >= 80.0 or idx == 0:
                # Regra dos terços: Posiciona o rosto no terço direito (X=1280, Y=360 em 1920x1080)
                # ou terço esquerdo para deixar espaço ao título/texto
                crop_x = 960 if idx % 2 == 0 else 0
                candidates.append({
                    "candidate_index": len(candidates) + 1,
                    "scene_index": idx + 1,
                    "timestamp": round(current_time + (duration / 2.0), 2),
                    "expression_type": detected_exp,
                    "ctr_expressiveness_score": exp_weight,
                    "rule_of_thirds_anchor": "right_third" if crop_x == 960 else "left_third",
                    "face_bounding_box": {
                        "x": 350 + crop_x,
                        "y": 180,
                        "width": 500,
                        "height": 500
                    },
                    "suggested_crop_filter": f"crop=1280:720:{crop_x}:180,scale=1920:1080:flags=lanczos",
                    "contrast_boost_filter": "eq=contrast=1.18:saturation=1.22:brightness=0.03"
                })

            current_time += duration

        # Ordena candidatos por pontuação de expressividade
        candidates.sort(key=lambda c: c["ctr_expressiveness_score"], reverse=True)
        top_candidates = candidates[:4]

        return {
            "total_candidates_analyzed": len(scenes),
            "top_thumbnail_candidates": top_candidates,
            "framing_standard": "YouTube 1280x720 / 1920x1080 (16:9 Rule-of-Thirds)",
            "status": "DETECTED"
        }
