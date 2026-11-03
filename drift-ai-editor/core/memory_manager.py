"""
Memory Manager & Garbage Collection Director for CutWire Drift AI.
Monitors process heap usage, enforces aggressive memory reclamation after heavy rendering/AI jobs,
and invokes OS-level working set trimming to prevent memory bloat.
"""
import os
import gc
import sys
import ctypes
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Any, Generator

@dataclass
class MemoryStats:
    rss_mb: float
    peak_rss_mb: float
    gc_counts: tuple[int, int, int]
    python_version: str

class MemoryManager:
    """
    Surgical memory management, GC triggering, and working set minimization.
    """

    @classmethod
    def get_memory_usage_mb(cls) -> float:
        """
        Gets current process Working Set (RSS) in Megabytes.
        """
        if sys.platform == "win32":
            try:
                # Windows API GetProcessMemoryInfo
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
                        ("PeakPagefileUsage", ctypes.c_size_t),
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
    def collect_garbage(cls, trim_os_working_set: bool = True) -> Dict[str, Any]:
        """
        Forces generation-2 GC collection and trims Windows working set.
        """
        mem_before = cls.get_memory_usage_mb()
        collected = gc.collect(generation=2)

        if trim_os_working_set and sys.platform == "win32":
            try:
                handle = ctypes.windll.kernel32.GetCurrentProcess()
                # EmptyWorkingSet minimizes RAM footprints on idle
                ctypes.windll.psapi.EmptyWorkingSet(handle)
            except Exception:
                pass

        mem_after = cls.get_memory_usage_mb()
        freed = max(0.0, round(mem_before - mem_after, 2))

        return {
            "collected_objects": collected,
            "mem_before_mb": mem_before,
            "mem_after_mb": mem_after,
            "freed_mb": freed
        }

    @classmethod
    def get_stats(cls) -> MemoryStats:
        rss = cls.get_memory_usage_mb()
        counts = gc.get_count()
        return MemoryStats(
            rss_mb=rss,
            peak_rss_mb=rss,
            gc_counts=counts,
            python_version=sys.version.split()[0]
        )

    @classmethod
    @contextmanager
    def memory_guard(cls, operation_name: str = "operation") -> Generator[None, None, None]:
        """
        Context manager that automatically cleans up memory upon exiting heavy code blocks.
        """
        try:
            yield
        finally:
            cls.collect_garbage(trim_os_working_set=True)

