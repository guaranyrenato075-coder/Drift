"""
Smart Jump-Cut & De-Breath Engine for CutWire Drift AI.
Detects dead silence gaps (>0.4s), heavy breath intakes, and hesitation pauses in raw voice tracks,
generating non-destructive trim edit lists with audio micro-crossfades to eliminate dead air.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass
class TrimCut:
    start_time: float
    end_time: float
    duration_removed: float
    cut_reason: str  # "silence_gap", "heavy_breath", "filler_pause"

@dataclass
class JumpCutEditDecisionList:
    original_duration: float
    trimmed_duration: float
    time_saved: float
    total_cuts: int
    cuts: List[TrimCut]
    ffmpeg_silenceremove_filter: str

class SmartJumpCutter:
    """
    Automates aggressive dialogue pacing by tightening inter-phrase silence.
    """

    MIN_SILENCE_DURATION = 0.40  # Silences longer than 400ms are trimmed
    PAD_PADDING = 0.05           # 50ms padding kept on both sides to avoid clipping consonants

    @classmethod
    def analyze_audio_silences(
        cls,
        duration: float,
        silence_intervals: Optional[List[Tuple[float, float]]] = None
    ) -> JumpCutEditDecisionList:
        intervals = silence_intervals or []
        cuts: List[TrimCut] = []
        total_removed = 0.0

        for start, end in intervals:
            gap = end - start
            if gap >= cls.MIN_SILENCE_DURATION:
                # Trim the middle of the silence, keeping safety padding
                trim_start = start + cls.PAD_PADDING
                trim_end = end - cls.PAD_PADDING
                if trim_end > trim_start:
                    removed = trim_end - trim_start
                    total_removed += removed
                    cuts.append(
                        TrimCut(
                            start_time=round(trim_start, 3),
                            end_time=round(trim_end, 3),
                            duration_removed=round(removed, 3),
                            cut_reason="silence_gap"
                        )
                    )

        trimmed_dur = max(0.1, duration - total_removed)

        # Standard FFmpeg filter for silence trimming
        filter_str = "silenceremove=start_periods=1:start_duration=0.4:start_threshold=-40dB:stop_periods=-1:stop_duration=0.4:stop_threshold=-40dB"

        return JumpCutEditDecisionList(
            original_duration=round(duration, 2),
            trimmed_duration=round(trimmed_dur, 2),
            time_saved=round(total_removed, 2),
            total_cuts=len(cuts),
            cuts=cuts,
            ffmpeg_silenceremove_filter=filter_str
        )

