"""
Automatic Chaptering & Video Timestamp Generator for CutWire Drift AI.
Generates YouTube/Spotify video description timestamps, WebVTT chapters, and FFmpeg MP4 chapter markers
from scene timings and key semantic transitions to maximize user retention and search algorithm SEO.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from models.scene_plan import ProjectPlan, Scene

@dataclass
class VideoChapter:
    index: int
    title: str
    start_sec: float
    end_sec: float
    formatted_start: str  # e.g. "00:00" or "01:24:05"

class AutoChapteringEngine:
    """
    Automated chapter generator and timestamp formatter for video projects.
    """

    @classmethod
    def format_timestamp(cls, seconds: float) -> str:
        """Formats seconds into MM:SS or HH:MM:SS."""
        total_sec = int(round(seconds))
        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        secs = total_sec % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @classmethod
    def generate_chapters(cls, plan: ProjectPlan) -> List[VideoChapter]:
        """
        Creates clean, logical chapters from the project's scenes.
        Ensures the first chapter starts exactly at 00:00 as required by YouTube.
        """
        if not plan.scenes:
            return [VideoChapter(index=1, title="Início", start_sec=0.0, end_sec=0.0, formatted_start="00:00")]

        chapters: List[VideoChapter] = []
        cumulative_time = 0.0

        for idx, s in enumerate(plan.scenes):
            dur = max(s.duration or 3.0, 0.5)
            # Create a concise, engaging chapter title
            title = s.narration_text.strip()
            if len(title) > 45:
                # Find punctuation break or truncate cleanly
                match = title[:45].rfind(" ")
                title = title[:match if match > 15 else 42] + "..."
            if not title:
                title = f"Parte {s.order}"

            # Make the first chapter always "Introdução" or matching theme
            if idx == 0:
                title = "01. Introdução: " + title

            chap = VideoChapter(
                index=idx + 1,
                title=title,
                start_sec=round(cumulative_time, 2),
                end_sec=round(cumulative_time + dur, 2),
                formatted_start=cls.format_timestamp(cumulative_time)
            )
            chapters.append(chap)
            cumulative_time += dur

        return chapters

    @classmethod
    def generate_youtube_description_block(cls, plan: ProjectPlan) -> str:
        """
        Outputs clean text block ready to copy and paste into YouTube video description.
        """
        chaps = cls.generate_chapters(plan)
        lines = [
            "⏱️ CAPÍTULOS & TIMESTAMPS:",
            "━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]
        for c in chaps:
            lines.append(f"{c.formatted_start} - {c.title}")

        lines.append("")
        lines.append("Produzido com CutWire Drift AI Video Editor 🎬")
        return "\n".join(lines)

    @classmethod
    def generate_webvtt(cls, plan: ProjectPlan) -> str:
        """
        Outputs WebVTT chapter format (.vtt) for web players.
        """
        chaps = cls.generate_chapters(plan)
        lines = ["WEBVTT - Chapters", ""]
        for c in chaps:
            s_min = int(c.start_sec // 60)
            s_sec = int(c.start_sec % 60)
            s_ms = int((c.start_sec - int(c.start_sec)) * 1000)

            e_min = int(c.end_sec // 60)
            e_sec = int(c.end_sec % 60)
            e_ms = int((c.end_sec - int(c.end_sec)) * 1000)

            lines.append(f"{s_min:02d}:{s_sec:02d}.{s_ms:03d} --> {e_min:02d}:{e_sec:02d}.{e_ms:03d}")
            lines.append(c.title)
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def generate_ffmpeg_metadata(cls, plan: ProjectPlan) -> str:
        """
        Outputs FFmpeg chapter metadata format for embedding inside MP4 containers.
        """
        chaps = cls.generate_chapters(plan)
        lines = [";FFMETADATA1", ""]
        for c in chaps:
            lines.append("[CHAPTER]")
            lines.append("TIMEBASE=1/1000")
            lines.append(f"START={int(c.start_sec * 1000)}")
            lines.append(f"END={int(c.end_sec * 1000)}")
            lines.append(f"title={c.title}")
            lines.append("")
        return "\n".join(lines)
