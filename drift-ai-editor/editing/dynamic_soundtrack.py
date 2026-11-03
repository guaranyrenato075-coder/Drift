from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import ProjectPlan, Scene
from analysis.emotional_curve import EmotionalCurveEngine, NarrativeArcPhase

@dataclass
class AudioStemCue:
    scene_order: int
    timeline_in_sec: float
    duration_sec: float
    ambient_bed_gain_db: float     # Subdued atmospheric layer
    rhythmic_pulse_gain_db: float  # Percussion layer
    climax_accent_gain_db: float   # Brass / orchestral riser
    ducking_depth_db: float        # Speech priority attenuation

@dataclass
class DynamicSoundtrackPlan:
    project_id: str
    total_duration_sec: float
    cues: List[AudioStemCue] = field(default_factory=list)
    recommended_tempo_bpm: int = 110
    music_key: str = "D minor"

class DynamicSoundtrackEngine:
    """
    Procedural & Adaptive Soundtrack Engine:
    Designs a living music track that breathes with the video:
      - Keeps audio ambient and low (-26dB) during exposition.
      - Automatically introduces rhythmic pulse during rising tension.
      - Fires dynamic climax accents and fuller volume at the narrative peak.
      - Gently fades out stems during speech pauses for maximum speech intelligibility.
    """

    @classmethod
    def generate_soundtrack_plan(cls, plan: ProjectPlan) -> DynamicSoundtrackPlan:
        modulations = EmotionalCurveEngine.plot_curve(plan.scenes)
        cues: List[AudioStemCue] = []
        cur_time = 0.0

        for idx, scene in enumerate(plan.scenes):
            dur = scene.duration or 4.0
            mod = modulations[idx] if idx < len(modulations) else None

            if mod and mod.arc_phase == NarrativeArcPhase.CLIMAX_REVELATION:
                bed_db = -16.0
                pulse_db = -14.0
                climax_db = -12.0
                duck_db = -18.0
            elif mod and mod.arc_phase == NarrativeArcPhase.RISING_TENSION:
                bed_db = -20.0
                pulse_db = -18.0
                climax_db = -99.0 # muted
                duck_db = -22.0
            elif mod and mod.arc_phase == NarrativeArcPhase.HOOK_CURIOSITY:
                bed_db = -18.0
                pulse_db = -16.0
                climax_db = -18.0 # quick intro hit
                duck_db = -20.0
            else:
                # Exposition / Outro
                bed_db = -24.0
                pulse_db = -99.0  # muted
                climax_db = -99.0 # muted
                duck_db = -24.0

            cues.append(
                AudioStemCue(
                    scene_order=scene.order,
                    timeline_in_sec=round(cur_time, 2),
                    duration_sec=round(dur, 2),
                    ambient_bed_gain_db=bed_db,
                    rhythmic_pulse_gain_db=pulse_db,
                    climax_accent_gain_db=climax_db,
                    ducking_depth_db=duck_db
                )
            )
            cur_time += dur

        return DynamicSoundtrackPlan(
            project_id=plan.project_id,
            total_duration_sec=round(cur_time, 2),
            cues=cues,
            recommended_tempo_bpm=110,
            music_key="D minor"
        )

