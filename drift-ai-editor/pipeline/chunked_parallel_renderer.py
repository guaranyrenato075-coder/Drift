"""
Chunked Parallel Render Pipeline for CutWire Drift AI.
Partitions the scene timeline into atomic render chunks, distributing workload
across all 24 CPU threads (or GPU NVENC sessions when available), and stitches
final video via lossless stream copy concatenation in sub-seconds.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import math
import uuid
from models.scene_plan import ProjectPlan, Scene
from core.hardware_telemetry import HardwareTelemetryProfiler

@dataclass
class RenderTaskChunk:
    chunk_index: int
    scene_orders: List[int]
    start_time: float
    duration: float
    output_temp_file: str
    encoder_args: List[str]
    is_gpu_mode: bool
    assigned_thread_budget: int

@dataclass
class ParallelRenderPlan:
    project_id: str
    total_scenes: int
    total_chunks: int
    concurrency_slots: int
    encoder_mode: str
    estimated_speedup_factor: float      # ex: 3.5x mais rápido que encode sequencial
    chunks: List[RenderTaskChunk]
    ffmpeg_concat_manifest: str         # Conteúdo para 'concat.txt' (-c copy)
    final_output_path: str

class ChunkedParallelRenderer:
    """
    Orchestrates parallel multi-core rendering tailored for high-thread CPUs and GPUs.
    """

    @classmethod
    def create_parallel_plan(
        cls,
        plan: ProjectPlan,
        target_chunk_sec: float = 18.0,
        output_dir: str = "d:/CUTWIREDRIFT/renders"
    ) -> ParallelRenderPlan:
        telemetry = HardwareTelemetryProfiler.get_telemetry()
        has_nvenc = telemetry.is_gpu_accelerated
        total_threads = telemetry.total_threads
        concurrency = telemetry.recommended_concurrency

        clean_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        proj_id = getattr(plan, "project_id", "drift_proj")

        chunks: List[RenderTaskChunk] = []
        concat_lines: List[str] = []

        cur_scenes: List[int] = []
        cur_dur = 0.0
        cur_start = 0.0
        chunk_idx = 1

        # Alocação de threads por chunk na CPU (ex: 24 threads / 4 slots = 6 threads por processo)
        threads_per_chunk = max(2, total_threads // max(1, concurrency))

        for idx, s in enumerate(plan.scenes):
            dur = s.duration if s.duration > 0 else 4.0
            cur_scenes.append(s.order)
            cur_dur += dur

            # Se atingiu o tamanho do bloco ou é a última cena
            if cur_dur >= target_chunk_sec or idx == len(plan.scenes) - 1:
                chunk_file = os.path.join(output_dir, f"{clean_title}_chunk_{chunk_idx:03d}.mp4").replace("\\", "/")
                
                if has_nvenc:
                    encoder_args = [
                        "-c:v", "h264_nvenc",
                        "-preset", "p4",
                        "-b:v", "8M",
                        "-c:a", "aac",
                        "-b:a", "192k"
                    ]
                else:
                    # Otimizado para os 24 threads do Xeon
                    encoder_args = [
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-tune", "fastdecode",
                        "-threads", str(threads_per_chunk),
                        "-b:v", "8M",
                        "-c:a", "aac",
                        "-b:a", "192k"
                    ]

                chunks.append(RenderTaskChunk(
                    chunk_index=chunk_idx,
                    scene_orders=list(cur_scenes),
                    start_time=round(cur_start, 2),
                    duration=round(cur_dur, 2),
                    output_temp_file=chunk_file,
                    encoder_args=encoder_args,
                    is_gpu_mode=has_nvenc,
                    assigned_thread_budget=threads_per_chunk
                ))

                concat_lines.append(f"file '{chunk_file}'")

                cur_start += cur_dur
                cur_scenes = []
                cur_dur = 0.0
                chunk_idx += 1

        speedup = round(min(concurrency * 0.88, 4.2), 1)
        final_out = os.path.join("d:/CUTWIREDRIFT", f"{clean_title}_Final.mp4").replace("\\", "/")

        return ParallelRenderPlan(
            project_id=proj_id,
            total_scenes=len(plan.scenes),
            total_chunks=len(chunks),
            concurrency_slots=concurrency,
            encoder_mode=telemetry.active_encoder_mode,
            estimated_speedup_factor=speedup,
            chunks=chunks,
            ffmpeg_concat_manifest="\n".join(concat_lines),
            final_output_path=final_out
        )

    @classmethod
    def create_chapter_render_plan(
        cls,
        scenes: List[Scene],
        chapter_title: str,
        output_master_file: str,
        target_chunk_sec: float = 18.0
    ) -> ParallelRenderPlan:
        """
        Creates an optimized parallel chunk render plan specifically for an isolated mega-doc chapter.
        """
        dummy_plan = ProjectPlan(
            project_id=f"chap_{uuid.uuid4().hex[:6]}" if "uuid" in globals() else "chap_render",
            title=chapter_title,
            scenes=scenes
        )
        plan_res = cls.create_parallel_plan(
            plan=dummy_plan,
            target_chunk_sec=target_chunk_sec,
            output_dir=os.path.dirname(output_master_file) or "d:/CUTWIREDRIFT/renders"
        )
        plan_res.final_output_path = output_master_file
        return plan_res


