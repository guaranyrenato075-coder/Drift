import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from models.scene_plan import ProjectPlan
from editing.deliverables_packager import DeliverablesPackager

@dataclass
class PublishManifest:
    project_id: str
    target_platform: str          # 'youtube', 'tiktok', 'google_drive'
    scheduled_timestamp: str
    video_file_path: str
    thumbnail_file_path: Optional[str]
    title: str
    description: str
    tags: List[str]
    privacy_status: str           # 'public', 'unlisted', 'private', 'scheduled'
    is_ready_for_dispatch: bool

class DirectPublisher:
    """
    Direct Multi-Platform Publisher & Staging Dispatcher:
    Prepares verified, automated release bundles for immediate or scheduled publication:
      - Bundles final MP4, high-res thumbnail, SEO description with chapters, and hashtags.
      - Verifies that video file and thumbnail exist on disk before staging dispatch.
    """

    @classmethod
    def stage_publication(
        cls,
        plan: ProjectPlan,
        video_path: Path,
        platform: str = "youtube",
        privacy: str = "scheduled",
        scheduled_delay_hours: int = 24
    ) -> PublishManifest:
        pack = DeliverablesPackager.generate_release_kit(plan)
        sched_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + (scheduled_delay_hours * 3600)))

        vid_file = Path(video_path)
        is_ready = vid_file.exists() and vid_file.stat().st_size > 1024

        thumb_path = vid_file.parent / f"{vid_file.stem}_thumb.jpg"

        manifest = PublishManifest(
            project_id=plan.project_id,
            target_platform=platform,
            scheduled_timestamp=sched_time,
            video_file_path=str(vid_file.resolve()),
            thumbnail_file_path=str(thumb_path.resolve()) if thumb_path.exists() else None,
            title=pack["title_variants"][0],
            description=pack["description"],
            tags=pack["tags"],
            privacy_status=privacy,
            is_ready_for_dispatch=is_ready
        )

        # Save manifest json
        manifest_file = vid_file.parent / f"publish_manifest_{platform}.json"
        manifest_file.write_text(json.dumps(manifest.__dict__, indent=2, ensure_ascii=False), encoding="utf-8")

        return manifest

