"""
Automated B-Roll Cutaway Bouncer for CutWire Drift AI.
Detects static scenes longer than a threshold (default 4.5s) and schedules dynamic cutaways
using alternative media candidates at 2.5s - 3.5s into the shot to prevent visual fatigue.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from models.scene_plan import ProjectPlan, Scene, MediaCandidate

@dataclass
class BrollCutaway:
    scene_order: int
    main_media_platform: str
    cutaway_media_platform: str
    cutaway_start_sec: float
    cutaway_duration_sec: float
    cutaway_candidate_id: str

class BrollBouncer:
    """
    Injects dynamic cutaways into long shots to enhance retention.
    """

    DEFAULT_THRESHOLD_SEC = 4.5
    DEFAULT_CUTAWAY_OFFSET_SEC = 2.5

    @classmethod
    def analyze_plan_cutaways(cls, plan: ProjectPlan, threshold_sec: float = DEFAULT_THRESHOLD_SEC) -> List[BrollCutaway]:
        cutaways: List[BrollCutaway] = []
        for s in plan.scenes:
            dur = max(s.duration or 3.0, 1.0)
            if dur >= threshold_sec and s.candidates and len(s.candidates) > 1 and s.selected_media:
                # Find an alternative candidate different from selected_media
                alt = None
                for c in s.candidates:
                    is_diff = False
                    if c.candidate_id and s.selected_media.candidate_id:
                        is_diff = (c.candidate_id != s.selected_media.candidate_id)
                    elif c.external_id and s.selected_media.external_id:
                        is_diff = (c.external_id != s.selected_media.external_id)
                    else:
                        is_diff = (c != s.selected_media)
                    if is_diff:
                        alt = c
                        break
                if alt:
                    cut_dur = round(min(3.0, dur - cls.DEFAULT_CUTAWAY_OFFSET_SEC), 2)
                    if cut_dur >= 1.0:
                        cutaways.append(BrollCutaway(
                            scene_order=s.order,
                            main_media_platform=s.selected_media.platform,
                            cutaway_media_platform=alt.platform,
                            cutaway_start_sec=cls.DEFAULT_CUTAWAY_OFFSET_SEC,
                            cutaway_duration_sec=cut_dur,
                            cutaway_candidate_id=alt.candidate_id or alt.external_id
                        ))
        return cutaways

    @classmethod
    def apply_cutaways_to_plan(cls, plan: ProjectPlan, threshold_sec: float = DEFAULT_THRESHOLD_SEC) -> Dict[str, Any]:
        cutaways = cls.analyze_plan_cutaways(plan, threshold_sec=threshold_sec)
        # Store cutaways manifest inside plan extra config for timeline builder
        plan.config.extra = plan.config.extra or {}
        plan.config.extra["broll_cutaways"] = [
            {
                "scene_order": c.scene_order,
                "main_platform": c.main_media_platform,
                "broll_platform": c.cutaway_media_platform,
                "start_sec": c.cutaway_start_sec,
                "duration_sec": c.cutaway_duration_sec,
                "candidate_id": c.cutaway_candidate_id
            }
            for c in cutaways
        ]

        return {
            "project_id": plan.project_id,
            "total_scenes": len(plan.scenes),
            "cutaways_injected": len(cutaways),
            "retention_boost_estimate_pct": min(25, len(cutaways) * 5),
            "cutaways": [c.__dict__ for c in cutaways]
        }
