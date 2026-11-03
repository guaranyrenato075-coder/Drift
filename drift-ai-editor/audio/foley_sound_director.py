"""
Intelligent Foley Sound Effects Director for CutWire Drift AI.
Analyzes scene visuals and physical action descriptions (footsteps, typing, doors, papers, rain)
and schedules synchronized physical foley sound effects on dedicated audio track A4_FOLEY.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional
from models.scene_plan import ProjectPlan, Scene

class FoleyCategory(str, Enum):
    FOOTSTEPS = "footsteps"
    KEYBOARD_TYPING = "keyboard_typing"
    PAGE_TURN = "page_turn"
    DOOR_CREAK = "door_creak"
    RAIN_ON_WINDOW = "rain_on_window"
    CLOCK_TICKING = "clock_ticking"
    METALLIC_CLINK = "metallic_clink"

@dataclass
class FoleyCue:
    scene_order: int
    timestamp: float
    category: FoleyCategory
    duration: float
    volume_db: float
    trigger_keyword: str
    timeline_track: str = "A4_FOLEY"

class FoleySoundDirector:
    """
    Scans scene imagery and context to schedule organic environmental foley sounds.
    """

    ACTION_MAP = [
        (["caminhando", "passos", "andar", "walking", "steps"], FoleyCategory.FOOTSTEPS, 2.0, -18.0),
        (["computador", "teclado", "escrevendo", "typing", "code"], FoleyCategory.KEYBOARD_TYPING, 3.0, -22.0),
        (["livro", "página", "manuscrito", "papel", "reading"], FoleyCategory.PAGE_TURN, 1.2, -16.0),
        (["porta", "fechando", "abrindo", "door"], FoleyCategory.DOOR_CREAK, 1.5, -16.0),
        (["chuva", "janela", "pingos", "rain"], FoleyCategory.RAIN_ON_WINDOW, 4.0, -20.0),
        (["relógio", "tempo", "segundos", "clock", "tick"], FoleyCategory.CLOCK_TICKING, 3.5, -24.0)
    ]

    @classmethod
    def schedule_foley(cls, plan: ProjectPlan) -> List[FoleyCue]:
        cues: List[FoleyCue] = []
        current_time = 0.0

        for scene in getattr(plan, "scenes", []):
            dur = getattr(scene, "duration", 4.0)
            combined_text = f"{scene.narration_text} {scene.visual_description}".lower()

            for keywords, cat, def_dur, vol in cls.ACTION_MAP:
                matched_kw = next((kw for kw in keywords if kw in combined_text), None)
                if matched_kw:
                    cue_dur = min(dur, def_dur)
                    cues.append(
                        FoleyCue(
                            scene_order=scene.order,
                            timestamp=round(current_time + 0.3, 2),
                            category=cat,
                            duration=round(cue_dur, 2),
                            volume_db=vol,
                            trigger_keyword=matched_kw
                        )
                    )
                    break  # Maximum 1 primary physical foley per scene to avoid clutter

            current_time += dur

        return cues

