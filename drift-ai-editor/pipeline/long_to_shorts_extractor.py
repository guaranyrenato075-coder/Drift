"""
Long-to-Shorts Viral Hook Extractor for CutWire Drift AI.
Scans long-form productions (podcasts, masterclasses, documentary episodes),
identifies peak emotional, controversial, or revelatory segments (30-60s),
and extracts self-contained vertical (9:16) Short projects with dynamic captions.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene, ProjectConfig

@dataclass
class ViralClipCandidate:
    clip_id: str
    title: str
    start_scene_order: int
    end_scene_order: int
    start_time: float
    end_time: float
    duration: float
    virality_score: int  # 0 to 100
    hook_reason: str
    scenes: List[Scene]

class LongToShortsExtractor:
    """
    Automates content repurposing from long-form landscape video into viral vertical shorts.
    """

    VIRAL_TRIGGERS = [
        ("segredo", 25, "Reveals confidential or counterintuitive insight"),
        ("nunca", 20, "Strong definitive negative assertion"),
        ("erro", 22, "Exposes common costly mistake"),
        ("verdade", 20, "Debunks widespread myth"),
        ("dinheiro", 18, "Financial or wealth-building leverage"),
        ("perigo", 24, "Urgent safety or threat warning"),
        ("chocante", 25, "High emotional surprise factor"),
        ("futuro", 15, "Visionary trend prediction")
    ]

    @classmethod
    def extract_shorts(
        cls,
        long_plan: ProjectPlan,
        min_duration: float = 20.0,
        max_duration: float = 60.0,
        top_k: int = 3
    ) -> List[ViralClipCandidate]:
        if not long_plan.scenes or len(long_plan.scenes) < 3:
            return []

        candidates: List[ViralClipCandidate] = []
        n = len(long_plan.scenes)

        for i in range(n):
            accum_dur = 0.0
            accum_scenes = []
            virality_score = 40

            for j in range(i, n):
                s = long_plan.scenes[j]
                dur = s.duration if s.duration > 0 else 4.0
                accum_dur += dur
                accum_scenes.append(s)

                t = s.narration_text.lower()
                for trigger, weight, desc in cls.VIRAL_TRIGGERS:
                    if trigger in t:
                        virality_score += weight

                if min_duration <= accum_dur <= max_duration:
                    first_scene = accum_scenes[0]
                    last_scene = accum_scenes[-1]
                    title_preview = first_scene.narration_text[:35].strip() + "..."

                    candidates.append(
                        ViralClipCandidate(
                            clip_id=f"short_{i:02d}_{j:02d}",
                            title=f"Viral Short: {title_preview}",
                            start_scene_order=first_scene.order,
                            end_scene_order=last_scene.order,
                            start_time=round(sum(s.duration for s in long_plan.scenes[:i]), 2),
                            end_time=round(sum(s.duration for s in long_plan.scenes[:j+1]), 2),
                            duration=round(accum_dur, 2),
                            virality_score=min(99, virality_score),
                            hook_reason="High keyword resonance with narrative climax",
                            scenes=list(accum_scenes)
                        )
                    )
                    break
                elif accum_dur > max_duration:
                    break

        # Sort by virality score descending
        candidates.sort(key=lambda c: c.virality_score, reverse=True)
        return candidates[:top_k]

