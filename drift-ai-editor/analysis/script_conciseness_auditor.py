"""
Script Conciseness Auditor for CutWire Drift AI.
Detects verbal filler words, padding phrases, and bloated sentence structures in narration scripts,
recommending pruned, high-impact edits and estimating time saved.
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

FILLER_PATTERNS = [
    # Portuguese fillers
    r"\btipo assim\b", r"\bna verdade\b", r"\bbasicamente\b", r"\bcomo você sabe\b",
    r"\bé importante notar que\b", r"\bé interessante observar que\b", r"\bvale ressaltar que\b",
    r"\bsem dúvida nenhuma\b", r"\bde uma certa forma\b", r"\bpor assim dizer\b",
    # English fillers
    r"\bliterally\b", r"\bbasically\b", r"\bactually\b", r"\bas you know\b",
    r"\bit goes without saying that\b", r"\bit is important to note that\b", r"\bat the end of the day\b",
]

@dataclass
class ConcisenessAlert:
    scene_order: int
    filler_match: str
    context_snippet: str
    suggestion: str

@dataclass
class ConcisenessReport:
    total_words_original: int
    total_fillers_detected: int
    conciseness_score: float       # 0.0 - 100.0 (100 = perfectly concise)
    estimated_seconds_saved: float
    pruned_script_preview: str
    alerts: List[ConcisenessAlert] = field(default_factory=list)

class ScriptConcisenessAuditor:
    """
    Audits narration text for maximum punchiness and retention.
    """

    @classmethod
    def audit_scene_text(cls, text: str, scene_order: int = 1) -> List[ConcisenessAlert]:
        alerts = []
        for pat in FILLER_PATTERNS:
            for match in re.finditer(pat, text, re.IGNORECASE):
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                snippet = "..." + text[start:end] + "..."
                alerts.append(ConcisenessAlert(
                    scene_order=scene_order,
                    filler_match=match.group(0),
                    context_snippet=snippet,
                    suggestion=f"Remover '{match.group(0)}' para aumentar dinamismo e retenção."
                ))
        return alerts

    @classmethod
    def audit_project(cls, plan: ProjectPlan) -> ConcisenessReport:
        total_words = 0
        total_fillers = 0
        alerts: List[ConcisenessAlert] = []
        pruned_paragraphs: List[str] = []

        for sc in plan.scenes:
            words = sc.narration_text.split()
            total_words += len(words)
            sc_alerts = cls.audit_scene_text(sc.narration_text, sc.order)
            alerts.extend(sc_alerts)
            total_fillers += len(sc_alerts)

            # Prune text
            pruned = sc.narration_text
            for pat in FILLER_PATTERNS:
                pruned = re.sub(pat, "", pruned, flags=re.IGNORECASE)
            # Normalize spaces
            pruned = re.sub(r"\s+", " ", pruned).strip()
            pruned_paragraphs.append(pruned)

        # Average speaking speed: ~2.5 words per second
        # Each filler averages ~2 words -> ~0.8s
        seconds_saved = total_fillers * 0.8

        if total_words > 0:
            penalty = (total_fillers / total_words) * 350.0
            score = max(20.0, min(100.0, 100.0 - penalty))
        else:
            score = 100.0

        return ConcisenessReport(
            total_words_original=total_words,
            total_fillers_detected=total_fillers,
            conciseness_score=round(score, 1),
            estimated_seconds_saved=round(seconds_saved, 1),
            pruned_script_preview=" ".join(pruned_paragraphs),
            alerts=alerts
        )

