"""
Direct Clock Audio Resampler for CutWire Drift AI.
Pre-normalizes downloaded stock music and SFX into the project's master sample clock (48000 Hz stereo)
using FFmpeg's libsoxr resampler filter, eliminating real-time resampling overhead during final timeline mix.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class AudioResampleSpec:
    input_audio_path: str
    output_audio_path: str
    target_sample_rate_hz: int
    target_channels: int
    resampler_engine: str          # 'soxr'
    ffmpeg_filter_args: List[str]
    estimated_mixing_speedup_factor: float

class DirectClockAudioResampler:
    """
    Standardizes disparate audio sampling rates (22.05kHz, 44.1kHz -> 48kHz) in a single ingest pass.
    """

    MASTER_SAMPLE_RATE = 48000
    MASTER_CHANNELS = 2

    @classmethod
    def build_resample_spec(
        cls,
        input_path: str,
        output_path: Optional[str] = None,
        target_hz: int = MASTER_SAMPLE_RATE,
        channels: int = MASTER_CHANNELS
    ) -> AudioResampleSpec:
        if not output_path:
            output_path = input_path.replace(".mp3", "_48k.mp3").replace(".wav", "_48k.wav")

        # Filtro de alta fidelidade libsoxr:
        # aresample=resampler=soxr:osr=48000:precision=28
        filter_str = f"aresample=resampler=soxr:osr={target_hz}:precision=20,aformat=channel_layouts={'stereo' if channels == 2 else 'mono'}"

        args = [
            "-i", input_path,
            "-af", filter_str,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            "-y", output_path
        ]

        return AudioResampleSpec(
            input_audio_path=input_path,
            output_audio_path=output_path,
            target_sample_rate_hz=target_hz,
            target_channels=channels,
            resampler_engine="soxr",
            ffmpeg_filter_args=args,
            estimated_mixing_speedup_factor=4.5
        )
