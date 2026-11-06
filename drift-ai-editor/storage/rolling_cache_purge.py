"""
Rolling Cache FIFO Purge Manager for CutWire Drift AI.
Enforces strict disk storage quotas (default 4 GB cap), automatically pruning oldest
intermediate chunks and cached download files to prevent disk exhaustion.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import time

@dataclass
class CachePurgeReport:
    directory_scanned: str
    total_files_before: int
    total_bytes_before: int
    files_deleted: int
    bytes_reclaimed: int
    total_bytes_after: int
    is_quota_respected: bool

class RollingCachePurgeManager:
    """
    Maintains a bounded disk cache footprint through chronological FIFO eviction.
    """

    @classmethod
    def enforce_cache_quota(
        cls,
        cache_dir: str = "d:/CUTWIREDRIFT/renders",
        max_bytes_quota: int = 4 * 1024 * 1024 * 1024, # 4 GB
        protected_prefixes: Optional[List[str]] = None
    ) -> CachePurgeReport:
        if not os.path.exists(cache_dir):
            return CachePurgeReport(
                directory_scanned=cache_dir,
                total_files_before=0,
                total_bytes_before=0,
                files_deleted=0,
                bytes_reclaimed=0,
                total_bytes_after=0,
                is_quota_respected=True
            )

        if protected_prefixes is None:
            protected_prefixes = [".checkpoint", "final", "output_master"]

        file_entries = []
        total_size = 0

        for root, _, files in os.walk(cache_dir):
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    stat = os.stat(full_path)
                    file_entries.append((stat.st_mtime, stat.st_size, full_path, f))
                    total_size += stat.st_size
                except OSError:
                    pass

        total_files_before = len(file_entries)
        total_bytes_before = total_size

        # Se estiver dentro da cota, nada a purgar
        if total_size <= max_bytes_quota:
            return CachePurgeReport(
                directory_scanned=cache_dir,
                total_files_before=total_files_before,
                total_bytes_before=total_bytes_before,
                files_deleted=0,
                bytes_reclaimed=0,
                total_bytes_after=total_bytes_before,
                is_quota_respected=True
            )

        # Ordena do mais antigo para o mais novo (FIFO)
        file_entries.sort(key=lambda x: x[0])

        files_deleted = 0
        bytes_reclaimed = 0

        for mtime, fsize, path, fname in file_entries:
            if total_size <= max_bytes_quota:
                break

            # Não apaga arquivos protegidos
            if any(fname.lower().startswith(p.lower()) for p in protected_prefixes):
                continue

            try:
                os.remove(path)
                files_deleted += 1
                bytes_reclaimed += fsize
                total_size -= fsize
            except OSError:
                pass

        return CachePurgeReport(
            directory_scanned=cache_dir,
            total_files_before=total_files_before,
            total_bytes_before=total_bytes_before,
            files_deleted=files_deleted,
            bytes_reclaimed=bytes_reclaimed,
            total_bytes_after=total_size,
            is_quota_respected=(total_size <= max_bytes_quota)
        )
