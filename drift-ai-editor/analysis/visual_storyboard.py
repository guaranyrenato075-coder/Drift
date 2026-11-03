from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene, MediaCandidate

@dataclass
class StoryboardCard:
    scene_order: int
    scene_id: str
    narration_snippet: str
    duration_sec: float
    shot_type: str
    emotional_tone: str
    primary_thumbnail_url: str
    primary_media_title: str
    primary_platform: str
    alternative_candidates: List[Dict[str, str]] = field(default_factory=list)
    transition_type: str = "crossfade"
    is_user_locked: bool = False

@dataclass
class StoryboardDeck:
    project_id: str
    project_title: str
    total_duration_sec: float
    cards_count: int
    cards: List[StoryboardCard] = field(default_factory=list)

class VisualStoryboardBuilder:
    """
    Constructs an interactive visual storyboard card-deck of the production:
    Presents each scene as a rich card with preview thumbnail, narration, duration,
    and alternative candidate carousel before committing changes to Drift's timeline.
    Allows visual drag-and-drop reordering, thumbnail swapping, and timing adjustments.
    """

    @classmethod
    def build_deck(cls, plan: ProjectPlan) -> StoryboardDeck:
        cards: List[StoryboardCard] = []
        total_sec = 0.0

        for scene in plan.scenes:
            dur = scene.duration or 4.0
            total_sec += dur

            thumb = ""
            m_title = "Nenhuma mídia"
            plat = "none"

            if scene.selected_media:
                thumb = scene.selected_media.preview_url or scene.selected_media.download_url
                m_title = scene.selected_media.title
                plat = scene.selected_media.platform

            alternatives = []
            for c in scene.candidates:
                if not scene.selected_media or c.candidate_id != scene.selected_media.candidate_id:
                    alternatives.append({
                        "candidate_id": c.candidate_id,
                        "title": c.title,
                        "thumbnail_url": c.preview_url or c.download_url,
                        "platform": c.platform,
                        "creator": c.creator
                    })

            cards.append(
                StoryboardCard(
                    scene_order=scene.order,
                    scene_id=scene.id,
                    narration_snippet=scene.narration_text[:60] + ("..." if len(scene.narration_text) > 60 else ""),
                    duration_sec=round(dur, 2),
                    shot_type="Plano Médio",
                    emotional_tone="Reflexivo",
                    primary_thumbnail_url=thumb,
                    primary_media_title=m_title,
                    primary_platform=plat,
                    alternative_candidates=alternatives[:3],
                    transition_type="crossfade"
                )
            )

        return StoryboardDeck(
            project_id=plan.project_id,
            project_title=plan.title,
            total_duration_sec=round(total_sec, 2),
            cards_count=len(cards),
            cards=cards
        )

    @classmethod
    def reorder_deck(cls, plan: ProjectPlan, new_order_list: List[int]) -> None:
        """
        Reorganizes scenes according to user's visual storyboard drag-and-drop order.
        new_order_list is a list of existing scene order numbers, e.g. [2, 1, 3].
        """
        order_map = {s.order: s for s in plan.scenes}
        reordered: List[Scene] = []
        for o in new_order_list:
            if o in order_map:
                reordered.append(order_map[o])

        # Append any scenes that were not in the reorder list
        for s in plan.scenes:
            if s not in reordered:
                reordered.append(s)

        plan.scenes = reordered
        plan.reindex_scenes()

