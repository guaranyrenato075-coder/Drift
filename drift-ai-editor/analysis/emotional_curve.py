from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from models.scene_plan import Scene

class NarrativeArcPhase(str, Enum):
    HOOK_CURIOSITY = "hook_curiosity"          # Initial engagement, provocative
    EXPOSITION_GROUNDING = "exposition_grounding" # Establish baseline, calm, wide shots
    RISING_TENSION = "rising_tension"          # Developing conflict/argument, increasing pace
    CLIMAX_REVELATION = "climax_revelation"    # Peak insight, dynamic impact, close-up
    CONTEMPLATION_OUTRO = "contemplation_outro"  # Philosophical resolution, reflective, wide

@dataclass
class SceneEmotionalModulation:
    scene_order: int
    arc_phase: NarrativeArcPhase
    energy_level: float               # 0.1 (whisper quiet) to 1.0 (explosive climax)
    pacing_multiplier: float          # Adjusts scene cut speed (e.g. 0.8: fast cut, 1.3: linger)
    music_volume_db: float            # Dynamic ducking offset (e.g. -18dB in climax, -24dB in speech)
    recommended_framing: str          # 'wide_angle', 'medium_shot', 'close_up_detail'
    transition_style: str             # 'hard_cut', 'crossfade', 'dissolve'

class EmotionalCurveEngine:
    """
    Analyzes narrative script progression and maps each scene onto a classic 5-stage
    dramatic emotional arc (Freytag's Pyramid / Hero's Journey).
    Dynamically modulates:
      - Cut tempo and shot duration
      - Music track intensity curve and volume balance
      - Framing tightness (wide vs intimate close-up)
    """

    CLIMAX_INDICATORS = ["finalmente", "verdade", "segredo", "crucial", "fundamental", "revelação", "muda tudo", "o ponto é", "climax", "truth", "secret"]
    TENSION_INDICATORS = ["conflito", "luta", "desafio", "dificuldade", "dor", "obstáculo", "pressão", "batalha", "perigo", "struggle", "fight", "pressure"]

    @classmethod
    def plot_curve(cls, scenes: List[Scene]) -> List[SceneEmotionalModulation]:
        total = len(scenes)
        modulations: List[SceneEmotionalModulation] = []

        if total == 0:
            return modulations

        for idx, scene in enumerate(scenes):
            progress_ratio = idx / max(1, total - 1)
            text_lower = (scene.narration_text + " " + scene.visual_description).lower()

            # 1. Determine Narrative Phase based on project timeline position & tokens
            if idx == 0:
                phase = NarrativeArcPhase.HOOK_CURIOSITY
                energy = 0.75
                pacing = 0.9      # Snappy opening
                music_db = -20.0
                framing = "wide_angle"
                trans = "crossfade"
            elif idx == total - 1:
                phase = NarrativeArcPhase.CONTEMPLATION_OUTRO
                energy = 0.4
                pacing = 1.35     # Let final takeaway linger
                music_db = -18.0
                framing = "wide_angle"
                trans = "dissolve"
            elif any(tok in text_lower for tok in cls.CLIMAX_INDICATORS) or (0.65 <= progress_ratio <= 0.85):
                phase = NarrativeArcPhase.CLIMAX_REVELATION
                energy = 0.95
                pacing = 0.8      # Rapid, intense cuts
                music_db = -16.0  # Louder presence
                framing = "close_up_detail"
                trans = "hard_cut"
            elif any(tok in text_lower for tok in cls.TENSION_INDICATORS) or (0.35 <= progress_ratio < 0.65):
                phase = NarrativeArcPhase.RISING_TENSION
                energy = 0.7
                pacing = 1.0
                music_db = -22.0
                framing = "medium_shot"
                trans = "crossfade"
            else:
                phase = NarrativeArcPhase.EXPOSITION_GROUNDING
                energy = 0.45
                pacing = 1.2
                music_db = -24.0
                framing = "medium_shot"
                trans = "crossfade"

            modulations.append(
                SceneEmotionalModulation(
                    scene_order=scene.order,
                    arc_phase=phase,
                    energy_level=round(energy, 2),
                    pacing_multiplier=round(pacing, 2),
                    music_volume_db=round(music_db, 1),
                    recommended_framing=framing,
                    transition_style=trans
                )
            )

        return modulations

