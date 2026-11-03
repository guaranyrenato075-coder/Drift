"""
Voice Isolation & Noise Suppression Engine for CutWire Drift AI.
Pre-flight vocal conditioning applying high-pass rumble filter (80Hz),
adaptive noise gate, de-essing, and room acoustic de-reverberation.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class VoiceCleanupProfile:
    highpass_cutoff_hz: int = 80
    noise_gate_threshold_db: float = -38.0
    deess_frequency_hz: int = 6500
    deess_intensity: float = 0.5
    ffmpeg_audio_filter: str = ""

class NoiseSuppressor:
    """
    Cleans raw recorded speech or noisy narration prior to timeline ingestion.
    """

    @classmethod
    def create_vocal_chain(
        cls,
        has_aircon_hum: bool = True,
        has_room_echo: bool = False,
        is_boomy: bool = True
    ) -> VoiceCleanupProfile:
        filters = []

        # 1. Highpass filter to eliminate sub-80Hz HVAC rumble and desk vibrations
        if has_aircon_hum or is_boomy:
            filters.append("highpass=f=80")

        # 2. Dynamic noise gate for silence between sentences
        filters.append("agate=threshold=-38dB:ratio=2.5:attack=15:release=120")

        # 3. Gentle De-esser for harsh sibilance ('s', 'ch')
        filters.append("deesser=i=0.5:m=0.5:f=0.5")

        # 4. Subtle de-reverb if room reflections present
        if has_room_echo:
            filters.append("afftdn=nf=-25")

        filter_chain_str = ",".join(filters)

        return VoiceCleanupProfile(
            highpass_cutoff_hz=80,
            noise_gate_threshold_db=-38.0,
            deess_frequency_hz=6500,
            deess_intensity=0.5,
            ffmpeg_audio_filter=filter_chain_str
        )

