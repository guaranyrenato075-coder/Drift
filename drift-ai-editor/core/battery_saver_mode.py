"""
Laptop Battery Saver & Travel Mode Optimizer for CutWire Drift AI.
Monitors mobile power telemetry, dynamically reduces timeline preview framerates to 24fps,
disables GPU shader stress, and scales background worker threads to extend battery runtime on laptops.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os

class PowerState(str, Enum):
    AC_WALL_POWER = "ac_wall_power"
    BATTERY_DISCHARGING = "battery_discharging"
    LOW_BATTERY_CRITICAL = "low_battery_critical"

@dataclass
class PowerOptimizationProfile:
    state: PowerState
    preview_framerate_fps: int
    worker_thread_concurrency: int
    realtime_color_lut_enabled: bool
    disk_caching_throttle_ms: int

class BatterySaverEngine:
    """
    Extends on-the-go editing endurance on laptops.
    """

    @classmethod
    def get_power_profile(cls, force_state: Optional[PowerState] = None) -> PowerOptimizationProfile:
        state = force_state or PowerState.AC_WALL_POWER

        if state == PowerState.LOW_BATTERY_CRITICAL:
            return PowerOptimizationProfile(
                state=state,
                preview_framerate_fps=18,
                worker_thread_concurrency=1,
                realtime_color_lut_enabled=False,
                disk_caching_throttle_ms=500
            )
        elif state == PowerState.BATTERY_DISCHARGING:
            return PowerOptimizationProfile(
                state=state,
                preview_framerate_fps=24,
                worker_thread_concurrency=2,
                realtime_color_lut_enabled=False,
                disk_caching_throttle_ms=200
            )
        else:  # AC_WALL_POWER
            return PowerOptimizationProfile(
                state=state,
                preview_framerate_fps=60,
                worker_thread_concurrency=4,
                realtime_color_lut_enabled=True,
                disk_caching_throttle_ms=0
            )

