from typing import List, Dict, Any, Optional
from collections import Counter
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene

@dataclass
class RepetitionAlert:
    category: str        # 'creator_repetition', 'platform_monotony', 'consecutive_color', 'concept_overuse'
    scene_orders: List[int]
    message: str
    remediation_suggestion: str

@dataclass
class VisualDiversityAudit:
    diversity_score: int             # 0 to 100
    is_sufficiently_diverse: bool
    unique_creators_count: int
    unique_platforms_count: int
    platform_distribution: Dict[str, int]
    alerts: List[RepetitionAlert] = field(default_factory=list)
    suggested_replacements: List[Dict[str, Any]] = field(default_factory=list)

class VisualDiversityController:
    """
    Visual Diversity & Anti-Fatigue Monitor:
    Audits the entire sequence of selected media candidates across all scenes to prevent
    aesthetic monotony:
      - Penalizes repeated creators and consecutive identical visual sources.
      - Calculates a global Diversity Score (0 to 100).
      - Pinpoints duplicate visual concepts and suggests diverse replacements from the candidate gallery.
    """

    @classmethod
    def audit_project_diversity(cls, plan: ProjectPlan) -> VisualDiversityAudit:
        if not plan.scenes:
            return VisualDiversityAudit(
                diversity_score=100,
                is_sufficiently_diverse=True,
                unique_creators_count=0,
                unique_platforms_count=0,
                platform_distribution={}
            )

        creators: List[str] = []
        platforms: List[str] = []
        alerts: List[RepetitionAlert] = []
        suggested_replacements: List[Dict[str, Any]] = []

        for scene in plan.scenes:
            media = scene.selected_media
            if media:
                creators.append(media.creator or "Unknown")
                platforms.append(media.platform or "generic")

        creator_counts = Counter(creators)
        platform_counts = Counter(platforms)

        # 1. Audit Creator Overuse (more than 2 appearances in short video or > 25% of all scenes)
        threshold = max(2, len(plan.scenes) // 4)
        for creator, count in creator_counts.items():
            if creator != "Unknown" and count > threshold:
                affected = [s.order for s in plan.scenes if s.selected_media and s.selected_media.creator == creator]
                alerts.append(
                    RepetitionAlert(
                        category="creator_repetition",
                        scene_orders=affected,
                        message=f"O autor '{creator}' foi selecionado {count} vezes, reduzindo a variedade estética.",
                        remediation_suggestion=f"Substitua os clipes das cenas {affected[1:]} por outros criadores."
                    )
                )

        # 2. Audit Consecutive Identical Platforms (e.g. 4 consecutive pexels or 4 consecutive pixabay)
        streak = 1
        for i in range(1, len(platforms)):
            if platforms[i] == platforms[i - 1]:
                streak += 1
                if streak >= 4:
                    affected = [plan.scenes[i - k].order for k in range(streak)]
                    alerts.append(
                        RepetitionAlert(
                            category="platform_monotony",
                            scene_orders=affected,
                            message=f"{streak} cenas consecutivas utilizam exclusivamente a plataforma '{platforms[i]}'.",
                            remediation_suggestion="Mescle com fontes abertas como Wikimedia, NASA, Coverr ou Acervo Local."
                        )
                    )
            else:
                streak = 1

        # 3. Suggest automated candidate swaps for repetitive scenes
        for alert in alerts:
            for s_order in alert.scene_orders[1:]:
                target_scene = next((s for s in plan.scenes if s.order == s_order), None)
                if target_scene and target_scene.candidates:
                    # Find alternative candidate with different creator/platform
                    alt = next(
                        (c for c in target_scene.candidates if c.creator != target_scene.selected_media.creator and c.platform != target_scene.selected_media.platform),
                        None
                    )
                    if alt:
                        suggested_replacements.append({
                            "scene_order": s_order,
                            "current_title": target_scene.selected_media.title,
                            "suggested_title": alt.title,
                            "suggested_platform": alt.platform,
                            "suggested_candidate_id": alt.candidate_id
                        })

        # Calculate Diversity Score
        penalty = (len(alerts) * 20)
        raw_score = max(0, 100 - penalty)
        is_diverse = raw_score >= 70 and len(alerts) == 0

        return VisualDiversityAudit(
            diversity_score=raw_score,
            is_sufficiently_diverse=is_diverse,
            unique_creators_count=len(creator_counts),
            unique_platforms_count=len(platform_counts),
            platform_distribution=dict(platform_counts),
            alerts=alerts,
            suggested_replacements=suggested_replacements
        )
