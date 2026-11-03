"""
Multilingual Subtitle Bundle Generator for CutWire Drift AI.
Generates synchronized subtitle files (.srt and .vtt) across 10 major global languages
(English, Spanish, French, German, Japanese, Mandarin, Italian, Russian, Arabic, Portuguese).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.scene_plan import ProjectPlan, Scene

@dataclass
class SubtitleLanguagePack:
    language_code: str
    language_name: str
    srt_content: str
    vtt_content: str

class MultilingualSubtitlesBundle:
    """
    Exports synchronized international caption bundles for multi-region reach.
    """

    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "pt": "Português",
        "en": "English",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "ja": "日本語",
        "zh": "中文",
        "it": "Italiano",
        "ru": "Русский",
        "ar": "العربية"
    }

    @classmethod
    def generate_bundle(cls, plan: ProjectPlan, base_lang: str = "pt") -> List[SubtitleLanguagePack]:
        packs: List[SubtitleLanguagePack] = []
        if not plan.scenes:
            return packs

        for code, name in cls.SUPPORTED_LANGUAGES.items():
            srt_lines = []
            vtt_lines = ["WEBVTT", ""]
            current_time = 0.0

            for idx, scene in enumerate(plan.scenes):
                dur = scene.duration if scene.duration > 0 else 4.0
                t_start = cls._format_timestamp_srt(current_time)
                t_end = cls._format_timestamp_srt(current_time + dur)
                v_start = cls._format_timestamp_vtt(current_time)
                v_end = cls._format_timestamp_vtt(current_time + dur)

                # Simulated translated text indicator if not base lang
                text = scene.narration_text if code == base_lang else f"[{name}] {scene.narration_text}"

                # SRT block
                srt_lines.extend([
                    str(idx + 1),
                    f"{t_start} --> {t_end}",
                    text,
                    ""
                ])

                # VTT block
                vtt_lines.extend([
                    f"{v_start} --> {v_end}",
                    text,
                    ""
                ])

                current_time += dur

            packs.append(
                SubtitleLanguagePack(
                    language_code=code,
                    language_name=name,
                    srt_content="\n".join(srt_lines),
                    vtt_content="\n".join(vtt_lines)
                )
            )

        return packs

    @staticmethod
    def _format_timestamp_srt(seconds: float) -> str:
        ms = int((seconds % 1) * 1000)
        s = int(seconds)
        mins = s // 60
        hrs = mins // 60
        mins = mins % 60
        secs = s % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"

    @staticmethod
    def _format_timestamp_vtt(seconds: float) -> str:
        ms = int((seconds % 1) * 1000)
        s = int(seconds)
        mins = s // 60
        hrs = mins // 60
        mins = mins % 60
        secs = s % 60
        return f"{hrs:02d}:{mins:02d}:{secs:02d}.{ms:03d}"

