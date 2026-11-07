"""
Windows Sleep-Inhibit Governor for CutWire Drift AI.
Uses Kernel32 SetThreadExecutionState to prevent the OS from going into standby/sleep mode
during long render sessions (10-30+ minutes), automatically restoring energy savings when done.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import sys
import ctypes

@dataclass
class SleepInhibitState:
    is_sleep_inhibited: bool
    platform: str
    active_jobs_count: int

class SleepInhibitGovernor:
    """
    Prevents unwanted system suspension during active batch production or parallel rendering.
    """

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

    _active_counter: int = 0

    @classmethod
    def inhibit_sleep(cls, keep_display_on: bool = False) -> SleepInhibitState:
        cls._active_counter += 1

        if sys.platform == "win32":
            try:
                flags = cls.ES_CONTINUOUS | cls.ES_SYSTEM_REQUIRED
                if keep_display_on:
                    flags |= cls.ES_DISPLAY_REQUIRED
                ctypes.windll.kernel32.SetThreadExecutionState(flags)
            except Exception:
                pass

        return SleepInhibitState(
            is_sleep_inhibited=True,
            platform=sys.platform,
            active_jobs_count=cls._active_counter
        )

    @classmethod
    def release_sleep(cls) -> SleepInhibitState:
        cls._active_counter = max(0, cls._active_counter - 1)

        if cls._active_counter == 0 and sys.platform == "win32":
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(cls.ES_CONTINUOUS)
            except Exception:
                pass

        return SleepInhibitState(
            is_sleep_inhibited=(cls._active_counter > 0),
            platform=sys.platform,
            active_jobs_count=cls._active_counter
        )

    @classmethod
    def is_inhibited(cls) -> bool:
        return cls._active_counter > 0

