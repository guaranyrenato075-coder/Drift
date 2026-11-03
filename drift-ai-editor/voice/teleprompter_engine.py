"""
Intelligent Voice-Paced Teleprompter Engine for CutWire Drift AI.
Maps real-time narration speech cadence to script lines, tracks words per minute (WPM),
and calculates smooth vertical scroll offsets to guide live microphone recordings.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class TeleprompterCue:
    line_number: int
    text: str
    target_start_sec: float
    target_end_sec: float
    cumulative_words: int
    scroll_position_pct: float  # 0.0 to 100.0%

@dataclass
class TeleprompterSession:
    total_words: int
    estimated_duration_sec: float
    wpm_speed: float
    cues: List[TeleprompterCue]

class TeleprompterEngine:
    """
    Coordinates speech-following scroll velocities for voiceover recording.
    """

    DEFAULT_WPM = 145.0  # Professional broadcasting reading speed

    @classmethod
    def prepare_session(cls, script_text: str, target_wpm: float = 145.0) -> TeleprompterSession:
        paragraphs = [p.strip() for p in script_text.splitlines() if p.strip()]
        if not paragraphs:
            return TeleprompterSession(0, 0.0, target_wpm, [])

        total_words = sum(len(p.split()) for p in paragraphs)
        total_duration = (total_words / target_wpm) * 60.0

        cues: List[TeleprompterCue] = []
        accum_words = 0
        current_time = 0.0

        for idx, p in enumerate(paragraphs):
            w_count = len(p.split())
            line_dur = (w_count / target_wpm) * 60.0
            accum_words += w_count
            scroll_pct = (accum_words / total_words) * 100.0 if total_words > 0 else 0.0

            cues.append(
                TeleprompterCue(
                    line_number=idx + 1,
                    text=p,
                    target_start_sec=round(current_time, 2),
                    target_end_sec=round(current_time + line_dur, 2),
                    cumulative_words=accum_words,
                    scroll_position_pct=round(scroll_pct, 1)
                )
            )
            current_time += line_dur

        return TeleprompterSession(
            total_words=total_words,
            estimated_duration_sec=round(total_duration, 2),
            wpm_speed=target_wpm,
            cues=cues
        )

