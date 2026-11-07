"""
Windows Background Disk I/O Governor for CutWire Drift AI.
Throttles disk read/write bandwidth and queues heavy video export I/O to background priority
via Windows Kernel32 PROCESS_MODE_BACKGROUND_BEGIN, preventing desktop UI stutters.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import sys
import ctypes

@dataclass
class DiskIoStatus:
    is_background_io_active: bool
    platform: str
    error_message: Optional[str] = None

class DiskIoGovernor:
    """
    Toggles low-priority background I/O on Windows to protect system responsiveness.
    """

    PROCESS_MODE_BACKGROUND_BEGIN = 0x00100000
    PROCESS_MODE_BACKGROUND_END = 0x00200000

    _is_active: bool = False

    @classmethod
    def begin_background_io(cls) -> DiskIoStatus:
        if sys.platform != "win32":
            return DiskIoStatus(is_background_io_active=False, platform=sys.platform, error_message="Non-Windows platform")

        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            res = ctypes.windll.kernel32.SetPriorityClass(handle, cls.PROCESS_MODE_BACKGROUND_BEGIN)
            if res:
                cls._is_active = True
                return DiskIoStatus(is_background_io_active=True, platform="win32")
            else:
                err = ctypes.GetLastError()
                return DiskIoStatus(is_background_io_active=False, platform="win32", error_message=f"ErrorCode {err}")
        except Exception as e:
            return DiskIoStatus(is_background_io_active=False, platform="win32", error_message=str(e))

    @classmethod
    def end_background_io(cls) -> DiskIoStatus:
        if sys.platform != "win32":
            return DiskIoStatus(is_background_io_active=False, platform=sys.platform)

        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            res = ctypes.windll.kernel32.SetPriorityClass(handle, cls.PROCESS_MODE_BACKGROUND_END)
            cls._is_active = False
            return DiskIoStatus(is_background_io_active=False, platform="win32")
        except Exception as e:
            return DiskIoStatus(is_background_io_active=False, platform="win32", error_message=str(e))

    @classmethod
    def is_active(cls) -> bool:
        return cls._is_active

