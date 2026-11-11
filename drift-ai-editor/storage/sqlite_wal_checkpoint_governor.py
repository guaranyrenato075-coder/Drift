"""
Módulo de Governança de Checkpoint e Compactação WAL do SQLite (SQLite WAL Checkpoint Governor).
Executa a manutenção assíncrona do Write-Ahead Logging (WAL) do banco de dados do projeto.
Aplica checkpoints passivos (wal_checkpoint PASSIVE) e incremental vacuum para desfragmentar
o arquivo de banco, liberar espaço em disco e evitar retenção desnecessária de cache em RAM.
"""

import sqlite3
import os
from pathlib import Path
from typing import Dict, Any, Optional
from config import DB_PATH


class SQLiteWALCheckpointGovernor:
    """
    Governador de manutenção e compactação de banco de dados SQLite em modo WAL.
    """

    @classmethod
    def execute_passive_checkpoint(cls, db_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Executa um checkpoint passivo que descarrega páginas WAL para o banco principal
        sem bloquear conexões de leitura simultâneas de usuários ou da UI.
        """
        target_path = Path(db_path) if db_path else DB_PATH
        if not target_path.exists():
            return {"status": "error", "message": f"Banco de dados não encontrado: {target_path}"}

        wal_file = Path(f"{target_path}-wal")
        wal_size_before = wal_file.stat().st_size if wal_file.exists() else 0

        conn = sqlite3.connect(str(target_path))
        try:
            # wal_checkpoint(PASSIVE): transfere páginas sem esperar leitores terminarem
            cursor = conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
            checkpoint_result = cursor.fetchone()
            # Retorna: (busy, log_pages, checkpointed_pages)
            busy = checkpoint_result[0] if checkpoint_result else 0
            log_pages = checkpoint_result[1] if checkpoint_result else 0
            checkpointed = checkpoint_result[2] if checkpoint_result else 0

            # Otimização incremental de espaço
            conn.execute("PRAGMA incremental_vacuum(50);")
            conn.commit()
        finally:
            conn.close()

        wal_size_after = wal_file.stat().st_size if wal_file.exists() else 0
        freed_bytes = max(0, wal_size_before - wal_size_after)

        return {
            "status": "success",
            "db_path": str(target_path),
            "busy_status": bool(busy),
            "wal_log_pages": log_pages,
            "pages_checkpointed": checkpointed,
            "wal_bytes_before": wal_size_before,
            "wal_bytes_after": wal_size_after,
            "space_freed_kb": round(freed_bytes / 1024, 2),
            "recommendation": "Checkpoint passivo concluído com sucesso. Páginas descarregadas no disco sem lock de leitura."
        }
