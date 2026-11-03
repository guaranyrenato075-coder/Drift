"""
YouTube Chapter & Timestamp Generator for CutWire Drift AI.
Detects narrative topic shifts and dramatic transitions across scenes,
generating YouTube description timestamp blocks and MP4/MKV embedded chapter markers.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class ChapterEntry:
    timestamp_sec: float
    formatted_time: str  # e.g., "02:14"
    title: str

@dataclass
class YoutubeChaptersManifest:
    total_chapters: int
    description_block: str
    ffmpeg_metadata_manifest: str
    entries: List[ChapterEntry]

class YoutubeChapterGenerator:
    """
    Parses timeline scenes and compiles standardized YouTube timestamp chapters.
    """

    @classmethod
    def generate_chapters(cls, plan: ProjectPlan) -> YoutubeChaptersManifest:
        if not plan.scenes:
            return YoutubeChaptersManifest(0, "", "", [])

        entries: List[ChapterEntry] = []
        current_time = 0.0

        # YouTube strictly requires chapter 1 to start at 00:00
        entries.append(
            ChapterEntry(
                timestamp_sec=0.0,
                formatted_time="00:00",
                title=f"Introdução: {plan.title}"
            )
        )

        min_chapter_interval = 25.0  # Chapters should be spaced by at least 25s
        last_chapter_time = 0.0

        for idx, scene in enumerate(plan.scenes):
            dur = scene.duration if scene.duration > 0 else 4.0
            
            # Detect section shifts or chapter triggers
            if idx > 0 and (current_time - last_chapter_time) >= min_chapter_interval:
                first_words = " ".join(scene.narration_text.split()[:4]).capitalize()
                formatted = cls._format_time(current_time)
                entries.append(
                    ChapterEntry(
                        timestamp_sec=round(current_time, 2),
                        formatted_time=formatted,
                        title=f"{first_words}..."
                    )
                )
                last_chapter_time = current_time

            current_time += dur

        # Format YouTube description text
        lines = ["📌 CAPÍTULOS DO VÍDEO:"]
        for e in entries:
            lines.append(f"{e.formatted_time} - {e.title}")
        desc_block = "\n".join(lines)

        # Build FFmpeg metadata format
        ff_lines = [";FFMETADATA1"]
        for i, e in enumerate(entries):
            start_ms = int(e.timestamp_sec * 1000)
            end_ms = int((entries[i+1].timestamp_sec * 1000) if i+1 < len(entries) else (current_time * 1000))
            ff_lines.extend([
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={start_ms}",
                f"END={end_ms}",
                f"title={e.title}"
            ])
        ff_manifest = "\n".join(ff_lines)

        return YoutubeChaptersManifest(
            total_chapters=len(entries),
            description_block=desc_block,
            ffmpeg_metadata_manifest=ff_manifest,
            entries=entries
        )

    @staticmethod
    def _format_time(seconds: float) -> str:
        s = int(seconds)
        mins = s // 60
        secs = s % 60
        return f"{mins:02d}:{secs:02d}"

