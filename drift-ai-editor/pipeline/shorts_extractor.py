"""
Automated Content Repurposer & Viral Shorts Extractor for CutWire Drift AI.
Identifies peak curiosity, high-energy hooks, and climactic segments in long-form projects,
generating autonomous 9:16 vertical short projects (30-55s) ready for YouTube Shorts, Reels, and TikTok.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import copy
import re
from models.scene_plan import ProjectPlan, Scene, ProjectConfig

@dataclass
class ExtractedShortSummary:
    short_index: int
    title: str
    start_scene_order: int
    end_scene_order: int
    total_duration_sec: float
    viral_hook_score: int  # 0 to 100
    target_aspect_ratio: str  # "9:16"
    recommended_hashtag: str

class ContentRepurposerShortsExtractor:
    """
    Scans long projects and carves out high-retention vertical short cuts.
    """

    HOOK_WORDS = {"segredo", "mistério", "nunca", "verdade", "choque", "incrível", "atenção", "urgente", "perigo", "descobriu"}

    @classmethod
    def _score_segment(cls, scenes: List[Scene]) -> int:
        score = 60
        combined_text = " ".join(s.narration_text for s in scenes).lower()
        matched_hooks = len(set(re.findall(r'\b\w+\b', combined_text)).intersection(cls.HOOK_WORDS))
        score += min(30, matched_hooks * 8)
        total_dur = sum(s.duration or 3.0 for s in scenes)
        if 30.0 <= total_dur <= 50.0:
            score += 10
        return min(100, score)

    @classmethod
    def extract_viral_shorts(
        cls,
        plan: ProjectPlan,
        max_shorts: int = 3,
        target_min_sec: float = 25.0,
        target_max_sec: float = 55.0
    ) -> List[Dict[str, Any]]:
        """
        Extracts up to max_shorts optimized short cuts from the base plan.
        """
        if not plan.scenes:
            return []

        candidates = []
        n = len(plan.scenes)

        for i in range(n):
            current_scenes = []
            dur = 0.0
            for j in range(i, n):
                s = plan.scenes[j]
                current_scenes.append(s)
                dur += s.duration or 3.0
                if dur >= target_min_sec:
                    if dur <= target_max_sec:
                        score = cls._score_segment(current_scenes)
                        candidates.append((i, j, dur, score, current_scenes))
                    break

        # Sort candidates by viral hook score descending
        candidates.sort(key=lambda x: x[3], reverse=True)

        selected = []
        used_indices = set()

        for start_idx, end_idx, dur, score, scenes in candidates:
            # Check overlap
            scene_range = set(range(start_idx, end_idx + 1))
            if not scene_range.intersection(used_indices):
                selected.append((start_idx, end_idx, dur, score, scenes))
                used_indices.update(scene_range)
                if len(selected) >= max_shorts:
                    break

        # If none met strict criteria, fallback to the first sequence of scenes
        if not selected and len(plan.scenes) >= 1:
            dur = sum(s.duration or 3.0 for s in plan.scenes[:3])
            selected.append((0, min(2, len(plan.scenes) - 1), dur, 75, plan.scenes[:3]))

        output_shorts = []
        for idx, (s_idx, e_idx, dur, score, scenes) in enumerate(selected, start=1):
            short_cfg = copy.deepcopy(plan.config)
            short_cfg.aspect_ratio = "9:16"
            short_cfg.update_resolution()

            short_scenes = []
            for order, s in enumerate(scenes, start=1):
                new_s = copy.deepcopy(s)
                new_s.order = order
                short_scenes.append(new_s)

            short_title = f"{plan.title} [Short #{idx}]"
            short_plan = ProjectPlan(
                title=short_title,
                config=short_cfg,
                scenes=short_scenes
            )

            output_shorts.append({
                "short_index": idx,
                "title": short_title,
                "start_scene_order": plan.scenes[s_idx].order,
                "end_scene_order": plan.scenes[e_idx].order,
                "total_duration_sec": round(dur, 2),
                "viral_hook_score": score,
                "target_aspect_ratio": "9:16",
                "recommended_hashtags": "#Shorts #Viral #Documentario #Curiosidades",
                "plan_dict": short_plan.to_dict()
            })

        return output_shorts
