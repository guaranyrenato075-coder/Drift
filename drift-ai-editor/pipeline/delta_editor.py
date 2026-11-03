from typing import List, Dict, Any, Tuple, Optional
from models.scene_plan import ProjectPlan, Scene
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner

class DeltaReeditor:
    """
    Intelligent incremental re-editor:
    Detects exact textual changes between old and updated scripts.
    Preserves all untouched scenes, their approved voice files, and cached media,
    regenerating only the modified scenes and shifting subsequent timeline timestamps.
    """

    @classmethod
    def apply_script_update(cls, plan: ProjectPlan, updated_raw_script: str) -> Tuple[List[int], List[int], List[int]]:
        """
        Parses updated script and performs semantic diff against existing plan.scenes.
        Returns:
          - modified_orders: Scene numbers where text changed (needs voice regeneration).
          - added_orders: New scenes appended or inserted.
          - deleted_orders: Scenes removed.
        """
        new_scenes = ScriptSegmenter.parse(
            updated_raw_script,
            default_language=plan.config.language,
            default_voice=plan.config.voice_id
        )
        VisualPlanner.plan_project(new_scenes)

        old_scenes_by_order: Dict[int, Scene] = {s.order: s for s in plan.scenes}
        new_scenes_by_order: Dict[int, Scene] = {s.order: s for s in new_scenes}

        modified_orders: List[int] = []
        added_orders: List[int] = []
        deleted_orders: List[int] = []

        final_scenes: List[Scene] = []

        for new_s in new_scenes:
            old_s = old_scenes_by_order.get(new_s.order)
            if not old_s:
                # Newly added scene
                added_orders.append(new_s.order)
                final_scenes.append(new_s)
            else:
                # Compare narration text
                clean_old = old_s.narration_text.strip().lower()
                clean_new = new_s.narration_text.strip().lower()
                if clean_old != clean_new:
                    # Text changed: preserve visual media if possible, but invalidate audio
                    old_s.narration_text = new_s.narration_text
                    old_s.visual_description = new_s.visual_description
                    old_s.audio_path = None  # Invalidate voice
                    old_s.audio_duration = 0.0
                    modified_orders.append(old_s.order)
                    final_scenes.append(old_s)
                else:
                    # Untouched scene: keep 100% of existing audio and media!
                    final_scenes.append(old_s)

        for old_order in old_scenes_by_order:
            if old_order not in new_scenes_by_order:
                deleted_orders.append(old_order)

        plan.scenes = final_scenes
        plan.raw_script = updated_raw_script
        plan.reindex_scenes()

        # Recalculate timeline positions
        cur_time = 0.0
        for s in plan.scenes:
            s.start_time = round(cur_time, 2)
            s.end_time = round(cur_time + (s.duration or 4.0), 2)
            cur_time = s.end_time

        return modified_orders, added_orders, deleted_orders

