"""
Viral Hook Vocabulary & Neuro-Linguistic Script Auditor for CutWire Drift AI.
Audits video narration transcripts for weak passive phrases and replaces them
with high-dopamine hypnotic power hooks that maximize engagement and watch time.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from models.scene_plan import Scene, ProjectPlan

@dataclass
class VocabularyAuditIssue:
    scene_order: int
    weak_phrase: str
    suggested_replacement: str
    impact_gain_pct: int
    justification: str

class ViralHookVocabularyAuditor:
    """
    Scans narration for passive cliches and injects high-impact curiosity triggers.
    """

    REPLACEMENTS = {
        "é interessante notar": "o que ninguém esperava é que",
        "podemos observar": "preste muita atenção nisto:",
        "com o passar do tempo": "em uma velocidade assustadora",
        "aconteceu uma situação": "ocorreu uma reviravolta chocante",
        "muitas pessoas acreditam": "quase todo mundo foi enganado por",
        "vamos analisar": "você está prestes a descobrir",
        "como todos sabem": "o que pouquíssimos realmente sabem",
        "é importante dizer": "o detalhe mais perturbador é que",
        "talvez seja possível": "a evidência aponta para algo estarrecedor"
    }

    @classmethod
    def audit_script_vocabulary(cls, plan: ProjectPlan) -> Dict[str, Any]:
        issues: List[VocabularyAuditIssue] = []

        for scene in plan.scenes:
            text = (scene.narration_text or "").lower()
            for weak, strong in cls.REPLACEMENTS.items():
                if weak in text:
                    issues.append(VocabularyAuditIssue(
                        scene_order=scene.order,
                        weak_phrase=weak,
                        suggested_replacement=strong,
                        impact_gain_pct=28,
                        justification=f"Substitui linguagem passiva monótona por gancho ativo de alta curiosidade."
                    ))

        neuro_score = max(50, 100 - (len(issues) * 12))

        return {
            "project_id": plan.project_id,
            "neuro_linguistic_score": neuro_score,
            "total_weak_phrases_found": len(issues),
            "script_grade": "A+" if len(issues) == 0 else ("B+" if len(issues) <= 2 else "C"),
            "issues": [i.__dict__ for i in issues]
        }

    @classmethod
    def auto_enhance_script_vocabulary(cls, plan: ProjectPlan) -> Dict[str, Any]:
        enhanced_count = 0

        for scene in plan.scenes:
            if not scene.narration_text:
                continue
            original = scene.narration_text
            modified = original
            for weak, strong in cls.REPLACEMENTS.items():
                pattern = re.compile(re.escape(weak), re.IGNORECASE)
                if pattern.search(modified):
                    modified = pattern.sub(strong, modified)
                    enhanced_count += 1
            scene.narration_text = modified

        return {
            "project_id": plan.project_id,
            "total_phrases_enhanced": enhanced_count,
            "status": "Roteiro polido com vocabulário de alta retenção neuro-linguística."
        }
