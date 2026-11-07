"""
Proactive RAM Working Set Flusher for CutWire Drift AI.
Triggers generational garbage collection and leverages native Windows kernel APIs
(EmptyWorkingSet / SetProcessWorkingSetSize) to release unused physical RAM back to the OS.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
import sys
import gc
import ctypes

@dataclass
class RamFlushReport:
    freed_python_objects: int
    working_set_before_mb: float
    working_set_after_mb: float
    memory_reclaimed_mb: float
    is_windows_api_applied: bool

class RamWorkingSetFlusher:
    """
    Reclaims unused physical memory after rendering chunks or processing media scenes.
    """

    @classmethod
    def get_current_working_set_mb(cls) -> float:
        if sys.platform == "win32":
            try:
                class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                    _fields_ = [
                        ("cb", ctypes.c_ulong),
                        ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)
                    ]

                counters = PROCESS_MEMORY_COUNTERS()
                counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                    return round(counters.WorkingSetSize / (1024 * 1024), 2)
            except Exception:
                pass
        return 0.0

    @classmethod
    def flush(cls) -> RamFlushReport:
        before_mb = cls.get_current_working_set_mb()

        # 1. Coleta forçada de lixo do Python em todas as 3 gerações
        collected = gc.collect(generation=2)

        # 2. Descarrega Working Set físico via Windows Kernel
        applied_win_api = False
        if sys.platform == "win32":
            try:
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                # EmptyWorkingSet descarta páginas não referenciadas para o standby list
                res = ctypes.windll.psapi.EmptyWorkingSet(handle)
                if not res:
                    # Fallback para SetProcessWorkingSetSize(-1, -1)
                    res = ctypes.windll.kernel32.SetProcessWorkingSetSize(handle, -1, -1)
                applied_win_api = bool(res)
            except Exception:
                applied_win_api = False

        after_mb = cls.get_current_working_set_mb()
        reclaimed = max(0.0, round(before_mb - after_mb, 2))

        return RamFlushReport(
            freed_python_objects=collected,
            working_set_before_mb=before_mb,
            working_set_after_mb=after_mb,
            memory_reclaimed_mb=reclaimed,
            is_windows_api_applied=applied_win_api
        )

