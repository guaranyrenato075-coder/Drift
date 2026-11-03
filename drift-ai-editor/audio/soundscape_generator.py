"""
Procedural Soundscape Generator for CutWire Drift AI.
Generates multi-layered ambient soundscapes according to scene environment classification
(e.g., Forest, Cyberpunk City, Deep Space, Storm, Historical Battlefield).
Manages bed layers, sporadic spot sound effects, and smooth crossfades between environments.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class EnvironmentType(str, Enum):
    NATURE_FOREST = "nature_forest"
    URBAN_METROPOLIS = "urban_metropolis"
    DEEP_SPACE = "deep_space"
    MEDIEVAL_HISTORICAL = "medieval_historical"
    CYBERPUNK = "cyberpunk"
    THUNDERSTORM = "thunderstorm"
    SUBTLE_INDOOR = "subtle_indoor"

@dataclass
class SoundscapeLayer:
    layer_id: str
    layer_name: str
    sound_type: str  # "continuous_bed", "spot_fx", "sub_drone"
    suggested_tags: List[str]
    volume_db: float  # e.g. -18.0 dB
    pan: float = 0.0   # -1.0 left to 1.0 right

@dataclass
class EnvironmentSoundscape:
    environment: EnvironmentType
    layers: List[SoundscapeLayer]
    reverb_preset: str  # "room", "cathedral", "outdoor", "void"
    crossfade_duration: float = 1.5

class SoundscapeGenerator:
    """
    Assembles layered auditory environments tailored to scene scripts.
    """

    PRESETS: Dict[EnvironmentType, Dict] = {
        EnvironmentType.NATURE_FOREST: {
            "reverb": "outdoor",
            "layers": [
                SoundscapeLayer("bed_wind", "Gentle Canopy Wind", "continuous_bed", ["wind", "leaves", "trees"], -22.0),
                SoundscapeLayer("bed_birds", "Distant Songbirds", "continuous_bed", ["birds", "chirp", "nature"], -26.0, 0.2),
                SoundscapeLayer("fx_twig", "Subtle Footsteps/Twigs", "spot_fx", ["twig", "snap", "forest"], -20.0, -0.3)
            ]
        },
        EnvironmentType.URBAN_METROPOLIS: {
            "reverb": "room",
            "layers": [
                SoundscapeLayer("bed_traffic", "Distant Highway Hum", "continuous_bed", ["traffic", "city", "hum"], -20.0),
                SoundscapeLayer("bed_siren", "Distant Siren Echo", "spot_fx", ["siren", "city_night"], -28.0, 0.5),
                SoundscapeLayer("fx_horns", "Subtle Car Horns", "spot_fx", ["car_horn", "street"], -25.0, -0.4)
            ]
        },
        EnvironmentType.DEEP_SPACE: {
            "reverb": "void",
            "layers": [
                SoundscapeLayer("drone_sub", "Sub-bass Cosmic Drone (40Hz)", "sub_drone", ["drone", "deep", "space"], -18.0),
                SoundscapeLayer("fx_pulsar", "High-frequency Shimmer", "continuous_bed", ["shimmer", "ethereal", "sci-fi"], -30.0, 0.0)
            ]
        },
        EnvironmentType.CYBERPUNK: {
            "reverb": "room",
            "layers": [
                SoundscapeLayer("bed_neon", "Neon Transformer Hum (60Hz)", "continuous_bed", ["electric", "buzz", "neon"], -24.0),
                SoundscapeLayer("bed_rain", "Wet Asphalt Drizzle", "continuous_bed", ["rain", "pavement", "drops"], -22.0),
                SoundscapeLayer("fx_glitch", "Digital Data Flutter", "spot_fx", ["glitch", "cyber", "beep"], -28.0, 0.3)
            ]
        }
    }

    @classmethod
    def create_soundscape(cls, environment: EnvironmentType) -> EnvironmentSoundscape:
        config = cls.PRESETS.get(environment, cls.PRESETS[EnvironmentType.NATURE_FOREST])
        return EnvironmentSoundscape(
            environment=environment,
            layers=config["layers"],
            reverb_preset=config["reverb"],
            crossfade_duration=1.5
        )

    @classmethod
    def detect_environment_from_text(cls, text: str) -> EnvironmentType:
        """Heuristic detection of environment keywords from scene narration."""
        t = text.lower()
        if any(w in t for w in ["espaço", "space", "galáxia", "estrela", "cosmos", "vácuo"]):
            return EnvironmentType.DEEP_SPACE
        elif any(w in t for w in ["cidade", "rua", "metrópole", "trânsito", "urbano", "prédio"]):
            return EnvironmentType.URBAN_METROPOLIS
        elif any(w in t for w in ["cyber", "futuro", "ia", "tecnologia", "robô", "neon"]):
            return EnvironmentType.CYBERPUNK
        elif any(w in t for w in ["tempestade", "chuva", "trovão", "storm", "relâmpago"]):
            return EnvironmentType.THUNDERSTORM
        else:
            return EnvironmentType.NATURE_FOREST

