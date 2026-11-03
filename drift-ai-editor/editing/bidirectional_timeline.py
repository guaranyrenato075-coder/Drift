import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene

@dataclass
class TextTimelineAnchor:
    scene_order: int
    char_start: int
    char_end: int
    text_snippet: str
    timeline_in_us: int
    timeline_out_us: int
    duration_sec: float

@dataclass
class SyncState:
    current_char_offset: int
    active_scene_order: int
    playhead_time_us: int
    anchors: List[TextTimelineAnchor] = field(default_factory=list)

class BidirectionalTimelineSync:
    """
    Bidirectional Script-to-Timeline Sync Engine:
    Maps text character offsets directly to timeline microsecond positions and vice-versa.
    Enables:
      1. Seeking timeline playhead instantly when clicking on a script word.
      2. Cutting or trimming script text to immediately crop the timeline clip.
      3. Highlighting script text in real-time as the video playhead moves.
    """

    @classmethod
    def index_script(cls, plan: ProjectPlan) -> List[TextTimelineAnchor]:
        anchors: List[TextTimelineAnchor] = []
        cur_char = 0
        cur_us = 0

        for scene in plan.scenes:
            dur_us = int((scene.duration or 4.0) * 1_000_000)
            text_len = len(scene.narration_text)
            anchor = TextTimelineAnchor(
                scene_order=scene.order,
                char_start=cur_char,
                char_end=cur_char + text_len,
                text_snippet=scene.narration_text,
                timeline_in_us=cur_us,
                timeline_out_us=cur_us + dur_us,
                duration_sec=scene.duration or 4.0
            )
            anchors.append(anchor)
            cur_char += text_len + 2 # account for separator
            cur_us += dur_us

        return anchors

    @classmethod
    def text_offset_to_timeline_us(cls, anchors: List[TextTimelineAnchor], char_pos: int) -> int:
        """Finds timeline microsecond timestamp corresponding to a character position in script."""
        for a in anchors:
            if a.char_start <= char_pos <= a.char_end:
                fraction = (char_pos - a.char_start) / max(1, a.char_end - a.char_start)
                delta = int((a.timeline_out_us - a.timeline_in_us) * fraction)
                return a.timeline_in_us + delta
        if anchors and char_pos > anchors[-1].char_end:
            return anchors[-1].timeline_out_us
        return 0

    @classmethod
    def timeline_us_to_text_offset(cls, anchors: List[TextTimelineAnchor], time_us: int) -> Tuple[int, Optional[TextTimelineAnchor]]:
        """Finds text character position and scene corresponding to a timeline playhead position."""
        for a in anchors:
            if a.timeline_in_us <= time_us <= a.timeline_out_us:
                dur = max(1, a.timeline_out_us - a.timeline_in_us)
                fraction = (time_us - a.timeline_in_us) / dur
                char_delta = int((a.char_end - a.char_start) * fraction)
                return a.char_start + char_delta, a
        return 0, anchors[0] if anchors else None

    @classmethod
    def delete_text_range(cls, plan: ProjectPlan, scene_order: int, remove_text: str) -> bool:
        """Removes a phrase from a scene's narration, adjusting its duration proportionally."""
        for s in plan.scenes:
            if s.order == scene_order:
                if remove_text in s.narration_text:
                    orig_len = len(s.narration_text) or 1
                    s.narration_text = s.narration_text.replace(remove_text, "").strip()
                    ratio = len(s.narration_text) / orig_len
                    s.duration = max(1.0, round((s.duration or 4.0) * ratio, 2))
                    s.audio_path = None # Invalidate voice for re-synthesis
                    return True
        return False

