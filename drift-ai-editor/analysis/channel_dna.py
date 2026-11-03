from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pipeline.style_engine import StyleProfile

@dataclass
class ChannelDnaProfile:
    channel_name: str
    target_genre: str                # 'educational_motion', 'investigative_journalism', 'stoic_essay', 'tech_breakdown'
    cut_frequency_asd: float         # Average Shot Duration in seconds (e.g. 2.1s for fast, 4.8s for slow)
    dominant_color_palette: List[str] # Hex colors, e.g. ["#0f172a", "#38bdf8", "#facc15"]
    font_hierarchy: Dict[str, str]   # {"title": "Anton", "subtitle": "Inter", "caption": "Montserrat"}
    audio_density: str               # 'intense_sfx', 'minimal_ambient', 'dynamic_score'
    pacing_multiplier: float
    style_profile: StyleProfile

class ChannelDnaExtractor:
    """
    Channel Aesthetic DNA Cloner:
    Reverse-engineers the signature style of renowned YouTube channels and media brands:
      - 'Kurzgesagt': Vibrant color palette, animated accents, 2.4s fast educational pacing.
      - 'Vox': High-contrast documentary, clean Montserrat fonts, kinetic text highlights, 3.2s ASD.
      - 'Magnates': Luxury golden/black tones, dramatic Ken Burns zooms, 4.0s ASD.
      - 'Nerdwriter': Contemplative essayist, soft crossfades, deep focus, 5.5s ASD.
    """

    KNOWN_CHANNEL_PRESETS = {
        "vox": ChannelDnaProfile(
            channel_name="Vox Style (Investigativo Dinâmico)",
            target_genre="investigative_journalism",
            cut_frequency_asd=3.2,
            dominant_color_palette=["#000000", "#FFE600", "#FFFFFF"],
            font_hierarchy={"title": "Montserrat Black", "subtitle": "Montserrat", "caption": "Inter"},
            audio_density="dynamic_score",
            pacing_multiplier=0.9,
            style_profile=StyleProfile(
                id="channel_vox",
                name="Estilo Vox / Jornalístico",
                description="Contraste alto, cortes secos e legendas amarelas destacadas.",
                pacing_multiplier=0.9,
                transition_type="hard_cut",
                transition_duration_ms=0,
                ken_burns_intensity=1.15,
                color_temperature="neutral",
                subtitle_font="Montserrat",
                subtitle_font_size=46,
                subtitle_color="#FFE600",
                subtitle_bg_color="#99000000",
                safe_zone_vertical_offset=160,
                music_mood="investigative_tension"
            )
        ),
        "kurzgesagt": ChannelDnaProfile(
            channel_name="Kurzgesagt Style (Ciência Vibrante)",
            target_genre="educational_motion",
            cut_frequency_asd=2.4,
            dominant_color_palette=["#0B1B3D", "#00F5D4", "#7B2CBF"],
            font_hierarchy={"title": "Inter Bold", "subtitle": "Inter", "caption": "Inter"},
            audio_density="intense_sfx",
            pacing_multiplier=0.8,
            style_profile=StyleProfile(
                id="channel_kurzgesagt",
                name="Estilo Kurzgesagt / Ciência",
                description="Visual colorido, cortes ritmados e ritmo enérgico de aprendizado.",
                pacing_multiplier=0.8,
                transition_type="crossfade",
                transition_duration_ms=250,
                ken_burns_intensity=1.20,
                color_temperature="cool",
                subtitle_font="Inter",
                subtitle_font_size=48,
                subtitle_color="#00F5D4",
                subtitle_bg_color="#B30B1B3D",
                safe_zone_vertical_offset=180,
                music_mood="cosmic_ambient"
            )
        ),
        "nerdwriter": ChannelDnaProfile(
            channel_name="Nerdwriter Style (Vídeo-Ensaio Filosófico)",
            target_genre="stoic_essay",
            cut_frequency_asd=5.2,
            dominant_color_palette=["#1E1E1E", "#D4AF37", "#F3F4F6"],
            font_hierarchy={"title": "Lora", "subtitle": "Inter", "caption": "Inter"},
            audio_density="minimal_ambient",
            pacing_multiplier=1.25,
            style_profile=StyleProfile(
                id="channel_nerdwriter",
                name="Estilo Nerdwriter / Vídeo-Ensaio",
                description="Ritmo contemplativo, tom reflexivo e transições suaves de cinema.",
                pacing_multiplier=1.25,
                transition_type="crossfade",
                transition_duration_ms=700,
                ken_burns_intensity=1.06,
                color_temperature="warm",
                subtitle_font="Inter",
                subtitle_font_size=40,
                subtitle_color="#F3F4F6",
                subtitle_bg_color="#80000000",
                safe_zone_vertical_offset=150,
                music_mood="ambient_calm"
            )
        )
    }

    @classmethod
    def get_preset(cls, preset_id: str) -> Optional[ChannelDnaProfile]:
        return cls.KNOWN_CHANNEL_PRESETS.get(preset_id.lower().strip())

    @classmethod
    def list_presets(cls) -> List[Dict[str, Any]]:
        return [
            {
                "id": k,
                "name": v.channel_name,
                "genre": v.target_genre,
                "asd": v.cut_frequency_asd,
                "colors": v.dominant_color_palette
            }
            for k, v in cls.KNOWN_CHANNEL_PRESETS.items()
        ]

