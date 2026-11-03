import time
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("drift.pipeline.job_manager")

class JobStage(str, Enum):
    INIT = "init"
    STORYBOARD = "storyboard"
    VOICE_SYNTHESIS = "voice_synthesis"
    AUDIO_ALIGNMENT = "audio_alignment"
    MEDIA_SEARCH = "media_search"
    MEDIA_RANKING = "media_ranking"
    TIMELINE_PLANNING = "timeline_planning"
    QUALITY_CHECK = "quality_check"
    TIMELINE_APPLY = "timeline_apply"
    EXPORT = "export"
    COMPLETED = "completed"
    FAILED = "failed"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JobCheckpoint:
    stage: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)
    message: str = ""

@dataclass
class PipelineJob:
    job_id: str
    project_id: str
    status: JobStatus = JobStatus.PENDING
    current_stage: JobStage = JobStage.INIT
    progress: float = 0.0  # 0.0 to 100.0
    status_message: str = "Iniciando pipeline..."
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    checkpoints: List[JobCheckpoint] = field(default_factory=list)
    error_message: Optional[str] = None
    stage_results: Dict[str, Any] = field(default_factory=dict)

class JobManager:
    """
    Pipeline Manager responsible for organizing workflow execution,
    persisting checkpoints, tracking atomic stages, and enabling safe resumption
    after network interruption or editor crashes.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path(__file__).resolve().parent.parent / "storage" / "jobs"
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._jobs: Dict[str, PipelineJob] = {}

    def create_job(self, project_id: str, job_id: Optional[str] = None) -> PipelineJob:
        if not job_id:
            job_id = f"job_{int(time.time()*1000)}_{project_id[:8]}"
        job = PipelineJob(job_id=job_id, project_id=project_id)
        self._jobs[job_id] = job
        self.save_job(job)
        return job

    def get_job(self, job_id: str) -> Optional[PipelineJob]:
        if job_id in self._jobs:
            return self._jobs[job_id]
        file_path = self.storage_dir / f"{job_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                checkpoints = [
                    JobCheckpoint(stage=c["stage"], timestamp=c["timestamp"], data=c.get("data", {}), message=c.get("message", ""))
                    for c in raw.get("checkpoints", [])
                ]
                job = PipelineJob(
                    job_id=raw["job_id"],
                    project_id=raw["project_id"],
                    status=JobStatus(raw.get("status", JobStatus.PENDING)),
                    current_stage=JobStage(raw.get("current_stage", JobStage.INIT)),
                    progress=float(raw.get("progress", 0.0)),
                    status_message=raw.get("status_message", ""),
                    created_at=float(raw.get("created_at", time.time())),
                    updated_at=float(raw.get("updated_at", time.time())),
                    checkpoints=checkpoints,
                    error_message=raw.get("error_message"),
                    stage_results=raw.get("stage_results", {})
                )
                self._jobs[job_id] = job
                return job
            except Exception as e:
                logger.error(f"Erro ao carregar job {job_id}: {e}")
                return None
        return None

    def update_stage(
        self,
        job_id: str,
        stage: JobStage,
        progress: float,
        message: str,
        result_data: Optional[Dict[str, Any]] = None
    ) -> Optional[PipelineJob]:
        job = self.get_job(job_id)
        if not job:
            return None

        job.current_stage = stage
        job.progress = progress
        job.status_message = message
        job.updated_at = time.time()
        job.status = JobStatus.RUNNING

        checkpoint = JobCheckpoint(stage=stage.value, timestamp=time.time(), data=result_data or {}, message=message)
        job.checkpoints.append(checkpoint)

        if result_data:
            job.stage_results[stage.value] = result_data

        self.save_job(job)
        return job

    def fail_job(self, job_id: str, error_msg: str) -> Optional[PipelineJob]:
        job = self.get_job(job_id)
        if not job:
            return None
        job.status = JobStatus.FAILED
        job.current_stage = JobStage.FAILED
        job.error_message = error_msg
        job.status_message = f"Falha na etapa {job.current_stage.value}: {error_msg}"
        job.updated_at = time.time()
        self.save_job(job)
        return job

    def complete_job(self, job_id: str, message: str = "Pipeline concluído com sucesso!") -> Optional[PipelineJob]:
        job = self.get_job(job_id)
        if not job:
            return None
        job.status = JobStatus.COMPLETED
        job.current_stage = JobStage.COMPLETED
        job.progress = 100.0
        job.status_message = message
        job.updated_at = time.time()
        self.save_job(job)
        return job

    def save_job(self, job: PipelineJob) -> None:
        file_path = self.storage_dir / f"{job.job_id}.json"
        data = {
            "job_id": job.job_id,
            "project_id": job.project_id,
            "status": job.status.value,
            "current_stage": job.current_stage.value,
            "progress": job.progress,
            "status_message": job.status_message,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "error_message": job.error_message,
            "stage_results": job.stage_results,
            "checkpoints": [
                {"stage": c.stage, "timestamp": c.timestamp, "data": c.data, "message": c.message}
                for c in job.checkpoints
            ]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def can_resume_stage(self, job: PipelineJob, stage: JobStage) -> bool:
        """Determines if a stage can be skipped because valid checkpoint results already exist."""
        return stage.value in job.stage_results and bool(job.stage_results[stage.value])

