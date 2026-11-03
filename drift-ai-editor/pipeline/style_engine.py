from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class StyleProfile:
    id: str
    name: str
    description: str
    pacing_multiplier: float        # 0.7 (fast) to 1.4 (slow/contemplative)
    transition_type: str            # 'crossfade', 'dissolve', 'dip_to_black', 'hard_cut'
    transition_duration_ms: int     # e.g., 500ms
    ken_burns_intensity: float      # 1.0 (subtle) to 1.35 (dramatic)
    color_temperature: str          # 'warm', 'cool', 'neutral', 'vintage_sepia'
    subtitle_font: str              # 'Inter', 'Anton', 'Montserrat'
    subtitle_font_size: int         # pixels
    subtitle_color: str             # hex color
    subtitle_bg_color: str          # hex with alpha
    safe_zone_vertical_offset: int  # safety margin for TikTok/Reels UI buttons
    music_mood: str                 # 'ambient_calm', 'epic_cinematic', 'lofi_reflective'

class StyleEngine:
    """
    Directs visual storytelling identity, pacing rules, color themes,
    and safe-zone layouts for multi-platform distribution (YouTube 16:9, Shorts/Reels 9:16, Feed 1:1).
    """

    PROFILES: Dict[str, StyleProfile] = {
        "filosofico": StyleProfile(
            id="filosofico",
            name="Ensaio Filosófico / Estoicismo",
            description="Ritmo contemplativo, cortes suaves, cores neutras/quentes e zoom lento.",
            pacing_multiplier=1.25,
            transition_type="crossfade",
            transition_duration_ms=600,
            ken_burns_intensity=1.08,
            color_temperature="warm",
            subtitle_font="Inter",
            subtitle_font_size=42,
            subtitle_color="#F8FAFC",
            subtitle_bg_color="#800F172A",
            safe_zone_vertical_offset=180,
            music_mood="ambient_calm"
        ),
        "documentario": StyleProfile(
            id="documentario",
            name="Documentário Investigativo",
            description="Visual sóbrio, takes firmes, contraste acentuado e transições diretas.",
            pacing_multiplier=1.0,
            transition_type="crossfade",
            transition_duration_ms=400,
            ken_burns_intensity=1.12,
            color_temperature="cool",
            subtitle_font="Montserrat",
            subtitle_font_size=44,
            subtitle_color="#FFFFFF",
            subtitle_bg_color="#99000000",
            safe_zone_vertical_offset=160,
            music_mood="investigative_tension"
        ),
        "universo": StyleProfile(
            id="universo",
            name="Ciência e Universo (Cósmico)",
            description="Takes expansivos, câmera em movimento contínuo, transições longas e imersivas.",
            pacing_multiplier=1.3,
            transition_type="crossfade",
            transition_duration_ms=800,
            ken_burns_intensity=1.20,
            color_temperature="cool",
            subtitle_font="Inter",
            subtitle_font_size=46,
            subtitle_color="#E2E8F0",
            subtitle_bg_color="#80020617",
            safe_zone_vertical_offset=180,
            music_mood="cosmic_ambient"
        ),
        "autoconhecimento": StyleProfile(
            id="autoconhecimento",
            name="Autoconhecimento Premium",
            description="Iluminação suave, tons dourados/claros, ritmo equilibrado e foco na voz humana.",
            pacing_multiplier=1.1,
            transition_type="dissolve",
            transition_duration_ms=500,
            ken_burns_intensity=1.10,
            color_temperature="warm",
            subtitle_font="Inter",
            subtitle_font_size=42,
            subtitle_color="#FEF3C7",
            subtitle_bg_color="#801C1917",
            safe_zone_vertical_offset=170,
            music_mood="reflective_piano"
        ),
        "shorts_dinamico": StyleProfile(
            id="shorts_dinamico",
            name="Shorts & Reels Dinâmico (Alta Retenção)",
            description="Ritmo veloz, legendas centrais destacadas, safe zones para botões do app e cortes secos.",
            pacing_multiplier=0.85,
            transition_type="hard_cut",
            transition_duration_ms=0,
            ken_burns_intensity=1.25,
            color_temperature="neutral",
            subtitle_font="Anton",
            subtitle_font_size=56,
            subtitle_color="#FACC15",  # Vibrant yellow for retention
            subtitle_bg_color="#B3000000",
            safe_zone_vertical_offset=280,  # Avoid TikTok description and side buttons
            music_mood="upbeat_modern"
        )
    }

    @classmethod
    def get_profile(cls, profile_id: str) -> StyleProfile:
        return cls.PROFILES.get(profile_id, cls.PROFILES["filosofico"])

    @classmethod
    def adapt_for_aspect_ratio(
        cls,
        profile: StyleProfile,
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """
        Calculates safe-zone crop coordinates, subtitle margins, and animation limits
        to ensure no text or critical faces are obscured by TikTok/Reels/Shorts UI overlays.
        """
        if aspect_ratio == "9:16":
            # Mobile Vertical Video (Shorts / Reels / TikTok)
            return {
                "aspect_ratio": "9:16",
                "width": 1080,
                "height": 1920,
                "safe_zone_top": 240,       # Avoid top status bar and search
                "safe_zone_bottom": profile.safe_zone_vertical_offset, # Avoid title & comments bar
                "safe_zone_right": 140,     # Avoid like, comment, share icons
                "safe_zone_left": 40,
                "subtitle_bottom_margin": profile.safe_zone_vertical_offset + 40,
                "reframe_mode": "center_crop_zoom"
            }
        elif aspect_ratio == "1:1":
            # Square Feed
            return {
                "aspect_ratio": "1:1",
                "width": 1080,
                "height": 1080,
                "safe_zone_top": 80,
                "safe_zone_bottom": 120,
                "safe_zone_right": 60,
                "safe_zone_left": 60,
                "subtitle_bottom_margin": 140,
                "reframe_mode": "center_crop"
            }
        else:
            # 16:9 Landscape (YouTube Desktop / TV)
            return {
                "aspect_ratio": "16:9",
                "width": 1920,
                "height": 1080,
                "safe_zone_top": 60,
                "safe_zone_bottom": 80,
                "safe_zone_right": 80,
                "safe_zone_left": 80,
                "subtitle_bottom_margin": 90,
                "reframe_mode": "fill"
            }

