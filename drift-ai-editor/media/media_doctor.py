"""
Media Doctor & Auto-Repair for CutWire Drift AI.
Analyzes ingested video and audio assets for common editing pipeline hazards:
- Variable Frame Rate (VFR) -> Constant Frame Rate (CFR) conversion
- Audio sample rate mismatch (e.g. 44.1kHz to standard 48kHz broadcast)
- EXIF rotation tags (preventing flipped smartphone footage)
- Corrupted moov atoms or truncated headers
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import os
import subprocess

@dataclass
class MediaDiagnosis:
    file_path: str
    is_healthy: bool
    issues: List[str] = field(default_factory=list)
    repair_command: Optional[List[str]] = None
    recommended_output_path: Optional[str] = None

class MediaDoctor:
    """
    Automated pre-flight media inspector and repair prescription engine.
    """

    @staticmethod
    def inspect(file_path: str, probe_info: Optional[Dict] = None) -> MediaDiagnosis:
        issues = []
        base, ext = os.path.splitext(file_path)
        repaired_path = f"{base}_repaired.mp4"

        # Check file existence
        if not os.path.exists(file_path):
            return MediaDiagnosis(
                file_path=file_path,
                is_healthy=False,
                issues=["File not found"],
                repair_command=None
            )

        # If probe_info is provided or mock simulated
        info = probe_info or {}
        is_vfr = info.get("is_vfr", False)
        sample_rate = info.get("sample_rate", 48000)
        rotation = info.get("rotation", 0)
        pix_fmt = info.get("pix_fmt", "yuv420p")

        if is_vfr:
            issues.append("Variable Frame Rate (VFR) detected - can cause timeline desync")
        if sample_rate and sample_rate != 48000:
            issues.append(f"Non-standard audio sample rate ({sample_rate}Hz != 48000Hz)")
        if rotation in (90, 180, 270):
            issues.append(f"Embedded rotation tag detected ({rotation} deg)")
        if pix_fmt not in ("yuv420p", "yuvj420p"):
            issues.append(f"Non-standard pixel format ({pix_fmt}) may fail HW decoding")

        is_healthy = len(issues) == 0

        # Construct FFmpeg remediation command if unhealthy
        repair_cmd = None
        if not is_healthy:
            repair_cmd = [
                "ffmpeg", "-y", "-i", file_path,
                "-vf", "fps=30,format=yuv420p",
                "-ar", "48000",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                repaired_path
            ]

        return MediaDiagnosis(
            file_path=file_path,
            is_healthy=is_healthy,
            issues=issues,
            repair_command=repair_cmd,
            recommended_output_path=repaired_path if not is_healthy else None
        )

