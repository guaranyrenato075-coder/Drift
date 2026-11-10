"""
Dynamic B-Roll Pacer & Visual Fatigue Preventer.
Analisa a densidade de B-rolls na timeline e calcula pontos ideais de inserção
para evitar fadiga visual e manter a taxa de retenção por corte frequente.
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class DynamicBrollPacer:
    """Audita a cadência de corte e sugere inserção dinâmica de B-roll."""

    DEFAULT_MAX_STATIC_DURATION = 4.5

    @classmethod
    def calculate_broll_pacing(cls, plan: ProjectPlan, max_static_duration: float = DEFAULT_MAX_STATIC_DURATION) -> Dict[str, Any]:
        """Calcula intervalos estáticos sem cortes e recomenda pontos de B-roll."""
        scenes = getattr(plan, "scenes", [])
        total_duration = sum(getattr(s, "duration", 5.0) for s in scenes)
        
        static_segments = []
        broll_recommendations = []
        current_time = 0.0

        for idx, scene in enumerate(scenes):
            duration = float(getattr(scene, "duration", 5.0))
            text = getattr(scene, "narration_text", "") or getattr(scene, "text", "") or getattr(scene, "narration", "") or ""
            
            # Se a cena for mais longa que o limiar seguro, precisa de B-roll secundário
            if duration > max_static_duration:
                # Extrai palavras-chave do texto
                words = re.findall(r"\b[A-Za-zÀ-ÖØ-öø-ÿ]{5,}\b", text)
                keywords = [w.lower() for w in words if w.lower() not in ["quando", "porque", "então", "sobre", "assim", "muito", "todos", "estava", "ainda"]]
                suggested_kw = keywords[0] if keywords else "contexto"

                split_point = round(current_time + (duration / 2.0), 2)
                broll_duration = round(min(duration * 0.45, 3.5), 2)

                static_segments.append({
                    "scene_index": idx + 1,
                    "duration": duration,
                    "exceeded_by": round(duration - max_static_duration, 2),
                    "status": "FATIGUE_RISK"
                })

                broll_recommendations.append({
                    "scene_index": idx + 1,
                    "insert_time": split_point,
                    "duration": broll_duration,
                    "suggested_query": suggested_kw,
                    "reason": f"Duração estática ({duration:.1f}s) excede o limiar de retenção de {max_static_duration:.1f}s"
                })

            current_time += duration

        total_static_risks = len(static_segments)
        if total_static_risks == 0:
            fatigue_risk = "LOW"
            pacing_grade = "A+ (Dinâmico e Rápido)"
        elif total_static_risks <= 2:
            fatigue_risk = "MODERATE"
            pacing_grade = "B (Bom, pequenos ajustes recomendados)"
        else:
            fatigue_risk = "HIGH"
            pacing_grade = "C (Risco de queda de retenção por estagnação visual)"

        return {
            "total_scenes": len(scenes),
            "total_duration": round(total_duration, 2),
            "max_static_threshold": max_static_duration,
            "static_risk_count": total_static_risks,
            "fatigue_risk": fatigue_risk,
            "pacing_grade": pacing_grade,
            "recommendations": broll_recommendations
        }

    @classmethod
    def auto_insert_broll_slots(cls, plan: ProjectPlan, max_static_duration: float = DEFAULT_MAX_STATIC_DURATION) -> Dict[str, Any]:
        """Aplica marcações automáticas de B-Roll nas cenas do projeto."""
        analysis = cls.calculate_broll_pacing(plan, max_static_duration)
        applied_count = 0

        scenes = getattr(plan, "scenes", [])
        for rec in analysis["recommendations"]:
            s_idx = rec["scene_index"] - 1
            if 0 <= s_idx < len(scenes):
                scene = scenes[s_idx]
                if not hasattr(scene, "broll_inserts") or getattr(scene, "broll_inserts") is None:
                    scene.broll_inserts = []
                scene.broll_inserts.append({
                    "offset": rec["insert_time"],
                    "duration": rec["duration"],
                    "query": rec["suggested_query"]
                })
                applied_count += 1

        return {
            "slots_created": applied_count,
            "status": "SUCCESS",
            "pacing_analysis": analysis
        }
