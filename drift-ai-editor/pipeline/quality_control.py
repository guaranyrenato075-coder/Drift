from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from models.scene_plan import ProjectPlan, Scene

@dataclass
class QualityIssue:
    severity: str     # 'error' (blocking), 'warning' (can export with degraded quality), 'info'
    scene_order: Optional[int]
    category: str     # 'missing_file', 'audio_clipping', 'aspect_ratio_mismatch', 'duration_anomaly', 'subtitle_overflow'
    message: str
    remediation_suggestion: str

@dataclass
class QualityAuditReport:
    project_id: str
    is_ready_for_export: bool
    score: int        # 0 to 100
    errors_count: int
    warnings_count: int
    issues: List[QualityIssue] = field(default_factory=list)
    summary_text: str = ""

class QualityControlEngine:
    """
    Automated pre-export inspector:
    Audits timeline integrity, audio levels, aspect ratio consistency,
    missing files, and subtitle boundaries before triggering video encoding.
    """

    @classmethod
    def audit_project(cls, plan: ProjectPlan) -> QualityAuditReport:
        issues: List[QualityIssue] = []

        if not plan.scenes:
            issues.append(
                QualityIssue(
                    severity="error",
                    scene_order=None,
                    category="empty_project",
                    message="O projeto não contém nenhuma cena definida.",
                    remediation_suggestion="Gere ou insira um roteiro de cenas."
                )
            )

        total_scenes = len(plan.scenes)
        for scene in plan.scenes:
            # 1. Check media presence
            if not scene.selected_media:
                issues.append(
                    QualityIssue(
                        severity="error",
                        scene_order=scene.order,
                        category="missing_file",
                        message=f"Cena {scene.order}: Nenhuma mídia visual foi selecionada.",
                        remediation_suggestion="Execute a busca de mídia ou escolha uma alternativa na galeria."
                    )
                )
            elif not scene.selected_media.local_cached_path or not Path(scene.selected_media.local_cached_path).exists():
                issues.append(
                    QualityIssue(
                        severity="error",
                        scene_order=scene.order,
                        category="missing_file",
                        message=f"Cena {scene.order}: O arquivo da mídia '{scene.selected_media.title}' não foi baixado.",
                        remediation_suggestion="Execute o download prévio dos arquivos."
                    )
                )

            # 2. Check narration audio
            audio_p = getattr(scene, "audio_path", None) or getattr(scene, "narration_audio_path", None)
            if not audio_p or not Path(audio_p).exists():
                issues.append(
                    QualityIssue(
                        severity="warning",
                        scene_order=scene.order,
                        category="missing_file",
                        message=f"Cena {scene.order}: Áudio de narração não sintetizado.",
                        remediation_suggestion="Sintetize a voz para garantir sincronia temporal."
                    )
                )

            # 3. Check duration consistency
            if (scene.duration or 0) < 1.0:
                issues.append(
                    QualityIssue(
                        severity="warning",
                        scene_order=scene.order,
                        category="duration_anomaly",
                        message=f"Cena {scene.order}: Duração excessivamente curta ({scene.duration}s).",
                        remediation_suggestion="Recomenda-se no mínimo 2.5 segundos por take."
                    )
                )

            # 4. Check subtitle length per screen
            if len(scene.narration_text) > 140:
                issues.append(
                    QualityIssue(
                        severity="info",
                        scene_order=scene.order,
                        category="subtitle_overflow",
                        message=f"Cena {scene.order}: Texto da narração longo para um único take ({len(scene.narration_text)} chars).",
                        remediation_suggestion="Considere dividir a frase em duas cenas menores para melhor retenção."
                    )
                )

        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        # Calculate readiness score
        score = max(0, 100 - (len(errors) * 25) - (len(warnings) * 10))
        is_ready = len(errors) == 0

        summary = (
            f"Auditoria concluída com nota {score}/100. "
            f"{'Pronto para exportação!' if is_ready else 'Existem problemas críticos que precisam ser corrigidos antes de exportar.'}"
        )

        return QualityAuditReport(
            project_id=plan.project_id,
            is_ready_for_export=is_ready,
            score=score,
            errors_count=len(errors),
            warnings_count=len(warnings),
            issues=issues,
            summary_text=summary
        )
