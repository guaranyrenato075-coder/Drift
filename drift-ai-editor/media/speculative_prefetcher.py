"""
Speculative Background Media Prefetcher for CutWire Drift AI.
Anticipates creator workflow by speculatively downloading top visual candidate assets
in asynchronous non-blocking worker threads immediately after script scene segmentation,
reducing user-perceived timeline building wait time to virtually zero.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import threading
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from models.scene_plan import ProjectPlan, Scene, MediaCandidate
from media.downloader import MediaDownloader

@dataclass
class PrefetchJobStatus:
    scene_order: int
    candidate_id: str
    platform: str
    status: str       # "queued", "downloading", "cached", "skipped", "error"
    local_path: Optional[str] = None
    download_time_sec: float = 0.0

@dataclass
class PrefetchBatchSummary:
    project_id: str
    total_scenes_queued: int
    completed_count: int
    already_cached_count: int
    failed_count: int
    elapsed_time_sec: float
    jobs: List[PrefetchJobStatus]

class SpeculativeMediaPrefetcher:
    """
    Asynchronous prefetch coordinator for instant timeline assembly.
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="PrefetchWorker")
        self.downloader = MediaDownloader()
        self.active_jobs: Dict[str, PrefetchJobStatus] = {}

    def prefetch_plan_candidates_async(
        self,
        plan: ProjectPlan,
        on_complete_callback=None
    ) -> threading.Thread:
        """
        Launches background speculative prefetching without blocking caller.
        """
        def _runner():
            summary = self.prefetch_plan_candidates_sync(plan)
            if on_complete_callback:
                try:
                    on_complete_callback(summary)
                except Exception:
                    pass

        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        return t

    def prefetch_plan_candidates_sync(self, plan: ProjectPlan) -> PrefetchBatchSummary:
        """
        Synchronously prefetches all selected or top candidates for the plan.
        """
        start_time = time.time()
        jobs: List[PrefetchJobStatus] = []
        futures = []

        for s in plan.scenes:
            cand = s.selected_media
            if not cand and s.candidates:
                cand = s.candidates[0]

            if not cand:
                continue

            if cand.local_cached_path and Path(cand.local_cached_path).exists():
                jobs.append(PrefetchJobStatus(
                    scene_order=s.order,
                    candidate_id=cand.candidate_id,
                    platform=cand.platform,
                    status="cached",
                    local_path=cand.local_cached_path,
                    download_time_sec=0.0
                ))
                continue

            job = PrefetchJobStatus(
                scene_order=s.order,
                candidate_id=cand.candidate_id,
                platform=cand.platform,
                status="queued"
            )
            jobs.append(job)

            # Agenda no pool de workers
            def _worker_fn(scene=s, candidate=cand, job_ref=job):
                t0 = time.time()
                job_ref.status = "downloading"
                try:
                    ok, path, _ = self.downloader.download_candidate(candidate)
                    if ok and path:
                        candidate.local_cached_path = str(path)
                        job_ref.local_path = str(path)
                        job_ref.status = "cached"
                    else:
                        job_ref.status = "error"
                except Exception:
                    job_ref.status = "error"
                job_ref.download_time_sec = round(time.time() - t0, 3)

            futures.append(self.executor.submit(_worker_fn))

        # Aguarda conclusão
        for f in futures:
            try:
                f.result(timeout=60)
            except Exception:
                pass

        elapsed = round(time.time() - start_time, 2)
        completed = sum(1 for j in jobs if j.status == "cached")
        already = sum(1 for j in jobs if j.status == "cached" and j.download_time_sec == 0.0)
        failed = sum(1 for j in jobs if j.status == "error")

        return PrefetchBatchSummary(
            project_id=getattr(plan, "project_id", "drift_proj"),
            total_scenes_queued=len(jobs),
            completed_count=completed,
            already_cached_count=already,
            failed_count=failed,
            elapsed_time_sec=elapsed,
            jobs=jobs
        )
