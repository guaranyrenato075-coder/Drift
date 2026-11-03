"""
Content-Addressable Storage (CAS) & NTFS Hardlink Deduplicator for CutWire Drift AI.
Eliminates duplicate storage of repeated stock assets, soundtrack stems, and sound effects
by storing a single physical block on disk and generating zero-byte O(1) NTFS hardlinks across projects.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
import os
import hashlib
from pathlib import Path

@dataclass
class DeduplicationStats:
    total_unique_assets: int
    total_referenced_links: int
    disk_saved_mb: float
    total_stored_mb: float
    savings_percentage: float

class MediaDeduplicator:
    """
    Intelligent media asset deduplication engine using SHA-256 content addressing and NTFS links.
    """

    def __init__(self, master_store_dir: str = "d:/CUTWIREDRIFT/.cas_store"):
        self.store_dir = Path(master_store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, str] = {}  # sha256 -> master_file_path
        self.link_counts: Dict[str, int] = {} # sha256 -> number of hardlinks created
        self._scan_existing_store()

    def _scan_existing_store(self):
        if self.store_dir.exists():
            for f in self.store_dir.glob("**/*"):
                if f.is_file():
                    sha = f.stem
                    self.registry[sha] = str(f).replace("\\", "/")
                    self.link_counts[sha] = 1

    @classmethod
    def compute_sha256(cls, file_path: str, chunk_size: int = 65536) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()

    def deduplicate_and_link(
        self,
        source_temp_path: str,
        destination_project_path: str
    ) -> Tuple[str, bool]:
        """
        Stores physical asset in CAS if unique, otherwise links to existing master file.
        Returns: (final_path, is_deduplicated)
        """
        if not os.path.exists(source_temp_path):
            return source_temp_path, False

        file_size = os.path.getsize(source_temp_path)
        sha = self.compute_sha256(source_temp_path)

        dest_p = Path(destination_project_path)
        dest_p.parent.mkdir(parents=True, exist_ok=True)

        is_dedup = False

        if sha in self.registry:
            # Asset já existe no armazenamento mestre! Não gasta espaço adicional em disco.
            master_path = self.registry[sha]
            if dest_p.exists():
                try:
                    dest_p.unlink()
                except Exception:
                    pass
            try:
                os.link(master_path, str(dest_p))
                is_dedup = True
            except Exception:
                # Fallback se volumes forem diferentes
                import shutil
                shutil.copyfile(master_path, str(dest_p))
            self.link_counts[sha] = self.link_counts.get(sha, 1) + 1
            return str(dest_p).replace("\\", "/"), True
        else:
            # Primeiro encontro do asset: armazena no CAS mestre
            shard = sha[:2]
            target_dir = self.store_dir / shard
            target_dir.mkdir(parents=True, exist_ok=True)
            master_p = target_dir / f"{sha}.bin"

            # Move ou copia para o master store
            import shutil
            shutil.copyfile(source_temp_path, str(master_p))
            self.registry[sha] = str(master_p).replace("\\", "/")
            self.link_counts[sha] = 1

            # Cria o hardlink para o projeto de destino
            if dest_p.exists():
                try:
                    dest_p.unlink()
                except Exception:
                    pass
            try:
                os.link(str(master_p), str(dest_p))
            except Exception:
                shutil.copyfile(str(master_p), str(dest_p))

            return str(dest_p).replace("\\", "/"), False

    def get_stats(self) -> DeduplicationStats:
        unique_count = len(self.registry)
        total_links = sum(self.link_counts.values())

        total_stored_bytes = 0
        for p in self.registry.values():
            if os.path.exists(p):
                total_stored_bytes += os.path.getsize(p)

        # Cada link além do primeiro representa economia de 100% de espaço
        avg_size = (total_stored_bytes / max(1, unique_count))
        saved_links = max(0, total_links - unique_count)
        saved_bytes = saved_links * avg_size

        saved_mb = round(saved_bytes / (1024 * 1024), 2)
        stored_mb = round(total_stored_bytes / (1024 * 1024), 2)
        
        total_potential_bytes = saved_bytes + total_stored_bytes
        savings_pct = round((saved_bytes / total_potential_bytes * 100.0) if total_potential_bytes > 0 else 0.0, 1)

        return DeduplicationStats(
            total_unique_assets=unique_count,
            total_referenced_links=total_links,
            disk_saved_mb=saved_mb,
            total_stored_mb=stored_mb,
            savings_percentage=savings_pct
        )
