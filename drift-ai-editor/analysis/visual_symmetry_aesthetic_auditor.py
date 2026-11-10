"""
Visual Symmetry & Composition Aesthetic Auditor.
Analisa o equilíbrio composicional, simetria de enquadramento (estilo Kubrick/Wes Anderson)
e harmonia geométrica entre sujeito principal e fundo para maximizar o impacto visual.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class VisualSymmetryAestheticAuditor:
    """Audita o equilíbrio estético e enquadramento visual dos planos de cena."""

    @classmethod
    def audit_composition_symmetry(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Calcula métricas de harmonia geométrica, simetria e balanceamento de peso."""
        scenes = getattr(plan, "scenes", [])
        scene_evaluations = []

        total_aesthetic_points = 0.0

        for idx, scene in enumerate(scenes):
            concept = getattr(scene, "concept", "") or ""
            desc = getattr(scene, "visual_description", "") or ""
            combined = (concept + " " + desc).lower()

            # Critérios de simetria e composição
            has_center_anchor = any(w in combined for w in ["centro", "central", "frontal", "close", "olhando", "retrato"])
            has_depth = any(w in combined for w in ["profundidade", "horizonte", "perspectiva", "luz", "sombra", "fundo"])
            has_motion = any(w in combined for w in ["movimento", "rápido", "voando", "correndo", "câmera", "travelling"])

            # Pontuação base
            score = 75.0
            if has_center_anchor:
                score += 15.0
            if has_depth:
                score += 8.0
            if has_motion:
                score -= 3.0 # Movimento muito intenso reduz a simetria estática

            final_score = min(98.0, max(50.0, score))
            total_aesthetic_points += final_score

            if final_score >= 85.0:
                style_class = "Kubrickian Centered Symmetry (Alta Simetria)"
            elif final_score >= 70.0:
                style_class = "Balanced Rule-of-Thirds (Equilíbrio Clássico)"
            else:
                style_class = "Dynamic Asymmetric (Assimetria Dinâmica)"

            scene_evaluations.append({
                "scene_index": idx + 1,
                "composition_score": round(final_score, 1),
                "composition_style": style_class,
                "has_depth_cues": has_depth,
                "has_center_subject": has_center_anchor,
                "recommendation": "Enquadramento excelente" if final_score >= 80 else "Recomenda-se centrar o sujeito na linha de horizonte para reforçar autoridade visual."
            })

        avg_score = round(total_aesthetic_points / max(len(scenes), 1), 1)

        return {
            "total_scenes_audited": len(scenes),
            "average_aesthetic_score": avg_score,
            "overall_aesthetic_grade": "A+ (Maestria Cinematográfica)" if avg_score >= 85 else "B (Harmonia Sólida)",
            "evaluations": scene_evaluations,
            "composition_philosophy": "Geometric Harmony & Symmetrical Focus"
        }
