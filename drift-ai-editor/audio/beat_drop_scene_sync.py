"""
Soundtrack Beat Drop & Rhythmic Scene Synchronizer for CutWire Drift AI.
Analyzes background music tempo (BPM) and aligns scene cuts to musical downbeats
to create hypnotic, movie-trailer-grade rhythmic editing.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import Scene, ProjectPlan

@dataclass
class RhythmicCutPoint:
    scene_order: int
    original_duration: float
    quantized_duration: float
    time_shift_ms: float
    target_musical_bar: int
    bpm: float

class SoundtrackBeatDropSceneSync:
    """
    Quantizes scene durations to musical bars and beats.
    """

    GENRE_DEFAULT_BPM: Dict[str, float] = {
        "cinematic_orchestral": 90.0,
        "cosmic_ambient": 75.0,
        "lofi_chill": 85.0,
        "phonk_upbeat": 128.0,
        "documentary_warm": 80.0
    }

    @classmethod
    def calculate_beat_interval(cls, bpm: float) -> float:
        # Seconds per quarter-note beat
        return 60.0 / max(bpm, 30.0)

    @classmethod
    def quantize_scene_cut(cls, duration: float, bpm: float) -> tuple[float, float, int]:
        """
        Rounds scene duration to the nearest musical half-bar or full bar (2 or 4 beats).
        """
        beat_sec = cls.calculate_beat_interval(bpm)
        bar_sec = beat_sec * 4.0  # 4/4 time signature
        half_bar_sec = beat_sec * 2.0

        # Find closest multiple of half_bar_sec
        steps = round(duration / half_bar_sec)
        quantized = max(half_bar_sec, steps * half_bar_sec)
        shift_ms = (quantized - duration) * 1000.0
        musical_bars = max(1, round(quantized / bar_sec))

        return round(quantized, 3), round(shift_ms, 1), musical_bars

    @classmethod
    def synchronize_timeline_to_bpm(cls, plan: ProjectPlan, bpm: float = 90.0) -> Dict[str, Any]:
        cuts: List[RhythmicCutPoint] = []
        total_time = 0.0

        for scene in plan.scenes:
            orig_dur = scene.duration or 3.5
            quantized_dur, shift_ms, bars = cls.quantize_scene_cut(orig_dur, bpm)
            scene.duration = quantized_dur

            cuts.append(RhythmicCutPoint(
                scene_order=scene.order,
                original_duration=orig_dur,
                quantized_duration=quantized_dur,
                time_shift_ms=shift_ms,
                target_musical_bar=bars,
                bpm=bpm
            ))
            total_time += quantized_dur

        return {
            "project_id": plan.project_id,
            "tempo_bpm": bpm,
            "beat_duration_sec": round(cls.calculate_beat_interval(bpm), 3),
            "total_synchronized_duration_sec": round(total_time, 2),
            "total_cuts_quantized": len(cuts),
            "cut_points": [c.__dict__ for c in cuts]
        }
