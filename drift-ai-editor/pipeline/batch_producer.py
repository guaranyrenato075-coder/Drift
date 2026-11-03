import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, ProjectConfig
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from analysis.storyboard_engine import StoryboardEngine
from pipeline.style_engine import StyleEngine, StyleProfile
from pipeline.timeline_planner import TimelinePlanner, AssemblyPlan
from storage.repository import ProjectRepository

@dataclass
class SeriesEpisodeInput:
    title: str
    script_text: str
    episode_number: int
    custom_voice_id: Optional[str] = None

@dataclass
class SeriesBatchResult:
    series_name: str
    total_episodes: int
    completed_episodes: int
    project_ids: List[str] = field(default_factory=list)
    assembly_plans: List[AssemblyPlan] = field(default_factory=list)
    summary: str = ""

class BatchProductionEngine:
    """
    Orchestrates end-to-end multi-episode video series production:
    Processes batch lists of scripts under a unified channel identity,
    reuses cached visual elements across episodes, tracks independent
    timelines, captions, and export deliverables.
    """

    def __init__(self, repo: Optional[ProjectRepository] = None):
        self.repo = repo or ProjectRepository()

    def process_series(
        self,
        series_name: str,
        episodes: List[SeriesEpisodeInput],
        style_id: str = "filosofico",
        aspect_ratio: str = "16:9"
    ) -> SeriesBatchResult:
        profile = StyleEngine.get_profile(style_id)
        project_ids: List[str] = []
        plans_list: List[AssemblyPlan] = []

        for ep in episodes:
            config = ProjectConfig(
                aspect_ratio=aspect_ratio,
                voice_id=ep.custom_voice_id or "default",
                language="pt"
            )
            config.update_resolution()

            project_title = f"{series_name} - Ep {ep.episode_number:02d}: {ep.title}"
            plan = ProjectPlan(
                title=project_title,
                raw_script=ep.script_text,
                config=config
            )

            # 1. Parse & Plan Scenes
            scenes = ScriptSegmenter.parse(ep.script_text, default_language="pt", default_voice=config.voice_id)
            VisualPlanner.plan_project(scenes)
            plan.scenes = scenes
            plan.reindex_scenes()

            # 2. Apply Storyboard & Visual Intents
            StoryboardEngine.apply_storyboard(plan.scenes)

            # 3. Create Pre-flight Assembly Plan
            assembly = TimelinePlanner.create_assembly_plan(plan, profile)
            plans_list.append(assembly)

            # 4. Save to Repository
            self.repo.save(plan)
            project_ids.append(plan.project_id)

        summary = (
            f"Série '{series_name}' configurada com sucesso: "
            f"{len(episodes)} episódios planejados e indexados sob o perfil '{profile.name}'."
        )

        return SeriesBatchResult(
            series_name=series_name,
            total_episodes=len(episodes),
            completed_episodes=len(episodes),
            project_ids=project_ids,
            assembly_plans=plans_list,
            summary=summary
        )

