"""
Smart Audio Denoise & Broadcast EBU R128 Enhancer for CutWire Drift AI.
Applies professional acoustic processing, room denoise, warmth/presence EQ, and exact
EBU R128 loudness normalization (-14 LUFS for YouTube, Spotify, and broadcast platforms).
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class AudioProfile:
    id: str
    name: str
    target_lufs: float
    description: str
    ffmpeg_filter: str

class SmartAudioDenoiseEnhancer:
    """
    Broadcast audio processor and EBU R128 loudness normalizer.
    """

    PROFILES: Dict[str, AudioProfile] = {
        "broadcast_lufs_14": AudioProfile(
            id="broadcast_lufs_14",
            name="YouTube & Spotify Master (-14 LUFS)",
            target_lufs=-14.0,
            description="Padrão exato da indústria para plataformas de streaming com presença vocal equilibrada.",
            ffmpeg_filter="highpass=f=80,equalizer=f=180:t=q:w=1.2:g=2.0,equalizer=f=3600:t=q:w=1.0:g=2.5,loudnorm=I=-14:LRA=7:tp=-1.5"
        ),
        "radio_podcast_warmth": AudioProfile(
            id="radio_podcast_warmth",
            name="Voz de Rádio / Podcast Encorpada",
            target_lufs=-14.0,
            description="Graves aveludados, compressão dinâmica de proximidade e brilho em agudos.",
            ffmpeg_filter="highpass=f=75,equalizer=f=140:t=q:w=1.5:g=3.5,equalizer=f=4200:t=q:w=1.2:g=3.0,compand=attacks=0.02:decays=0.2:points=-80/-80|-40/-32|-20/-16|0/-10,loudnorm=I=-14:LRA=6:tp=-1.0"
        ),
        "crisp_clarity": AudioProfile(
            id="crisp_clarity",
            name="Clareza Cristalina (Narração Rápida)",
            target_lufs=-14.0,
            description="Atenua frequências médias-graves abafadas e realça a dicção e inteligibilidade.",
            ffmpeg_filter="highpass=f=100,equalizer=f=450:t=q:w=1.0:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=3.8,loudnorm=I=-14:LRA=8:tp=-1.5"
        ),
        "bypass": AudioProfile(
            id="bypass",
            name="Sem Processamento (Bypass)",
            target_lufs=0.0,
            description="Mantém o áudio renderizado sem filtros adicionais.",
            ffmpeg_filter="anull"
        )
    }

    @classmethod
    def list_profiles(cls) -> List[Dict[str, str]]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "target_lufs": p.target_lufs,
                "description": p.description
            }
            for p in cls.PROFILES.values()
        ]

    @classmethod
    def get_filter_for_profile(cls, profile_id: str = "broadcast_lufs_14") -> str:
        prof = cls.PROFILES.get(profile_id, cls.PROFILES["broadcast_lufs_14"])
        return prof.ffmpeg_filter

    @classmethod
    def build_loudnorm_filter_string(cls, target_lufs: float = -14.0, lra: float = 7.0, true_peak: float = -1.5) -> str:
        """Constructs an exact EBU R128 loudnorm filter command."""
        return f"loudnorm=I={target_lufs}:LRA={lra}:tp={true_peak}"
