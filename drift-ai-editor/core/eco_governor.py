"""
Adaptive Eco-Governor & Thermal Governor for CutWire Drift AI.
Throttles process priority, caps thread utilization to preserve responsive desktop multitasking,
and limits CPU thermal spikes on high-core processors (Intel Xeon E5-2650 v4).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import sys
import ctypes

@dataclass
class EcoPolicy:
    mode: str                    # 'eco_silent', 'balanced', 'maximum_performance'
    total_system_threads: int
    assigned_worker_threads: int
    reserved_os_threads: int
    windows_priority_class: str
    target_cpu_cap_percent: int

class EcoGovernor:
    """
    Dynamically adjusts Windows process priority and CPU thread budgets to ensure
    cool, quiet, and 100% responsive multitasking during heavy renders.
    """

    # Windows Priority Class Constants
    IDLE_PRIORITY_CLASS = 0x00000040
    BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
    NORMAL_PRIORITY_CLASS = 0x00000020
    ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
    HIGH_PRIORITY_CLASS = 0x00000080

    @classmethod
    def calculate_thread_budget(
        cls,
        mode: str = "eco_silent",
        total_threads: Optional[int] = None
    ) -> EcoPolicy:
        if total_threads is None:
            total_threads = os.cpu_count() or 4

        if mode == "eco_silent":
            # Reserva 4 threads para o Windows/Navegador; mínimo de 2 threads
            reserved = 4 if total_threads >= 8 else 2
            assigned = max(2, total_threads - reserved)
            prio = "BELOW_NORMAL"
            cap = 80
        elif mode == "balanced":
            reserved = 2 if total_threads >= 6 else 1
            assigned = max(2, total_threads - reserved)
            prio = "BELOW_NORMAL"
            cap = 90
        else: # maximum_performance
            reserved = 0
            assigned = total_threads
            prio = "NORMAL"
            cap = 100

        return EcoPolicy(
            mode=mode,
            total_system_threads=total_threads,
            assigned_worker_threads=assigned,
            reserved_os_threads=reserved,
            windows_priority_class=prio,
            target_cpu_cap_percent=cap
        )

    @classmethod
    def apply_process_priority(cls, priority: str = "BELOW_NORMAL") -> bool:
        """
        Sets process priority class in Windows kernel to ensure smooth UI responsiveness.
        """
        if sys.platform != "win32":
            return False

        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            prio_map = {
                "IDLE": cls.IDLE_PRIORITY_CLASS,
                "BELOW_NORMAL": cls.BELOW_NORMAL_PRIORITY_CLASS,
                "NORMAL": cls.NORMAL_PRIORITY_CLASS,
                "ABOVE_NORMAL": cls.ABOVE_NORMAL_PRIORITY_CLASS,
                "HIGH": cls.HIGH_PRIORITY_CLASS
            }
            code = prio_map.get(priority.upper(), cls.BELOW_NORMAL_PRIORITY_CLASS)
            res = ctypes.windll.kernel32.SetPriorityClass(handle, code)
            return bool(res)
        except Exception:
            return False
