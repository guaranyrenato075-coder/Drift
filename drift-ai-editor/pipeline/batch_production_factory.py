"""
Autonomous Batch Production Factory (Piloto Automático em Lote) for CutWire Drift AI.
Produces end-to-end multi-video catalogs unattended: accepts lists of topics,
generates scripts, synthesizes voices, fetches and auto-remediates commercial media,
mixes adaptive soundtracks with auto-ducking, generates karaoke captions, renders thumbnails,
and packages publication-ready SEO deliverables into structured folders.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import time
import json
import threading
from pathlib import Path

from models.scene_plan import ProjectPlan, ProjectConfig, Scene, MediaCandidate
from analysis.script_generator import ScriptGenerator
from analysis.segmenter import ScriptSegmenter
from analysis.visual_planner import VisualPlanner
from voice.local_neural_fallback import LocalNeuralVoiceFallback
from media.copyright_analyzer import CopyrightAnalyzer
from audio.auto_ducking_soundtrack import AutoDuckingSoundtrackMixer
from editing.karaoke_subtitle_generator import KaraokeSubtitleGenerator
from pipeline.thumbnail_studio import ThumbnailStudio
from pipeline.publication_seo_kit import PublicationSeoKitGenerator
from pipeline.chunked_parallel_renderer import ChunkedParallelRenderer
from storage.repository import ProjectRepository

@dataclass
class BatchVideoJob:
    job_id: str
    topic: str
    status: str             # "queued", "generating_script", "synthesizing_voice", "remediating_media", "ready", "failed"
    progress_pct: int       # 0 a 100%
    project_id: Optional[str] = None
    output_dir: Optional[str] = None
    title: Optional[str] = None
    total_scenes: int = 0
    duration_sec: float = 0.0
    copyright_monetizable: bool = True
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

@dataclass
class BatchFactoryState:
    factory_id: str
    total_jobs: int
    completed_jobs: int
    active_job_index: int
    is_running: bool
    overall_progress_pct: float
    output_root_dir: str
    jobs: List[BatchVideoJob]

class BatchProductionFactory:
    """
    Unattended, multi-video mass production orchestrator.
    """

    def __init__(self, output_root: str = "d:/CUTWIREDRIFT/batch_output", repo: Optional[ProjectRepository] = None):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.repo = repo or ProjectRepository()
        self.jobs: List[BatchVideoJob] = []
        self.is_running = False
        self.active_job_index = 0
        self._thread: Optional[threading.Thread] = None

    def create_batch_from_topics(self, topics: List[str]) -> List[BatchVideoJob]:
        """
        Enqueues a list of topics for autonomous mass production.
        """
        clean_topics = [t.strip() for t in topics if t.strip()]
        self.jobs = [
            BatchVideoJob(
                job_id=f"batch_{int(time.time())}_{idx+1:02d}",
                topic=t,
                status="queued",
                progress_pct=0
            )
            for idx, t in enumerate(clean_topics)
        ]
        self.active_job_index = 0
        return self.jobs

    def start_batch_async(self) -> bool:
        """
        Starts autonomous batch execution in background thread.
        """
        if self.is_running or not self.jobs:
            return False

        self.is_running = True
        self._thread = threading.Thread(target=self._run_factory_loop, daemon=True)
        self._thread.start()
        return True

    def stop_batch(self):
        """Signals the batch worker to stop after the current video."""
        self.is_running = False

    def _run_factory_loop(self):
        for idx, job in enumerate(self.jobs):
            if not self.is_running:
                break

            self.active_job_index = idx
            self._process_single_video(job)

        self.is_running = False

    def _process_single_video(self, job: BatchVideoJob):
        try:
            job.status = "generating_script"
            job.progress_pct = 15

            # 1. Geração de roteiro via IA
            script_text = ScriptGenerator.generate(job.topic)
            clean_title = "".join(c for c in job.topic if c.isalnum() or c in (" ", "_", "-")).strip()
            job.title = clean_title

            # 2. Segmentação em Cenas e Planejamento Visual
            scenes = ScriptSegmenter.parse(script_text)
            if not scenes:
                # Fallback de pelo menos 3 cenas se o texto for curto
                scenes = [
                    Scene(order=1, narration_text=f"Apresentando uma análise profunda sobre {job.topic}.", duration=4.0),
                    Scene(order=2, narration_text=f"Os princípios fundamentais de {job.topic} que mudam sua percepção.", duration=5.0),
                    Scene(order=3, narration_text="Aplique este conhecimento hoje e transforme seus resultados.", duration=4.5)
                ]

            VisualPlanner.plan_project(scenes)
            job.total_scenes = len(scenes)
            job.progress_pct = 35

            # 3. Síntese de Vozes Neurais Offline / TTS Local
            job.status = "synthesizing_voice"
            video_slug = "".join(c for c in clean_title if c.isalnum() or c in ("_", "-")).replace(" ", "_").lower()
            job_dir = self.output_root / f"{job.job_id}_{video_slug}"
            job_dir.mkdir(parents=True, exist_ok=True)
            job.output_dir = str(job_dir).replace("\\", "/")

            audio_dir = job_dir / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            total_dur = 0.0
            for s in scenes:
                LocalNeuralVoiceFallback.process_scene_fallback(s, output_folder=str(audio_dir))
                total_dur += (s.duration if s.duration > 0 else 4.0)

            job.duration_sec = round(total_dur, 2)
            job.progress_pct = 55

            # 4. Criação do ProjectPlan
            plan = ProjectPlan(
                project_id=job.job_id,
                title=clean_title,
                config=ProjectConfig(aspect_ratio="16:9", media_type="video", language="pt"),
                scenes=scenes
            )

            # 5. Mídias e Auto-Remediação de Copyright 100% Comercial
            job.status = "remediating_media"
            remed_res = CopyrightAnalyzer.auto_remediate_project(plan)
            job.copyright_monetizable = remed_res.get("is_safe_for_monetization", True)
            job.progress_pct = 70

            # 6. Trilha Sonora Adaptativa com Auto-Ducking
            mix_plan = AutoDuckingSoundtrackMixer.generate_mix_plan(plan)

            # 7. Legendas Cinéticas Estilo Karaokê / Hormozi (.ASS)
            karaoke = KaraokeSubtitleGenerator.generate_ass_script(plan)
            ass_path = job_dir / "legendas_karaoke.ass"
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(karaoke.ass_script_content)

            # 8. Thumbnails de Alta Conversão com Heatmap
            thumbnails = ThumbnailStudio.generate_ab_variants(plan)
            thumbs_info_path = job_dir / "thumbnails_estrategias.json"
            with open(thumbs_info_path, "w", encoding="utf-8") as f:
                json.dump([t.__dict__ for t in thumbnails], f, indent=2, ensure_ascii=False)

            # 9. Kit de Publicação & SEO Completo (Títulos A/B, Capítulos e Descrição)
            pub_kit = PublicationSeoKitGenerator.generate_complete_kit(plan)
            pub_txt_path = job_dir / "publicacao_youtube_e_tiktok.txt"
            with open(pub_txt_path, "w", encoding="utf-8") as f:
                f.write(pub_kit.complete_youtube_description)

            # 10. Manifesto de Renderização Paralela
            render_plan = ChunkedParallelRenderer.create_parallel_plan(plan, output_dir=str(job_dir / "chunks"))
            manifest_path = job_dir / "render_manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump({
                    "total_chunks": render_plan.total_chunks,
                    "concurrency": render_plan.concurrency_slots,
                    "encoder_mode": render_plan.encoder_mode,
                    "speedup": render_plan.estimated_speedup_factor,
                    "concat_manifest": render_plan.ffmpeg_concat_manifest,
                    "final_output": render_plan.final_output_path
                }, f, indent=2, ensure_ascii=False)

            # 11. Salva no repositório SQLite
            self.repo.save(plan)
            job.project_id = plan.project_id
            job.status = "ready"
            job.progress_pct = 100
            job.completed_at = time.time()

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.progress_pct = 0

    def get_state(self) -> BatchFactoryState:
        total = len(self.jobs)
        completed = sum(1 for j in self.jobs if j.status == "ready")
        
        overall = 0.0
        if total > 0:
            sum_pcts = sum(j.progress_pct for j in self.jobs)
            overall = round(sum_pcts / total, 1)

        return BatchFactoryState(
            factory_id=f"factory_drift",
            total_jobs=total,
            completed_jobs=completed,
            active_job_index=self.active_job_index,
            is_running=self.is_running,
            overall_progress_pct=overall,
            output_root_dir=str(self.output_root).replace("\\", "/"),
            jobs=list(self.jobs)
        )
