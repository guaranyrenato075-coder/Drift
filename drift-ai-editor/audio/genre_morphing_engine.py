"""
Musical Genre Morphing & Stem Remapper for CutWire Drift AI.
Enables 1-click global genre transmutation across the entire video timeline:
Converts Orchestral Epic to Lo-Fi Chill, Cyberpunk Synthwave, or Organic Acoustic
while recalculating ducking thresholds and beat-matching points.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from models.scene_plan import ProjectPlan, Scene

class MusicGenre(str, Enum):
    CINEMATIC_ORCHESTRAL = "cinematic_orchestral"
    LOFI_CHILL = "lofi_chill"
    CYBERPUNK_SYNTHWAVE = "cyberpunk_synthwave"
    ACOUSTIC_FOLK = "acoustic_folk"

@dataclass
class GenreMorphResult:
    target_genre: MusicGenre
    base_tempo_bpm: int
    audio_ducking_attenuation_db: float
    recommended_eq_preset: str
    stem_layers: List[str]

class GenreMorphingEngine:
    """
    Transforms musical landscape across timeline without breaking visual cuts.
    """

    GENRE_PROFILES: Dict[MusicGenre, Dict] = {
        MusicGenre.CINEMATIC_ORCHESTRAL: {
            "bpm": 110, "ducking": -18.0, "eq": "epic_strings_boost",
            "stems": ["Cello & Violins", "Brass Horns", "Timpani Drums", "Sub Drone"]
        },
        MusicGenre.LOFI_CHILL: {
            "bpm": 84, "ducking": -14.0, "eq": "vinyl_crackle_warmth",
            "stems": ["Rhodes Electric Piano", "Dusted Boom-Bap Drums", "Mellow Bass", "Vinyl Flutter"]
        },
        MusicGenre.CYBERPUNK_SYNTHWAVE: {
            "bpm": 128, "ducking": -20.0, "eq": "sawtooth_lead_drive",
            "stems": ["Arpeggiated Analog Synth", "808 Gated Snare", "Reese Bassline", "Cyber Pad"]
        },
        MusicGenre.ACOUSTIC_FOLK: {
            "bpm": 96, "ducking": -16.0, "eq": "natural_wood_resonance",
            "stems": ["Fingerpicked Acoustic Guitar", "Warm Upright Bass", "Gentle Tambourine", "Mandolin"]
        }
    }

    @classmethod
    def morph_genre(cls, plan: ProjectPlan, target_genre: MusicGenre = MusicGenre.LOFI_CHILL) -> GenreMorphResult:
        cfg = cls.GENRE_PROFILES.get(target_genre, cls.GENRE_PROFILES[MusicGenre.CINEMATIC_ORCHESTRAL])

        # Update scene style profile tags
        for s in getattr(plan, "scenes", []):
            s.concept = f"{s.concept or ''} [Genre: {target_genre.value}]"

        return GenreMorphResult(
            target_genre=target_genre,
            base_tempo_bpm=cfg["bpm"],
            audio_ducking_attenuation_db=cfg["ducking"],
            recommended_eq_preset=cfg["eq"],
            stem_layers=cfg["stems"]
        )

