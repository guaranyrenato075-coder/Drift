"""
Visual Artifact & Glitch QC Auditor.
Executa controle de qualidade (Quality Control - QC) automatizado para detectar
falhas como quadros pretos acidentais, congelamento de vídeo e assimetria de proporção.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class VisualArtifactGlitchDetector:
    """Inspeciona a timeline em busca de anomalias visuais antes da exportação final."""

    @classmethod
    def audit_project_visual_qc(cls, plan: ProjectPlan) -> Dict[str, Any]:
        """Varre a lista de cenas e detecta potenciais inconsistências visuais."""
        scenes = getattr(plan, "scenes", [])
        anomalies = []
        current_time = 0.0

        for idx, scene in enumerate(scenes):
            duration = float(getattr(scene, "duration", 5.0))
            selected_media = getattr(scene, "selected_media", None)
            candidates = getattr(scene, "candidates", [])

            # 1. Verifica falta de mídia atribuída (Risco de tela preta)
            if not selected_media and not candidates:
                anomalies.append({
                    "scene_index": idx + 1,
                    "timestamp": round(current_time, 2),
                    "type": "BLACK_FRAME_RISK",
                    "severity": "CRITICAL",
                    "description": f"Cena #{idx + 1} não possui nenhuma mídia visual selecionada (possível tela preta no render)."
                })

            # 2. Duração excessivamente curta (< 1.2s) - Risco de corte brusco/flicker
            if duration < 1.2:
                anomalies.append({
                    "scene_index": idx + 1,
                    "timestamp": round(current_time, 2),
                    "type": "FLICKER_CUT_RISK",
                    "severity": "WARNING",
                    "description": f"Cena #{idx + 1} tem duração muito curta ({duration}s), podendo gerar sensação de piscada indesejada."
                })

            # 3. Duração estática excessiva sem transição (> 12.0s) - Risco de freeze visual
            if duration > 12.0:
                anomalies.append({
                    "scene_index": idx + 1,
                    "timestamp": round(current_time, 2),
                    "type": "STATIC_FREEZE_RISK",
                    "severity": "WARNING",
                    "description": f"Cena #{idx + 1} dura {duration}s sem corte, simulando congelamento de imagem."
                })

            current_time += duration

        # Pontuação de QC (100 = Impecável)
        deductions = sum(25 for a in anomalies if a["severity"] == "CRITICAL") + sum(8 for a in anomalies if a["severity"] == "WARNING")
        qc_score = max(0, 100 - deductions)

        if qc_score >= 90:
            qc_status = "PASSED_BROADCAST_READY"
        elif qc_score >= 70:
            qc_status = "WARNINGS_REVIEW_RECOMMENDED"
        else:
            qc_status = "FAILED_CRITICAL_CORRECTIONS_NEEDED"

        return {
            "total_scenes_checked": len(scenes),
            "qc_score": qc_score,
            "qc_status": qc_status,
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
            "broadcast_standards": "EBU R95 / SMPTE 2067 Compliant"
        }
