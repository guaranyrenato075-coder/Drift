"""
Adaptive BPM & Procedural Soundtrack Composer for CutWire Drift AI.
Dynamically maps narrative tension scores to musical tempo (BPM) and stem instrumentation layers
(sub-bass, rhythmic pulse, ambient strings, harmonic synth), generating responsive background scores.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class SoundtrackStemLayer:
    layer_name: str
    instrument: str
    is_active: bool
    volume_db: float

@dataclass
class AdaptiveMusicSection:
    scene_order: int
    start_time: float
    duration: float
    target_bpm: int
    tension_level: str  # "low", "medium", "climax", "resolution"
    active_stems: List[SoundtrackStemLayer]

@dataclass
class AdaptiveScoreComposition:
    base_bpm: int
    peak_bpm: int
    total_sections: int
    sections: List[AdaptiveMusicSection]

class AdaptiveBpmComposer:
    """
    Composes tempo-adaptive soundtrack structures responding to narrative dramatic arcs.
    """

    BASE_BPM = 100
    CLIMAX_BPM = 135

    @classmethod
    def compose_for_plan(cls, plan: ProjectPlan) -> AdaptiveScoreComposition:
        if not plan.scenes:
            return AdaptiveScoreComposition(cls.BASE_BPM, cls.BASE_BPM, 0, [])

        sections: List[AdaptiveMusicSection] = []
        current_time = 0.0
        n = len(plan.scenes)

        for idx, scene in enumerate(plan.scenes):
            dur = scene.duration if scene.duration > 0 else 4.0
            ratio = idx / max(1, n - 1)

            # Dramatic arc mapping: Intro (relaxed) -> Buildup -> Climax -> Outro
            if ratio < 0.25:
                bpm = 95
                tension = "low"
                stems = [
                    SoundtrackStemLayer("ambient_pad", "Warm Synth Strings", True, -16.0),
                    SoundtrackStemLayer("bass_drone", "40Hz Sub Drone", True, -20.0),
                    SoundtrackStemLayer("drums", "Kick/Snare Pulse", False, -99.0)
                ]
            elif ratio < 0.55:
                bpm = 115
                tension = "medium"
                stems = [
                    SoundtrackStemLayer("ambient_pad", "Synth Arpeggio", True, -18.0),
                    SoundtrackStemLayer("bass_drone", "Plucked Bassline", True, -16.0),
                    SoundtrackStemLayer("drums", "Steady Percussion", True, -18.0)
                ]
            elif ratio < 0.85:
                bpm = 132
                tension = "climax"
                stems = [
                    SoundtrackStemLayer("ambient_pad", "Epic Orchestral Strings", True, -14.0),
                    SoundtrackStemLayer("bass_drone", "Driving Sub Bass", True, -12.0),
                    SoundtrackStemLayer("drums", "High-Energy Cinematic Drums", True, -14.0)
                ]
            else:
                bpm = 102
                tension = "resolution"
                stems = [
                    SoundtrackStemLayer("ambient_pad", "Soothing Ambient Piano", True, -16.0),
                    SoundtrackStemLayer("bass_drone", "Gentle Sub Bass", True, -22.0),
                    SoundtrackStemLayer("drums", "Kick/Snare", False, -99.0)
                ]

            sections.append(
                AdaptiveMusicSection(
                    scene_order=scene.order,
                    start_time=round(current_time, 2),
                    duration=round(dur, 2),
                    target_bpm=bpm,
                    tension_level=tension,
                    active_stems=stems
                )
            )
            current_time += dur

        return AdaptiveScoreComposition(
            base_bpm=95,
            peak_bpm=132,
            total_sections=len(sections),
            sections=sections
        )
