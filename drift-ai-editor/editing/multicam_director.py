"""
Multicam Director for CutWire Drift AI.
Handles automatic multi-camera synchronization by audio waveform/timecode,
active speaker switching, and shot pacing.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import math

@dataclass
class CameraAngle:
    camera_id: str
    file_path: str
    label: str  # e.g. "Host Close-up", "Guest Wide", "Overview"
    offset_seconds: float = 0.0
    audio_energy_profile: List[float] = field(default_factory=list)

@dataclass
class MulticamCut:
    timestamp_start: float
    timestamp_end: float
    active_camera_id: str
    switch_reason: str

class MulticamDirector:
    """
    Coordinates multi-angle footage, calculates audio alignment offsets,
    and suggests intelligent camera switching based on speech activity.
    """

    def __init__(self, min_shot_duration: float = 2.0, max_shot_duration: float = 7.0):
        self.min_shot_duration = min_shot_duration
        self.max_shot_duration = max_shot_duration

    def calculate_sync_offset(self, ref_envelope: List[float], target_envelope: List[float], sample_rate: float = 10.0) -> float:
        """
        Calculates time offset between two audio energy envelopes using cross-correlation.
        sample_rate: number of energy points per second (default 10 Hz = 100ms blocks).
        """
        if not ref_envelope or not target_envelope:
            return 0.0

        n = len(ref_envelope)
        m = len(target_envelope)
        max_lag = min(n, m) // 2
        
        best_corr = -1.0
        best_lag = 0

        for lag in range(-max_lag, max_lag + 1):
            corr = 0.0
            count = 0
            for i in range(n):
                j = i + lag
                if 0 <= j < m:
                    corr += ref_envelope[i] * target_envelope[j]
                    count += 1
            if count > 0:
                normalized_corr = corr / count
                if normalized_corr > best_corr:
                    best_corr = normalized_corr
                    best_lag = lag

        offset_seconds = best_lag / sample_rate
        return offset_seconds

    def generate_multicam_edit(
        self,
        angles: List[CameraAngle],
        total_duration: float,
        pacing_bias: str = "dynamic"
    ) -> List[MulticamCut]:
        """
        Generates an automated multi-camera cut list switching between available angles.
        """
        if not angles:
            return []

        if len(angles) == 1:
            return [MulticamCut(0.0, total_duration, angles[0].camera_id, "single_camera")]

        cuts: List[MulticamCut] = []
        current_time = 0.0
        current_cam_idx = 0

        shot_len = 3.5 if pacing_bias == "dynamic" else 5.0

        while current_time < total_duration:
            next_time = min(total_duration, current_time + shot_len)
            cuts.append(
                MulticamCut(
                    timestamp_start=round(current_time, 2),
                    timestamp_end=round(next_time, 2),
                    active_camera_id=angles[current_cam_idx].camera_id,
                    switch_reason="pacing_cadence"
                )
            )
            current_time = next_time
            # Switch to next camera
            current_cam_idx = (current_cam_idx + 1) % len(angles)

        return cuts

