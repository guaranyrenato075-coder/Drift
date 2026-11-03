"""
Karaoke-Style Kinetic Subtitle Generator for CutWire Drift AI (Alex Hormozi / TikTok Style).
Compiles word-by-word synchronized Advanced SubStation Alpha (.ass) scripts
featuring active word neon highlighting, bold outline borders, and strict TikTok Safe-Zone vertical placement.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import os
import re
from models.scene_plan import ProjectPlan, Scene

@dataclass
class KaraokeWordTimestamp:
    word: str
    start_sec: float
    end_sec: float
    duration_cs: int      # Duração em centissegundos (para a tag \k do formato ASS)
    is_keyword: bool

@dataclass
class KaraokeDialogueLine:
    scene_order: int
    start_formatted: str  # "0:00:01.20"
    end_formatted: str    # "0:00:04.50"
    raw_text: str
    ass_karaoke_text: str # "{\k20}A {\k30}disciplina {\k25}diária..."

@dataclass
class KaraokeSubtitleScript:
    project_id: str
    total_lines: int
    highlight_color_bgr: str  # ASS usa &H00BBGGRR& (ex: &H0000E5FF& para Amarelo/Dourado)
    ass_script_content: str
    output_filename: str

class KaraokeSubtitleGenerator:
    """
    Transforms scene narration text and duration into TikTok-ready karaoke ASS scripts.
    """

    KEYWORD_BOOST = {"nunca", "sempre", "segredo", "atenção", "mente", "sucesso", "foco", "erro", "verdade", "poder"}

    @classmethod
    def _format_timestamp(cls, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        if cs >= 100:
            cs = 99
        return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"

    @classmethod
    def generate_ass_script(
        cls,
        plan: ProjectPlan,
        font_name: str = "Arial Black",
        font_size: int = 58,
        highlight_color_hex: str = "#00FF66", # Verde Neon
        safe_zone_vertical_margin: int = 420
    ) -> KaraokeSubtitleScript:
        # Converter cor hex para formato ASS (&H00BBGGRR&)
        hex_clean = highlight_color_hex.lstrip("#")
        r, g, b = hex_clean[0:2], hex_clean[2:4], hex_clean[4:6]
        ass_highlight = f"&H00{b}{g}{r}&"

        header = f"""[Script Info]
Title: Drift AI Karaoke Captions
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: HormoziKaraoke,{font_name},{font_size},&H00FFFFFF&,{ass_highlight},&H00000000&,&H80000000&,-1,0,0,0,100,100,0,0,1,5.0,2.0,2,40,40,{safe_zone_vertical_margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        dialogue_lines: List[KaraokeDialogueLine] = []
        cur_time = 0.0

        for s in plan.scenes:
            dur = s.duration if s.duration > 0 else 4.0
            scene_start = cur_time
            scene_end = cur_time + dur

            text = (s.narration_text or "").strip()
            if text:
                words = text.split()
                per_word_dur = dur / max(1, len(words))

                # Monta a linha com tags \k de karaoke
                karaoke_parts = []
                for w in words:
                    clean_w = re.sub(r'[^\w\s]', '', w.lower())
                    is_kw = clean_w in cls.KEYWORD_BOOST
                    duration_cs = max(10, int(round(per_word_dur * 100)))

                    if is_kw:
                        # Palavra chave recebe destaque com cor especial
                        karaoke_parts.append(f"{{\\k{duration_cs}\\c{ass_highlight}}}{w}{{\\c&H00FFFFFF&}}")
                    else:
                        karaoke_parts.append(f"{{\\k{duration_cs}}}{w}")

                ass_text = " ".join(karaoke_parts)
                start_str = cls._format_timestamp(scene_start)
                end_str = cls._format_timestamp(scene_end)

                dialogue_lines.append(KaraokeDialogueLine(
                    scene_order=s.order,
                    start_formatted=start_str,
                    end_formatted=end_str,
                    raw_text=text,
                    ass_karaoke_text=f"Dialogue: 0,{start_str},{end_str},HormoziKaraoke,,0,0,0,,{ass_text}"
                ))

            cur_time = scene_end

        event_lines = [line.ass_karaoke_text for line in dialogue_lines]
        full_content = header + "\n".join(event_lines) + "\n"

        clean_title = "".join(c for c in plan.title if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        out_filename = f"{clean_title}_karaoke.ass"

        return KaraokeSubtitleScript(
            project_id=getattr(plan, "project_id", "drift_proj"),
            total_lines=len(dialogue_lines),
            highlight_color_bgr=ass_highlight,
            ass_script_content=full_content,
            output_filename=out_filename
        )

