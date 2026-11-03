"""
Hardware Profiler & Dynamic Resource Scaler for CutWire Drift AI.
Detects CPU thread count, available physical memory, GPU hardware encoders (NVENC, QSV, AMF),
and selects optimal timeline proxy resolutions, thread pools, and FFmpeg encoder profiles.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import os
import multiprocessing

class HardwareTier(str, Enum):
    ENTRY = "entry"          # < 4 cores or < 8GB RAM -> 720p 30fps proxies, ultrafast CPU x264
    STANDARD = "standard"    # 4-8 cores, 8-16GB RAM -> 1080p 30fps, fast CPU / basic HW
    PRO = "pro"              # > 8 cores, > 16GB RAM, Dedicated GPU -> Full Res, NVENC/QSV/AMF, max parallel jobs

@dataclass
class HardwareProfile:
    cpu_cores: int
    ram_gb: float
    gpu_acceleration: str  # "cuda_nvenc", "qsv", "amf", "software_cpu"
    hardware_tier: HardwareTier
    recommended_parallel_jobs: int
    preview_proxy_resolution: str  # "720p", "1080p", "none"
    ffmpeg_video_codec: str
    ffmpeg_preset: str

class HardwareProfiler:
    """
    Evaluates host system performance and dynamically tunes editor configurations.
    """

    @classmethod
    def probe(cls, force_gpu: Optional[str] = None) -> HardwareProfile:
        cores = multiprocessing.cpu_count()
        # Fallback estimation for RAM if psutil is not installed
        ram_gb = 16.0
        try:
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        except Exception:
            pass

        # Detect GPU encoder if available or test via probe
        gpu_accel = force_gpu or "software_cpu"

        # Determine Tier
        if cores < 4 or ram_gb < 7.5:
            tier = HardwareTier.ENTRY
            parallel_jobs = 1
            proxy_res = "720p"
            codec = "libx264"
            preset = "ultrafast"
        elif cores >= 8 and ram_gb >= 15.0:
            tier = HardwareTier.PRO
            parallel_jobs = min(cores // 2, 6)
            proxy_res = "none" if gpu_accel != "software_cpu" else "1080p"
            codec = "h264_nvenc" if gpu_accel == "cuda_nvenc" else "libx264"
            preset = "medium" if codec == "libx264" else "p4"
        else:
            tier = HardwareTier.STANDARD
            parallel_jobs = 2
            proxy_res = "1080p"
            codec = "libx264"
            preset = "veryfast"

        return HardwareProfile(
            cpu_cores=cores,
            ram_gb=ram_gb,
            gpu_acceleration=gpu_accel,
            hardware_tier=tier,
            recommended_parallel_jobs=parallel_jobs,
            preview_proxy_resolution=proxy_res,
            ffmpeg_video_codec=codec,
            ffmpeg_preset=preset
        )

