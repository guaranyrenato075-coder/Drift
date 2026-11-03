"""
Archival Video Restoration & Noise Reduction Engine for CutWire Drift AI.
Restores vintage, compressed, or noisy historical footage (e.g. vintage NASA, WWI archives)
using temporal wavelet denoising (hqdn3d), unsharp mask edge enhancement, and luma stabilization.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class RestorationPreset(str, Enum):
    VINTAGE_ARCHIVE = "vintage_archive"    # Heavy de-noise, moderate unsharp sharpening
    MODERN_LOW_LIGHT = "modern_low_light"  # Sensor chroma noise removal
    WEB_DEBLOCK = "web_deblock"            # Anti-macroblocking for low-bitrate downloads
    SUBTLE_ENHANCE = "subtle_enhance"      # Gentle edge definition enhancement

@dataclass
class RestorationFilterSpec:
    preset: RestorationPreset
    denoise_temporal_strength: float
    unsharp_amount: float
    ffmpeg_filter: str

class VideoRestorationEngine:
    """
    Cleans artifact-laden source footage prior to timeline export.
    """

    @classmethod
    def get_restoration_filter(cls, preset: RestorationPreset = RestorationPreset.SUBTLE_ENHANCE) -> RestorationFilterSpec:
        if preset == RestorationPreset.VINTAGE_ARCHIVE:
            t_str = 6.0
            sharp = 1.3
            f_chain = "hqdn3d=4.0:3.0:6.0:4.5,unsharp=5:5:1.2:5:5:0.0"
        elif preset == RestorationPreset.MODERN_LOW_LIGHT:
            t_str = 4.0
            sharp = 1.0
            f_chain = "hqdn3d=2.0:4.0:3.0:5.0,unsharp=3:3:0.8:3:3:0.0"
        elif preset == RestorationPreset.WEB_DEBLOCK:
            t_str = 3.0
            sharp = 0.9
            f_chain = "deblock=filter=medium:block=4,unsharp=3:3:0.7:3:3:0.0"
        else:  # SUBTLE_ENHANCE
            t_str = 1.5
            sharp = 0.8
            f_chain = "hqdn3d=1.5:1.5:2.0:2.0,unsharp=3:3:0.6:3:3:0.0"

        return RestorationFilterSpec(
            preset=preset,
            denoise_temporal_strength=t_str,
            unsharp_amount=sharp,
            ffmpeg_filter=f_chain
        )

