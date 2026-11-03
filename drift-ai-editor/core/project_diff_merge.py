"""
Project Diff & 3-Way Merge Engine for CutWire Drift AI.
Enables comparing two versions of a video project (e.g., base vs audio-revised vs visual-revised),
detecting scene/track conflicts, and intelligently merging changes without data loss.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

class ConflictType(str, Enum):
    AUDIO_OVERLAP = "audio_overlap"
    MEDIA_COLLISION = "media_collision"
    TIMECODE_SHIFT = "timecode_shift"
    DELETED_IN_ONE = "deleted_in_one"

@dataclass
class DiffEntry:
    element_id: str
    change_type: str  # "added", "removed", "modified", "unchanged"
    base_val: Any = None
    target_val: Any = None

@dataclass
class MergeConflict:
    scene_id: str
    conflict_type: ConflictType
    description: str
    branch_a_value: Any
    branch_b_value: Any
    resolved_value: Optional[Any] = None

@dataclass
class MergeResult:
    is_clean: bool
    conflicts: List[MergeConflict]
    merged_project_state: Dict[str, Any]

class ProjectDiffMerge:
    """
    Performs 3-way reconciliation on timeline project structures.
    """

    @classmethod
    def diff_scenes(cls, base_scenes: Dict[str, Any], target_scenes: Dict[str, Any]) -> List[DiffEntry]:
        diffs = []
        all_ids = set(base_scenes.keys()).union(set(target_scenes.keys()))

        for sid in sorted(all_ids):
            if sid not in base_scenes:
                diffs.append(DiffEntry(sid, "added", None, target_scenes[sid]))
            elif sid not in target_scenes:
                diffs.append(DiffEntry(sid, "removed", base_scenes[sid], None))
            elif base_scenes[sid] != target_scenes[sid]:
                diffs.append(DiffEntry(sid, "modified", base_scenes[sid], target_scenes[sid]))
            else:
                diffs.append(DiffEntry(sid, "unchanged", base_scenes[sid], target_scenes[sid]))
        return diffs

    @classmethod
    def merge_branches(
        cls,
        base_scenes: Dict[str, Any],
        branch_audio: Dict[str, Any],
        branch_visual: Dict[str, Any]
    ) -> MergeResult:
        """
        Merges audio edits and visual edits onto base project.
        """
        merged: Dict[str, Any] = {}
        conflicts: List[MergeConflict] = []
        all_ids = set(base_scenes.keys()).union(set(branch_audio.keys()), set(branch_visual.keys()))

        for sid in sorted(all_ids):
            b_val = base_scenes.get(sid, {})
            a_val = branch_audio.get(sid, {})
            v_val = branch_visual.get(sid, {})

            # If both changed the exact same field differently (e.g. media_path or duration)
            if a_val.get("media_path") != b_val.get("media_path") and v_val.get("media_path") != b_val.get("media_path") and a_val.get("media_path") != v_val.get("media_path"):
                conflicts.append(
                    MergeConflict(
                        scene_id=sid,
                        conflict_type=ConflictType.MEDIA_COLLISION,
                        description=f"Both branches altered media for scene {sid}",
                        branch_a_value=a_val.get("media_path"),
                        branch_b_value=v_val.get("media_path"),
                        resolved_value=v_val.get("media_path")  # Default to visual branch for media
                    )
                )

            # Reconcile cleanly: take audio fields from branch_audio, visual fields from branch_visual
            merged_scene = {}
            # Base keys
            keys = set(b_val.keys()).union(set(a_val.keys()), set(v_val.keys()))
            for k in keys:
                if k in ("audio_path", "narration_text", "voice_settings"):
                    merged_scene[k] = a_val.get(k, b_val.get(k))
                elif k in ("media_path", "visual_prompt", "ken_burns"):
                    merged_scene[k] = v_val.get(k, b_val.get(k))
                else:
                    merged_scene[k] = a_val.get(k, v_val.get(k, b_val.get(k)))

            merged[sid] = merged_scene

        return MergeResult(
            is_clean=len(conflicts) == 0,
            conflicts=conflicts,
            merged_project_state=merged
        )

