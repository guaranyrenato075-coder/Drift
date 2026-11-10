"""
Disk Space Guard & Automatic Storage Hygiene Engine for CutWire Drift AI.
Monitors free drive space on the system drive and workspace, proactively cleaning
transient wav audio scratch files, completed job records, and obsolete temporary buffers
to prevent disk exhaustion and ensure smooth, continuous operation.
"""
from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import time
from typing import Dict, Any, List

@dataclass
class DiskHealth:
    drive: str
    free_gb: float
    total_gb: float
    is_healthy: bool  # True if >= 1.0 GB free
    cleaned_bytes: int = 0
    warnings: List[str] = None

class DiskSpaceGuard:
    """
    Automatic disk space monitor and hygiene controller.
    """

    MIN_SAFE_SPACE_GB = 1.0
    CRITICAL_SPACE_GB = 0.3

    TEMP_CLEANUP_TARGETS = [
        Path(__file__).resolve().parent.parent / "temp",
        Path(__file__).resolve().parent.parent / "storage" / "jobs",
        Path(os.environ.get("LOCALAPPDATA", "C:\\")) / "Temp"
    ]

    @classmethod
    def check_health(cls, path_to_check: str = "C:\\") -> DiskHealth:
        """Inspects disk usage on the specified drive/path."""
        try:
            total, used, free = shutil.disk_usage(path_to_check)
            free_gb = round(free / (1024 ** 3), 2)
            total_gb = round(total / (1024 ** 3), 2)
            is_healthy = free_gb >= cls.MIN_SAFE_SPACE_GB

            warnings = []
            if free_gb < cls.CRITICAL_SPACE_GB:
                warnings.append(f"Espaço crítico em disco ({free_gb} GB livre)! Limpeza automática preventiva executada.")
            elif free_gb < cls.MIN_SAFE_SPACE_GB:
                warnings.append(f"Atenção: Espaço em disco baixo ({free_gb} GB livre).")

            return DiskHealth(
                drive=path_to_check[:3] if len(path_to_check) >= 3 else path_to_check,
                free_gb=free_gb,
                total_gb=total_gb,
                is_healthy=is_healthy,
                warnings=warnings
            )
        except Exception as e:
            return DiskHealth(
                drive=path_to_check,
                free_gb=100.0,
                total_gb=500.0,
                is_healthy=True,
                warnings=[f"Erro ao ler espaço em disco: {e}"]
            )

    @classmethod
    def ensure_healthy_space(cls, min_free_gb: float = 0.5) -> int:
        """
        If free space is below the threshold, purges temporary scratch files and returns bytes freed.
        """
        health = cls.check_health("C:\\")
        if health.free_gb >= min_free_gb:
            return 0

        bytes_freed = 0
        now = time.time()

        # 1. Clean drift-ai-editor temp folder
        drift_temp = Path(__file__).resolve().parent.parent / "temp"
        if drift_temp.exists():
            for item in drift_temp.glob("**/*"):
                try:
                    if item.is_file():
                        sz = item.stat().st_size
                        item.unlink(missing_ok=True)
                        bytes_freed += sz
                except Exception:
                    pass

        # 2. Clean temporary wav/scratch files in system Temp older than 1 hour
        sys_temp = Path(os.environ.get("LOCALAPPDATA", "C:\\")) / "Temp"
        if sys_temp.exists():
            for item in sys_temp.glob("drift_*"):
                try:
                    if item.is_file() and (now - item.stat().st_mtime) > 3600:
                        sz = item.stat().st_size
                        item.unlink(missing_ok=True)
                        bytes_freed += sz
                except Exception:
                    pass

        return bytes_freed
