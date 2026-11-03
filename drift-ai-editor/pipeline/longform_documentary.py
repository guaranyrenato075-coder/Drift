from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene

@dataclass
class DocumentaryChapter:
    chapter_index: int
    title: str
    act_type: str              # 'act_1_hook_context', 'act_2_the_turning_point', 'act_3_escalation', 'act_4_climax', 'act_5_epilogue'
    start_time_sec: float
    end_time_sec: float
    scenes_count: int
    musical_theme: str         # 'calm_mystery', 'dark_revelation', 'epic_resolution'
    recap_prompt: Optional[str] = None

@dataclass
class LongformStructure:
    project_id: str
    total_chapters: int
    total_estimated_duration_min: float
    chapters: List[DocumentaryChapter] = field(default_factory=list)

class LongformDocumentaryEngine:
    """
    Longform Video-Essay & Documentary Structuring Engine:
    Designs compelling multi-chapter architectures for 20-60 minute productions:
      - Breaks long narrative arcs into balanced 5-8 minute acts.
      - Inserts chapter transition breaks and musical motif changes between acts.
      - Maintains visual continuity of central themes across dozens of scenes.
    """

    ACT_TEMPLATES = [
        ("A Origem e o Paradoxo", "act_1_hook_context", "calm_mystery"),
        ("A Ilusão Desmorona", "act_2_the_turning_point", "rising_curiosity"),
        ("O Ponto Sem Retorno", "act_3_escalation", "dark_tension"),
        ("A Grande Revelação", "act_4_climax", "epic_revelation"),
        ("O Que Fica Para a História", "act_5_epilogue", "philosophical_outro")
    ]

    @classmethod
    def structure_documentary(
        cls,
        plan: ProjectPlan,
        scenes_per_act: int = 5
    ) -> LongformStructure:
        chapters: List[DocumentaryChapter] = []
        scenes = plan.scenes
        total_scenes = len(scenes)

        if total_scenes == 0:
            return LongformStructure(project_id=plan.project_id, total_chapters=0, total_estimated_duration_min=0.0)

        chunk_size = max(2, scenes_per_act)
        act_idx = 0
        cur_time = 0.0

        for i in range(0, total_scenes, chunk_size):
            chunk = scenes[i:i + chunk_size]
            chunk_dur = sum((s.duration or 4.0) for s in chunk)
            template = cls.ACT_TEMPLATES[act_idx % len(cls.ACT_TEMPLATES)]

            ch = DocumentaryChapter(
                chapter_index=act_idx + 1,
                title=f"Capítulo {act_idx + 1}: {template[0]}",
                act_type=template[1],
                start_time_sec=round(cur_time, 2),
                end_time_sec=round(cur_time + chunk_dur, 2),
                scenes_count=len(chunk),
                musical_theme=template[2]
            )
            chapters.append(ch)
            cur_time += chunk_dur
            act_idx += 1

        total_min = round(cur_time / 60.0, 1)
        return LongformStructure(
            project_id=plan.project_id,
            total_chapters=len(chapters),
            total_estimated_duration_min=total_min,
            chapters=chapters
        )

