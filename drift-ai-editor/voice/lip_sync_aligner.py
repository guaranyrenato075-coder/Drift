"""
Lip Sync & Multilingual Dubbing Aligner for CutWire Drift AI.
Computes time-stretching factors, phoneme/viseme timing maps,
and audio rate adjustments so dubbed voice tracks align with source video cuts.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

@dataclass
class DubbingCue:
    cue_id: str
    original_start: float
    original_end: float
    dubbed_duration: float
    required_stretch_factor: float  # < 1.0 = speed up, > 1.0 = slow down
    is_within_tolerances: bool
    ffmpeg_tempo_filter: str

@dataclass
class VisemeKeyframe:
    timestamp: float
    viseme: str  # e.g., 'A', 'E', 'O', 'M', 'rest'
    intensity: float  # 0.0 to 1.0

class LipSyncAligner:
    """
    Coordinates dubbing duration matching and viseme shape generation.
    """

    MIN_STRETCH = 0.75  # Max 33% speedup without sounding comical
    MAX_STRETCH = 1.30  # Max 30% slowdown without sluggishness

    @classmethod
    def calculate_dub_alignment(
        cls,
        cue_id: str,
        original_start: float,
        original_end: float,
        dubbed_natural_duration: float
    ) -> DubbingCue:
        target_duration = max(0.1, original_end - original_start)
        ratio = target_duration / max(0.1, dubbed_natural_duration)

        # In FFmpeg, atempo > 1 speeds up, atempo < 1 slows down
        # If dubbed audio is 4s and target is 3s, tempo = 4.0 / 3.0 = 1.333
        tempo = dubbed_natural_duration / target_duration
        is_safe = (cls.MIN_STRETCH <= (1.0 / tempo) <= cls.MAX_STRETCH) if tempo > 0 else False

        tempo_clamped = max(0.5, min(2.0, tempo))
        tempo_filter = f"atempo={tempo_clamped:.3f}"

        return DubbingCue(
            cue_id=cue_id,
            original_start=original_start,
            original_end=original_end,
            dubbed_duration=dubbed_natural_duration,
            required_stretch_factor=ratio,
            is_within_tolerances=is_safe,
            ffmpeg_tempo_filter=tempo_filter
        )

    @classmethod
    def generate_viseme_track(cls, phoneme_sequence: List[Tuple[float, str]]) -> List[VisemeKeyframe]:
        """
        Maps phonemes (e.g., IPA or ARPAbet) to basic visual mouth shapes.
        """
        mapping = {
            "AA": "O", "AO": "O", "OW": "O", "UW": "O",
            "EH": "E", "IY": "E", "EY": "E", "IH": "E",
            "B": "M", "P": "M", "M": "M",
            "F": "F", "V": "F",
            "T": "D", "D": "D", "S": "D", "Z": "D",
            "SIL": "rest", "SP": "rest"
        }
        keyframes: List[VisemeKeyframe] = []
        for t, ph in phoneme_sequence:
            vis = mapping.get(ph.upper(), "A")
            intensity = 0.0 if vis == "rest" else 0.85
            keyframes.append(VisemeKeyframe(timestamp=round(t, 3), viseme=vis, intensity=intensity))
        return keyframes

