from typing import List, Dict, Any
from pathlib import Path
from models.scene_plan import ProjectPlan, Scene

class CaptionManager:
    """
    Manages subtitles and captions generation from scene plans.
    """

    @staticmethod
    def build_subtitle_cues(scenes: List[Scene]) -> List[Dict[str, Any]]:
        """
        Creates cue dictionaries formatted for Drift's set_subtitle_cues:
        [{"in": start_sec, "out": end_sec, "text": string}, ...]
        """
        cues: List[Dict[str, Any]] = []
        for s in scenes:
            if not s.narration_text.strip():
                continue
            start = round(s.start_time, 2)
            end = round(s.end_time if s.end_time > s.start_time else s.start_time + s.duration, 2)
            if end <= start:
                end = start + 2.0

            cues.append({
                "in": start,
                "out": end,
                "text": s.narration_text.strip()
            })
        return cues

    @staticmethod
    def format_srt_time(seconds: float) -> str:
        millis = int((seconds % 1) * 1000)
        seconds_int = int(seconds)
        hours = seconds_int // 3600
        mins = (seconds_int % 3600) // 60
        secs = seconds_int % 60
        return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    @classmethod
    def export_srt(cls, scenes: List[Scene], output_path: Path | str) -> Path:
        """
        Exports scene narrations and timings to a standard .srt file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        cues = cls.build_subtitle_cues(scenes)

        lines: List[str] = []
        for idx, cue in enumerate(cues, 1):
            time_str = f"{cls.format_srt_time(cue['in'])} --> {cls.format_srt_time(cue['out'])}"
            lines.append(str(idx))
            lines.append(time_str)
            lines.append(cue["text"])
            lines.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return path

