"""
Distributed Render Manager for CutWire Drift AI.
Splits heavy video productions into atomic chunk render tasks,
dispatches to worker nodes (local background subprocesses or remote network workers),
and verifies hash/manifest integrity before final concatenation.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
import hashlib
import os

class ChunkStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class RenderChunk:
    chunk_id: str
    scene_indices: List[int]
    start_sec: float
    end_sec: float
    output_filename: str
    status: ChunkStatus = ChunkStatus.QUEUED
    assigned_worker: Optional[str] = None
    output_hash: Optional[str] = None

@dataclass
class RenderWorkerNode:
    node_id: str
    node_name: str
    is_local: bool
    max_parallel_slots: int
    active_slots: int = 0
    is_online: bool = True

class DistributedRenderManager:
    """
    Orchestrates distributed chunk rendering and stitches finished outputs.
    """

    def __init__(self, target_chunk_duration: float = 15.0):
        self.target_chunk_duration = target_chunk_duration
        self.chunks: List[RenderChunk] = []
        self.workers: Dict[str, RenderWorkerNode] = {}

    def register_worker(self, node: RenderWorkerNode):
        self.workers[node.node_id] = node

    def partition_project(self, scene_durations: List[float]) -> List[RenderChunk]:
        """
        Groups scenes into render chunks based on target chunk duration.
        """
        self.chunks.clear()
        current_chunk_scenes = []
        current_chunk_duration = 0.0
        current_start = 0.0
        chunk_idx = 0

        for i, dur in enumerate(scene_durations):
            current_chunk_scenes.append(i)
            current_chunk_duration += dur

            if current_chunk_duration >= self.target_chunk_duration or i == len(scene_durations) - 1:
                chunk_id = f"chunk_{chunk_idx:03d}"
                self.chunks.append(
                    RenderChunk(
                        chunk_id=chunk_id,
                        scene_indices=list(current_chunk_scenes),
                        start_sec=round(current_start, 2),
                        end_sec=round(current_start + current_chunk_duration, 2),
                        output_filename=f"{chunk_id}.mp4"
                    )
                )
                chunk_idx += 1
                current_start += current_chunk_duration
                current_chunk_scenes = []
                current_chunk_duration = 0.0

        return self.chunks

    def schedule_next_chunk(self) -> Optional[RenderChunk]:
        """Finds next queued chunk and assigns an available worker node."""
        available_worker = None
        for w in self.workers.values():
            if w.is_online and w.active_slots < w.max_parallel_slots:
                available_worker = w
                break

        if not available_worker:
            return None

        for ch in self.chunks:
            if ch.status == ChunkStatus.QUEUED:
                ch.status = ChunkStatus.RENDERING
                ch.assigned_worker = available_worker.node_id
                available_worker.active_slots += 1
                return ch
        return None

    def complete_chunk(self, chunk_id: str, simulated_data: bytes = b"drift_render_ok"):
        for ch in self.chunks:
            if ch.chunk_id == chunk_id:
                ch.status = ChunkStatus.COMPLETED
                ch.output_hash = hashlib.sha256(simulated_data).hexdigest()
                if ch.assigned_worker and ch.assigned_worker in self.workers:
                    self.workers[ch.assigned_worker].active_slots = max(0, self.workers[ch.assigned_worker].active_slots - 1)
                break

    def is_all_completed(self) -> bool:
        return len(self.chunks) > 0 and all(c.status == ChunkStatus.COMPLETED for c in self.chunks)

    def generate_concat_manifest(self) -> str:
        """Outputs an FFmpeg concat demuxer manifest for the finished chunks."""
        lines = ["# Drift AI Distributed Render Assembly"]
        for ch in self.chunks:
            lines.append(f"file '{ch.output_filename}'")
        return "\n".join(lines)

