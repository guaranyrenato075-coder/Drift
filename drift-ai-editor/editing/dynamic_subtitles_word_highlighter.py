"""
Dynamic Subtitles Word Highlighter.
Gera legendas animadas no formato Advanced SubStation Alpha (.ASS) com
realce palavra por palavra (karaoke style) inspirado em criadores de alta retenção.
"""

from typing import Dict, Any, List
import re
from models.scene_plan import ProjectPlan


class DynamicSubtitlesWordHighlighter:
    """Gera arquivos .ASS com efeitos de realce de cor dinâmico palavra por palavra."""

    STYLE_PRESETS = {
        "hormozi_bold_yellow": {
            "name": "Alex Hormozi (Bold Amarelo)",
            "font_name": "Impact",
            "font_size": 48,
            "primary_color": "&H00FFFFFF",     # Branco
            "highlight_color": "&H0000FFFF",   # Amarelo (&HAABBGGRR)
            "outline_color": "&H00000000",     # Preto
            "outline_width": 3.5,
            "shadow_offset": 2.0,
            "alignment": 2                     # Centro inferior
        },
        "mrbeast_impact_green": {
            "name": "MrBeast (Impact Verde Neon)",
            "font_name": "Komika Axis",
            "font_size": 52,
            "primary_color": "&H00FFFFFF",
            "highlight_color": "&H0033FF00",   # Verde neon
            "outline_color": "&H00000000",
            "outline_width": 4.0,
            "shadow_offset": 2.5,
            "alignment": 2
        },
        "minimal_cinema_white": {
            "name": "Minimal Cinema (Elegante Neutro)",
            "font_name": "Montserrat",
            "font_size": 40,
            "primary_color": "&H00D0D0D0",
            "highlight_color": "&H00FFFFFF",
            "outline_color": "&H00101010",
            "outline_width": 2.0,
            "shadow_offset": 1.0,
            "alignment": 2
        },
        "cyberpunk_neon_cyan": {
            "name": "Cyberpunk (Ciano & Magenta)",
            "font_name": "Arial Black",
            "font_size": 46,
            "primary_color": "&H00FFFF00",     # Ciano
            "highlight_color": "&H00FF00FF",   # Magenta
            "outline_color": "&H00000000",
            "outline_width": 3.5,
            "shadow_offset": 2.0,
            "alignment": 2
        }
    }

    @classmethod
    def get_available_styles(cls) -> Dict[str, Dict[str, Any]]:
        return cls.STYLE_PRESETS

    @classmethod
    def generate_ass_subtitle_content(
        cls,
        plan: ProjectPlan,
        style_name: str = "hormozi_bold_yellow"
    ) -> Dict[str, Any]:
        """Gera o conteúdo textual completo do arquivo .ASS com tags de karaoke."""
        if style_name not in cls.STYLE_PRESETS:
            style_name = "hormozi_bold_yellow"

        st = cls.STYLE_PRESETS[style_name]
        scenes = getattr(plan, "scenes", [])

        # Cabeçalho do arquivo ASS
        header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "PlayResX: 1920\n"
            "PlayResY: 1080\n"
            "WrapStyle: 0\n"
            "ScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"Style: Default,{st['font_name']},{st['font_size']},{st['primary_color']},{st['highlight_color']},"
            f"{st['outline_color']},&H00000000,-1,0,0,0,100,100,0,0,1,{st['outline_width']},{st['shadow_offset']},"
            f"{st['alignment']},40,40,65,1\n\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        )

        dialogue_lines = []
        current_time = 0.0

        for scene in scenes:
            duration = float(getattr(scene, "duration", 5.0))
            text = getattr(scene, "narration_text", "") or getattr(scene, "text", "") or ""
            words = text.split()
            if not words:
                words = ["..."]

            # Formata tempos de início e fim
            s_mins, s_secs = divmod(current_time, 60)
            s_hours, s_mins = divmod(s_mins, 60)
            start_str = f"{int(s_hours)}:{int(s_mins):02d}:{s_secs:05.2f}"

            end_time = current_time + duration
            e_mins, e_secs = divmod(end_time, 60)
            e_hours, e_mins = divmod(e_mins, 60)
            end_str = f"{int(e_hours)}:{int(e_mins):02d}:{e_secs:05.2f}"

            # Calcula tempo por palavra em centésimos de segundo para tag de karaoke (\k<centisecs>)
            centisecs_per_word = max(10, int((duration * 100) / max(len(words), 1)))
            karaoke_text = "".join(f"{{\\k{centisecs_per_word}}}{w} " for w in words).strip()

            dialogue_lines.append(
                f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{karaoke_text}"
            )
            current_time += duration

        ass_full_script = header + "\n".join(dialogue_lines) + "\n"

        return {
            "style_name": style_name,
            "style_details": st,
            "total_dialogue_events": len(dialogue_lines),
            "ass_content": ass_full_script,
            "ffmpeg_subtitle_filter": f"subtitles=subtitles.ass:force_style='Fontname={st['font_name']}'"
        }
