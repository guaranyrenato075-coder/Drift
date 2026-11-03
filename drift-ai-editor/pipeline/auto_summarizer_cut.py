"""
1-Click TL;DR Summary Reel Generator for CutWire Drift AI.
Condenses long-form multi-scene productions into a punchy 60-90s executive summary reel,
extracting the opening hook, primary turning point, and core thesis resolution.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class SummaryReelPlan:
    original_duration: float
    summary_duration: float
    compression_ratio_pct: float
    selected_scene_orders: List[int]
    summary_scenes: List[Scene]

class AutoSummarizerCut:
    """
    Distills long videos into compact social teaser cuts.
    """

    @classmethod
    def condense_project(cls, plan: ProjectPlan, target_max_duration: float = 75.0) -> SummaryReelPlan:
        if not plan.scenes:
            return SummaryReelPlan(0.0, 0.0, 100.0, [], [])

        orig_dur = plan.total_duration()
        if orig_dur <= target_max_duration:
            # Already short enough
            return SummaryReelPlan(
                original_duration=orig_dur,
                summary_duration=orig_dur,
                compression_ratio_pct=100.0,
                selected_scene_orders=[s.order for s in plan.scenes],
                summary_scenes=list(plan.scenes)
            )

        # Strategic selection: Hook (scene 1), Turning Point (middle scene), Resolution (final scene)
        n = len(plan.scenes)
        hook_scene = plan.scenes[0]
        mid_scene = plan.scenes[n // 2]
        final_scene = plan.scenes[-1]

        chosen = [hook_scene, mid_scene, final_scene]
        # If still under target, add second scene for momentum
        if n > 3 and sum(s.duration for s in chosen) + plan.scenes[1].duration <= target_max_duration:
            chosen.insert(1, plan.scenes[1])

        summary_dur = sum(s.duration for s in chosen)
        ratio = (summary_dur / max(0.1, orig_dur)) * 100.0

        return SummaryReelPlan(
            original_duration=round(orig_dur, 2),
            summary_duration=round(summary_dur, 2),
            compression_ratio_pct=round(ratio, 1),
            selected_scene_orders=[s.order for s in chosen],
            summary_scenes=chosen
        )

