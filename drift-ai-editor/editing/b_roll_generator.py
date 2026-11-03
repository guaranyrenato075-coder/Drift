import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene

@dataclass
class BRollInsert:
    insert_id: str
    scene_order: int
    trigger_keyword: str
    timeline_in_sec: float
    duration_sec: float           # Typically 1.5s to 2.5s quick cutaway
    suggested_search_query: str
    track_index: int = 1          # Track V2 (overlays above base V1)
    transition_in: str = "cut"
    transition_out: str = "cut"

@dataclass
class BRollSchedule:
    project_id: str
    total_inserts: int
    inserts: List[BRollInsert] = field(default_factory=list)

class BRollDirector:
    """
    Automated B-Roll Cutaway Director:
    Scans narration for tangible concrete objects, historical artifacts, and action nouns:
      - Automatically schedules quick 1.5s - 2.0s B-roll overlays on Track V2.
      - Keeps the primary voiceover and background continuity flowing without interruption.
      - Enriches long talking-head or continuous landscape takes with illustrative detail.
    """

    CONCRETE_TRIGGERS = {
        "livro": "antique old open book pages cinematic close up",
        "mapa": "vintage ancient world map magnifying glass",
        "relógio": "ticking mechanical watch gears macro detail",
        "carta": "person writing letter quill fountain pen",
        "dinheiro": "counting paper currency money economy",
        "espada": "ancient steel sword battle artifact",
        "telescópio": "giant optical telescope night sky dome",
        "estrada": "winding mountain road aerial drone",
        "computador": "cyberpunk hacker code typing keyboard",
        "mãos": "hands working artisan craft close up"
    }

    @classmethod
    def schedule_b_roll(cls, plan: ProjectPlan) -> BRollSchedule:
        inserts: List[BRollInsert] = []
        cur_timeline_sec = 0.0

        for scene in plan.scenes:
            dur = scene.duration or 4.0
            text_lower = scene.narration_text.lower()

            # Find matching concrete triggers
            for token, query in cls.CONCRETE_TRIGGERS.items():
                if token in text_lower and dur >= 3.5:
                    # Place B-roll midway through the scene
                    insert_start = round(cur_timeline_sec + 1.2, 2)
                    insert_dur = min(2.0, round(dur - 1.4, 2))
                    if insert_dur >= 1.0:
                        inserts.append(
                            BRollInsert(
                                insert_id=f"broll_{scene.order}_{token}",
                                scene_order=scene.order,
                                trigger_keyword=token,
                                timeline_in_sec=insert_start,
                                duration_sec=insert_dur,
                                suggested_search_query=query,
                                track_index=1
                            )
                        )
                    break # At most 1 B-roll insert per scene to avoid clutter

            cur_timeline_sec += dur

        return BRollSchedule(
            project_id=plan.project_id,
            total_inserts=len(inserts),
            inserts=inserts
        )

