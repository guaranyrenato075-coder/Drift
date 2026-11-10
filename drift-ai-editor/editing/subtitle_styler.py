"""
AI Dynamic Subtitle Styler for CutWire Drift AI.
Generates visually stylized Advanced SubStation Alpha (.ASS) subtitle files with custom fonts,
high-contrast outlines, glowing shadows, and word-by-word highlight effects (Hormozi/MrBeast, Neon Glow, Cinema Classic, Minimalist).
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
from models.scene_plan import Scene, ProjectPlan

@dataclass
class SubtitleStylePreset:
    id: str
    name: str
    font_name: str
    font_size: int
    primary_color: str     # &HAABBGGRR in ASS hex
    secondary_color: str
    outline_color: str
    back_color: str
    bold: int
    italic: int
    border_style: int
    outline_width: float
    shadow_depth: float
    alignment: int         # 2 = Bottom Center, 5 = Top Center, 8 = Top Center, 5 = Middle Center
    margin_v: int
    description: str

class AITranscriptionSubtitleStyler:
    """
    Crafts high-impact stylized subtitles for vertical and widescreen videos.
    """

    PRESETS: Dict[str, SubtitleStylePreset] = {
        "hormozi_viral": SubtitleStylePreset(
            id="hormozi_viral",
            name="Hormozi / MrBeast Pop (Viral)",
            font_name="Montserrat ExtraBold",
            font_size=42,
            primary_color="&H0000FFFF",    # Yellow (#FFFF00)
            secondary_color="&H0000FF00",  # Lime Green highlight
            outline_color="&H00000000",    # Black outline
            back_color="&H80000000",       # Dark drop shadow
            bold=1,
            italic=0,
            border_style=1,
            outline_width=4.0,
            shadow_depth=2.0,
            alignment=2,                   # Bottom Center
            margin_v=90,
            description="Letras amarelas com contorno grosso preto e destaque dinâmico para viralização em Shorts e TikTok."
        ),
        "neon_glow": SubtitleStylePreset(
            id="neon_glow",
            name="Neon Glow (Cyberpunk & Sci-Fi)",
            font_name="Arial Black",
            font_size=38,
            primary_color="&H00FFFF00",    # Cyan (#00FFFF)
            secondary_color="&H00FF00FF",  # Magenta
            outline_color="&H001A0B2E",    # Deep purple
            back_color="&H00000000",
            bold=1,
            italic=0,
            border_style=1,
            outline_width=3.5,
            shadow_depth=4.0,
            alignment=2,
            margin_v=85,
            description="Brilho neon ciano e magenta com alto contraste contra planos escuros e espaciais."
        ),
        "cinema_classic": SubtitleStylePreset(
            id="cinema_classic",
            name="Cinema Classic (Netflix / Documentário)",
            font_name="Helvetica",
            font_size=28,
            primary_color="&H00FFFFFF",    # Pure White
            secondary_color="&H00D0D0D0",
            outline_color="&H00000000",
            back_color="&HA0000000",       # Semi-transparent box
            bold=0,
            italic=0,
            border_style=1,
            outline_width=1.5,
            shadow_depth=1.0,
            alignment=2,
            margin_v=50,
            description="Letras brancas elegantes com leve contorno preto e fade suave para documentários formais."
        ),
        "minimalist_clean": SubtitleStylePreset(
            id="minimalist_clean",
            name="Minimalist Clean (Didático & Negócios)",
            font_name="Segoe UI Semibold",
            font_size=32,
            primary_color="&H00F0F0F0",    # Off-white
            secondary_color="&H0038BDF8",  # Sky blue
            outline_color="&H001E293B",    # Slate dark
            back_color="&H00000000",
            bold=1,
            italic=0,
            border_style=1,
            outline_width=2.0,
            shadow_depth=1.5,
            alignment=2,
            margin_v=75,
            description="Design limpo, espaçado e contemporâneo focado em leitura clara sem poluição visual."
        )
    }

    @classmethod
    def list_styles(cls) -> List[Dict[str, str]]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "font_name": p.font_name,
                "font_size": str(p.font_size)
            }
            for p in cls.PRESETS.values()
        ]

    @classmethod
    def format_ass_time(cls, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int(round((seconds - int(seconds)) * 100))
        if centisecs >= 100:
            centisecs = 99
        return f"{hours:01d}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    @classmethod
    def generate_styled_ass(cls, plan: ProjectPlan, style_id: str = "hormozi_viral", output_path: Optional[str] = None) -> str:
        preset = cls.PRESETS.get(style_id, cls.PRESETS["hormozi_viral"])
        w = plan.config.width
        h = plan.config.height

        header = f"""[Script Info]
Title: Drift AI Subtitles - {preset.name}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: {w}
PlayResY: {h}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{preset.font_name},{preset.font_size},{preset.primary_color},{preset.secondary_color},{preset.outline_color},{preset.back_color},{preset.bold},{preset.italic},0,0,100,100,0,0,{preset.border_style},{preset.outline_width},{preset.shadow_depth},{preset.alignment},20,20,{preset.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        cumulative = 0.0
        for s in plan.scenes:
            dur = max(s.duration or 3.0, 0.5)
            start_str = cls.format_ass_time(cumulative)
            end_str = cls.format_ass_time(cumulative + dur)
            text = s.narration_text.strip()
            if text:
                if style_id == "hormozi_viral":
                    # Highlight first word with secondary color
                    words = text.split()
                    if len(words) > 1:
                        highlighted_text = f"{{\\c{preset.secondary_color}}}{words[0]}{{\\c{preset.primary_color}}} " + " ".join(words[1:])
                    else:
                        highlighted_text = text
                else:
                    highlighted_text = text
                events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{highlighted_text}")
            cumulative += dur

        full_content = header + "\n".join(events) + "\n"

        if output_path:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(full_content, encoding="utf-8")

        return full_content
