"""
Aesthetic Theme Director for CutWire Drift AI.
Applies holistic production design themes across color grading (LUT), typography fonts,
caption animations, transitions, and audio mastering signatures.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from models.scene_plan import ProjectPlan

class AestheticTheme(str, Enum):
    CYBERPUNK_NEON = "cyberpunk_neon"
    VINTAGE_DOCUMENTARY = "vintage_documentary"
    NORDIC_MINIMALIST = "nordic_minimalist"
    SILICON_VALLEY_SAAS = "silicon_valley_saas"
    TRUE_CRIME_NOIR = "true_crime_noir"

@dataclass
class ThemePresetSpec:
    theme: AestheticTheme
    name: str
    description: str
    lut_filter: str
    font_family: str
    primary_accent_color: str
    default_transition: str
    audio_eq_profile: str

THEME_REGISTRY: Dict[AestheticTheme, ThemePresetSpec] = {
    AestheticTheme.CYBERPUNK_NEON: ThemePresetSpec(
        theme=AestheticTheme.CYBERPUNK_NEON,
        name="Cyberpunk Neon",
        description="High-contrast teal and magenta, futuristic fonts, hard kinetic cuts.",
        lut_filter="curves=all='0/0 0.5/0.45 1/1':blue='0/0.05 1/1':red='0/0 0.5/0.55 1/1'",
        font_family="Orbitron, Montserrat",
        primary_accent_color="#00FFAA",
        default_transition="glitch_cut",
        audio_eq_profile="bass_boost_sub"
    ),
    AestheticTheme.VINTAGE_DOCUMENTARY: ThemePresetSpec(
        theme=AestheticTheme.VINTAGE_DOCUMENTARY,
        name="Vintage Documentary",
        description="Warm sepia tones, serif typography, subtle film grain and gentle cross-dissolves.",
        lut_filter="curves=all='0/0.05 1/0.95':red='0/0.05 1/1':blue='0/0 1/0.90',noise=alls=6:allf=t+u",
        font_family="Merriweather, Playfair Display",
        primary_accent_color="#D4AF37",
        default_transition="cross_dissolve",
        audio_eq_profile="warm_tape_analog"
    ),
    AestheticTheme.NORDIC_MINIMALIST: ThemePresetSpec(
        theme=AestheticTheme.NORDIC_MINIMALIST,
        name="Nordic Minimalist",
        description="Clean desaturated cool tones, elegant modern sans-serif, clean whip cuts.",
        lut_filter="hue=s=0.85,curves=all='0/0.02 0.5/0.52 1/1'",
        font_family="Inter, Helvetica Neue",
        primary_accent_color="#FFFFFF",
        default_transition="whip_pan",
        audio_eq_profile="crystal_clean_podcast"
    ),
    AestheticTheme.SILICON_VALLEY_SAAS: ThemePresetSpec(
        theme=AestheticTheme.SILICON_VALLEY_SAAS,
        name="Silicon Valley SaaS",
        description="Vibrant tech blues and purples, bold punchy headings, smooth zooms.",
        lut_filter="eq=contrast=1.1:saturation=1.15",
        font_family="Plus Jakarta Sans, Poppins",
        primary_accent_color="#3B82F6",
        default_transition="slide_left",
        audio_eq_profile="modern_punch_master"
    ),
    AestheticTheme.TRUE_CRIME_NOIR: ThemePresetSpec(
        theme=AestheticTheme.TRUE_CRIME_NOIR,
        name="True Crime Noir",
        description="Moody shadows, crushed blacks, ominous red accents, cold audio presence.",
        lut_filter="curves=all='0/0 0.3/0.18 1/0.95':green='0/0 1/0.85'",
        font_family="Bebas Neue, Oswald",
        primary_accent_color="#E50914",
        default_transition="fade_to_black",
        audio_eq_profile="ominous_dark_ambience"
    ),
}

class AestheticThemeDirector:
    """
    Applies unified theme presets across all project scenes.
    """

    @classmethod
    def get_preset(cls, theme: AestheticTheme) -> ThemePresetSpec:
        return THEME_REGISTRY.get(theme, THEME_REGISTRY[AestheticTheme.NORDIC_MINIMALIST])

    @classmethod
    def apply_theme_to_project(cls, plan: ProjectPlan, theme: AestheticTheme) -> ThemePresetSpec:
        spec = cls.get_preset(theme)
        for sc in plan.scenes:
            curr_trans = getattr(sc, "transition", None)
            if not curr_trans or curr_trans == "hard_cut":
                sc.transition = spec.default_transition
        return spec
