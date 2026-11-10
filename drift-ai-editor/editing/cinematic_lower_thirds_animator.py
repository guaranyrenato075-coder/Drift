"""
Cinematic Lower Thirds Animator.
Gera grafismos inferiores (Lower Thirds) com tipografia moderna,
barras de destaque animadas, entrada wipe e saída fade-out para identificação de tópicos.
"""

from typing import Dict, Any, List
from models.scene_plan import ProjectPlan


class CinematicLowerThirdsAnimator:
    """Gera overlays FFmpeg e diretivas de animação para Lower Thirds."""

    STYLES = {
        "tech_cyber_bar": {
            "name": "Tech Cyber Bar (Neon Ciano)",
            "primary_color": "0x00F0FF",
            "secondary_color": "0x0f172a",
            "font": "Arial-Bold",
            "font_size": 28,
            "sub_font_size": 18,
            "bar_height": 65,
            "description": "Estilo moderno futurista com linha vertical ciano e fundo escuro semi-transparente."
        },
        "broadcast_news_slate": {
            "name": "Broadcast News (Jornalismo Dinâmico)",
            "primary_color": "0xDC2626",
            "secondary_color": "0xFFFFFF",
            "font": "Helvetica-Bold",
            "font_size": 30,
            "sub_font_size": 20,
            "bar_height": 70,
            "description": "Tarja clássica de telejornal com fundo vermelho de destaque e texto branco nítido."
        },
        "documentary_minimal": {
            "name": "Documentary Minimal (Cinema Nobre)",
            "primary_color": "0xFFFFFF",
            "secondary_color": "0x18181b",
            "font": "Georgia",
            "font_size": 26,
            "sub_font_size": 16,
            "bar_height": 55,
            "description": "Tipografia serifada discreta com transparência elegante para cinema e documentários."
        },
        "gold_luxury_serif": {
            "name": "Gold Luxury Serif (Premium)",
            "primary_color": "0xD4AF37",
            "secondary_color": "0x0A0A0A",
            "font": "Times-Bold",
            "font_size": 28,
            "sub_font_size": 18,
            "bar_height": 60,
            "description": "Tons dourados com fundo preto fosco para vídeos institucionais e alta classe."
        }
    }

    @classmethod
    def get_available_styles(cls) -> Dict[str, Dict[str, Any]]:
        return cls.STYLES

    @classmethod
    def generate_lower_third_overlay(
        cls,
        title: str,
        subtitle: str = "",
        style_name: str = "tech_cyber_bar",
        start_time: float = 2.0,
        duration: float = 5.0
    ) -> Dict[str, Any]:
        """Gera a cadeia de filtros drawtext e drawbox para FFmpeg."""
        if style_name not in cls.STYLES:
            style_name = "tech_cyber_bar"

        st = cls.STYLES[style_name]
        end_time = round(start_time + duration, 2)

        # Filtro de caixa de fundo semi-transparente com animação de fade
        enable_expr = f"between(t,{start_time},{end_time})"
        
        box_filter = (
            f"drawbox=x=80:y=H-180:w=640:h={st['bar_height']}:color={st['secondary_color']}@0.85:t=fill:enable='{enable_expr}'"
        )
        accent_line = (
            f"drawbox=x=80:y=H-180:w=8:h={st['bar_height']}:color={st['primary_color']}:t=fill:enable='{enable_expr}'"
        )
        title_text = (
            f"drawtext=text='{title}':x=105:y=H-165:fontsize={st['font_size']}:fontcolor=white:enable='{enable_expr}'"
        )
        sub_text = (
            f"drawtext=text='{subtitle}':x=105:y=H-135:fontsize={st['sub_font_size']}:fontcolor={st['primary_color']}:enable='{enable_expr}'"
            if subtitle else ""
        )

        filters = [box_filter, accent_line, title_text]
        if sub_text:
            filters.append(sub_text)

        full_filter_chain = ",".join(filters)

        return {
            "title": title,
            "subtitle": subtitle,
            "style_name": style_name,
            "style_details": st,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "ffmpeg_filter": full_filter_chain
        }

    @classmethod
    def generate_plan_lower_thirds(cls, plan: ProjectPlan, style_name: str = "tech_cyber_bar") -> Dict[str, Any]:
        """Gera lower thirds automáticos nos inícios de cada capítulo ou cena principal."""
        scenes = getattr(plan, "scenes", [])
        overlays = []
        current_time = 0.0

        for idx, scene in enumerate(scenes):
            duration = float(getattr(scene, "duration", 5.0))
            scene_title = getattr(scene, "title", "") or f"Capítulo {idx + 1}"
            concept = getattr(scene, "concept", "") or "Tópico Essencial"

            # Insere Lower Third na cena se tiver mais de 4s
            if duration >= 4.0:
                entry_time = round(current_time + 1.0, 1)
                lt = cls.generate_lower_third_overlay(
                    title=scene_title,
                    subtitle=concept,
                    style_name=style_name,
                    start_time=entry_time,
                    duration=min(4.5, duration - 1.0)
                )
                overlays.append(lt)

            current_time += duration

        return {
            "total_lower_thirds": len(overlays),
            "style_applied": style_name,
            "overlays": overlays
        }
