"""
Social Media Multi-Platform Export Presets Orchestrator for CutWire Drift AI.
Generates simultaneous platform-optimized renders (YouTube 16:9 4K/1080p, TikTok/Shorts 9:16 vertical,
Instagram Feed/LinkedIn 1:1 square, and Broadcast Podcast MP3) from a single master project plan.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from models.scene_plan import ProjectPlan

@dataclass
class ExportPlatformSpec:
    preset_id: str
    name: str
    target_platform: str
    aspect_ratio: str
    resolution: str
    video_codec: str
    audio_lufs: float
    ffmpeg_video_args: str
    recommended_use: str

class SocialMediaMultiExportPresets:
    """
    Orchestrates multi-channel video deliverable generation.
    """

    PRESETS: Dict[str, ExportPlatformSpec] = {
        "youtube_16_9": ExportPlatformSpec(
            preset_id="youtube_16_9",
            name="YouTube Long-Form (16:9 Widescreen)",
            target_platform="YouTube / Vimeo",
            aspect_ratio="16:9",
            resolution="1920x1080",
            video_codec="libx264",
            audio_lufs=-14.0,
            ffmpeg_video_args="-c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p",
            recommended_use="Vídeos de 10 a 60 minutos com capítulos, descrição rica e tags de 500 chars."
        ),
        "shorts_reels_9_16": ExportPlatformSpec(
            preset_id="shorts_reels_9_16",
            name="TikTok / Reels / YouTube Shorts (9:16 Vertical)",
            target_platform="TikTok / Instagram Reels / Shorts",
            aspect_ratio="9:16",
            resolution="1080x1920",
            video_codec="libx264",
            audio_lufs=-14.0,
            ffmpeg_video_args="-vf 'crop=ih*(9/16):ih,scale=1080:1920' -c:v libx264 -crf 20 -preset faster",
            recommended_use="Cortes virais de 30 a 60s com legendas dinâmicas elevadas no terço central."
        ),
        "feed_linkedin_1_1": ExportPlatformSpec(
            preset_id="feed_linkedin_1_1",
            name="Instagram Feed / LinkedIn Square (1:1)",
            target_platform="Instagram Feed / LinkedIn / Twitter",
            aspect_ratio="1:1",
            resolution="1080x1080",
            video_codec="libx264",
            audio_lufs=-14.0,
            ffmpeg_video_args="-vf 'crop=min(iw\\,ih):min(iw\\,ih),scale=1080:1080' -c:v libx264 -crf 19",
            recommended_use="Formato quadrado com alta taxa de engajamento no feed mobile e desktop."
        ),
        "podcast_audio_mp3": ExportPlatformSpec(
            preset_id="podcast_audio_mp3",
            name="Podcast Audio Only Master (MP3 320kbps)",
            target_platform="Spotify / Apple Podcasts / Amazon Music",
            aspect_ratio="N/A",
            resolution="N/A",
            video_codec="none",
            audio_lufs=-16.0,
            ffmpeg_video_args="-vn -c:a libmp3lame -b:a 320k",
            recommended_use="Distribuição pura de áudio masterizado para plataformas de podcasting."
        )
    }

    @classmethod
    def list_presets(cls) -> List[Dict[str, Any]]:
        return [
            {
                "preset_id": p.preset_id,
                "name": p.name,
                "target_platform": p.target_platform,
                "aspect_ratio": p.aspect_ratio,
                "resolution": p.resolution,
                "video_codec": p.video_codec,
                "audio_lufs": p.audio_lufs,
                "recommended_use": p.recommended_use
            }
            for p in cls.PRESETS.values()
        ]

    @classmethod
    def build_export_manifest(cls, plan: ProjectPlan, selected_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Builds the batch render manifest containing commands and parameters for all targets.
        """
        targets = selected_ids or list(cls.PRESETS.keys())
        tasks = []

        for pid in targets:
            spec = cls.PRESETS.get(pid)
            if not spec:
                continue

            base_name = f"{plan.project_id}_{spec.preset_id}"
            ext = ".mp3" if spec.preset_id == "podcast_audio_mp3" else ".mp4"
            out_file = f"storage/renders/{base_name}{ext}"

            tasks.append({
                "preset_id": spec.preset_id,
                "name": spec.name,
                "output_file": out_file,
                "resolution": spec.resolution,
                "aspect_ratio": spec.aspect_ratio,
                "target_platform": spec.target_platform,
                "ffmpeg_command": f"ffmpeg -i master.mp4 {spec.ffmpeg_video_args} {out_file}"
            })

        return {
            "project_id": plan.project_id,
            "total_exports_planned": len(tasks),
            "export_tasks": tasks
        }
