"""
Voice Emotion & Pitch Shifter for CutWire Drift AI.
Applies emotional intonation profiles (whispered mystery, explosive climax, solemn outro)
by computing speech tempo modifiers, pitch transposition (semitones), and formant shifts.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class EmotionalState(str, Enum):
    MYSTERIOUS_WHISPER = "mysterious_whisper"  # Slightly slowed, subtle pitch drop
    DRAMATIC_CLIMAX = "dramatic_climax"        # Slightly accelerated, energized pitch rise
    SOLEMN_OUTRO = "solemn_outro"              # Measured tempo, warm chest resonance
    NEUTRAL_DOCUMENTARY = "neutral_documentary"# Natural baseline

@dataclass
class VoiceModulationProfile:
    emotion: EmotionalState
    tempo_rate: float        # 1.0 = normal (e.g. 0.92 for mystery, 1.08 for climax)
    pitch_semitones: float   # 0.0 = normal (e.g. -1.2 for solemn, +1.5 for climax)
    formant_shift: float     # 1.0 = normal
    ffmpeg_rubberband_filter: str

class VoiceEmotionShifter:
    """
    Sculpts synthesized voiceover delivery to match scene dramatic urgency.
    """

    PROFILES: Dict[EmotionalState, Dict] = {
        EmotionalState.MYSTERIOUS_WHISPER: {
            "tempo": 0.94, "pitch": -0.8, "formant": 0.98,
            "filter": "rubberband=tempo=0.94:pitch=-0.8"
        },
        EmotionalState.DRAMATIC_CLIMAX: {
            "tempo": 1.06, "pitch": 1.2, "formant": 1.04,
            "filter": "rubberband=tempo=1.06:pitch=1.2"
        },
        EmotionalState.SOLEMN_OUTRO: {
            "tempo": 0.92, "pitch": -1.5, "formant": 0.95,
            "filter": "rubberband=tempo=0.92:pitch=-1.5"
        },
        EmotionalState.NEUTRAL_DOCUMENTARY: {
            "tempo": 1.00, "pitch": 0.0, "formant": 1.00,
            "filter": "anull"
        }
    }

    @classmethod
    def get_modulation(cls, emotion: EmotionalState = EmotionalState.NEUTRAL_DOCUMENTARY) -> VoiceModulationProfile:
        p = cls.PROFILES.get(emotion, cls.PROFILES[EmotionalState.NEUTRAL_DOCUMENTARY])
        return VoiceModulationProfile(
            emotion=emotion,
            tempo_rate=p["tempo"],
            pitch_semitones=p["pitch"],
            formant_shift=p["formant"],
            ffmpeg_rubberband_filter=p["filter"]
        )

