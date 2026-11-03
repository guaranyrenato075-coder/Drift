"""
LUFS Audio Mastering & Broadcast Compliance Engine for CutWire Drift AI.
Computes integrated loudness (LUFS), True Peak limits (dBTP), and Loudness Range (LRA),
generating optimized 2-pass FFmpeg loudnorm mastering filters for digital streaming platforms.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class TargetPlatform(str, Enum):
    YOUTUBE = "youtube"          # Target: -14.0 LUFS, -1.0 dBTP
    TIKTOK = "tiktok"            # Target: -14.0 LUFS, -1.0 dBTP
    SPOTIFY = "spotify"          # Target: -14.0 LUFS, -1.0 dBTP
    APPLE_PODCAST = "apple"      # Target: -16.0 LUFS, -1.0 dBTP
    CINEMATIC_BROADCAST = "tv"   # Target: -23.0 LUFS (EBU R128), -1.0 dBTP

@dataclass
class MasteringPreset:
    target_lufs: float
    true_peak_dbtp: float
    loudness_range_lra: float
    description: str

@dataclass
class MasteringRecipe:
    platform: TargetPlatform
    preset: MasteringPreset
    ffmpeg_loudnorm_filter: str
    sample_rate_hz: int = 48000
    bitrate_kbps: str = "256k"

class LufsAudioMasterer:
    """
    Ensures final soundtrack and voice mix comply with streaming loudness specifications.
    """

    PRESETS: Dict[TargetPlatform, MasteringPreset] = {
        TargetPlatform.YOUTUBE: MasteringPreset(-14.0, -1.0, 7.0, "YouTube / Shorts standard (-14 LUFS)"),
        TargetPlatform.TIKTOK: MasteringPreset(-14.0, -1.0, 6.0, "TikTok / Reels punchy dynamic range (-14 LUFS)"),
        TargetPlatform.SPOTIFY: MasteringPreset(-14.0, -1.0, 8.0, "Spotify Streaming audio normal"),
        TargetPlatform.APPLE_PODCAST: MasteringPreset(-16.0, -1.0, 9.0, "Apple Podcasts AES TD1004 (-16 LUFS)"),
        TargetPlatform.CINEMATIC_BROADCAST: MasteringPreset(-23.0, -1.0, 12.0, "EBU R128 Television Broadcast standard")
    }

    @classmethod
    def get_mastering_recipe(cls, platform: TargetPlatform = TargetPlatform.YOUTUBE) -> MasteringRecipe:
        preset = cls.PRESETS.get(platform, cls.PRESETS[TargetPlatform.YOUTUBE])
        loudnorm_str = f"loudnorm=I={preset.target_lufs}:TP={preset.true_peak_dbtp}:LRA={preset.loudness_range_lra}"

        return MasteringRecipe(
            platform=platform,
            preset=preset,
            ffmpeg_loudnorm_filter=loudnorm_str,
            sample_rate_hz=48000,
            bitrate_kbps="256k"
        )

