"""
Render Checkpoint and Crash-Proof Resume Manager for CutWire Drift AI.
Ensures zero progress loss during long-form (10-30+ min) video exports by caching completed
parallel chunks and resuming interrupted renders from the exact point of interruption.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import os
import json
import time

@dataclass
class ChunkCheckpointEntry:
    chunk_index: int
    output_file: str
    expected_duration: float
    file_size_bytes: int
    is_completed: bool
    completed_at_timestamp: float

@dataclass
class RenderCheckpointState:
    project_id: str
    total_chunks: int
    completed_chunks: int
    pending_chunks: List[int]
    is_fully_completed: bool
    checkpoint_file: str
    entries: Dict[int, ChunkCheckpointEntry]

class RenderCheckpointManager:
    """
    Manages persistent disk checkpoints for chunked video rendering.
    """

    @classmethod
    def get_checkpoint_path(cls, output_dir: str, project_id: str) -> str:
        clean_id = "".join(c for c in project_id if c.isalnum() or c in ("-", "_"))
        return os.path.join(output_dir, f".checkpoint_{clean_id}.json").replace("\\", "/")

    @classmethod
    def load_or_init_state(
        cls,
        project_id: str,
        total_chunks: int,
        output_dir: str = "d:/CUTWIREDRIFT/renders"
    ) -> RenderCheckpointState:
        os.makedirs(output_dir, exist_ok=True)
        ckpt_path = cls.get_checkpoint_path(output_dir, project_id)

        entries: Dict[int, ChunkCheckpointEntry] = {}

        if os.path.exists(ckpt_path):
            try:
                with open(ckpt_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                raw_entries = data.get("entries", {})
                for k, v in raw_entries.items():
                    idx = int(k)
                    file_path = v.get("output_file", "")
                    
                    # Validação física: o arquivo deve existir no disco e ter tamanho > 0
                    exists = os.path.exists(file_path) and os.path.getsize(file_path) > 1024
                    
                    entries[idx] = ChunkCheckpointEntry(
                        chunk_index=idx,
                        output_file=file_path,
                        expected_duration=v.get("expected_duration", 0.0),
                        file_size_bytes=os.path.getsize(file_path) if exists else 0,
                        is_completed=exists and v.get("is_completed", False),
                        completed_at_timestamp=v.get("completed_at_timestamp", 0.0)
                    )
            except Exception:
                entries = {}

        # Preenche os chunks que ainda não possuem registro
        for idx in range(1, total_chunks + 1):
            if idx not in entries:
                entries[idx] = ChunkCheckpointEntry(
                    chunk_index=idx,
                    output_file="",
                    expected_duration=0.0,
                    file_size_bytes=0,
                    is_completed=False,
                    completed_at_timestamp=0.0
                )

        completed_count = sum(1 for e in entries.values() if e.is_completed)
        pending = [idx for idx, e in entries.items() if not e.is_completed]
        is_done = (completed_count == total_chunks) and (total_chunks > 0)

        return RenderCheckpointState(
            project_id=project_id,
            total_chunks=total_chunks,
            completed_chunks=completed_count,
            pending_chunks=sorted(pending),
            is_fully_completed=is_done,
            checkpoint_file=ckpt_path,
            entries=entries
        )

    @classmethod
    def record_chunk_completed(
        cls,
        state: RenderCheckpointState,
        chunk_index: int,
        output_file: str,
        duration: float
    ) -> None:
        file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
        state.entries[chunk_index] = ChunkCheckpointEntry(
            chunk_index=chunk_index,
            output_file=output_file,
            expected_duration=duration,
            file_size_bytes=file_size,
            is_completed=(file_size > 1024),
            completed_at_timestamp=time.time()
        )

        state.completed_chunks = sum(1 for e in state.entries.values() if e.is_completed)
        state.pending_chunks = sorted([idx for idx, e in state.entries.items() if not e.is_completed])
        state.is_fully_completed = (state.completed_chunks == state.total_chunks)

        # Salva atomicamente no disco
        cls.save_state(state)

    @classmethod
    def save_state(cls, state: RenderCheckpointState) -> None:
        raw_dict = {
            "project_id": state.project_id,
            "total_chunks": state.total_chunks,
            "completed_chunks": state.completed_chunks,
            "is_fully_completed": state.is_fully_completed,
            "updated_at": time.time(),
            "entries": {str(k): asdict(v) for k, v in state.entries.items()}
        }
        temp_file = state.checkpoint_file + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(raw_dict, f, indent=2)
        os.replace(temp_file, state.checkpoint_file)

    @classmethod
    def cleanup_checkpoint(cls, state: RenderCheckpointState) -> None:
        """Removes the checkpoint file once the final video is assembled."""
        if os.path.exists(state.checkpoint_file):
            try:
                os.remove(state.checkpoint_file)
            except OSError:
                pass
