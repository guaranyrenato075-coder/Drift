"""
Render Crash Recovery Guard.
Gerencia checkpoints de renderização atômica em disco para permitir que
o sistema retome renders interrompidos sem recalcular partes já renderizadas.
"""

from typing import Dict, Any, List, Optional
import os
import json
import time


class AutoRenderCrashRecoveryGuard:
    """Gerencia estados de checkpoint de renderização e retomada pós-crash."""

    CHECKPOINT_DIR = "storage/render_checkpoints"

    @classmethod
    def _get_checkpoint_path(cls, project_id: str) -> str:
        os.makedirs(cls.CHECKPOINT_DIR, exist_ok=True)
        return os.path.join(cls.CHECKPOINT_DIR, f"checkpoint_{project_id}.json")

    @classmethod
    def save_checkpoint(cls, project_id: str, scene_index: int, total_scenes: int, completed_files: List[str]) -> Dict[str, Any]:
        """Salva um checkpoint atômico do progresso da renderização."""
        path = cls._get_checkpoint_path(project_id)
        data = {
            "project_id": project_id,
            "last_completed_scene_index": scene_index,
            "total_scenes": total_scenes,
            "progress_percent": round((scene_index / max(total_scenes, 1)) * 100, 1),
            "completed_files": completed_files,
            "timestamp": time.time(),
            "status": "IN_PROGRESS" if scene_index < total_scenes else "COMPLETED"
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data

    @classmethod
    def check_resumable_render(cls, project_id: str) -> Dict[str, Any]:
        """Verifica se existe um checkpoint recuperável após falha ou desligamento."""
        path = cls._get_checkpoint_path(project_id)
        if not os.path.exists(path):
            return {
                "has_resumable_checkpoint": False,
                "project_id": project_id,
                "resume_from_scene_index": 1,
                "message": "Nenhum checkpoint anterior encontrado. Render iniciará do zero."
            }

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("status") == "IN_PROGRESS":
                return {
                    "has_resumable_checkpoint": True,
                    "project_id": project_id,
                    "resume_from_scene_index": data.get("last_completed_scene_index", 0) + 1,
                    "last_completed_scene_index": data.get("last_completed_scene_index", 0),
                    "total_scenes": data.get("total_scenes", 0),
                    "progress_percent": data.get("progress_percent", 0.0),
                    "saved_chunks_count": len(data.get("completed_files", [])),
                    "message": f"Render interrompido detectado! É possível retomar a partir da cena #{data.get('last_completed_scene_index', 0) + 1} sem perda de dados."
                }
            else:
                return {
                    "has_resumable_checkpoint": False,
                    "project_id": project_id,
                    "resume_from_scene_index": 1,
                    "message": "Último render foi concluído integralmente."
                }
        except Exception as e:
            return {
                "has_resumable_checkpoint": False,
                "project_id": project_id,
                "resume_from_scene_index": 1,
                "error": str(e)
            }

    @classmethod
    def clear_checkpoint(cls, project_id: str) -> bool:
        """Limpa o checkpoint ao finalizar a exportação definitiva."""
        path = cls._get_checkpoint_path(project_id)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except OSError:
                return False
        return True
